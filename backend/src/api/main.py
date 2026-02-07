"""FastAPI main application."""

import json

from backend.src.api import schemas
from backend.src.api.dependencies import get_unit_of_work
from backend.src.infrastructure.cache import RedisCache
from backend.src.infrastructure.database import init_db
from backend.src.infrastructure.models import Source
from backend.src.infrastructure.scheduler import FeedScheduler
from backend.src.infrastructure.settings_store import load_settings
from backend.src.infrastructure.unit_of_work import UnitOfWork
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from shared.logging import get_logger

logger = get_logger(__name__)
_scheduler: FeedScheduler | None = None
_cache: RedisCache | None = None

app = FastAPI(
    title="Government Feed API",
    description="Aggregator for institutional news and government communications",
    version="0.1.0",
)

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database, cache, and scheduler on startup."""
    global _scheduler, _cache
    logger.info("Starting Government Feed API")
    init_db()
    logger.info("Database initialized successfully")

    settings = load_settings()

    redis_url = settings.get("redis_url", "redis://localhost:6379")
    _cache = RedisCache(url=redis_url)
    if _cache.is_available():
        logger.info("Redis cache enabled")
    else:
        logger.info("Redis cache not available, running without cache")

    if settings.get("scheduler_enabled", True):
        _scheduler = FeedScheduler()
        _scheduler.start()
        logger.info("Background scheduler started")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown scheduler gracefully."""
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown()
        _scheduler = None
        logger.info("Background scheduler stopped")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Government Feed API", "version": "0.1.0", "status": "running"}


# ==================== SOURCES ENDPOINTS ====================


@app.get("/api/sources", response_model=list[schemas.SourceResponse])
async def get_sources(uow: UnitOfWork = Depends(get_unit_of_work)):
    """Get all sources."""
    if _cache:
        cached = _cache.get("sources:all")
        if cached:
            return JSONResponse(content=json.loads(cached))

    sources = uow.source_repository.get_all()
    result = [schemas.SourceResponse.model_validate(s).model_dump(mode="json") for s in sources]

    if _cache:
        _cache.set("sources:all", json.dumps(result), ttl=3600)

    return result


@app.get("/api/sources/{source_id}", response_model=schemas.SourceResponse)
async def get_source(source_id: int, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Get source by ID."""
    if _cache:
        cached = _cache.get(f"source:{source_id}")
        if cached:
            return JSONResponse(content=json.loads(cached))

    source = uow.source_repository.get_by_id(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    result = schemas.SourceResponse.model_validate(source).model_dump(mode="json")

    if _cache:
        _cache.set(f"source:{source_id}", json.dumps(result), ttl=3600)

    return source


@app.post("/api/sources", response_model=schemas.SourceResponse, status_code=201)
async def create_source(source: schemas.SourceCreate, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Create new source."""
    logger.info(f"Creating new source: {source.name}")
    db_source = Source(**source.model_dump())
    uow.source_repository.add(db_source)
    uow.commit()
    logger.info(f"Source created successfully: ID={db_source.id}, name={db_source.name}")

    if _cache:
        _cache.delete("sources:all")

    return db_source


@app.put("/api/sources/{source_id}", response_model=schemas.SourceResponse)
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

    if _cache:
        _cache.delete(f"source:{source_id}")
        _cache.delete("sources:all")

    return db_source


@app.delete("/api/sources/{source_id}", status_code=204)
async def delete_source(source_id: int, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Delete source."""
    db_source = uow.source_repository.get_by_id(source_id)
    if not db_source:
        logger.warning(f"Delete failed: Source {source_id} not found")
        raise HTTPException(status_code=404, detail="Source not found")

    logger.info(f"Deleting source: ID={source_id}, name={db_source.name}")
    uow.source_repository.delete(db_source)
    uow.commit()
    logger.info(f"Source deleted successfully: ID={source_id}")

    if _cache:
        _cache.delete(f"source:{source_id}")
        _cache.delete("sources:all")

    return None


@app.post("/api/sources/{source_id}/process")
async def process_feed(source_id: int, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Process feed and import news."""
    from backend.src.infrastructure.feed_parser import FeedParserService

    source = uow.source_repository.get_by_id(source_id)
    if not source:
        logger.warning(f"Process feed failed: Source {source_id} not found")
        raise HTTPException(status_code=404, detail="Source not found")

    logger.info(f"Processing feed for source: ID={source_id}, name={source.name}")
    # Note: FeedParserService still uses db directly - will be refactored separately
    parser = FeedParserService(uow._db)
    imported_count = parser.parse_and_import(source)

    if imported_count > 0:
        logger.info(f"Feed processed successfully: {imported_count} news items imported from {source.name}")

        if _cache:
            _cache.delete("news:recent:*")

        return {
            "success": True,
            "message": f"Feed importato con successo! {imported_count} notizie aggiunte.",
        }
    else:
        logger.warning(f"Feed processing completed with no new items from {source.name}")
        return {"success": False, "message": "Nessuna nuova notizia trovata o errore nel parsing."}


# ==================== NEWS ENDPOINTS ====================


@app.get("/api/news", response_model=list[schemas.NewsItemResponse])
async def get_news(limit: int = 50, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Get recent news items."""
    cache_key = f"news:recent:{limit}"

    if _cache:
        cached = _cache.get(cache_key)
        if cached:
            return JSONResponse(content=json.loads(cached))

    news = uow.news_repository.get_recent(limit)
    result = [schemas.NewsItemResponse.model_validate(n).model_dump(mode="json") for n in news]

    if _cache:
        _cache.set(cache_key, json.dumps(result), ttl=300)

    return result


@app.get("/api/news/{news_id}", response_model=schemas.NewsItemResponse)
async def get_news_item(news_id: int, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Get news item by ID."""
    if _cache:
        cached = _cache.get(f"news:{news_id}")
        if cached:
            return JSONResponse(content=json.loads(cached))

    news = uow.news_repository.get_by_id(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")

    result = schemas.NewsItemResponse.model_validate(news).model_dump(mode="json")

    if _cache:
        _cache.set(f"news:{news_id}", json.dumps(result), ttl=300)

    return news


# ==================== SETTINGS ENDPOINTS ====================


@app.get("/api/settings")
async def get_settings():
    """Get application settings."""
    from backend.src.infrastructure.settings_store import load_settings

    return load_settings()


@app.put("/api/settings")
async def update_settings(settings: dict):
    """Update application settings."""
    from backend.src.infrastructure.settings_store import save_settings

    logger.info("Updating application settings")
    save_settings(settings)
    logger.info("Settings updated successfully")
    return {"success": True, "message": "Impostazioni salvate"}


@app.get("/api/settings/features")
async def get_features():
    """Get feature flags."""
    from backend.src.infrastructure.settings_store import load_settings

    settings = load_settings()
    return {
        "ai_enabled": settings.get("ai_enabled", True),
        "verification_enabled": False,
        "blockchain_enabled": False,
    }


# ==================== SCHEDULER ENDPOINTS ====================


@app.get("/api/scheduler/status")
async def get_scheduler_status():
    """Get background scheduler status."""
    if _scheduler is None:
        return {"running": False, "jobs": []}
    return _scheduler.get_status()


@app.post("/api/scheduler/trigger")
async def trigger_poll():
    """Manually trigger feed polling."""
    if _scheduler is None:
        raise HTTPException(status_code=503, detail="Scheduler not running")
    _scheduler.trigger_poll_now()
    return {"success": True, "message": "Feed polling triggered"}


# ==================== AI ENDPOINTS ====================


@app.post("/api/news/{news_id}/summarize")
async def summarize_news(news_id: int, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Generate AI summary for news item."""
    from backend.src.infrastructure.ai_service import OllamaService
    from backend.src.infrastructure.settings_store import load_settings

    news = uow.news_repository.get_by_id(news_id)
    if not news:
        logger.warning(f"Summarize failed: News item {news_id} not found")
        raise HTTPException(status_code=404, detail="News item not found")

    settings = load_settings()
    if not settings.get("ai_enabled", False):
        logger.warning("Summarize failed: AI is disabled in settings")
        raise HTTPException(status_code=400, detail="AI non abilitata nelle impostazioni")

    logger.info(f"Generating AI summary for news item: ID={news_id}, title={news.title[:50]}...")
    ollama = OllamaService(
        endpoint=settings.get("ollama_endpoint", "http://localhost:11434"),
        model=settings.get("ollama_model", "deepseek-r1:7b"),
    )

    # Fetch full article content from URL if available
    text_to_summarize = ""
    if news.external_id:
        # Try web scraping first
        text_to_summarize = await ollama.fetch_article_content(news.external_id)

    # Fallback to feed content if scraping failed or no URL
    if not text_to_summarize or text_to_summarize.startswith("Impossibile recuperare"):
        text_to_summarize = news.content if news.content else news.title

    max_words = settings.get("summary_max_words", 200)
    summary = await ollama.summarize(text_to_summarize, max_length=max_words)

    # Check if summary is an error message
    is_error = summary.startswith("Errore") or summary.startswith("Servizio")

    # Save summary to database (even error messages, so we know it was attempted)
    news.summary = summary if not is_error else None
    uow.news_repository.update(news)
    uow.commit()

    if _cache:
        _cache.delete(f"news:{news_id}")

    if is_error:
        logger.warning(f"AI summary failed for news item {news_id}: {summary}")
        return {"success": False, "summary": summary, "message": summary}

    logger.info(f"AI summary generated and saved for news item {news_id}")
    return {"success": True, "summary": summary}


# ==================== CACHE ENDPOINTS ====================


@app.get("/api/cache/status")
async def get_cache_status():
    """Get Redis cache status."""
    if _cache is None:
        return {"available": False, "message": "Cache not initialized"}
    return {
        "available": _cache.is_available(),
        "message": "Cache is operational" if _cache.is_available() else "Cache is unavailable",
    }
