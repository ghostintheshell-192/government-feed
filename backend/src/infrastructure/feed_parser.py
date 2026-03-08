"""Feed parsing service for RSS/Atom feeds."""

from datetime import UTC, datetime
from hashlib import sha256

import feedparser
import httpx
from backend.src.infrastructure.models import NewsItem, Source
from backend.src.infrastructure.resilience import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    retry_feed_fetch,
)
from bs4 import BeautifulSoup
from shared.logging import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__name__)

# Module-level circuit breaker for feed fetching
_cb_feed_fetch = CircuitBreaker("feed_fetch", failure_threshold=5, recovery_timeout=60.0)


class FeedParserService:
    """Service for parsing RSS/Atom feeds."""

    def __init__(self, db: Session):
        self.db = db

    def parse_and_import(self, source: Source) -> int:
        """Parse feed and import news items. Returns count of imported items."""
        try:
            logger.info("Parsing feed from source: %s", source.name)

            # Fetch feed content with resilience
            try:
                xml_content = _cb_feed_fetch.call(self._fetch_feed_content_sync, source.feed_url)
            except CircuitBreakerOpenError:
                logger.warning(
                    "Feed fetch circuit breaker is open — skipping source %s", source.name
                )
                return 0

            feed = feedparser.parse(xml_content)

            if feed.bozo:  # Feed parse error
                logger.warning("Feed parse error for %s: %s", source.name, feed.bozo_exception)
                return 0

            imported_count = 0

            for entry in feed.entries:
                # Extract data from entry
                title = entry.get("title", "")
                link = entry.get("link", "")
                content = self._extract_content(entry)
                raw_summary = entry.get("summary", "")
                summary = self._strip_html(raw_summary) if raw_summary else ""

                # Parse published date
                published_at = self._parse_date(entry)

                # Create content hash for deduplication
                content_hash = self._create_hash(title, content, source.id, published_at)

                # Check if already exists
                existing = (
                    self.db.query(NewsItem)
                    .filter(NewsItem.content_hash == content_hash)
                    .first()
                )

                if existing:
                    continue

                # Create new news item
                news_item = NewsItem(
                    source_id=source.id,
                    external_id=link,
                    title=title,
                    content=content,
                    summary=summary if summary else None,
                    published_at=published_at,
                    fetched_at=datetime.now(UTC),
                    content_hash=content_hash,
                    verification_status="pending",
                )

                self.db.add(news_item)
                imported_count += 1

            # Update source last_fetched
            source.last_fetched = datetime.now(UTC)

            self.db.commit()
            logger.info("Imported %d news items from %s", imported_count, source.name)
            return imported_count

        except Exception as e:
            self.db.rollback()
            logger.error("Error parsing feed from %s: %s", source.name, e)
            return 0

    @retry_feed_fetch
    def _fetch_feed_content_sync(self, url: str) -> str:
        """Fetch feed XML content via httpx with retry."""
        logger.info("Fetching feed content from: %s", url)
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.text

    def _extract_content(self, entry: object) -> str:
        """Extract content from feed entry."""
        # Try different content fields
        content = ""
        if hasattr(entry, "content") and entry.content:  # type: ignore[union-attr]
            content = entry.content[0].get("value", "")  # type: ignore[union-attr]
        elif hasattr(entry, "description"):
            content = entry.description  # type: ignore[union-attr]
        elif hasattr(entry, "summary"):
            content = entry.summary  # type: ignore[union-attr]

        # Strip HTML tags and return clean text
        return self._strip_html(content) if content else ""

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

    def _parse_date(self, entry: object) -> datetime:
        """Parse date from feed entry."""
        if hasattr(entry, "published_parsed") and entry.published_parsed:  # type: ignore[union-attr]
            return datetime(*entry.published_parsed[:6])  # type: ignore[union-attr]
        if hasattr(entry, "updated_parsed") and entry.updated_parsed:  # type: ignore[union-attr]
            return datetime(*entry.updated_parsed[:6])  # type: ignore[union-attr]
        return datetime.now(UTC)

    def _create_hash(self, title: str, content: str, source_id: int, published_at: datetime) -> str:
        """Create content hash for deduplication."""
        content_str = f"{title}|{content}|{source_id}|{published_at.isoformat()}"
        return sha256(content_str.encode()).hexdigest()
