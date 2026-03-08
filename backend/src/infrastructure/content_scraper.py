"""Content scraping service for fetching full article text from URLs."""

import re
from urllib.parse import urljoin

import httpx
from backend.src.infrastructure.resilience import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    retry_web_scraping,
)
from bs4 import BeautifulSoup, Tag
from shared.logging import get_logger

logger = get_logger(__name__)

_cb_scraping = CircuitBreaker("content_scraping", failure_threshold=5, recovery_timeout=60.0)

# Tags to preserve in the cleaned HTML output
ALLOWED_TAGS = {
    "p",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "table",
    "thead",
    "tbody",
    "tfoot",
    "tr",
    "th",
    "td",
    "strong",
    "b",
    "em",
    "i",
    "blockquote",
    "a",
    "br",
    "sup",
    "sub",
    "caption",
    "img",
}

# Self-closing tags that don't need a closing tag
SELF_CLOSING_TAGS = {"br", "img"}

# Attributes to keep per tag
ALLOWED_ATTRS = {
    "a": ["href"],
    "img": ["src", "alt"],
}


def _clean_html(element: Tag, base_url: str = "") -> str:
    """Extract semantic HTML from a BeautifulSoup element, keeping only allowed tags."""
    # Remove noise elements inside content
    for noise in element.select(
        "nav, .menu, .sidebar, .breadcrumb, .pagination, .share-links, "
        ".social-share, .related-posts, .comments, form, "
        "script, style, iframe, noscript, svg, video, audio"
    ):
        noise.decompose()

    # Walk the tree and rebuild with only allowed tags
    result_parts: list[str] = []
    _walk_element(element, result_parts, base_url)
    html = "".join(result_parts)

    # Clean up excessive whitespace in the output
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html.strip()


def _resolve_url(url: str, base_url: str) -> str:
    """Resolve a potentially relative URL against a base URL."""
    if not url or not base_url:
        return url
    # Skip data URIs and already-absolute URLs
    if url.startswith(("data:", "http://", "https://")):
        return url
    return urljoin(base_url, url)


def _walk_element(element: Tag, parts: list[str], base_url: str = "") -> None:
    """Recursively walk the DOM tree, keeping only allowed tags."""
    for child in element.children:
        if isinstance(child, Tag):
            if child.name in ALLOWED_TAGS:
                # Build opening tag with allowed attributes
                attrs = ""
                if child.name in ALLOWED_ATTRS:
                    for attr in ALLOWED_ATTRS[child.name]:
                        raw = child.get(attr)
                        if not raw:
                            continue
                        val = raw if isinstance(raw, str) else raw[0]
                        # Resolve relative URLs for src and href
                        if attr in ("src", "href"):
                            val = _resolve_url(val, base_url)
                        attrs += f' {attr}="{val}"'
                parts.append(f"<{child.name}{attrs}>")
                if child.name not in SELF_CLOSING_TAGS:
                    _walk_element(child, parts, base_url)
                    parts.append(f"</{child.name}>")
            else:
                # Unwrap: keep children but drop the tag itself
                _walk_element(child, parts, base_url)
        else:
            # NavigableString — text content
            text = str(child)
            if text.strip():
                parts.append(text)


class ContentScraper:
    """Service for fetching and extracting article content from URLs."""

    async def fetch_article_content(self, url: str) -> str:
        """Fetch and extract content from article URL, preserving semantic HTML."""
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
        """Fetch article with retry and extract main content as clean HTML."""
        logger.info("Fetching article content from URL: %s", url)
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            for element in soup(
                ["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]
            ):
                element.decompose()

            main_content = None
            for selector in [
                "article",
                "main",
                '[role="main"]',
                ".content",
                "#content",
                ".article-body",
                ".entry-content",
                ".post-content",
                ".field--name-body",
                ".node__content",
                "#main-content",
                ".page-content",
            ]:
                main_content = soup.select_one(selector)
                if main_content:
                    break

            if not main_content:
                main_content = soup.body

            if not main_content:
                return ""

            return _clean_html(main_content, base_url=url)
