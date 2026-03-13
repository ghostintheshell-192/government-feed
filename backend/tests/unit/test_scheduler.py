"""Unit tests for FeedScheduler."""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from backend.src.infrastructure.scheduler import FeedScheduler


class TestFeedSchedulerLifecycle:
    """Tests for scheduler start/shutdown lifecycle."""

    def test_start_creates_jobs(self) -> None:
        """Scheduler start adds 3 jobs and starts the scheduler."""
        scheduler = FeedScheduler()
        scheduler.start()
        try:
            status = scheduler.get_status()
            assert status["running"] is True
            assert len(status["jobs"]) == 3
            job_ids = [j["id"] for j in status["jobs"]]
            assert "poll_feeds" in job_ids
            assert "cleanup" in job_ids
            assert "health_check" in job_ids
        finally:
            scheduler.shutdown()

    def test_shutdown_stops_scheduler(self) -> None:
        """Scheduler shutdown stops the scheduler."""
        scheduler = FeedScheduler()
        scheduler.start()
        scheduler.shutdown()
        status = scheduler.get_status()
        assert status["running"] is False

    def test_get_status_before_start(self) -> None:
        """get_status works before scheduler is started."""
        scheduler = FeedScheduler()
        status = scheduler.get_status()
        assert status["running"] is False
        assert status["jobs"] == []

    def test_job_names(self) -> None:
        """Jobs have human-readable names."""
        scheduler = FeedScheduler()
        scheduler.start()
        try:
            status = scheduler.get_status()
            job_names = {j["id"]: j["name"] for j in status["jobs"]}
            assert job_names["poll_feeds"] == "Poll all feeds"
            assert job_names["cleanup"] == "Cleanup old news"
            assert job_names["health_check"] == "Health check sources"
        finally:
            scheduler.shutdown()

    def test_jobs_have_next_run_time(self) -> None:
        """All jobs have a next_run_time after start."""
        scheduler = FeedScheduler()
        scheduler.start()
        try:
            status = scheduler.get_status()
            for job in status["jobs"]:
                assert job["next_run_time"] is not None
        finally:
            scheduler.shutdown()


class TestPollAllFeeds:
    """Tests for _poll_all_feeds job."""

    @patch("backend.src.infrastructure.scheduler.FeedParserService")
    @patch("backend.src.infrastructure.scheduler.UnitOfWork")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_polls_source_never_fetched(
        self,
        mock_session_local: MagicMock,
        mock_uow_cls: MagicMock,
        mock_parser_cls: MagicMock,
    ) -> None:
        """Polls active sources that have never been fetched."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        source = MagicMock()
        source.id = 1
        source.name = "New Feed"
        source.last_fetched = None
        source.update_frequency_minutes = 60

        mock_uow = MagicMock()
        mock_uow.subscription_repository.get_subscribed_source_ids.return_value = [1]
        mock_uow.source_repository.get_all.return_value = [source]
        mock_uow_cls.return_value = mock_uow

        mock_parser = MagicMock()
        mock_parser.parse_and_import.return_value = 5
        mock_parser_cls.return_value = mock_parser

        scheduler = FeedScheduler()
        scheduler._poll_all_feeds()

        mock_parser.parse_and_import.assert_called_once_with(source)
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.FeedParserService")
    @patch("backend.src.infrastructure.scheduler.UnitOfWork")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_polls_source_due_for_update(
        self,
        mock_session_local: MagicMock,
        mock_uow_cls: MagicMock,
        mock_parser_cls: MagicMock,
    ) -> None:
        """Polls source whose last_fetched exceeds update_frequency_minutes."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        source = MagicMock()
        source.id = 1
        source.name = "Due Feed"
        source.last_fetched = datetime.now(UTC) - timedelta(minutes=120)
        source.update_frequency_minutes = 60

        mock_uow = MagicMock()
        mock_uow.subscription_repository.get_subscribed_source_ids.return_value = [1]
        mock_uow.source_repository.get_all.return_value = [source]
        mock_uow_cls.return_value = mock_uow

        mock_parser = MagicMock()
        mock_parser.parse_and_import.return_value = 3
        mock_parser_cls.return_value = mock_parser

        scheduler = FeedScheduler()
        scheduler._poll_all_feeds()

        mock_parser.parse_and_import.assert_called_once_with(source)
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.FeedParserService")
    @patch("backend.src.infrastructure.scheduler.UnitOfWork")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_skips_recently_fetched(
        self,
        mock_session_local: MagicMock,
        mock_uow_cls: MagicMock,
        mock_parser_cls: MagicMock,
    ) -> None:
        """Skips sources fetched recently (within update_frequency_minutes)."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        source = MagicMock()
        source.id = 1
        source.name = "Recent Feed"
        source.last_fetched = datetime.now(UTC) - timedelta(minutes=5)
        source.update_frequency_minutes = 60

        mock_uow = MagicMock()
        mock_uow.subscription_repository.get_subscribed_source_ids.return_value = [1]
        mock_uow.source_repository.get_all.return_value = [source]
        mock_uow_cls.return_value = mock_uow

        scheduler = FeedScheduler()
        scheduler._poll_all_feeds()

        # Parser should never be instantiated for a recently-fetched source
        mock_parser_cls.assert_not_called()
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.FeedParserService")
    @patch("backend.src.infrastructure.scheduler.UnitOfWork")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_polls_multiple_sources(
        self,
        mock_session_local: MagicMock,
        mock_uow_cls: MagicMock,
        mock_parser_cls: MagicMock,
    ) -> None:
        """Polls all due sources, skips those not due."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        source_due = MagicMock()
        source_due.id = 1
        source_due.name = "Due"
        source_due.last_fetched = None
        source_due.update_frequency_minutes = 60

        source_recent = MagicMock()
        source_recent.id = 2
        source_recent.name = "Recent"
        source_recent.last_fetched = datetime.now(UTC) - timedelta(minutes=5)
        source_recent.update_frequency_minutes = 60

        mock_uow = MagicMock()
        mock_uow.subscription_repository.get_subscribed_source_ids.return_value = [1, 2]
        mock_uow.source_repository.get_all.return_value = [source_due, source_recent]
        mock_uow_cls.return_value = mock_uow

        mock_parser = MagicMock()
        mock_parser.parse_and_import.return_value = 2
        mock_parser_cls.return_value = mock_parser

        scheduler = FeedScheduler()
        scheduler._poll_all_feeds()

        # Parser created only for due source
        mock_parser.parse_and_import.assert_called_once_with(source_due)
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.FeedParserService")
    @patch("backend.src.infrastructure.scheduler.UnitOfWork")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_handles_parse_error(
        self,
        mock_session_local: MagicMock,
        mock_uow_cls: MagicMock,
        mock_parser_cls: MagicMock,
    ) -> None:
        """Handles exceptions during feed parsing gracefully."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        source = MagicMock()
        source.id = 1
        source.name = "Error Feed"
        source.last_fetched = None
        source.update_frequency_minutes = 60

        mock_uow = MagicMock()
        mock_uow.subscription_repository.get_subscribed_source_ids.return_value = [1]
        mock_uow.source_repository.get_all.return_value = [source]
        mock_uow_cls.return_value = mock_uow

        mock_parser = MagicMock()
        mock_parser.parse_and_import.side_effect = Exception("parse error")
        mock_parser_cls.return_value = mock_parser

        scheduler = FeedScheduler()
        # Should not raise — error is caught internally
        scheduler._poll_all_feeds()
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.FeedParserService")
    @patch("backend.src.infrastructure.scheduler.UnitOfWork")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_no_active_sources(
        self,
        mock_session_local: MagicMock,
        mock_uow_cls: MagicMock,
        mock_parser_cls: MagicMock,
    ) -> None:
        """Does nothing when there are no active sources."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_uow = MagicMock()
        mock_uow.subscription_repository.get_subscribed_source_ids.return_value = []
        mock_uow.source_repository.get_all.return_value = []
        mock_uow_cls.return_value = mock_uow

        scheduler = FeedScheduler()
        scheduler._poll_all_feeds()

        mock_parser_cls.assert_not_called()
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.UnitOfWork")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_session_closed_on_error(
        self,
        mock_session_local: MagicMock,
        mock_uow_cls: MagicMock,
    ) -> None:
        """Database session is closed even when UoW raises."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_uow = MagicMock()
        mock_uow.subscription_repository.get_subscribed_source_ids.side_effect = Exception(
            "db connection error"
        )
        mock_uow_cls.return_value = mock_uow

        scheduler = FeedScheduler()
        scheduler._poll_all_feeds()

        mock_db.close.assert_called_once()


class TestCleanupOldNews:
    """Tests for _cleanup_old_news job."""

    @patch("backend.src.infrastructure.scheduler.load_settings")
    @patch("backend.src.infrastructure.scheduler.UnitOfWork")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_deletes_old_news(
        self,
        mock_session_local: MagicMock,
        mock_uow_cls: MagicMock,
        mock_load_settings: MagicMock,
    ) -> None:
        """Deletes news items older than retention period."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_load_settings.return_value = {"news_retention_days": 30}

        mock_db.query.return_value.filter.return_value.delete.return_value = 10

        mock_uow = MagicMock()
        mock_uow_cls.return_value = mock_uow

        scheduler = FeedScheduler()
        scheduler._cleanup_old_news()

        mock_db.query.assert_called_once()
        mock_uow.commit.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.load_settings")
    @patch("backend.src.infrastructure.scheduler.UnitOfWork")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_uses_default_retention(
        self,
        mock_session_local: MagicMock,
        mock_uow_cls: MagicMock,
        mock_load_settings: MagicMock,
    ) -> None:
        """Uses default 30 days if news_retention_days not present."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_load_settings.return_value = {}

        mock_db.query.return_value.filter.return_value.delete.return_value = 0

        mock_uow = MagicMock()
        mock_uow_cls.return_value = mock_uow

        scheduler = FeedScheduler()
        scheduler._cleanup_old_news()

        mock_uow.commit.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.load_settings")
    @patch("backend.src.infrastructure.scheduler.UnitOfWork")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_custom_retention_period(
        self,
        mock_session_local: MagicMock,
        mock_uow_cls: MagicMock,
        mock_load_settings: MagicMock,
    ) -> None:
        """Uses custom retention days from settings."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_load_settings.return_value = {"news_retention_days": 7}

        mock_db.query.return_value.filter.return_value.delete.return_value = 50

        mock_uow = MagicMock()
        mock_uow_cls.return_value = mock_uow

        scheduler = FeedScheduler()
        scheduler._cleanup_old_news()

        mock_load_settings.assert_called_once()
        mock_uow.commit.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.load_settings")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_handles_cleanup_error(
        self, mock_session_local: MagicMock, mock_load_settings: MagicMock
    ) -> None:
        """Handles exceptions during cleanup with rollback."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_load_settings.return_value = {"news_retention_days": 30}

        mock_db.query.return_value.filter.return_value.delete.side_effect = Exception(
            "db error"
        )

        scheduler = FeedScheduler()
        # Should not raise
        scheduler._cleanup_old_news()

        mock_db.rollback.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.load_settings")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_no_commit_on_error(
        self, mock_session_local: MagicMock, mock_load_settings: MagicMock
    ) -> None:
        """Does not commit when an error occurs during deletion."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_load_settings.return_value = {"news_retention_days": 30}

        mock_db.query.return_value.filter.return_value.delete.side_effect = Exception(
            "constraint violation"
        )

        scheduler = FeedScheduler()
        scheduler._cleanup_old_news()

        mock_db.commit.assert_not_called()
        mock_db.rollback.assert_called_once()


class TestHealthCheckSources:
    """Tests for _health_check_sources job (delegates to HealthMonitorService)."""

    @patch("backend.src.infrastructure.health_monitor.HealthMonitorService")
    @patch("backend.src.infrastructure.scheduler.UnitOfWork")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_delegates_to_health_monitor(
        self,
        mock_session_local: MagicMock,
        mock_uow_cls: MagicMock,
        mock_monitor_cls: MagicMock,
    ) -> None:
        """Delegates health checking to HealthMonitorService."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_monitor = MagicMock()
        mock_monitor.check_all_subscribed.return_value = [
            {"new_status": "healthy"},
            {"new_status": "degraded"},
        ]
        mock_monitor_cls.return_value = mock_monitor

        scheduler = FeedScheduler()
        scheduler._health_check_sources()

        mock_monitor.check_all_subscribed.assert_called_once_with(user_id=1)
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.health_monitor.HealthMonitorService")
    @patch("backend.src.infrastructure.scheduler.UnitOfWork")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_handles_monitor_exception(
        self,
        mock_session_local: MagicMock,
        mock_uow_cls: MagicMock,
        mock_monitor_cls: MagicMock,
    ) -> None:
        """Does not crash when HealthMonitorService raises."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_monitor = MagicMock()
        mock_monitor.check_all_subscribed.side_effect = Exception("unexpected error")
        mock_monitor_cls.return_value = mock_monitor

        scheduler = FeedScheduler()
        scheduler._health_check_sources()

        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.UnitOfWork")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_session_closed_on_query_error(
        self,
        mock_session_local: MagicMock,
        mock_uow_cls: MagicMock,
    ) -> None:
        """Database session is closed even when query raises."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_uow = MagicMock()
        mock_uow.subscription_repository.get_subscribed_source_ids.side_effect = Exception(
            "db unavailable"
        )
        mock_uow_cls.return_value = mock_uow

        scheduler = FeedScheduler()
        scheduler._health_check_sources()

        mock_db.close.assert_called_once()


class TestTriggerPollNow:
    """Tests for trigger_poll_now."""

    def test_trigger_modifies_job(self) -> None:
        """trigger_poll_now makes the poll job run immediately."""
        scheduler = FeedScheduler()
        scheduler.start()
        try:
            scheduler.trigger_poll_now()
            # The job should still exist after triggering
            status = scheduler.get_status()
            job_ids = [j["id"] for j in status["jobs"]]
            assert "poll_feeds" in job_ids
        finally:
            scheduler.shutdown()

    def test_trigger_before_start_does_not_raise(self) -> None:
        """trigger_poll_now is a no-op when scheduler hasn't started."""
        scheduler = FeedScheduler()
        # Should not raise — get_job returns None and the if-guard skips
        scheduler.trigger_poll_now()
