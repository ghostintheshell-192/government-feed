"""Admin endpoints for feed inspection, content cleanup, and diagnostics."""

import re

from backend.src.api import schemas, state
from backend.src.api.dependencies import get_unit_of_work
from backend.src.infrastructure.models import NewsItem, Source
from backend.src.infrastructure.unit_of_work import UnitOfWork
from fastapi import APIRouter, Depends, HTTPException
from shared.logging import get_logger
from sqlalchemy import func

logger = get_logger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin"])

_HTML_TAG_PATTERN = re.compile(r"<[a-zA-Z][^>]*>")


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
    parser = FeedParserService(uow._db)
    imported = parser.parse_and_import(source)
    logger.info(f"Reimported {imported} articles for source {source_id} ({source.name})")

    if state.cache:
        state.cache.delete("news:*")

    return schemas.ReimportResultResponse(
        purged=purged,
        imported=imported,
    )


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
    """Find and fix articles with HTML tags in content or summary."""
    db = uow._db
    all_items = db.query(NewsItem).all()

    flagged: list[schemas.HtmlResidueFlagResponse] = []
    fixed_count = 0

    for item in all_items:
        for field_name in ("content", "summary"):
            value = getattr(item, field_name)
            if value and _HTML_TAG_PATTERN.search(value):
                flagged.append(
                    schemas.HtmlResidueFlagResponse(
                        id=item.id,
                        title=item.title,
                        field=field_name,
                    )
                )
                if not dry_run:
                    cleaned = _HTML_TAG_PATTERN.sub("", value)
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

    # HTML residue in content or summary
    all_items = db.query(NewsItem.id, NewsItem.title, NewsItem.content, NewsItem.summary).all()
    html_residue = []
    for item in all_items:
        if item.content and _HTML_TAG_PATTERN.search(item.content):
            html_residue.append(
                schemas.HtmlResidueFlagResponse(id=item.id, title=item.title, field="content")
            )
        if item.summary and _HTML_TAG_PATTERN.search(item.summary):
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
