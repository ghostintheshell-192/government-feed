"""FastAPI main application."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from backend.src.api import state
from backend.src.api.routes import admin, ai, cache, catalog, news, scheduler, settings, sources
from backend.src.infrastructure.cache import RedisCache
from backend.src.infrastructure.database import init_db
from backend.src.infrastructure.scheduler import FeedScheduler
from backend.src.infrastructure.settings_store import load_settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.logging import get_logger

logger = get_logger(__name__)


def _read_version() -> str:
    """Read version from frontend/package.json (single source of truth)."""
    import json

    for path in [Path("frontend/package.json"), Path(__file__).parents[4] / "frontend" / "package.json"]:
        if path.is_file():
            data = json.loads(path.read_text())
            return data.get("version", "unknown")
    return "unknown"


APP_VERSION = _read_version()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize and cleanup application resources."""
    logger.info("Starting Government Feed API")
    init_db()
    logger.info("Database initialized successfully")

    app_settings = load_settings()

    redis_url = app_settings.get("redis_url", "redis://localhost:6379")
    state.cache = RedisCache(url=redis_url)
    if state.cache.is_available():
        logger.info("Redis cache enabled")
    else:
        logger.info("Redis cache not available, running without cache")

    if app_settings.get("scheduler_enabled", True):
        state.scheduler = FeedScheduler()
        state.scheduler.start()
        logger.info("Background scheduler started")

    yield

    if state.scheduler is not None:
        state.scheduler.shutdown()
        state.scheduler = None
        logger.info("Background scheduler stopped")


app = FastAPI(
    title="Government Feed API",
    description="Aggregator for institutional news and government communications",
    version=APP_VERSION,
    lifespan=lifespan,
)

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(sources.router)
app.include_router(news.router)
app.include_router(ai.router)
app.include_router(settings.router)
app.include_router(scheduler.router)
app.include_router(cache.router)
app.include_router(catalog.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Government Feed API", "version": APP_VERSION, "status": "running"}
