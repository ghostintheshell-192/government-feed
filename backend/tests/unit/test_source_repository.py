"""Unit tests for SourceRepository."""

import pytest

from backend.src.infrastructure.repositories.source_repository import SourceRepository
from backend.tests.conftest import sample_source


class TestSourceRepository:
    """Tests for SourceRepository with in-memory SQLite."""

    def test_add_and_get_by_id(self, db_session):
        repo = SourceRepository(db_session)
        source = sample_source(name="Gazzetta Ufficiale")
        repo.add(source)
        db_session.flush()

        result = repo.get_by_id(source.id)
        assert result is not None
        assert result.name == "Gazzetta Ufficiale"

    def test_get_by_id_not_found(self, db_session):
        repo = SourceRepository(db_session)
        result = repo.get_by_id(9999)
        assert result is None

    def test_get_all_ordered_by_name(self, db_session):
        repo = SourceRepository(db_session)
        repo.add(sample_source(name="Zebra Source"))
        repo.add(sample_source(name="Alpha Source"))
        db_session.flush()

        results = repo.get_all()
        names = [s.name for s in results]
        assert names == sorted(names)

    def test_get_active_sources(self, db_session):
        repo = SourceRepository(db_session)
        repo.add(sample_source(name="Active One", is_active=True))
        repo.add(sample_source(name="Inactive One", is_active=False))
        db_session.flush()

        active = repo.get_active_sources()
        assert all(s.is_active for s in active)
        active_names = [s.name for s in active]
        assert "Active One" in active_names
        assert "Inactive One" not in active_names

    def test_update(self, db_session):
        repo = SourceRepository(db_session)
        source = sample_source(name="Original Name")
        repo.add(source)
        db_session.flush()

        source.name = "Updated Name"
        repo.update(source)
        db_session.flush()

        result = repo.get_by_id(source.id)
        assert result.name == "Updated Name"

    def test_delete(self, db_session):
        repo = SourceRepository(db_session)
        source = sample_source(name="To Delete")
        repo.add(source)
        db_session.flush()
        source_id = source.id

        repo.delete(source)
        db_session.flush()

        result = repo.get_by_id(source_id)
        assert result is None

    def test_add_none_raises(self, db_session):
        repo = SourceRepository(db_session)
        with pytest.raises(ValueError, match="Source cannot be None"):
            repo.add(None)

    def test_update_none_raises(self, db_session):
        repo = SourceRepository(db_session)
        with pytest.raises(ValueError, match="Source cannot be None"):
            repo.update(None)

    def test_delete_none_raises(self, db_session):
        repo = SourceRepository(db_session)
        with pytest.raises(ValueError, match="Source cannot be None"):
            repo.delete(None)
