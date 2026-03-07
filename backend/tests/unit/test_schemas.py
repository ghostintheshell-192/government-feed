"""Unit tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from backend.src.api.schemas import (
    NewsItemResponse,
    SourceCreate,
    SourceResponse,
    SourceUpdate,
)


class TestSourceCreate:
    """Tests for SourceCreate schema."""

    def test_valid_source(self):
        source = SourceCreate(name="Test", feed_url="https://example.com/feed")
        assert source.name == "Test"
        assert source.feed_url == "https://example.com/feed"
        assert source.source_type == "RSS"
        assert source.update_frequency_minutes == 60

    def test_empty_name_raises(self):
        with pytest.raises(ValidationError):
            SourceCreate(name="", feed_url="https://example.com/feed")

    def test_empty_feed_url_raises(self):
        with pytest.raises(ValidationError):
            SourceCreate(name="Test", feed_url="")

    def test_negative_frequency_raises(self):
        with pytest.raises(ValidationError):
            SourceCreate(
                name="Test",
                feed_url="https://example.com/feed",
                update_frequency_minutes=0,
            )


class TestSourceUpdate:
    """Tests for SourceUpdate schema."""

    def test_with_is_active(self):
        source = SourceUpdate(
            name="Updated", feed_url="https://example.com/feed", is_active=False
        )
        assert source.is_active is False


class TestSourceResponse:
    """Tests for SourceResponse schema with from_attributes."""

    def test_from_dict(self):
        from datetime import datetime

        data = {
            "id": 1,
            "name": "Test",
            "feed_url": "https://example.com",
            "source_type": "RSS",
            "description": None,
            "category": None,
            "update_frequency_minutes": 60,
            "is_active": True,
            "last_fetched": None,
            "created_at": datetime(2025, 1, 1),
            "updated_at": datetime(2025, 1, 1),
        }
        response = SourceResponse(**data)
        assert response.id == 1
        assert response.is_active is True


class TestNewsItemResponse:
    """Tests for NewsItemResponse schema."""

    def test_from_dict(self):
        from datetime import datetime

        data = {
            "id": 1,
            "source_id": 1,
            "external_id": "https://example.com/article/1",
            "title": "Test News",
            "content": "Some content",
            "summary": None,
            "published_at": datetime(2025, 1, 1),
            "fetched_at": datetime(2025, 1, 1),
            "relevance_score": None,
            "verification_status": "pending",
        }
        response = NewsItemResponse(**data)
        assert response.id == 1
        assert response.title == "Test News"
        assert response.verification_status == "pending"
