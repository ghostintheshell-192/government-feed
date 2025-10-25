"""FastAPI main application."""


from backend.src.api import schemas
from backend.src.infrastructure.database import get_db, init_db
from backend.src.infrastructure.models import NewsItem, Source
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from shared.logging import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__name__)

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
    """Initialize database on startup."""
    logger.info("Starting Government Feed API")
    init_db()
    logger.info("Database initialized successfully")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Government Feed API", "version": "0.1.0", "status": "running"}


# ==================== SOURCES ENDPOINTS ====================


@app.get("/api/sources", response_model=list[schemas.SourceResponse])
async def get_sources(db: Session = Depends(get_db)):
    """Get all sources."""
    sources = db.query(Source).all()
    return sources


@app.get("/api/sources/{source_id}", response_model=schemas.SourceResponse)
async def get_source(source_id: int, db: Session = Depends(get_db)):
    """Get source by ID."""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@app.post("/api/sources", response_model=schemas.SourceResponse, status_code=201)
async def create_source(source: schemas.SourceCreate, db: Session = Depends(get_db)):
    """Create new source."""
    logger.info(f"Creating new source: {source.name}")
    db_source = Source(**source.model_dump())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    logger.info(f"Source created successfully: ID={db_source.id}, name={db_source.name}")
    return db_source


@app.put("/api/sources/{source_id}", response_model=schemas.SourceResponse)
async def update_source(
    source_id: int, source: schemas.SourceUpdate, db: Session = Depends(get_db)
):
    """Update source."""
    db_source = db.query(Source).filter(Source.id == source_id).first()
    if not db_source:
        logger.warning(f"Update failed: Source {source_id} not found")
        raise HTTPException(status_code=404, detail="Source not found")

    logger.info(f"Updating source: ID={source_id}, name={db_source.name}")
    for key, value in source.model_dump().items():
        setattr(db_source, key, value)

    db.commit()
    db.refresh(db_source)
    logger.info(f"Source updated successfully: ID={source_id}")
    return db_source


@app.delete("/api/sources/{source_id}", status_code=204)
async def delete_source(source_id: int, db: Session = Depends(get_db)):
    """Delete source."""
    db_source = db.query(Source).filter(Source.id == source_id).first()
    if not db_source:
        logger.warning(f"Delete failed: Source {source_id} not found")
        raise HTTPException(status_code=404, detail="Source not found")

    logger.info(f"Deleting source: ID={source_id}, name={db_source.name}")
    db.delete(db_source)
    db.commit()
    logger.info(f"Source deleted successfully: ID={source_id}")
    return None


@app.post("/api/sources/{source_id}/process")
async def process_feed(source_id: int, db: Session = Depends(get_db)):
    """Process feed and import news."""
    from backend.src.infrastructure.feed_parser import FeedParserService

    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        logger.warning(f"Process feed failed: Source {source_id} not found")
        raise HTTPException(status_code=404, detail="Source not found")

    logger.info(f"Processing feed for source: ID={source_id}, name={source.name}")
    parser = FeedParserService(db)
    imported_count = parser.parse_and_import(source)

    if imported_count > 0:
        logger.info(f"Feed processed successfully: {imported_count} news items imported from {source.name}")
        return {
            "success": True,
            "message": f"Feed importato con successo! {imported_count} notizie aggiunte.",
        }
    else:
        logger.warning(f"Feed processing completed with no new items from {source.name}")
        return {"success": False, "message": "Nessuna nuova notizia trovata o errore nel parsing."}


# ==================== NEWS ENDPOINTS ====================


@app.get("/api/news", response_model=list[schemas.NewsItemResponse])
async def get_news(limit: int = 50, db: Session = Depends(get_db)):
    """Get recent news items."""
    news = db.query(NewsItem).order_by(NewsItem.published_at.desc()).limit(limit).all()
    return news


@app.get("/api/news/{news_id}", response_model=schemas.NewsItemResponse)
async def get_news_item(news_id: int, db: Session = Depends(get_db)):
    """Get news item by ID."""
    news = db.query(NewsItem).filter(NewsItem.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")
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


# ==================== AI ENDPOINTS ====================


@app.post("/api/news/{news_id}/summarize")
async def summarize_news(news_id: int, db: Session = Depends(get_db)):
    """Generate AI summary for news item."""
    from backend.src.infrastructure.ai_service import OllamaService
    from backend.src.infrastructure.settings_store import load_settings

    news = db.query(NewsItem).filter(NewsItem.id == news_id).first()
    if not news:
        logger.warning(f"Summarize failed: News item {news_id} not found")
        raise HTTPException(status_code=404, detail="News item not found")

    settings = load_settings()
    if not settings.get("ai_enabled", False):
        logger.warning(f"Summarize failed: AI is disabled in settings")
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

    # Save summary to database
    news.summary = summary
    db.commit()

    logger.info(f"AI summary generated and saved for news item {news_id}")
    return {"success": True, "summary": summary}
