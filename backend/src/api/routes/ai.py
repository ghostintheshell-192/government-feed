"""AI-related endpoints (summarization)."""

from backend.src.api import state
from backend.src.api.dependencies import get_unit_of_work
from backend.src.infrastructure.unit_of_work import UnitOfWork
from fastapi import APIRouter, Depends, HTTPException
from shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/news", tags=["ai"])


@router.post("/{news_id}/summarize")
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

    if state.cache:
        state.cache.delete(f"news:{news_id}")

    if is_error:
        logger.warning(f"AI summary failed for news item {news_id}: {summary}")
        return {"success": False, "summary": summary, "message": summary}

    logger.info(f"AI summary generated and saved for news item {news_id}")
    return {"success": True, "summary": summary}
