"""Content scraping service for fetching full article text from URLs."""

import httpx
from backend.src.infrastructure.resilience import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    retry_web_scraping,
)
from bs4 import BeautifulSoup
from shared.logging import get_logger

logger = get_logger(__name__)

_cb_scraping = CircuitBreaker("content_scraping", failure_threshold=5, recovery_timeout=60.0)


class ContentScraper:
    """Service for fetching and extracting article content from URLs."""

    async def fetch_article_content(self, url: str) -> str:
        """Fetch and extract text content from article URL."""
        try:
            return await _cb_scraping.call_async(self._fetch_impl, url)
        except CircuitBreakerOpenError:
            logger.warning("Content scraping circuit breaker is open — skipping %s", url)
            return "Servizio di scraping temporaneamente non disponibile"
        except Exception as e:
            logger.error("Error fetching article from %s: %s", url, e)
            return f"Impossibile recuperare il contenuto dall'URL: {e}"

    @retry_web_scraping
    async def _fetch_impl(self, url: str) -> str:
        """Fetch article with retry and extract main content."""
        logger.info("Fetching article content from URL: %s", url)
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()

            main_content = None
            for selector in ["article", "main", '[role="main"]', ".content", "#content"]:
                main_content = soup.select_one(selector)
                if main_content:
                    break

            if not main_content:
                main_content = soup.body

            if main_content:
                text = main_content.get_text(separator=" ", strip=True)
                return " ".join(text.split())

            return ""
