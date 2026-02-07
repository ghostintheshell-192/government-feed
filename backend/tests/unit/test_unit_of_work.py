"""Unit tests for Unit of Work pattern."""

from backend.src.infrastructure.repositories.news_repository import NewsRepository
from backend.src.infrastructure.repositories.source_repository import SourceRepository
from backend.src.infrastructure.unit_of_work import UnitOfWork
from backend.tests.conftest import sample_source


class TestUnitOfWork:
    """Tests for UnitOfWork."""

    def test_lazy_init_news_repository(self, db_session):
        uow = UnitOfWork(db_session)
        assert uow._news_repository is None
        repo = uow.news_repository
        assert isinstance(repo, NewsRepository)

    def test_lazy_init_source_repository(self, db_session):
        uow = UnitOfWork(db_session)
        assert uow._source_repository is None
        repo = uow.source_repository
        assert isinstance(repo, SourceRepository)

    def test_repository_is_cached(self, db_session):
        uow = UnitOfWork(db_session)
        repo1 = uow.news_repository
        repo2 = uow.news_repository
        assert repo1 is repo2

    def test_commit(self, db_session):
        uow = UnitOfWork(db_session)
        source = sample_source(name="Commit Test")
        uow.source_repository.add(source)
        uow.commit()
        # After commit, source should have an ID
        assert source.id is not None

    def test_rollback(self, db_session):
        uow = UnitOfWork(db_session)
        source = sample_source(name="Rollback Test")
        uow.source_repository.add(source)
        db_session.flush()
        source_id = source.id

        uow.rollback()
        result = uow.source_repository.get_by_id(source_id)
        assert result is None

    def test_close(self, db_session):
        uow = UnitOfWork(db_session)
        # close should not raise
        uow.close()
