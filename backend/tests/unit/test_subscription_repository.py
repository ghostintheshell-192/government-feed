"""Unit tests for SubscriptionRepository."""

import pytest

from backend.src.infrastructure.repositories.subscription_repository import (
    SubscriptionRepository,
)
from backend.tests.conftest import sample_source, sample_subscription


class TestSubscriptionRepository:
    """Tests for SubscriptionRepository."""

    def test_add_and_get(self, db_session):
        source = sample_source(name="Sub Source")
        db_session.add(source)
        db_session.flush()

        repo = SubscriptionRepository(db_session)
        sub = sample_subscription(source_id=source.id)
        repo.add(sub)
        db_session.flush()

        found = repo.get_by_user_and_source(1, source.id)
        assert found is not None
        assert found.source_id == source.id
        assert found.user_id == 1

    def test_get_by_user_and_source_not_found(self, db_session):
        repo = SubscriptionRepository(db_session)
        assert repo.get_by_user_and_source(1, 9999) is None

    def test_get_by_user(self, db_session):
        s1 = sample_source(name="Source A", feed_url="https://a.com/feed")
        s2 = sample_source(name="Source B", feed_url="https://b.com/feed")
        db_session.add_all([s1, s2])
        db_session.flush()

        repo = SubscriptionRepository(db_session)
        repo.add(sample_subscription(source_id=s1.id))
        repo.add(sample_subscription(source_id=s2.id))
        db_session.flush()

        subs = repo.get_by_user(1)
        assert len(subs) == 2

    def test_get_by_user_active_only(self, db_session):
        s1 = sample_source(name="Active", feed_url="https://active.com/feed")
        s2 = sample_source(name="Inactive", feed_url="https://inactive.com/feed")
        db_session.add_all([s1, s2])
        db_session.flush()

        repo = SubscriptionRepository(db_session)
        repo.add(sample_subscription(source_id=s1.id, is_active=True))
        repo.add(sample_subscription(source_id=s2.id, is_active=False))
        db_session.flush()

        active = repo.get_by_user(1, active_only=True)
        assert len(active) == 1
        assert active[0].source_id == s1.id

        all_subs = repo.get_by_user(1, active_only=False)
        assert len(all_subs) == 2

    def test_get_subscribed_source_ids(self, db_session):
        s1 = sample_source(name="Src 1", feed_url="https://1.com/feed")
        s2 = sample_source(name="Src 2", feed_url="https://2.com/feed")
        db_session.add_all([s1, s2])
        db_session.flush()

        repo = SubscriptionRepository(db_session)
        repo.add(sample_subscription(source_id=s1.id))
        repo.add(sample_subscription(source_id=s2.id))
        db_session.flush()

        ids = repo.get_subscribed_source_ids(1)
        assert set(ids) == {s1.id, s2.id}

    def test_delete(self, db_session):
        source = sample_source(name="Del Source", feed_url="https://del.com/feed")
        db_session.add(source)
        db_session.flush()

        repo = SubscriptionRepository(db_session)
        sub = sample_subscription(source_id=source.id)
        repo.add(sub)
        db_session.flush()

        repo.delete(sub)
        db_session.flush()

        assert repo.get_by_user_and_source(1, source.id) is None
