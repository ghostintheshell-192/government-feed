"""Integration tests for catalog API endpoints."""

from backend.src.infrastructure.models import NewsItem, Source, Subscription
from backend.tests.conftest import sample_news_item, sample_source


class TestCatalogBrowse:
    """Tests for GET /api/catalog."""

    def test_browse_empty_catalog(self, test_client):
        response = test_client.get("/api/catalog")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["pagination"]["total"] == 0

    def test_browse_returns_all_sources(self, test_client, db_session):
        s1 = sample_source(name="Source A", feed_url="https://a.com/feed")
        s2 = sample_source(name="Source B", feed_url="https://b.com/feed")
        db_session.add_all([s1, s2])
        db_session.commit()

        response = test_client.get("/api/catalog")
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["total"] == 2
        assert len(data["items"]) == 2

    def test_browse_filter_by_geographic_level(self, test_client, db_session):
        s1 = Source(
            name="National", feed_url="https://n.com/feed",
            geographic_level="NATIONAL",
        )
        s2 = Source(
            name="Local", feed_url="https://l.com/feed",
            geographic_level="LOCAL",
        )
        db_session.add_all([s1, s2])
        db_session.commit()

        response = test_client.get("/api/catalog?geographic_level=NATIONAL")
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["total"] == 1
        assert data["items"][0]["name"] == "National"

    def test_browse_search(self, test_client, db_session):
        db_session.add(Source(name="Banca d'Italia", feed_url="https://bdi.it/feed"))
        db_session.add(Source(name="ISTAT", feed_url="https://istat.it/feed"))
        db_session.commit()

        response = test_client.get("/api/catalog?search=banca")
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["total"] == 1
        assert "Banca" in data["items"][0]["name"]

    def test_browse_marks_subscribed(self, test_client, db_session):
        s1 = sample_source(name="Subscribed", feed_url="https://sub.com/feed")
        s2 = sample_source(name="Not Subscribed", feed_url="https://unsub.com/feed")
        db_session.add_all([s1, s2])
        db_session.flush()

        db_session.add(Subscription(user_id=1, source_id=s1.id))
        db_session.commit()

        response = test_client.get("/api/catalog")
        data = response.json()
        items = {item["name"]: item for item in data["items"]}
        assert items["Subscribed"]["is_subscribed"] is True
        assert items["Not Subscribed"]["is_subscribed"] is False

    def test_browse_pagination(self, test_client, db_session):
        for i in range(5):
            db_session.add(Source(name=f"Source {i}", feed_url=f"https://{i}.com/feed"))
        db_session.commit()

        response = test_client.get("/api/catalog?limit=2&offset=0")
        data = response.json()
        assert len(data["items"]) == 2
        assert data["pagination"]["total"] == 5
        assert data["pagination"]["has_more"] is True

        response = test_client.get("/api/catalog?limit=2&offset=4")
        data = response.json()
        assert len(data["items"]) == 1
        assert data["pagination"]["has_more"] is False


class TestCatalogStats:
    """Tests for GET /api/catalog/stats."""

    def test_stats_empty(self, test_client):
        response = test_client.get("/api/catalog/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_sources"] == 0

    def test_stats_by_level(self, test_client, db_session):
        db_session.add(Source(
            name="National", feed_url="https://n.com/feed", geographic_level="NATIONAL"
        ))
        db_session.add(Source(
            name="Local", feed_url="https://l.com/feed", geographic_level="LOCAL"
        ))
        db_session.commit()

        response = test_client.get("/api/catalog/stats")
        data = response.json()
        assert data["total_sources"] == 2
        assert data["by_geographic_level"]["NATIONAL"] == 1
        assert data["by_geographic_level"]["LOCAL"] == 1


class TestSubscribe:
    """Tests for POST /api/catalog/{source_id}/subscribe."""

    def test_subscribe_success(self, test_client, db_session):
        source = sample_source(name="New Sub")
        db_session.add(source)
        db_session.commit()

        response = test_client.post(f"/api/catalog/{source.id}/subscribe")
        assert response.status_code == 201
        data = response.json()
        assert data["source_id"] == source.id
        assert data["is_active"] is True

    def test_subscribe_nonexistent_source(self, test_client):
        response = test_client.post("/api/catalog/9999/subscribe")
        assert response.status_code == 404

    def test_subscribe_duplicate(self, test_client, db_session):
        source = sample_source(name="Dup Sub", feed_url="https://dup.com/feed")
        db_session.add(source)
        db_session.flush()
        db_session.add(Subscription(user_id=1, source_id=source.id))
        db_session.commit()

        response = test_client.post(f"/api/catalog/{source.id}/subscribe")
        assert response.status_code == 409


class TestUnsubscribe:
    """Tests for DELETE /api/catalog/{source_id}/subscribe."""

    def test_unsubscribe_success(self, test_client, db_session):
        source = sample_source(name="Unsub", feed_url="https://unsub.com/feed")
        db_session.add(source)
        db_session.flush()
        db_session.add(Subscription(user_id=1, source_id=source.id))
        db_session.commit()

        response = test_client.delete(f"/api/catalog/{source.id}/subscribe")
        assert response.status_code == 204

        # Source still exists in catalog
        response = test_client.get("/api/catalog")
        assert response.json()["pagination"]["total"] == 1

    def test_unsubscribe_not_found(self, test_client):
        response = test_client.delete("/api/catalog/9999/subscribe")
        assert response.status_code == 404

    def test_unsubscribe_deletes_news(self, test_client, db_session):
        source = sample_source(name="Unsub News", feed_url="https://unsub-news.com/feed")
        db_session.add(source)
        db_session.flush()
        db_session.add(Subscription(user_id=1, source_id=source.id))
        db_session.add(sample_news_item(
            source_id=source.id, content_hash="unsub_news_test_1"
        ))
        db_session.commit()

        response = test_client.delete(f"/api/catalog/{source.id}/subscribe")
        assert response.status_code == 204

        # News items should be deleted
        news_count = db_session.query(NewsItem).filter_by(source_id=source.id).count()
        assert news_count == 0

        # Source still exists
        assert db_session.query(Source).filter_by(id=source.id).first() is not None
