"""Unit tests for FeedScheduler."""

from datetime import datetime, timedelta
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
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_polls_source_never_fetched(
        self, mock_session_local: MagicMock, mock_parser_cls: MagicMock
    ) -> None:
        """Polls active sources that have never been fetched."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        source = MagicMock()
        source.name = "New Feed"
        source.last_fetched = None
        source.update_frequency_minutes = 60

        mock_db.query.return_value.filter.return_value.all.return_value = [source]

        mock_parser = MagicMock()
        mock_parser.parse_and_import.return_value = 5
        mock_parser_cls.return_value = mock_parser

        scheduler = FeedScheduler()
        scheduler._poll_all_feeds()

        mock_parser.parse_and_import.assert_called_once_with(source)
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.FeedParserService")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_polls_source_due_for_update(
        self, mock_session_local: MagicMock, mock_parser_cls: MagicMock
    ) -> None:
        """Polls source whose last_fetched exceeds update_frequency_minutes."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        source = MagicMock()
        source.name = "Due Feed"
        source.last_fetched = datetime.utcnow() - timedelta(minutes=120)
        source.update_frequency_minutes = 60

        mock_db.query.return_value.filter.return_value.all.return_value = [source]

        mock_parser = MagicMock()
        mock_parser.parse_and_import.return_value = 3
        mock_parser_cls.return_value = mock_parser

        scheduler = FeedScheduler()
        scheduler._poll_all_feeds()

        mock_parser.parse_and_import.assert_called_once_with(source)
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.FeedParserService")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_skips_recently_fetched(
        self, mock_session_local: MagicMock, mock_parser_cls: MagicMock
    ) -> None:
        """Skips sources fetched recently (within update_frequency_minutes)."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        source = MagicMock()
        source.name = "Recent Feed"
        source.last_fetched = datetime.utcnow() - timedelta(minutes=5)
        source.update_frequency_minutes = 60

        mock_db.query.return_value.filter.return_value.all.return_value = [source]

        scheduler = FeedScheduler()
        scheduler._poll_all_feeds()

        # Parser should never be instantiated for a recently-fetched source
        mock_parser_cls.assert_not_called()
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.FeedParserService")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_polls_multiple_sources(
        self, mock_session_local: MagicMock, mock_parser_cls: MagicMock
    ) -> None:
        """Polls all due sources, skips those not due."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        source_due = MagicMock()
        source_due.name = "Due"
        source_due.last_fetched = None
        source_due.update_frequency_minutes = 60

        source_recent = MagicMock()
        source_recent.name = "Recent"
        source_recent.last_fetched = datetime.utcnow() - timedelta(minutes=5)
        source_recent.update_frequency_minutes = 60

        mock_db.query.return_value.filter.return_value.all.return_value = [
            source_due,
            source_recent,
        ]

        mock_parser = MagicMock()
        mock_parser.parse_and_import.return_value = 2
        mock_parser_cls.return_value = mock_parser

        scheduler = FeedScheduler()
        scheduler._poll_all_feeds()

        # Parser created only for due source
        mock_parser.parse_and_import.assert_called_once_with(source_due)
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.FeedParserService")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_handles_parse_error(
        self, mock_session_local: MagicMock, mock_parser_cls: MagicMock
    ) -> None:
        """Handles exceptions during feed parsing gracefully."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        source = MagicMock()
        source.name = "Error Feed"
        source.last_fetched = None
        source.update_frequency_minutes = 60

        mock_db.query.return_value.filter.return_value.all.return_value = [source]

        mock_parser = MagicMock()
        mock_parser.parse_and_import.side_effect = Exception("parse error")
        mock_parser_cls.return_value = mock_parser

        scheduler = FeedScheduler()
        # Should not raise — error is caught internally
        scheduler._poll_all_feeds()
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.FeedParserService")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_no_active_sources(
        self, mock_session_local: MagicMock, mock_parser_cls: MagicMock
    ) -> None:
        """Does nothing when there are no active sources."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.filter.return_value.all.return_value = []

        scheduler = FeedScheduler()
        scheduler._poll_all_feeds()

        mock_parser_cls.assert_not_called()
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.FeedParserService")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_session_closed_on_error(
        self, mock_session_local: MagicMock, mock_parser_cls: MagicMock
    ) -> None:
        """Database session is closed even when query raises."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.side_effect = Exception("db connection error")

        scheduler = FeedScheduler()
        scheduler._poll_all_feeds()

        mock_db.close.assert_called_once()


class TestCleanupOldNews:
    """Tests for _cleanup_old_news job."""

    @patch("backend.src.infrastructure.scheduler.load_settings")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_deletes_old_news(
        self, mock_session_local: MagicMock, mock_load_settings: MagicMock
    ) -> None:
        """Deletes news items older than retention period."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_load_settings.return_value = {"news_retention_days": 30}

        mock_db.query.return_value.filter.return_value.delete.return_value = 10

        scheduler = FeedScheduler()
        scheduler._cleanup_old_news()

        mock_db.query.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.load_settings")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_uses_default_retention(
        self, mock_session_local: MagicMock, mock_load_settings: MagicMock
    ) -> None:
        """Uses default 30 days if news_retention_days not present."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_load_settings.return_value = {}

        mock_db.query.return_value.filter.return_value.delete.return_value = 0

        scheduler = FeedScheduler()
        scheduler._cleanup_old_news()

        # load_settings().get("news_retention_days", 30) should fall through to 30
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.load_settings")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_custom_retention_period(
        self, mock_session_local: MagicMock, mock_load_settings: MagicMock
    ) -> None:
        """Uses custom retention days from settings."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_load_settings.return_value = {"news_retention_days": 7}

        mock_db.query.return_value.filter.return_value.delete.return_value = 50

        scheduler = FeedScheduler()
        scheduler._cleanup_old_news()

        mock_load_settings.assert_called_once()
        mock_db.commit.assert_called_once()
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
    """Tests for _health_check_sources job."""

    @patch("backend.src.infrastructure.scheduler.httpx")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_checks_active_sources(
        self, mock_session_local: MagicMock, mock_httpx: MagicMock
    ) -> None:
        """Performs HEAD request on active source URLs."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        source = MagicMock()
        source.name = "Healthy Feed"
        source.feed_url = "https://example.com/feed.xml"

        mock_db.query.return_value.filter.return_value.all.return_value = [source]

        mock_client = MagicMock()
        mock_httpx.Client.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_httpx.Client.return_value.__exit__ = MagicMock(return_value=False)

        scheduler = FeedScheduler()
        scheduler._health_check_sources()

        mock_client.head.assert_called_once_with(
            "https://example.com/feed.xml", timeout=10.0, follow_redirects=True
        )
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.httpx")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_checks_multiple_sources(
        self, mock_session_local: MagicMock, mock_httpx: MagicMock
    ) -> None:
        """Checks all active sources."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        source_a = MagicMock()
        source_a.name = "Feed A"
        source_a.feed_url = "https://example.com/a.xml"

        source_b = MagicMock()
        source_b.name = "Feed B"
        source_b.feed_url = "https://example.com/b.xml"

        mock_db.query.return_value.filter.return_value.all.return_value = [
            source_a,
            source_b,
        ]

        mock_client = MagicMock()
        mock_httpx.Client.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_httpx.Client.return_value.__exit__ = MagicMock(return_value=False)

        scheduler = FeedScheduler()
        scheduler._health_check_sources()

        assert mock_client.head.call_count == 2
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.httpx")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_handles_unhealthy_source(
        self, mock_session_local: MagicMock, mock_httpx: MagicMock
    ) -> None:
        """Handles connection failure for a source without crashing."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        source = MagicMock()
        source.name = "Dead Feed"
        source.feed_url = "https://example.com/dead.xml"

        mock_db.query.return_value.filter.return_value.all.return_value = [source]

        mock_client = MagicMock()
        mock_client.head.side_effect = Exception("connection refused")
        mock_httpx.Client.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_httpx.Client.return_value.__exit__ = MagicMock(return_value=False)

        scheduler = FeedScheduler()
        # Should not raise — per-source errors are caught
        scheduler._health_check_sources()
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.httpx")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_continues_after_one_source_fails(
        self, mock_session_local: MagicMock, mock_httpx: MagicMock
    ) -> None:
        """Continues checking remaining sources after one fails."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        source_bad = MagicMock()
        source_bad.name = "Bad Feed"
        source_bad.feed_url = "https://example.com/bad.xml"

        source_good = MagicMock()
        source_good.name = "Good Feed"
        source_good.feed_url = "https://example.com/good.xml"

        mock_db.query.return_value.filter.return_value.all.return_value = [
            source_bad,
            source_good,
        ]

        # Each source gets its own Client() context manager call, so we need
        # to set up the mock to track per-call behavior. We mock at the
        # head() level: first call raises, second succeeds.
        mock_client_bad = MagicMock()
        mock_client_bad.head.side_effect = Exception("timeout")

        mock_client_good = MagicMock()

        # Each `with httpx.Client() as client:` creates a new context manager
        cm_bad = MagicMock()
        cm_bad.__enter__ = MagicMock(return_value=mock_client_bad)
        cm_bad.__exit__ = MagicMock(return_value=False)

        cm_good = MagicMock()
        cm_good.__enter__ = MagicMock(return_value=mock_client_good)
        cm_good.__exit__ = MagicMock(return_value=False)

        mock_httpx.Client.side_effect = [cm_bad, cm_good]

        scheduler = FeedScheduler()
        scheduler._health_check_sources()

        # Both sources were checked (second was not skipped)
        mock_client_bad.head.assert_called_once()
        mock_client_good.head.assert_called_once_with(
            "https://example.com/good.xml", timeout=10.0, follow_redirects=True
        )
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.httpx")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_no_sources(
        self, mock_session_local: MagicMock, mock_httpx: MagicMock
    ) -> None:
        """Does nothing when there are no active sources."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.filter.return_value.all.return_value = []

        scheduler = FeedScheduler()
        scheduler._health_check_sources()

        mock_httpx.Client.assert_not_called()
        mock_db.close.assert_called_once()

    @patch("backend.src.infrastructure.scheduler.httpx")
    @patch("backend.src.infrastructure.scheduler.SessionLocal")
    def test_session_closed_on_query_error(
        self, mock_session_local: MagicMock, mock_httpx: MagicMock
    ) -> None:
        """Database session is closed even when query raises."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.side_effect = Exception("db unavailable")

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
