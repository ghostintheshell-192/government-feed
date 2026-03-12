"""Shared test fixtures for Government Feed backend tests."""

from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.src.infrastructure.database import Base, get_db
from backend.src.infrastructure.models import NewsItem, Source, Subscription
from backend.src.infrastructure.unit_of_work import UnitOfWork


@pytest.fixture(scope="session")
def db_engine():
    """Create a SQLite in-memory engine for testing."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    return engine


@pytest.fixture(scope="session")
def db_tables(db_engine):
    """Create all database tables once per test session."""
    Base.metadata.create_all(bind=db_engine)
    yield
    Base.metadata.drop_all(bind=db_engine)


@pytest.fixture
def db_session(db_engine, db_tables):
    """Provide a transactional database session that rolls back after each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    TestSession = sessionmaker(bind=connection)
    session = TestSession()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def uow(db_session):
    """Provide a UnitOfWork wrapping the test database session."""
    return UnitOfWork(db_session)


@pytest.fixture
def test_client(db_session):
    """Create a FastAPI TestClient with overridden database dependency."""
    from fastapi.testclient import TestClient

    from backend.src.api.main import app

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app, raise_server_exceptions=False) as client:
        yield client

    app.dependency_overrides.clear()


def sample_source(**kwargs) -> Source:
    """Factory for creating test Source ORM instances."""
    defaults = {
        "name": "Test Source",
        "description": "A test source",
        "feed_url": "https://example.com/feed.xml",
        "source_type": "RSS",
        "category": "government",
        "update_frequency_minutes": 60,
        "is_active": True,
        "created_at": datetime(2025, 1, 1),
        "updated_at": datetime(2025, 1, 1),
    }
    defaults.update(kwargs)
    return Source(**defaults)


def sample_news_item(source_id: int = 1, **kwargs) -> NewsItem:
    """Factory for creating test NewsItem ORM instances."""
    defaults = {
        "source_id": source_id,
        "external_id": "https://example.com/article/1",
        "title": "Test News Item",
        "content": "This is test content for a news item.",
        "summary": None,
        "published_at": datetime(2025, 1, 15, 12, 0, 0),
        "fetched_at": datetime(2025, 1, 15, 12, 5, 0),
        "content_hash": "abc123def456",
        "relevance_score": None,
        "verification_status": "pending",
        "created_at": datetime(2025, 1, 15, 12, 5, 0),
        "updated_at": datetime(2025, 1, 15, 12, 5, 0),
    }
    defaults.update(kwargs)
    return NewsItem(**defaults)


def sample_subscription(source_id: int = 1, **kwargs) -> Subscription:
    """Factory for creating test Subscription ORM instances."""
    defaults = {
        "user_id": 1,
        "source_id": source_id,
        "is_active": True,
        "added_at": datetime(2025, 1, 1),
    }
    defaults.update(kwargs)
    return Subscription(**defaults)
