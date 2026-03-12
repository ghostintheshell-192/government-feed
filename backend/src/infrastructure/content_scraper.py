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


_MAX_FRAGMENT_LENGTH = 160

# Heading text patterns that signal the end of article content.
# Everything from these headings onward is boilerplate (contacts, related docs, etc.)
# Patterns cover EN and IT sources; extend as new languages are added.
_BOILERPLATE_HEADING_PATTERNS = re.compile(
    r"^("
    # EN patterns
    r"further\s+information"
    r"|related\s+documents?"
    r"|more\s+on\s+the\s+same\s+topic"
    r"|contact\s*(us|info|information)?"
    r"|press\s+contacts?"
    r"|see\s+also"
    # IT patterns
    r"|ulteriori\s+informazioni"
    r"|documenti\s+correlati"
    r"|contatti"
    r"|per\s+saperne\s+di\s+più"
    r"|vedi\s+anche"
    r")$",
    re.IGNORECASE,
)


def _is_continuation_fragment(text: str, prev_text: str) -> bool:
    """Detect orphaned continuation fragments using structural signals.

    Instead of matching specific legal keywords, this uses language-agnostic
    heuristics: continuation punctuation, lowercase starts (mid-sentence),
    and whether the previous paragraph ends with continuation punctuation.
    """
    if not text or len(text) > _MAX_FRAGMENT_LENGTH:
        return False
    # Current paragraph starts with continuation punctuation
    if text[0] in ",;(":
        return True
    # Current paragraph starts with lowercase — mid-sentence continuation
    if text[0].islower():
        return True
    # Short sign-off pattern like -CFTC- or -END-
    if text[0] == "-" and len(text) < 30 and re.match(r"^-\w+", text):
        return True
    # Previous paragraph ends with continuation punctuation — next is continuation
    if prev_text:
        last_char = prev_text.rstrip()[-1] if prev_text.rstrip() else ""
        if last_char in ",;:":
            return True
    return False


def _merge_citation_fragments(element: Tag) -> None:
    """Merge short continuation <p> fragments into the preceding <p>.

    Government and regulatory documents often split citation references across
    multiple <p> tags. This function detects fragments using structural signals
    (punctuation, case, paragraph length) rather than keyword matching, making
    it work across languages and jurisdictions.

    Only merges paragraphs that share the same direct parent (no cross-block
    merging).
    """
    for p in list(element.find_all("p")):
        if p.parent is None:
            continue  # already detached
        text = p.get_text(strip=True)
        prev = p.find_previous_sibling("p")
        if prev is None or prev.parent is not p.parent:
            continue
        prev_text = prev.get_text(strip=True)
        if not _is_continuation_fragment(text, prev_text):
            continue
        # Merge: append a space then move all children of p into prev
        prev.append(" ")
        for child in list(p.children):
            prev.append(child.extract())
        p.decompose()


def _remove_trailing_boilerplate(element: Tag) -> None:
    """Remove boilerplate sections from the end of article content.

    Government pages often end with contact blocks, related documents,
    and "more on the same topic" sections identified by heading text
    rather than CSS classes. This removes the heading and all subsequent
    siblings when a boilerplate heading is detected.
    """
    headings = element.find_all(re.compile(r"^h[1-6]$"))
    for heading in headings:
        text = heading.get_text(strip=True)
        if _BOILERPLATE_HEADING_PATTERNS.match(text):
            # Remove this heading and everything after it
            for sibling in list(heading.find_next_siblings()):
                sibling.decompose()
            heading.decompose()
            break  # only trim from the first match onward


def _clean_html(element: Tag, base_url: str = "") -> str:
    """Extract semantic HTML from a BeautifulSoup element, keeping only allowed tags."""
    # Remove noise elements inside content
    for noise in element.select(
        "nav, aside, .menu, .sidebar, .breadcrumb, .pagination, "
        ".share-links, .social-share, .comments, form, "
        "script, style, iframe, noscript, svg, video, audio, "
        # Related/recommended content sections (common across CMS platforms)
        '[class*="related"], [class*="recommended"], [class*="more-on"], '
        '[class*="teaser"], [role="complementary"]'
    ):
        noise.decompose()

    # Remove trailing boilerplate sections (contacts, related docs, etc.)
    _remove_trailing_boilerplate(element)

    # Merge citation/continuation fragments before walking the tree
    _merge_citation_fragments(element)

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
        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            },
        ) as client:
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
