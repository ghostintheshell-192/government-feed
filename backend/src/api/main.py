"""FastAPI main application."""

from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.src.api import schemas
from backend.src.infrastructure.database import get_db, init_db
from backend.src.infrastructure.models import NewsItem, Source

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
    init_db()


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
    db_source = Source(**source.model_dump())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


@app.put("/api/sources/{source_id}", response_model=schemas.SourceResponse)
async def update_source(
    source_id: int, source: schemas.SourceUpdate, db: Session = Depends(get_db)
):
    """Update source."""
    db_source = db.query(Source).filter(Source.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")

    for key, value in source.model_dump().items():
        setattr(db_source, key, value)

    db.commit()
    db.refresh(db_source)
    return db_source


@app.delete("/api/sources/{source_id}", status_code=204)
async def delete_source(source_id: int, db: Session = Depends(get_db)):
    """Delete source."""
    db_source = db.query(Source).filter(Source.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")

    db.delete(db_source)
    db.commit()
    return None


@app.post("/api/sources/{source_id}/process")
async def process_feed(source_id: int, db: Session = Depends(get_db)):
    """Process feed and import news."""
    from backend.src.infrastructure.feed_parser import FeedParserService

    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    parser = FeedParserService(db)
    imported_count = parser.parse_and_import(source)

    if imported_count > 0:
        return {
            "success": True,
            "message": f"Feed importato con successo! {imported_count} notizie aggiunte.",
        }
    else:
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

    save_settings(settings)
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
        raise HTTPException(status_code=404, detail="News item not found")

    settings = load_settings()
    if not settings.get("ai_enabled", False):
        raise HTTPException(status_code=400, detail="AI non abilitata nelle impostazioni")

    # Use content or title for summarization
    text_to_summarize = news.content if news.content else news.title

    ollama = OllamaService(
        endpoint=settings.get("ollama_endpoint", "http://localhost:11434"),
        model=settings.get("ollama_model", "deepseek-r1:7b"),
    )

    summary = await ollama.summarize(text_to_summarize)

    # Save summary to database
    news.summary = summary
    db.commit()

    return {"success": True, "summary": summary}
