"""Catalog endpoints for browsing and subscribing to sources."""

from backend.src.api import schemas, state
from backend.src.api.dependencies import get_unit_of_work
from backend.src.infrastructure.models import Source, Subscription
from backend.src.infrastructure.unit_of_work import UnitOfWork
from fastapi import APIRouter, Depends, HTTPException
from shared.logging import get_logger
from sqlalchemy import func

logger = get_logger(__name__)
router = APIRouter(prefix="/api/catalog", tags=["catalog"])

# Default user ID for single-user mode (M5 will replace with auth)
_USER_ID = 1


@router.get("", response_model=schemas.PaginatedCatalogResponse)
async def browse_catalog(
    limit: int = 20,
    offset: int = 0,
    geographic_level: str | None = None,
    search: str | None = None,
    tag: str | None = None,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Browse all sources in the catalog with optional filters."""
    db = uow._db
    query = db.query(Source)

    if geographic_level:
        query = query.filter(Source.geographic_level == geographic_level.upper())

    if search and search.strip():
        search_lower = search.lower()
        query = query.filter(
            (Source.name.ilike(f"%{search_lower}%"))
            | (Source.description.ilike(f"%{search_lower}%"))
        )

    if tag and tag.strip():
        # JSON array contains — SQLite uses json_each for this
        query = query.filter(Source.tags.contains(tag))

    total = query.count()
    sources = query.order_by(Source.name).offset(offset).limit(limit).all()

    # Get user's subscribed source IDs for marking
    subscribed_ids = set(uow.subscription_repository.get_subscribed_source_ids(_USER_ID))

    items = [
        schemas.CatalogSourceResponse(
            id=s.id,
            name=s.name,
            description=s.description,
            feed_url=s.feed_url,
            source_type=s.source_type,
            category=s.category,
            geographic_level=s.geographic_level,
            country_code=s.country_code,
            region=s.region,
            tags=s.tags or [],
            is_curated=s.is_curated,
            is_subscribed=s.id in subscribed_ids,
        )
        for s in sources
    ]

    return schemas.PaginatedCatalogResponse(
        items=items,
        pagination=schemas.PaginationMeta(
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total,
        ),
    )


@router.get("/stats", response_model=schemas.CatalogStatsResponse)
async def catalog_stats(uow: UnitOfWork = Depends(get_unit_of_work)):
    """Get catalog statistics: counts by geographic level and top tags."""
    db = uow._db

    total = db.query(func.count(Source.id)).scalar() or 0

    # Count by geographic level
    level_rows = (
        db.query(Source.geographic_level, func.count(Source.id))
        .filter(Source.geographic_level.isnot(None))
        .group_by(Source.geographic_level)
        .all()
    )
    by_level = {row[0]: row[1] for row in level_rows}

    # Top tags — collect all tags and count
    all_sources = db.query(Source.tags).filter(Source.tags.isnot(None)).all()
    tag_counts: dict[str, int] = {}
    for (tags,) in all_sources:
        if isinstance(tags, list):
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
    top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:20]

    return schemas.CatalogStatsResponse(
        total_sources=total,
        by_geographic_level=by_level,
        top_tags=top_tags,
    )


@router.post("/{source_id}/subscribe", response_model=schemas.SubscriptionResponse, status_code=201)
async def subscribe(source_id: int, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Subscribe to a catalog source."""
    source = uow.source_repository.get_by_id(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    existing = uow.subscription_repository.get_by_user_and_source(_USER_ID, source_id)
    if existing:
        raise HTTPException(status_code=409, detail="Already subscribed")

    sub = Subscription(user_id=_USER_ID, source_id=source_id)
    uow.subscription_repository.add(sub)
    uow.commit()
    logger.info("User %d subscribed to source %d (%s)", _USER_ID, source_id, source.name)

    if state.cache:
        state.cache.delete("sources:all")
        state.cache.delete("news:*")

    return sub


@router.delete("/{source_id}/subscribe", status_code=204)
async def unsubscribe(source_id: int, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Unsubscribe from a catalog source."""
    sub = uow.subscription_repository.get_by_user_and_source(_USER_ID, source_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    deleted_news = uow.news_repository.delete_by_source_id(source_id)
    uow.subscription_repository.delete(sub)
    uow.commit()
    logger.info(
        "User %d unsubscribed from source %d, deleted %d news items",
        _USER_ID, source_id, deleted_news,
    )

    if state.cache:
        state.cache.delete("sources:all")
        state.cache.delete("news:*")

    return None
