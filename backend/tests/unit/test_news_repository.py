"""Unit tests for NewsRepository."""

from datetime import datetime

import pytest

from backend.src.infrastructure.repositories.news_repository import NewsRepository
from backend.tests.conftest import sample_news_item, sample_source


class TestNewsRepository:
    """Tests for NewsRepository with in-memory SQLite."""

    def _add_source(self, db_session):
        """Helper: add a source and return its ID."""
        source = sample_source(name="Test Source for News")
        db_session.add(source)
        db_session.flush()
        return source.id

    def test_add_and_get_by_id(self, db_session):
        source_id = self._add_source(db_session)
        repo = NewsRepository(db_session)

        item = sample_news_item(source_id=source_id, content_hash="hash_unique_1")
        repo.add(item)
        db_session.flush()

        result = repo.get_by_id(item.id)
        assert result is not None
        assert result.title == "Test News Item"

    def test_get_by_id_not_found(self, db_session):
        repo = NewsRepository(db_session)
        result = repo.get_by_id(9999)
        assert result is None

    def test_get_by_content_hash_found(self, db_session):
        source_id = self._add_source(db_session)
        repo = NewsRepository(db_session)

        item = sample_news_item(source_id=source_id, content_hash="find_me_hash")
        repo.add(item)
        db_session.flush()

        result = repo.get_by_content_hash("find_me_hash")
        assert result is not None
        assert result.content_hash == "find_me_hash"

    def test_get_by_content_hash_not_found(self, db_session):
        repo = NewsRepository(db_session)
        result = repo.get_by_content_hash("nonexistent_hash")
        assert result is None

    def test_get_by_content_hash_empty_raises(self, db_session):
        repo = NewsRepository(db_session)
        with pytest.raises(ValueError, match="Content hash cannot be empty"):
            repo.get_by_content_hash("")

    def test_get_recent_order_desc(self, db_session):
        source_id = self._add_source(db_session)
        repo = NewsRepository(db_session)

        repo.add(sample_news_item(
            source_id=source_id,
            title="Older",
            content_hash="recent_1",
            published_at=datetime(2025, 1, 1),
        ))
        repo.add(sample_news_item(
            source_id=source_id,
            title="Newer",
            content_hash="recent_2",
            published_at=datetime(2025, 6, 1),
        ))
        db_session.flush()

        results = repo.get_recent(limit=10)
        assert len(results) >= 2
        assert results[0].title == "Newer"
        assert results[1].title == "Older"

    def test_get_recent_respects_limit(self, db_session):
        source_id = self._add_source(db_session)
        repo = NewsRepository(db_session)

        for i in range(5):
            repo.add(sample_news_item(
                source_id=source_id,
                title=f"Item {i}",
                content_hash=f"limit_test_{i}",
            ))
        db_session.flush()

        results = repo.get_recent(limit=2)
        assert len(results) == 2

    def test_get_recent_invalid_limit_raises(self, db_session):
        repo = NewsRepository(db_session)
        with pytest.raises(ValueError, match="Limit must be greater than zero"):
            repo.get_recent(limit=0)

    def test_get_by_date_range(self, db_session):
        source_id = self._add_source(db_session)
        repo = NewsRepository(db_session)

        repo.add(sample_news_item(
            source_id=source_id,
            title="In Range",
            content_hash="date_range_1",
            published_at=datetime(2025, 3, 15),
        ))
        repo.add(sample_news_item(
            source_id=source_id,
            title="Out of Range",
            content_hash="date_range_2",
            published_at=datetime(2024, 1, 1),
        ))
        db_session.flush()

        results = repo.get_by_date_range(datetime(2025, 1, 1), datetime(2025, 12, 31))
        titles = [r.title for r in results]
        assert "In Range" in titles
        assert "Out of Range" not in titles

    def test_get_by_date_range_invalid_raises(self, db_session):
        repo = NewsRepository(db_session)
        with pytest.raises(ValueError, match="Start date must be before end date"):
            repo.get_by_date_range(datetime(2025, 12, 1), datetime(2025, 1, 1))

    def test_search_by_title(self, db_session):
        source_id = self._add_source(db_session)
        repo = NewsRepository(db_session)

        repo.add(sample_news_item(
            source_id=source_id,
            title="Government Budget Report",
            content_hash="search_1",
        ))
        db_session.flush()

        results = repo.search("budget")
        assert any("Budget" in r.title for r in results)

    def test_search_by_content(self, db_session):
        source_id = self._add_source(db_session)
        repo = NewsRepository(db_session)

        repo.add(sample_news_item(
            source_id=source_id,
            title="Generic Title",
            content="Important legislative decree published today",
            content_hash="search_2",
        ))
        db_session.flush()

        results = repo.search("legislative")
        assert len(results) >= 1

    def test_search_empty_term_returns_empty(self, db_session):
        repo = NewsRepository(db_session)
        assert repo.search("") == []
        assert repo.search("   ") == []

    def test_add_none_raises(self, db_session):
        repo = NewsRepository(db_session)
        with pytest.raises(ValueError, match="News item cannot be None"):
            repo.add(None)

    def test_update_none_raises(self, db_session):
        repo = NewsRepository(db_session)
        with pytest.raises(ValueError, match="News item cannot be None"):
            repo.update(None)
