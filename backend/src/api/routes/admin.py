"""Admin endpoints for feed inspection, content cleanup, and diagnostics."""

import re

from backend.src.api import schemas, state
from backend.src.api.dependencies import get_unit_of_work
from backend.src.infrastructure.models import NewsItem, Source
from backend.src.infrastructure.unit_of_work import UnitOfWork
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from shared.logging import get_logger
from sqlalchemy import func

logger = get_logger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin"])

# Tags that are legitimate semantic content — never flag or remove these.
_SEMANTIC_TAGS = frozenset({
    "p", "br", "hr",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li",
    "table", "thead", "tbody", "tfoot", "tr", "th", "td", "caption", "colgroup", "col",
    "a", "strong", "em", "b", "i", "u", "s", "code", "span", "sub", "sup", "mark",
    "blockquote", "pre", "figure", "figcaption", "img",
    "dl", "dt", "dd", "abbr", "cite", "q", "time",
})

# Tags whose content should be removed entirely (not just the tag, but everything inside).
_REMOVE_WITH_CONTENT_TAGS = frozenset({
    "script", "style", "noscript", "iframe", "object", "embed", "applet",
    "form", "input", "button", "select", "textarea",
    "svg", "math",
})

# Pattern to detect non-semantic HTML tags (excludes closing tags and semantic tags).
# Used for flagging: if an article contains tags outside the semantic whitelist, it has residue.
_RESIDUE_TAG_PATTERN = re.compile(r"</?([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>")

# Patterns for cleanup: remove dangerous tags with their content, then strip remaining non-semantic tags.
_REMOVE_WITH_CONTENT_PATTERN = re.compile(
    r"<(" + "|".join(_REMOVE_WITH_CONTENT_TAGS) + r")\b[^>]*>[\s\S]*?</\1>",
    re.IGNORECASE,
)
_NON_SEMANTIC_TAG_PATTERN = re.compile(r"</?([a-zA-Z][a-zA-Z0-9]*)\b[^>]*/?>")


def _has_html_residue(text: str) -> bool:
    """Check if text contains non-semantic HTML tags."""
    for match in _RESIDUE_TAG_PATTERN.finditer(text):
        tag_name = match.group(1).lower()
        if tag_name not in _SEMANTIC_TAGS:
            return True
    return False


def _clean_html_residue(text: str) -> str:
    """Remove non-semantic HTML while preserving structural markup."""
    # First: remove dangerous tags with all their content
    cleaned = _REMOVE_WITH_CONTENT_PATTERN.sub("", text)

    # Second: strip remaining non-semantic tags (tag only, not content)
    def _replace_non_semantic(match: re.Match[str]) -> str:
        tag_name = match.group(1).lower()
        if tag_name in _SEMANTIC_TAGS:
            return match.group(0)  # keep semantic tags
        return ""

    cleaned = _NON_SEMANTIC_TAG_PATTERN.sub(_replace_non_semantic, cleaned)

    # Clean up excessive whitespace left by removals
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


# ==================== FEED INSPECTOR ====================


@router.get("/sources/{source_id}/preview", response_model=list[schemas.NewsPreviewResponse])
async def preview_source(
    source_id: int,
    limit: int = 20,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Preview last N articles from a specific source."""
    source = uow.source_repository.get_by_id(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    items = (
        uow._db.query(NewsItem)
        .filter(NewsItem.source_id == source_id)
        .order_by(NewsItem.published_at.desc())
        .limit(limit)
        .all()
    )

    return [
        schemas.NewsPreviewResponse(
            id=item.id,
            title=item.title,
            published_at=item.published_at,
            snippet=(item.content[:200] + "...") if item.content and len(item.content) > 200 else item.content,
        )
        for item in items
    ]


@router.get("/sources/{source_id}/stats", response_model=schemas.SourceStatsResponse)
async def source_stats(
    source_id: int,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Get statistics for a specific source."""
    source = uow.source_repository.get_by_id(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    db = uow._db
    row = (
        db.query(
            func.count(NewsItem.id).label("count"),
            func.min(NewsItem.published_at).label("earliest"),
            func.max(NewsItem.published_at).label("latest"),
            func.avg(func.length(NewsItem.content)).label("avg_length"),
        )
        .filter(NewsItem.source_id == source_id)
        .one()
    )

    return schemas.SourceStatsResponse(
        source_id=source_id,
        source_name=source.name,
        article_count=row.count,
        earliest_article=row.earliest,
        latest_article=row.latest,
        avg_content_length=round(row.avg_length) if row.avg_length else None,
        last_fetched=source.last_fetched,
        is_active=source.is_active,
    )


# ==================== CONTENT CLEANUP ====================


@router.post("/sources/{source_id}/purge", response_model=schemas.CleanupResultResponse)
async def purge_source(
    source_id: int,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Delete all articles for a source (keeps the source record)."""
    source = uow.source_repository.get_by_id(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    count = (
        uow._db.query(NewsItem)
        .filter(NewsItem.source_id == source_id)
        .delete(synchronize_session="fetch")
    )
    uow.commit()

    logger.info(f"Purged {count} articles from source {source_id} ({source.name})")

    if state.cache:
        state.cache.delete("news:*")

    return schemas.CleanupResultResponse(
        matched=count,
        deleted=count,
        dry_run=False,
    )


@router.post("/sources/{source_id}/reimport", response_model=schemas.ReimportResultResponse)
async def reimport_source(
    source_id: int,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Purge all articles for a source and trigger immediate re-import."""
    from backend.src.infrastructure.feed_parser import FeedParserService

    source = uow.source_repository.get_by_id(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    # Purge
    purged = (
        uow._db.query(NewsItem)
        .filter(NewsItem.source_id == source_id)
        .delete(synchronize_session="fetch")
    )
    uow.commit()
    logger.info(f"Purged {purged} articles from source {source_id} before reimport")

    # Re-import
    parser = FeedParserService(uow)
    imported = parser.parse_and_import(source)
    logger.info(f"Reimported {imported} articles for source {source_id} ({source.name})")

    if state.cache:
        state.cache.delete("news:*")

    return schemas.ReimportResultResponse(
        purged=purged,
        imported=imported,
    )


@router.post("/sources/{source_id}/fetch-content")
async def bulk_fetch_content(
    source_id: int,
    force: bool = False,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> StreamingResponse:
    """Fetch full article content for all articles of a source.

    Streams progress as newline-delimited JSON (NDJSON). Each line is a JSON object:
    - Progress: {"current": 3, "total": 42, "title": "...", "status": "fetched"|"skipped"|"failed"}
    - Final:    {"done": true, "fetched": 30, "skipped": 8, "failed": 4, "total": 42}

    Scrapes articles that have no substantial content (< 500 chars) unless force=True.
    """
    import asyncio
    import json

    from backend.src.infrastructure.content_scraper import ContentScraper

    source = uow.source_repository.get_by_id(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    items = (
        uow._db.query(NewsItem)
        .filter(NewsItem.source_id == source_id)
        .order_by(NewsItem.published_at.desc())
        .all()
    )

    async def generate():  # type: ignore[no-untyped-def]
        scraper = ContentScraper()
        fetched = 0
        skipped = 0
        failed = 0
        total = len(items)

        for i, item in enumerate(items, 1):
            title = (item.title[:60] + "...") if len(item.title) > 60 else item.title

            # Skip articles without a URL
            if not item.external_id:
                skipped += 1
                yield json.dumps(
                    {"current": i, "total": total, "title": title, "status": "skipped"}
                ) + "\n"
                continue

            # Skip articles that already have substantial content (unless force)
            if not force and item.content and len(item.content) > 500:
                skipped += 1
                yield json.dumps(
                    {"current": i, "total": total, "title": title, "status": "skipped"}
                ) + "\n"
                continue

            try:
                content = await scraper.fetch_article_content(item.external_id)
                if content and not content.startswith(
                    "Impossibile"
                ) and not content.startswith("Servizio"):
                    item.content = content
                    fetched += 1
                    yield json.dumps(
                        {"current": i, "total": total, "title": title, "status": "fetched"}
                    ) + "\n"
                else:
                    failed += 1
                    yield json.dumps(
                        {"current": i, "total": total, "title": title, "status": "failed"}
                    ) + "\n"
            except Exception:
                logger.warning(f"Bulk fetch failed for article {item.id}: {item.external_id}")
                failed += 1
                yield json.dumps(
                    {"current": i, "total": total, "title": title, "status": "failed"}
                ) + "\n"

            # Polite delay between requests
            await asyncio.sleep(0.5)

        if fetched > 0:
            uow.commit()
            logger.info(
                f"Bulk fetch for source {source_id} ({source.name}): "
                f"{fetched} fetched, {skipped} skipped, {failed} failed"
            )

            if state.cache:
                state.cache.delete("news:*")

        yield json.dumps(
            {"done": True, "total": total, "fetched": fetched, "skipped": skipped, "failed": failed}
        ) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")


@router.post("/cleanup/by-pattern", response_model=schemas.CleanupResultResponse)
async def cleanup_by_pattern(
    request: schemas.PatternCleanupRequest,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Delete articles matching a title or content pattern (with dry-run mode)."""
    column = NewsItem.title if request.field == "title" else NewsItem.content
    query = uow._db.query(NewsItem).filter(column.ilike(f"%{request.pattern}%"))

    if request.source_id is not None:
        query = query.filter(NewsItem.source_id == request.source_id)

    matched = query.count()

    if request.dry_run:
        return schemas.CleanupResultResponse(
            matched=matched,
            deleted=0,
            dry_run=True,
        )

    deleted = query.delete(synchronize_session="fetch")
    uow.commit()
    logger.info(
        f"Pattern cleanup: deleted {deleted} articles matching '{request.pattern}' in {request.field}"
    )

    if state.cache:
        state.cache.delete("news:*")

    return schemas.CleanupResultResponse(
        matched=matched,
        deleted=deleted,
        dry_run=False,
    )


@router.post("/cleanup/html-residue", response_model=schemas.HtmlResidueResultResponse)
async def cleanup_html_residue(
    dry_run: bool = True,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Find and fix articles with non-semantic HTML tags in content or summary.

    Preserves structural markup (p, h1-h6, ul/ol/li, table, a, strong, em, etc.)
    while removing non-content tags (script, style, iframe, form, div, span classes, etc.).
    Dangerous tags (script, style, iframe) are removed with their content.
    """
    db = uow._db
    all_items = db.query(NewsItem).all()

    flagged: list[schemas.HtmlResidueFlagResponse] = []
    fixed_count = 0

    for item in all_items:
        for field_name in ("content", "summary"):
            value = getattr(item, field_name)
            if value and _has_html_residue(value):
                flagged.append(
                    schemas.HtmlResidueFlagResponse(
                        id=item.id,
                        title=item.title,
                        field=field_name,
                    )
                )
                if not dry_run:
                    cleaned = _clean_html_residue(value)
                    setattr(item, field_name, cleaned)
                    fixed_count += 1

    if not dry_run and fixed_count > 0:
        uow.commit()
        logger.info(f"HTML residue cleanup: fixed {fixed_count} fields across {len(flagged)} flags")

        if state.cache:
            state.cache.delete("news:*")

    return schemas.HtmlResidueResultResponse(
        flagged=flagged,
        fixed=fixed_count,
        dry_run=dry_run,
    )


@router.post("/cleanup/orphans", response_model=schemas.CleanupResultResponse)
async def cleanup_orphans(
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Delete articles whose source_id references a non-existent source."""
    db = uow._db
    source_ids_select = db.query(Source.id).scalar_subquery()
    orphan_query = db.query(NewsItem).filter(~NewsItem.source_id.in_(source_ids_select))

    matched = orphan_query.count()
    deleted = orphan_query.delete(synchronize_session="fetch")
    uow.commit()

    if deleted > 0:
        logger.info(f"Orphan cleanup: deleted {deleted} articles with no matching source")

        if state.cache:
            state.cache.delete("news:*")

    return schemas.CleanupResultResponse(
        matched=matched,
        deleted=deleted,
        dry_run=False,
    )


# ==================== DIAGNOSTICS ====================


@router.get("/stats", response_model=schemas.GlobalStatsResponse)
async def global_stats(
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Get global database statistics."""
    db = uow._db

    total_articles = db.query(func.count(NewsItem.id)).scalar() or 0
    total_sources = db.query(func.count(Source.id)).scalar() or 0

    per_source = (
        db.query(
            Source.id,
            Source.name,
            func.count(NewsItem.id).label("count"),
        )
        .outerjoin(NewsItem, NewsItem.source_id == Source.id)
        .group_by(Source.id, Source.name)
        .order_by(func.count(NewsItem.id).desc())
        .all()
    )

    return schemas.GlobalStatsResponse(
        total_articles=total_articles,
        total_sources=total_sources,
        per_source=[
            schemas.PerSourceCountResponse(
                source_id=row.id,
                source_name=row.name,
                article_count=row.count,
            )
            for row in per_source
        ],
    )


@router.get("/quality-report", response_model=schemas.QualityReportResponse)
async def quality_report(
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Flag suspicious content: short, long, HTML residue, duplicate titles, empty sources."""
    db = uow._db

    # Short content (< 50 chars)
    short = (
        db.query(NewsItem.id, NewsItem.title, func.length(NewsItem.content).label("length"))
        .filter(NewsItem.content.isnot(None), func.length(NewsItem.content) < 50)
        .all()
    )

    # Long content (> 50000 chars)
    long = (
        db.query(NewsItem.id, NewsItem.title, func.length(NewsItem.content).label("length"))
        .filter(func.length(NewsItem.content) > 50000)
        .all()
    )

    # HTML residue in content or summary (only non-semantic tags)
    all_items = db.query(NewsItem.id, NewsItem.title, NewsItem.content, NewsItem.summary).all()
    html_residue = []
    for item in all_items:
        if item.content and _has_html_residue(item.content):
            html_residue.append(
                schemas.HtmlResidueFlagResponse(id=item.id, title=item.title, field="content")
            )
        if item.summary and _has_html_residue(item.summary):
            html_residue.append(
                schemas.HtmlResidueFlagResponse(id=item.id, title=item.title, field="summary")
            )

    # Duplicate titles within same source
    dupes = (
        db.query(NewsItem.title, NewsItem.source_id, func.count(NewsItem.id).label("count"))
        .group_by(NewsItem.title, NewsItem.source_id)
        .having(func.count(NewsItem.id) > 1)
        .all()
    )

    # Sources with 0 articles
    source_ids_with_articles = db.query(NewsItem.source_id).distinct().scalar_subquery()
    empty_sources = (
        db.query(Source.id, Source.name)
        .filter(~Source.id.in_(source_ids_with_articles))
        .all()
    )

    return schemas.QualityReportResponse(
        total_articles=db.query(func.count(NewsItem.id)).scalar() or 0,
        total_sources=db.query(func.count(Source.id)).scalar() or 0,
        short_content=[
            schemas.ContentLengthFlagResponse(id=r.id, title=r.title, length=r.length)
            for r in short
        ],
        long_content=[
            schemas.ContentLengthFlagResponse(id=r.id, title=r.title, length=r.length)
            for r in long
        ],
        html_residue=html_residue,
        duplicate_titles=[
            schemas.DuplicateTitleResponse(title=r.title, source_id=r.source_id, count=r.count)
            for r in dupes
        ],
        empty_sources=[
            schemas.EmptySourceResponse(id=r.id, name=r.name)
            for r in empty_sources
        ],
    )
