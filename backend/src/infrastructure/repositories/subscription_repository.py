"""Concrete implementation of Subscription repository."""

from backend.src.core.repositories.subscription_repository import ISubscriptionRepository
from backend.src.infrastructure.models import Subscription
from shared.logging import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__name__)


class SubscriptionRepository(ISubscriptionRepository):
    """SQLAlchemy implementation of Subscription repository."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self._db = db

    def get_by_user_and_source(self, user_id: int, source_id: int) -> Subscription | None:
        """Get subscription for a specific user and source."""
        return (
            self._db.query(Subscription)
            .filter(Subscription.user_id == user_id, Subscription.source_id == source_id)
            .first()
        )

    def get_by_user(self, user_id: int, active_only: bool = True) -> list[Subscription]:
        """Get all subscriptions for a user."""
        query = self._db.query(Subscription).filter(Subscription.user_id == user_id)
        if active_only:
            query = query.filter(Subscription.is_active == True)  # noqa: E712
        return query.all()

    def get_subscribed_source_ids(self, user_id: int) -> list[int]:
        """Get list of source IDs the user is subscribed to."""
        rows = (
            self._db.query(Subscription.source_id)
            .filter(Subscription.user_id == user_id, Subscription.is_active == True)  # noqa: E712
            .all()
        )
        return [row[0] for row in rows]

    def add(self, subscription: Subscription) -> Subscription:
        """Add a new subscription."""
        self._db.add(subscription)
        logger.debug("Added subscription: user=%d, source=%d", subscription.user_id, subscription.source_id)
        return subscription

    def delete(self, subscription: Subscription) -> None:
        """Delete a subscription."""
        self._db.delete(subscription)
        logger.debug("Deleted subscription: user=%d, source=%d", subscription.user_id, subscription.source_id)
