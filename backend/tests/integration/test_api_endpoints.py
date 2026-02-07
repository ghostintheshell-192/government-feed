"""Integration tests for FastAPI API endpoints."""

from datetime import datetime
from unittest.mock import patch

from backend.tests.conftest import sample_news_item, sample_source


class TestHealthCheck:
    """Test root health check endpoint."""

    def test_root(self, test_client):
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert "version" in data


class TestSourcesEndpoints:
    """Tests for /api/sources endpoints."""

    def test_list_sources_empty(self, test_client):
        response = test_client.get("/api/sources")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_source(self, test_client):
        payload = {
            "name": "Test Source",
            "feed_url": "https://example.com/feed.xml",
            "source_type": "RSS",
            "update_frequency_minutes": 60,
        }
        response = test_client.post("/api/sources", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Source"
        assert data["id"] is not None
        assert data["is_active"] is True

    def test_get_source(self, test_client, db_session):
        source = sample_source(name="Get Me")
        db_session.add(source)
        db_session.flush()

        response = test_client.get(f"/api/sources/{source.id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Get Me"

    def test_get_source_not_found(self, test_client):
        response = test_client.get("/api/sources/9999")
        assert response.status_code == 404

    def test_update_source(self, test_client, db_session):
        source = sample_source(name="Old Name")
        db_session.add(source)
        db_session.flush()

        payload = {
            "name": "New Name",
            "feed_url": "https://example.com/new-feed.xml",
            "source_type": "RSS",
            "update_frequency_minutes": 30,
            "is_active": False,
        }
        response = test_client.put(f"/api/sources/{source.id}", json=payload)
        assert response.status_code == 200
        assert response.json()["name"] == "New Name"
        assert response.json()["is_active"] is False

    def test_update_source_not_found(self, test_client):
        payload = {
            "name": "No Source",
            "feed_url": "https://example.com/feed.xml",
            "source_type": "RSS",
            "update_frequency_minutes": 60,
            "is_active": True,
        }
        response = test_client.put("/api/sources/9999", json=payload)
        assert response.status_code == 404

    def test_delete_source(self, test_client, db_session):
        source = sample_source(name="Delete Me")
        db_session.add(source)
        db_session.flush()

        response = test_client.delete(f"/api/sources/{source.id}")
        assert response.status_code == 204

    def test_delete_source_not_found(self, test_client):
        response = test_client.delete("/api/sources/9999")
        assert response.status_code == 404


class TestNewsEndpoints:
    """Tests for /api/news endpoints."""

    def test_list_news_empty(self, test_client):
        response = test_client.get("/api/news")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["pagination"]["total"] == 0
        assert data["pagination"]["has_more"] is False

    def test_list_news_with_data(self, test_client, db_session):
        source = sample_source(name="News Source")
        db_session.add(source)
        db_session.flush()

        item = sample_news_item(source_id=source.id, content_hash="api_test_hash_1")
        db_session.add(item)
        db_session.flush()

        response = test_client.get("/api/news")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert data["pagination"]["total"] >= 1

    def test_list_news_pagination_params(self, test_client, db_session):
        source = sample_source(name="Pagination Source")
        db_session.add(source)
        db_session.flush()

        for i in range(5):
            db_session.add(sample_news_item(
                source_id=source.id,
                content_hash=f"pagination_api_{i}",
                title=f"Pagination Item {i}",
            ))
        db_session.flush()

        response = test_client.get("/api/news?limit=2&offset=0")
        data = response.json()
        assert len(data["items"]) == 2
        assert data["pagination"]["limit"] == 2
        assert data["pagination"]["offset"] == 0
        assert data["pagination"]["has_more"] is True

    def test_list_news_source_filter(self, test_client, db_session):
        source_a = sample_source(name="Filter Source A")
        source_b = sample_source(name="Filter Source B", feed_url="https://b.com/feed.xml")
        db_session.add(source_a)
        db_session.add(source_b)
        db_session.flush()

        db_session.add(sample_news_item(
            source_id=source_a.id, content_hash="filter_api_a", title="From A",
        ))
        db_session.add(sample_news_item(
            source_id=source_b.id, content_hash="filter_api_b", title="From B",
        ))
        db_session.flush()

        response = test_client.get(f"/api/news?source_id={source_a.id}")
        data = response.json()
        titles = [item["title"] for item in data["items"]]
        assert "From A" in titles
        assert "From B" not in titles

    def test_list_news_search_filter(self, test_client, db_session):
        source = sample_source(name="Search API Source")
        db_session.add(source)
        db_session.flush()

        db_session.add(sample_news_item(
            source_id=source.id, content_hash="search_api_1", title="Budget Report 2025",
        ))
        db_session.add(sample_news_item(
            source_id=source.id, content_hash="search_api_2", title="Weather Update",
        ))
        db_session.flush()

        response = test_client.get("/api/news?search=budget")
        data = response.json()
        assert data["pagination"]["total"] >= 1
        assert all("Budget" in item["title"] or "budget" in (item["content"] or "")
                    for item in data["items"])

    def test_list_news_date_range_filter(self, test_client, db_session):
        source = sample_source(name="Date API Source")
        db_session.add(source)
        db_session.flush()

        db_session.add(sample_news_item(
            source_id=source.id, content_hash="date_api_1",
            title="Old News", published_at=datetime(2024, 1, 1),
        ))
        db_session.add(sample_news_item(
            source_id=source.id, content_hash="date_api_2",
            title="Recent News", published_at=datetime(2025, 6, 1),
        ))
        db_session.flush()

        response = test_client.get("/api/news?date_from=2025-01-01T00:00:00&date_to=2025-12-31T23:59:59")
        data = response.json()
        titles = [item["title"] for item in data["items"]]
        assert "Recent News" in titles
        assert "Old News" not in titles

    def test_get_news_item_not_found(self, test_client):
        response = test_client.get("/api/news/9999")
        assert response.status_code == 404


class TestSettingsEndpoints:
    """Tests for /api/settings endpoints."""

    @patch("backend.src.infrastructure.settings_store.load_settings")
    def test_get_settings(self, mock_load, test_client):
        mock_load.return_value = {"ai_enabled": True, "ollama_model": "test"}
        response = test_client.get("/api/settings")
        assert response.status_code == 200
        assert response.json()["ai_enabled"] is True

    @patch("backend.src.infrastructure.settings_store.save_settings")
    def test_update_settings(self, mock_save, test_client):
        payload = {"ai_enabled": False}
        response = test_client.put("/api/settings", json=payload)
        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_save.assert_called_once_with({"ai_enabled": False})

    @patch("backend.src.infrastructure.settings_store.load_settings")
    def test_get_features(self, mock_load, test_client):
        mock_load.return_value = {"ai_enabled": True}
        response = test_client.get("/api/settings/features")
        assert response.status_code == 200
        data = response.json()
        assert data["ai_enabled"] is True
        assert data["verification_enabled"] is False
        assert data["blockchain_enabled"] is False


class TestSummarizeEndpoint:
    """Tests for /api/news/{id}/summarize endpoint."""

    def test_summarize_news_not_found(self, test_client):
        response = test_client.post("/api/news/9999/summarize")
        assert response.status_code == 404

    @patch("backend.src.infrastructure.settings_store.load_settings")
    def test_summarize_ai_disabled(self, mock_load, test_client, db_session):
        source = sample_source(name="AI Source")
        db_session.add(source)
        db_session.flush()

        item = sample_news_item(source_id=source.id, content_hash="summarize_test_1")
        db_session.add(item)
        db_session.flush()

        mock_load.return_value = {"ai_enabled": False}
        response = test_client.post(f"/api/news/{item.id}/summarize")
        assert response.status_code == 400
        assert "AI non abilitata" in response.json()["detail"]
