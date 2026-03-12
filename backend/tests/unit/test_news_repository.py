"""Unit tests for NewsRepository."""

from datetime import datetime

import pytest

from backend.src.infrastructure.repositories.news_repository import NewsRepository
from backend.tests.conftest import sample_news_item, sample_source


class TestNewsRepository:
    """Tests for NewsRepository with in-memory SQLite."""

    def _add_source(self, db_session, name="Test Source for News"):
        """Helper: add a source and return its ID."""
        source = sample_source(name=name)
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

        items, total = repo.get_recent(limit=10)
        assert total >= 2
        assert len(items) >= 2
        assert items[0].title == "Newer"
        assert items[1].title == "Older"

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

        items, total = repo.get_recent(limit=2)
        assert len(items) == 2
        assert total >= 5

    def test_get_recent_invalid_limit_raises(self, db_session):
        repo = NewsRepository(db_session)
        with pytest.raises(ValueError, match="Limit must be greater than zero"):
            repo.get_recent(limit=0)

    def test_get_recent_with_offset(self, db_session):
        source_id = self._add_source(db_session)
        repo = NewsRepository(db_session)

        for i in range(5):
            repo.add(sample_news_item(
                source_id=source_id,
                title=f"Offset Item {i}",
                content_hash=f"offset_test_{i}",
                published_at=datetime(2025, 1, i + 1),
            ))
        db_session.flush()

        items_page1, total1 = repo.get_recent(limit=2, offset=0)
        items_page2, total2 = repo.get_recent(limit=2, offset=2)

        assert total1 == total2
        assert len(items_page1) == 2
        assert len(items_page2) == 2
        # Pages should not overlap
        page1_ids = {item.id for item in items_page1}
        page2_ids = {item.id for item in items_page2}
        assert page1_ids.isdisjoint(page2_ids)

    def test_get_recent_negative_offset_raises(self, db_session):
        repo = NewsRepository(db_session)
        with pytest.raises(ValueError, match="Offset must be non-negative"):
            repo.get_recent(offset=-1)

    def test_get_recent_total_count(self, db_session):
        source_id = self._add_source(db_session)
        repo = NewsRepository(db_session)

        for i in range(3):
            repo.add(sample_news_item(
                source_id=source_id,
                title=f"Count Item {i}",
                content_hash=f"count_test_{i}",
            ))
        db_session.flush()

        items, total = repo.get_recent(limit=1)
        assert len(items) == 1
        assert total >= 3

    def test_get_recent_filter_by_source(self, db_session):
        source_id_a = self._add_source(db_session, name="Source A")
        source_id_b = self._add_source(db_session, name="Source B")
        repo = NewsRepository(db_session)

        repo.add(sample_news_item(
            source_id=source_id_a,
            title="From Source A",
            content_hash="source_filter_a",
        ))
        repo.add(sample_news_item(
            source_id=source_id_b,
            title="From Source B",
            content_hash="source_filter_b",
        ))
        db_session.flush()

        items, total = repo.get_recent(source_ids=[source_id_a])
        titles = [item.title for item in items]
        assert "From Source A" in titles
        assert "From Source B" not in titles
        assert total >= 1

    def test_get_recent_filter_by_search(self, db_session):
        source_id = self._add_source(db_session)
        repo = NewsRepository(db_session)

        repo.add(sample_news_item(
            source_id=source_id,
            title="Government Budget Report",
            content_hash="search_filter_1",
        ))
        repo.add(sample_news_item(
            source_id=source_id,
            title="Weather Forecast",
            content_hash="search_filter_2",
        ))
        db_session.flush()

        items, total = repo.get_recent(search="budget")
        assert total >= 1
        assert all("Budget" in item.title or "budget" in (item.content or "") for item in items)

    def test_get_recent_filter_by_date_range(self, db_session):
        source_id = self._add_source(db_session)
        repo = NewsRepository(db_session)

        repo.add(sample_news_item(
            source_id=source_id,
            title="January News",
            content_hash="date_filter_1",
            published_at=datetime(2025, 1, 15),
        ))
        repo.add(sample_news_item(
            source_id=source_id,
            title="June News",
            content_hash="date_filter_2",
            published_at=datetime(2025, 6, 15),
        ))
        db_session.flush()

        items, total = repo.get_recent(
            date_from=datetime(2025, 5, 1),
            date_to=datetime(2025, 7, 1),
        )
        titles = [item.title for item in items]
        assert "June News" in titles
        assert "January News" not in titles

    def test_get_recent_combined_filters(self, db_session):
        source_id_a = self._add_source(db_session, name="Source Combined A")
        source_id_b = self._add_source(db_session, name="Source Combined B")
        repo = NewsRepository(db_session)

        repo.add(sample_news_item(
            source_id=source_id_a,
            title="Budget Report January",
            content_hash="combined_1",
            published_at=datetime(2025, 1, 15),
        ))
        repo.add(sample_news_item(
            source_id=source_id_a,
            title="Budget Report June",
            content_hash="combined_2",
            published_at=datetime(2025, 6, 15),
        ))
        repo.add(sample_news_item(
            source_id=source_id_b,
            title="Budget Report June B",
            content_hash="combined_3",
            published_at=datetime(2025, 6, 15),
        ))
        db_session.flush()

        items, total = repo.get_recent(
            source_ids=[source_id_a],
            search="budget",
            date_from=datetime(2025, 5, 1),
            date_to=datetime(2025, 7, 1),
        )
        assert total == 1
        assert items[0].title == "Budget Report June"

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

    def test_delete_by_source_id(self, db_session):
        source_id = self._add_source(db_session, name="Delete Source News")
        repo = NewsRepository(db_session)

        for i in range(3):
            repo.add(sample_news_item(
                source_id=source_id,
                title=f"Delete Item {i}",
                content_hash=f"delete_source_{i}",
            ))
        db_session.flush()

        count = repo.delete_by_source_id(source_id)
        assert count == 3

        items, total = repo.get_recent(source_ids=[source_id])
        assert total == 0

    def test_delete_by_source_id_no_items(self, db_session):
        repo = NewsRepository(db_session)
        count = repo.delete_by_source_id(9999)
        assert count == 0

    def test_get_recent_empty_source_ids_returns_empty(self, db_session):
        """When source_ids is an empty list, no results should be returned."""
        source_id = self._add_source(db_session, name="Empty Filter Source")
        repo = NewsRepository(db_session)
        repo.add(sample_news_item(
            source_id=source_id,
            title="Should Not Appear",
            content_hash="empty_filter_test",
        ))
        db_session.flush()

        items, total = repo.get_recent(source_ids=[])
        assert items == []
        assert total == 0

    def test_update_none_raises(self, db_session):
        repo = NewsRepository(db_session)
        with pytest.raises(ValueError, match="News item cannot be None"):
            repo.update(None)
