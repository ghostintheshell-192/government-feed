"""Source management endpoints."""

import json

from backend.src.api import schemas, state
from backend.src.api.dependencies import get_unit_of_work
from backend.src.infrastructure.models import Source, Subscription
from backend.src.infrastructure.unit_of_work import UnitOfWork
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/sources", tags=["sources"])

# Default user ID for single-user mode (M5 will replace with auth)
_USER_ID = 1


@router.get("", response_model=list[schemas.SourceResponse])
async def get_sources(uow: UnitOfWork = Depends(get_unit_of_work)):
    """Get subscribed sources only."""
    if state.cache:
        cached = state.cache.get("sources:all")
        if cached:
            return JSONResponse(content=json.loads(cached))

    subscribed_ids = uow.subscription_repository.get_subscribed_source_ids(_USER_ID)
    sources = uow.source_repository.get_by_ids(subscribed_ids)
    result = [schemas.SourceResponse.model_validate(s).model_dump(mode="json") for s in sources]

    if state.cache:
        state.cache.set("sources:all", json.dumps(result), ttl=3600)

    return result


@router.get("/{source_id}", response_model=schemas.SourceResponse)
async def get_source(source_id: int, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Get source by ID."""
    if state.cache:
        cached = state.cache.get(f"source:{source_id}")
        if cached:
            return JSONResponse(content=json.loads(cached))

    source = uow.source_repository.get_by_id(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    result = schemas.SourceResponse.model_validate(source).model_dump(mode="json")

    if state.cache:
        state.cache.set(f"source:{source_id}", json.dumps(result), ttl=3600)

    return source


@router.post("", response_model=schemas.SourceResponse, status_code=201)
async def create_source(source: schemas.SourceCreate, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Create new source and auto-subscribe."""
    logger.info(f"Creating new source: {source.name}")
    db_source = Source(**source.model_dump())
    uow.source_repository.add(db_source)
    uow._db.flush()  # get the ID before creating subscription

    sub = Subscription(user_id=_USER_ID, source_id=db_source.id)
    uow.subscription_repository.add(sub)
    uow.commit()
    logger.info(f"Source created and subscribed: ID={db_source.id}, name={db_source.name}")

    if state.cache:
        state.cache.delete("sources:all")
        state.cache.delete("news:*")

    return db_source


@router.put("/{source_id}", response_model=schemas.SourceResponse)
async def update_source(
    source_id: int, source: schemas.SourceUpdate, uow: UnitOfWork = Depends(get_unit_of_work)
):
    """Update source."""
    db_source = uow.source_repository.get_by_id(source_id)
    if not db_source:
        logger.warning(f"Update failed: Source {source_id} not found")
        raise HTTPException(status_code=404, detail="Source not found")

    logger.info(f"Updating source: ID={source_id}, name={db_source.name}")
    for key, value in source.model_dump().items():
        setattr(db_source, key, value)

    uow.source_repository.update(db_source)
    uow.commit()
    logger.info(f"Source updated successfully: ID={source_id}")

    if state.cache:
        state.cache.delete(f"source:{source_id}")
        state.cache.delete("sources:all")

    return db_source


@router.delete("/{source_id}", status_code=204)
async def delete_source(source_id: int, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Unsubscribe from source and clean up news items."""
    sub = uow.subscription_repository.get_by_user_and_source(_USER_ID, source_id)
    if not sub:
        logger.warning(f"Unsubscribe failed: no subscription for source {source_id}")
        raise HTTPException(status_code=404, detail="Subscription not found")

    deleted_news = uow.news_repository.delete_by_source_id(source_id)
    uow.subscription_repository.delete(sub)
    uow.commit()
    logger.info(
        "Unsubscribed from source %d: removed subscription + %d news items",
        source_id, deleted_news,
    )

    if state.cache:
        state.cache.delete(f"source:{source_id}")
        state.cache.delete("sources:all")
        state.cache.delete("news:*")

    return None


@router.post("/discover", response_model=schemas.FeedDiscoveryResponse)
async def discover_feeds(request: schemas.FeedDiscoveryRequest):
    """Discover RSS/Atom feeds from a URL or search query."""
    from backend.src.infrastructure.feed_discovery import FeedDiscoveryService

    logger.info("Feed discovery requested for: %s", request.query)
    service = FeedDiscoveryService()
    feeds, searched_sites = await service.discover(request.query)

    logger.info("Feed discovery found %d feeds from %d sites", len(feeds), len(searched_sites))
    return schemas.FeedDiscoveryResponse(
        feeds=[
            schemas.DiscoveredFeedResponse(
                url=f.url,
                title=f.title,
                feed_type=f.feed_type,
                site_url=f.site_url,
                entry_count=f.entry_count,
            )
            for f in feeds
        ],
        searched_sites=searched_sites,
    )


@router.post("/{source_id}/process")
async def process_feed(source_id: int, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Process feed and import news."""
    from backend.src.infrastructure.feed_parser import FeedParserService

    source = uow.source_repository.get_by_id(source_id)
    if not source:
        logger.warning(f"Process feed failed: Source {source_id} not found")
        raise HTTPException(status_code=404, detail="Source not found")

    logger.info(f"Processing feed for source: ID={source_id}, name={source.name}")
    parser = FeedParserService(uow)
    try:
        imported_count = parser.parse_and_import(source)
    except Exception:
        logger.exception(f"Error processing feed for source {source_id}")
        return {"success": False, "error": True, "message": "Errore nel caricamento del feed."}

    if imported_count > 0:
        logger.info(
            f"Feed processed successfully: {imported_count} news items imported from {source.name}"
        )

        if state.cache:
            state.cache.delete("news:*")

        return {
            "success": True,
            "error": False,
            "message": f"Feed importato con successo! {imported_count} notizie aggiunte.",
        }
    else:
        logger.info(f"No new items from {source.name}")
        return {"success": False, "error": False, "message": "Nessuna nuova notizia trovata."}
