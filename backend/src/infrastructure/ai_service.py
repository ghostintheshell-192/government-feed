"""AI service for content summarization using Ollama."""

import httpx
from backend.src.infrastructure.resilience import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    retry_ollama_api,
    retry_web_scraping,
)
from bs4 import BeautifulSoup
from shared.logging import get_logger

logger = get_logger(__name__)

# Module-level circuit breakers (shared across instances for global state)
_cb_ollama = CircuitBreaker("ollama_api", failure_threshold=5, recovery_timeout=60.0)
_cb_scraping = CircuitBreaker("web_scraping", failure_threshold=5, recovery_timeout=60.0)


class OllamaService:
    """Service for interacting with Ollama API."""

    def __init__(self, endpoint: str, model: str):
        self.endpoint = endpoint
        self.model = model

    async def fetch_article_content(self, url: str) -> str:
        """Fetch and extract text content from article URL."""
        try:
            return await _cb_scraping.call_async(self._fetch_article_content_impl, url)
        except CircuitBreakerOpenError:
            logger.warning("Web scraping circuit breaker is open — skipping fetch for %s", url)
            return "Servizio di scraping temporaneamente non disponibile"
        except Exception as e:
            logger.error("Error fetching article from %s: %s", url, e)
            return f"Impossibile recuperare il contenuto dall'URL: {e}"

    @retry_web_scraping
    async def _fetch_article_content_impl(self, url: str) -> str:
        """Internal: fetch article with retry."""
        logger.info("Fetching article content from URL: %s", url)
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script, style, nav, footer, header elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()

            # Try to find main content area (common patterns)
            main_content = None
            for selector in ["article", "main", '[role="main"]', ".content", "#content"]:
                main_content = soup.select_one(selector)
                if main_content:
                    break

            # If no main content found, use body
            if not main_content:
                main_content = soup.body

            if main_content:
                # Extract text and clean up
                text = main_content.get_text(separator=" ", strip=True)
                # Collapse multiple spaces/newlines
                text = " ".join(text.split())
                return text

            return ""

    async def summarize(self, content: str, max_length: int = 200) -> str:
        """Summarize content using Ollama."""
        try:
            return await _cb_ollama.call_async(self._summarize_impl, content, max_length)
        except CircuitBreakerOpenError:
            logger.warning("Ollama circuit breaker is open — skipping summarization")
            return "Servizio AI temporaneamente non disponibile"
        except Exception as e:
            logger.error("Error calling AI service: %s", e)
            return f"Errore nella chiamata AI: {e}"

    @retry_ollama_api
    async def _summarize_impl(self, content: str, max_length: int = 200) -> str:
        """Internal: call Ollama with retry."""
        logger.info("Generating summary (max %d words)", max_length)
        # Strip HTML tags from content
        content = self._strip_html(content)

        # Truncate content if too long (max 2000 characters)
        if len(content) > 2000:
            content = content[:2000] + "..."

        prompt = f"""Riassumi brevemente il seguente testo in italiano, in massimo {max_length} parole:

{content}

Riassunto:"""

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.endpoint}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9,
                    },
                },
            )

            if response.status_code == 200:
                data = response.json()
                raw_response = data.get("response", "").strip()
                # Remove <think> blocks if present (DeepSeek reasoning)
                summary = self._extract_summary(raw_response)
                logger.info("Summary generated successfully")
                return summary
            else:
                raise httpx.HTTPStatusError(
                    f"AI service error: HTTP {response.status_code}",
                    request=response.request,
                    response=response,
                )

    def _strip_html(self, html_content: str) -> str:
        """Remove HTML tags and return clean text."""
        if not html_content:
            return ""

        soup = BeautifulSoup(html_content, "html.parser")
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text and clean up whitespace
        text = soup.get_text(separator=" ", strip=True)
        # Collapse multiple spaces into one
        text = " ".join(text.split())
        return text

    def _extract_summary(self, response: str) -> str:
        """Extract summary from response, removing <think> blocks if present.

        DeepSeek models may include reasoning in <think>...</think> blocks.
        This method removes those blocks to return only the actual summary.
        """
        # Find and remove <think>...</think> block
        think_start = response.lower().find("<think>")
        think_end = response.lower().find("</think>")

        if think_start >= 0 and think_end > think_start:
            # Remove the entire <think>...</think> block including tags
            response = response[:think_start] + response[think_end + 8:]

        return response.strip()
