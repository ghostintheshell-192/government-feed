"""News item endpoints."""

import json
from datetime import datetime

from backend.src.api import schemas, state
from backend.src.api.dependencies import get_unit_of_work
from backend.src.infrastructure.unit_of_work import UnitOfWork
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("", response_model=schemas.PaginatedNewsResponse)
async def get_news(
    limit: int = 20,
    offset: int = 0,
    source_id: list[int] | None = Query(None),
    search: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Get recent news items with pagination and filters."""
    cache_key = f"news:{limit}:{offset}:{source_id}:{search}:{date_from}:{date_to}"

    if state.cache:
        cached = state.cache.get(cache_key)
        if cached:
            return JSONResponse(content=json.loads(cached))

    items, total = uow.news_repository.get_recent(
        limit=limit,
        offset=offset,
        source_ids=source_id,
        search=search,
        date_from=date_from,
        date_to=date_to,
    )

    result = schemas.PaginatedNewsResponse(
        items=[schemas.NewsItemResponse.model_validate(n) for n in items],
        pagination=schemas.PaginationMeta(
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total,
        ),
    )

    if state.cache:
        state.cache.set(cache_key, result.model_dump_json(), ttl=300)

    return result


@router.get("/{news_id}", response_model=schemas.NewsItemResponse)
async def get_news_item(news_id: int, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Get news item by ID."""
    if state.cache:
        cached = state.cache.get(f"news:{news_id}")
        if cached:
            return JSONResponse(content=json.loads(cached))

    news = uow.news_repository.get_by_id(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")

    result = schemas.NewsItemResponse.model_validate(news).model_dump(mode="json")

    if state.cache:
        state.cache.set(f"news:{news_id}", json.dumps(result), ttl=300)

    return news


@router.post("/{news_id}/fetch-content")
async def fetch_news_content(
    news_id: int, force: bool = False, uow: UnitOfWork = Depends(get_unit_of_work)
):
    """Fetch full article content from source URL."""
    from backend.src.infrastructure.content_scraper import ContentScraper

    news = uow.news_repository.get_by_id(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")

    if not news.external_id:
        raise HTTPException(status_code=400, detail="Nessun URL disponibile per questo articolo")

    # If we already have substantial content, return it without re-scraping
    if not force and news.content and len(news.content) > 500:
        return {"success": True, "content": news.content}

    scraper = ContentScraper()
    content = await scraper.fetch_article_content(news.external_id)

    if not content or content.startswith("Impossibile") or content.startswith("Servizio"):
        return {"success": False, "message": content or "Impossibile recuperare il contenuto"}

    # Save scraped content to database
    news.content = content
    uow.news_repository.update(news)
    uow.commit()

    if state.cache:
        state.cache.delete(f"news:{news_id}")
        state.cache.delete("news:*")

    return {"success": True, "content": content}
