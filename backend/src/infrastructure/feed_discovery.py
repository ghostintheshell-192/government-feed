"""Feed discovery service for finding RSS/Atom feeds from websites or search queries."""

from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import feedparser
import httpx
from backend.src.infrastructure.resilience import retry_web_scraping
from bs4 import BeautifulSoup
from shared.logging import get_logger

logger = get_logger(__name__)

_COMMON_FEED_PATHS = [
    "/feed",
    "/rss",
    "/rss.xml",
    "/feed.xml",
    "/atom.xml",
    "/feeds/posts/default",
    "/feed/rss",
    "/feed/atom",
]

_FEED_LINK_TYPES = [
    "application/rss+xml",
    "application/atom+xml",
    "application/rdf+xml",
    "application/xml",
]


@dataclass
class DiscoveredFeed:
    """A discovered feed with metadata."""

    url: str
    title: str
    feed_type: str
    site_url: str
    entry_count: int


class FeedDiscoveryService:
    """Service for discovering RSS/Atom feeds from URLs or search queries."""

    def __init__(self, timeout: float = 15.0) -> None:
        self._timeout = timeout

    async def discover(self, query: str) -> tuple[list[DiscoveredFeed], list[str]]:
        """Discover feeds from a URL or search query.

        Returns a tuple of (discovered_feeds, searched_sites).
        """
        query = query.strip()
        if query.startswith("http://") or query.startswith("https://"):
            feeds = await self._discover_from_url(query)
            return feeds, [query]

        # Search via DuckDuckGo and discover feeds from top results
        sites = self._search_sites(query)
        all_feeds: list[DiscoveredFeed] = []
        seen_urls: set[str] = set()

        for site_url in sites:
            try:
                feeds = await self._discover_from_url(site_url)
                for feed in feeds:
                    if feed.url not in seen_urls:
                        seen_urls.add(feed.url)
                        all_feeds.append(feed)
            except Exception as e:
                logger.warning("Failed to discover feeds from %s: %s", site_url, e)

        return all_feeds, sites

    def _search_sites(self, query: str) -> list[str]:
        """Search DuckDuckGo for relevant sites."""
        try:
            from duckduckgo_search import DDGS

            with DDGS() as ddgs:
                results = list(ddgs.text(f"{query} RSS feed", max_results=5))
            urls = [r["href"] for r in results if "href" in r]
            if urls:
                logger.info("DuckDuckGo found %d sites for '%s'", len(urls), query)
                return urls
            logger.info("DuckDuckGo returned no results for '%s'", query)
        except Exception as e:
            logger.warning("DuckDuckGo search failed: %s", e)
        return []

    async def _discover_from_url(self, url: str) -> list[DiscoveredFeed]:
        """Discover feeds from a specific URL."""
        feeds: list[DiscoveredFeed] = []
        seen_urls: set[str] = set()

        # First check if the URL itself is a feed
        direct_feed = await self._validate_feed(url, url)
        if direct_feed:
            return [direct_feed]

        # Fetch HTML and look for feed links
        html = await self._fetch_html(url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            for link_type in _FEED_LINK_TYPES:
                for link in soup.find_all("link", type=link_type):
                    href = link.get("href")
                    if href and isinstance(href, str):
                        feed_url = urljoin(url, href)
                        if feed_url not in seen_urls:
                            seen_urls.add(feed_url)
                            link_title = link.get("title")
                            title_str = str(link_title) if link_title else None
                            feed = await self._validate_feed(feed_url, url, title_str)
                            if feed:
                                feeds.append(feed)

        # Try common paths
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        for path in _COMMON_FEED_PATHS:
            candidate = base + path
            if candidate not in seen_urls:
                seen_urls.add(candidate)
                feed = await self._validate_feed(candidate, url)
                if feed:
                    feeds.append(feed)

        return feeds

    @retry_web_scraping
    async def _fetch_html(self, url: str) -> str | None:
        """Fetch HTML content from a URL."""
        async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if "html" in content_type or "xml" not in content_type:
                return response.text
            return response.text

    async def _validate_feed(
        self, feed_url: str, site_url: str, title: str | None = None
    ) -> DiscoveredFeed | None:
        """Validate a URL as a feed and return metadata."""
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout, follow_redirects=True
            ) as client:
                response = await client.get(feed_url)
                response.raise_for_status()

            parsed = feedparser.parse(response.text)

            # Check if it's a valid feed
            if not parsed.feed or parsed.bozo:
                # bozo feeds might still be usable if they have entries
                if not parsed.entries:
                    return None

            feed_title = title or getattr(parsed.feed, "title", None) or feed_url
            feed_type = "Atom" if "atom" in response.headers.get("content-type", "").lower() or hasattr(parsed.feed, "id") else "RSS"

            return DiscoveredFeed(
                url=feed_url,
                title=feed_title,
                feed_type=feed_type,
                site_url=site_url,
                entry_count=len(parsed.entries),
            )
        except Exception as e:
            logger.debug("URL %s is not a valid feed: %s", feed_url, e)
            return None
