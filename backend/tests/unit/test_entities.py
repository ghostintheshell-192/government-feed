"""Unit tests for core domain entities."""

from backend.src.core.entities import NewsItem, Source


class TestSource:
    """Tests for Source entity."""

    def test_defaults(self):
        source = Source()
        assert source.id is None
        assert source.name == ""
        assert source.feed_url == ""
        assert source.source_type == "RSS"
        assert source.is_active is True
        assert source.category is None
        assert source.description is None
        assert source.update_frequency_minutes == 60
        assert source.last_fetched is None

    def test_custom_values(self):
        source = Source(
            name="Test",
            feed_url="https://example.com/feed",
            source_type="Atom",
            category="economy",
        )
        assert source.name == "Test"
        assert source.feed_url == "https://example.com/feed"
        assert source.source_type == "Atom"
        assert source.category == "economy"


class TestNewsItem:
    """Tests for NewsItem entity."""

    def test_defaults(self):
        item = NewsItem()
        assert item.id is None
        assert item.source_id == 0
        assert item.title == ""
        assert item.content is None
        assert item.content_hash == ""
        assert item.verification_status == "pending"
        assert item.relevance_score is None

    def test_update_content_hash(self):
        item = NewsItem(title="Test", content="Content", source_id=1)
        item.update_content_hash()
        assert item.content_hash != ""
        assert len(item.content_hash) == 64  # SHA256 hex

    def test_content_hash_is_deterministic(self):
        from datetime import datetime

        fixed_time = datetime(2025, 1, 1)
        item1 = NewsItem(
            title="Test", content="Content", source_id=1, published_at=fixed_time
        )
        item2 = NewsItem(
            title="Test", content="Content", source_id=1, published_at=fixed_time
        )
        item1.update_content_hash()
        item2.update_content_hash()
        assert item1.content_hash == item2.content_hash

    def test_content_hash_changes_with_different_input(self):
        from datetime import datetime

        fixed_time = datetime(2025, 1, 1)
        item1 = NewsItem(
            title="Title A", content="Content", source_id=1, published_at=fixed_time
        )
        item2 = NewsItem(
            title="Title B", content="Content", source_id=1, published_at=fixed_time
        )
        item1.update_content_hash()
        item2.update_content_hash()
        assert item1.content_hash != item2.content_hash
