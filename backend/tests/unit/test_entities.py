"""Unit tests for core domain entities."""

import pytest

from backend.src.core.entities import (
    Category,
    NewsItem,
    Source,
    VerificationStatus,
)


class TestVerificationStatus:
    """Tests for VerificationStatus enum."""

    def test_pending_value(self):
        assert VerificationStatus.PENDING.value == "pending"

    def test_verified_value(self):
        assert VerificationStatus.VERIFIED.value == "verified"

    def test_failed_value(self):
        assert VerificationStatus.FAILED.value == "failed"

    def test_is_string_enum(self):
        assert isinstance(VerificationStatus.PENDING, str)


class TestSource:
    """Tests for Source entity."""

    def test_defaults(self):
        source = Source()
        assert source.id is None
        assert source.name == ""
        assert source.url == ""
        assert source.feed_type == "rss"
        assert source.is_active is True
        assert source.country == "IT"
        assert source.category == "government"

    def test_custom_values(self):
        source = Source(name="Test", url="https://example.com", country="US")
        assert source.name == "Test"
        assert source.url == "https://example.com"
        assert source.country == "US"


class TestCategory:
    """Tests for Category entity."""

    def test_defaults(self):
        cat = Category()
        assert cat.id is None
        assert cat.name == ""
        assert cat.slug == ""
        assert cat.parent_id is None

    def test_custom_values(self):
        cat = Category(name="Politics", slug="politics", parent_id=1)
        assert cat.name == "Politics"
        assert cat.slug == "politics"
        assert cat.parent_id == 1


class TestNewsItem:
    """Tests for NewsItem entity."""

    def test_defaults(self):
        item = NewsItem()
        assert item.id is None
        assert item.source_id == 0
        assert item.title == ""
        assert item.content is None
        assert item.content_hash == ""
        assert item.verification_status == VerificationStatus.PENDING
        assert item.blockchain_certificate is None
        assert item.categories == []

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

    def test_mark_as_verified(self):
        item = NewsItem()
        item.mark_as_verified("cert-abc-123")
        assert item.verification_status == VerificationStatus.VERIFIED
        assert item.blockchain_certificate == "cert-abc-123"

    def test_mark_as_verified_raises_on_empty_certificate(self):
        item = NewsItem()
        with pytest.raises(ValueError, match="Certificate cannot be empty"):
            item.mark_as_verified("")

    def test_mark_as_verified_updates_timestamp(self):
        from datetime import datetime

        old_time = datetime(2020, 1, 1)
        item = NewsItem(updated_at=old_time)
        item.mark_as_verified("cert")
        assert item.updated_at > old_time
