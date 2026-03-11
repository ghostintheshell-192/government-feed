"""Abstract repository interface for Subscription entities."""

from abc import ABC, abstractmethod

from backend.src.core.entities import Subscription


class ISubscriptionRepository(ABC):
    """Abstract base class for Subscription repository."""

    @abstractmethod
    def get_by_user_and_source(self, user_id: int, source_id: int) -> Subscription | None:
        """Get subscription for a specific user and source."""
        pass

    @abstractmethod
    def get_by_user(self, user_id: int, active_only: bool = True) -> list[Subscription]:
        """Get all subscriptions for a user."""
        pass

    @abstractmethod
    def get_subscribed_source_ids(self, user_id: int) -> list[int]:
        """Get list of source IDs the user is subscribed to."""
        pass

    @abstractmethod
    def add(self, subscription: Subscription) -> Subscription:
        """Add a new subscription."""
        pass

    @abstractmethod
    def delete(self, subscription: Subscription) -> None:
        """Delete a subscription."""
        pass
