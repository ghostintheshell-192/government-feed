"""Tests for API endpoints not covered by test_api_endpoints.py.

Covers: discover_feeds, process_feed, fetch_news_content,
        scheduler endpoints, cache status, settings validation.
"""

from unittest.mock import AsyncMock, MagicMock, patch

from backend.tests.conftest import sample_news_item, sample_source


class TestFeedDiscoveryEndpoint:
    """Tests for POST /api/sources/discover."""

    @patch("backend.src.infrastructure.feed_discovery.FeedDiscoveryService")
    def test_discover_feeds_success(self, mock_service_cls, test_client):
        from backend.src.infrastructure.feed_discovery import DiscoveredFeed

        mock_instance = AsyncMock()
        mock_instance.discover.return_value = (
            [
                DiscoveredFeed(
                    url="https://example.com/feed.xml",
                    title="Test Feed",
                    feed_type="RSS",
                    site_url="https://example.com",
                    entry_count=5,
                )
            ],
            ["https://example.com"],
        )
        mock_service_cls.return_value = mock_instance

        response = test_client.post(
            "/api/sources/discover", json={"query": "https://example.com"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["feeds"]) == 1
        assert data["feeds"][0]["url"] == "https://example.com/feed.xml"
        assert data["searched_sites"] == ["https://example.com"]

    def test_discover_feeds_empty_query(self, test_client):
        response = test_client.post("/api/sources/discover", json={"query": ""})
        assert response.status_code == 422  # Validation error (min_length=1)

    def test_discover_feeds_missing_query(self, test_client):
        response = test_client.post("/api/sources/discover", json={})
        assert response.status_code == 422


class TestProcessFeedEndpoint:
    """Tests for POST /api/sources/{source_id}/process."""

    def test_process_feed_success(self, test_client, db_session):
        source = sample_source()
        db_session.add(source)
        db_session.flush()

        with patch("backend.src.infrastructure.feed_parser.FeedParserService") as mock_parser_cls:
            mock_parser = MagicMock()
            mock_parser.parse_and_import.return_value = 3
            mock_parser_cls.return_value = mock_parser

            response = test_client.post(f"/api/sources/{source.id}/process")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "3" in data["message"]

    def test_process_feed_no_results(self, test_client, db_session):
        source = sample_source()
        db_session.add(source)
        db_session.flush()

        with patch("backend.src.infrastructure.feed_parser.FeedParserService") as mock_parser_cls:
            mock_parser = MagicMock()
            mock_parser.parse_and_import.return_value = 0
            mock_parser_cls.return_value = mock_parser

            response = test_client.post(f"/api/sources/{source.id}/process")

        assert response.status_code == 200
        assert response.json()["success"] is False

    def test_process_feed_not_found(self, test_client):
        response = test_client.post("/api/sources/9999/process")
        assert response.status_code == 404


class TestFetchContentEndpoint:
    """Tests for POST /api/news/{news_id}/fetch-content."""

    def test_fetch_content_success(self, test_client, db_session):
        source = sample_source()
        db_session.add(source)
        db_session.flush()

        news = sample_news_item(
            source_id=source.id,
            content="Short",
            external_id="https://example.com/article",
        )
        db_session.add(news)
        db_session.flush()

        with patch("backend.src.infrastructure.content_scraper.ContentScraper") as mock_scraper_cls:
            mock_scraper = AsyncMock()
            mock_scraper.fetch_article_content.return_value = "Full article content here"
            mock_scraper_cls.return_value = mock_scraper

            response = test_client.post(f"/api/news/{news.id}/fetch-content")

        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["content"] == "Full article content here"

    def test_fetch_content_already_has_content(self, test_client, db_session):
        source = sample_source()
        db_session.add(source)
        db_session.flush()

        news = sample_news_item(
            source_id=source.id,
            content="A" * 600,  # > 500 chars
            external_id="https://example.com/article",
        )
        db_session.add(news)
        db_session.flush()

        # Should return existing content without scraping
        response = test_client.post(f"/api/news/{news.id}/fetch-content")

        assert response.status_code == 200
        assert response.json()["success"] is True
        assert len(response.json()["content"]) == 600

    def test_fetch_content_no_url(self, test_client, db_session):
        source = sample_source()
        db_session.add(source)
        db_session.flush()

        news = sample_news_item(source_id=source.id, external_id=None, content="Short")
        db_session.add(news)
        db_session.flush()

        response = test_client.post(f"/api/news/{news.id}/fetch-content")
        assert response.status_code == 400

    def test_fetch_content_not_found(self, test_client):
        response = test_client.post("/api/news/9999/fetch-content")
        assert response.status_code == 404

    def test_fetch_content_scraper_error(self, test_client, db_session):
        source = sample_source()
        db_session.add(source)
        db_session.flush()

        news = sample_news_item(
            source_id=source.id,
            content="Short",
            external_id="https://example.com/article",
        )
        db_session.add(news)
        db_session.flush()

        with patch("backend.src.infrastructure.content_scraper.ContentScraper") as mock_scraper_cls:
            mock_scraper = AsyncMock()
            mock_scraper.fetch_article_content.return_value = "Impossibile recuperare il contenuto"
            mock_scraper_cls.return_value = mock_scraper

            response = test_client.post(f"/api/news/{news.id}/fetch-content")

        assert response.status_code == 200
        assert response.json()["success"] is False


class TestSchedulerEndpoints:
    """Tests for scheduler status and trigger endpoints."""

    def test_scheduler_status(self, test_client):
        response = test_client.get("/api/scheduler/status")
        assert response.status_code == 200
        data = response.json()
        # Scheduler may or may not be running in test environment
        assert "running" in data or "jobs" in data

    def test_cache_status(self, test_client):
        response = test_client.get("/api/cache/status")
        assert response.status_code == 200
        data = response.json()
        assert "available" in data


class TestSettingsValidation:
    """Tests for settings endpoint input validation (Pydantic schema)."""

    @patch("backend.src.infrastructure.settings_store.save_settings")
    @patch("backend.src.infrastructure.settings_store.load_settings")
    def test_rejects_arbitrary_keys(self, mock_load, mock_save, test_client):
        """Arbitrary keys should be ignored by Pydantic schema."""
        mock_load.return_value = {"ai_enabled": True}
        response = test_client.put(
            "/api/settings", json={"malicious_key": "evil_value"}
        )
        assert response.status_code == 200
        # No malicious key should have been saved
        if mock_save.called:
            saved = mock_save.call_args[0][0]
            assert "malicious_key" not in saved

    @patch("backend.src.infrastructure.settings_store.save_settings")
    @patch("backend.src.infrastructure.settings_store.load_settings")
    def test_validates_summary_max_words_range(self, mock_load, mock_save, test_client):
        """summary_max_words must be between 10 and 1000."""
        mock_load.return_value = {}
        response = test_client.put(
            "/api/settings", json={"summary_max_words": 5}
        )
        assert response.status_code == 422  # Below minimum

    @patch("backend.src.infrastructure.settings_store.save_settings")
    @patch("backend.src.infrastructure.settings_store.load_settings")
    def test_validates_retention_days_range(self, mock_load, mock_save, test_client):
        """news_retention_days must be between 1 and 365."""
        mock_load.return_value = {}
        response = test_client.put(
            "/api/settings", json={"news_retention_days": 0}
        )
        assert response.status_code == 422

        response = test_client.put(
            "/api/settings", json={"news_retention_days": 500}
        )
        assert response.status_code == 422

    @patch("backend.src.infrastructure.settings_store.save_settings")
    @patch("backend.src.infrastructure.settings_store.load_settings")
    def test_accepts_valid_settings(self, mock_load, mock_save, test_client):
        """Valid settings should be accepted."""
        mock_load.return_value = {"ai_enabled": True}
        response = test_client.put(
            "/api/settings",
            json={
                "ai_enabled": False,
                "summary_max_words": 150,
                "scheduler_enabled": True,
                "news_retention_days": 60,
            },
        )
        assert response.status_code == 200
        saved = mock_save.call_args[0][0]
        assert saved["ai_enabled"] is False
        assert saved["summary_max_words"] == 150
        assert saved["news_retention_days"] == 60

    @patch("backend.src.infrastructure.settings_store.save_settings")
    @patch("backend.src.infrastructure.settings_store.load_settings")
    def test_partial_update_preserves_existing(self, mock_load, mock_save, test_client):
        """Partial updates should not erase existing settings."""
        mock_load.return_value = {
            "ai_enabled": True,
            "ollama_model": "deepseek-r1:7b",
            "summary_max_words": 200,
        }
        response = test_client.put(
            "/api/settings", json={"ai_enabled": False}
        )
        assert response.status_code == 200
        saved = mock_save.call_args[0][0]
        assert saved["ai_enabled"] is False
        assert saved["ollama_model"] == "deepseek-r1:7b"  # Preserved
        assert saved["summary_max_words"] == 200  # Preserved
