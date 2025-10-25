"""Feed parsing service for RSS/Atom feeds."""

from datetime import datetime
from hashlib import sha256

import feedparser
from backend.src.infrastructure.models import NewsItem, Source
from bs4 import BeautifulSoup
from shared.logging import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__name__)


class FeedParserService:
    """Service for parsing RSS/Atom feeds."""

    def __init__(self, db: Session):
        self.db = db

    def parse_and_import(self, source: Source) -> int:
        """Parse feed and import news items. Returns count of imported items."""
        try:
            logger.info(f"Parsing feed from source: {source.name}")
            feed = feedparser.parse(source.feed_url)

            if feed.bozo:  # Feed parse error
                logger.warning(f"Feed parse error for {source.name}: {feed.bozo_exception}")
                return 0

            imported_count = 0

            for entry in feed.entries:
                # Extract data from entry
                title = entry.get("title", "")
                link = entry.get("link", "")
                content = self._extract_content(entry)
                summary = entry.get("summary", "")

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
                    fetched_at=datetime.utcnow(),
                    content_hash=content_hash,
                    verification_status="pending",
                )

                self.db.add(news_item)
                imported_count += 1

            # Update source last_fetched
            source.last_fetched = datetime.utcnow()

            self.db.commit()
            logger.info(f"Imported {imported_count} news items from {source.name}")
            return imported_count

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error parsing feed from {source.name}: {e}")
            return 0

    def _extract_content(self, entry) -> str:
        """Extract content from feed entry."""
        # Try different content fields
        content = ""
        if hasattr(entry, "content") and entry.content:
            content = entry.content[0].get("value", "")
        elif hasattr(entry, "description"):
            content = entry.description
        elif hasattr(entry, "summary"):
            content = entry.summary

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

    def _parse_date(self, entry) -> datetime:
        """Parse date from feed entry."""
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            return datetime(*entry.published_parsed[:6])
        if hasattr(entry, "updated_parsed") and entry.updated_parsed:
            return datetime(*entry.updated_parsed[:6])
        return datetime.utcnow()

    def _create_hash(self, title: str, content: str, source_id: int, published_at: datetime) -> str:
        """Create content hash for deduplication."""
        content_str = f"{title}|{content}|{source_id}|{published_at.isoformat()}"
        return sha256(content_str.encode()).hexdigest()
