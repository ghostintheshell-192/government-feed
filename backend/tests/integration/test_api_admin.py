"""Integration tests for admin API endpoints."""

from datetime import datetime

from backend.tests.conftest import sample_news_item, sample_source


class TestFeedInspector:
    """Tests for /api/admin/sources/{id}/preview and stats."""

    def test_preview_returns_articles(self, test_client, db_session):
        source = sample_source(name="Preview Source")
        db_session.add(source)
        db_session.flush()

        for i in range(3):
            db_session.add(
                sample_news_item(
                    source_id=source.id,
                    title=f"Article {i}",
                    content_hash=f"preview-{i}",
                    published_at=datetime(2025, 1, 10 + i),
                )
            )
        db_session.flush()

        response = test_client.get(f"/api/admin/sources/{source.id}/preview")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        # Should be ordered by published_at desc
        assert data[0]["title"] == "Article 2"

    def test_preview_respects_limit(self, test_client, db_session):
        source = sample_source(name="Limit Source")
        db_session.add(source)
        db_session.flush()

        for i in range(5):
            db_session.add(
                sample_news_item(
                    source_id=source.id,
                    title=f"Item {i}",
                    content_hash=f"limit-{i}",
                    published_at=datetime(2025, 2, 1 + i),
                )
            )
        db_session.flush()

        response = test_client.get(f"/api/admin/sources/{source.id}/preview?limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_preview_source_not_found(self, test_client):
        response = test_client.get("/api/admin/sources/9999/preview")
        assert response.status_code == 404

    def test_preview_truncates_snippet(self, test_client, db_session):
        source = sample_source(name="Snippet Source")
        db_session.add(source)
        db_session.flush()

        db_session.add(
            sample_news_item(
                source_id=source.id,
                title="Long content",
                content="x" * 300,
                content_hash="snippet-long",
            )
        )
        db_session.flush()

        response = test_client.get(f"/api/admin/sources/{source.id}/preview")
        data = response.json()
        assert data[0]["snippet"].endswith("...")
        assert len(data[0]["snippet"]) == 203  # 200 + "..."

    def test_stats_returns_data(self, test_client, db_session):
        source = sample_source(name="Stats Source")
        db_session.add(source)
        db_session.flush()

        db_session.add(
            sample_news_item(
                source_id=source.id,
                title="Stats item",
                content="Some content here",
                content_hash="stats-1",
                published_at=datetime(2025, 3, 1),
            )
        )
        db_session.flush()

        response = test_client.get(f"/api/admin/sources/{source.id}/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["source_id"] == source.id
        assert data["source_name"] == "Stats Source"
        assert data["article_count"] == 1
        assert data["avg_content_length"] is not None

    def test_stats_source_not_found(self, test_client):
        response = test_client.get("/api/admin/sources/9999/stats")
        assert response.status_code == 404


class TestContentCleanup:
    """Tests for cleanup endpoints."""

    def test_purge_deletes_articles(self, test_client, db_session):
        source = sample_source(name="Purge Source")
        db_session.add(source)
        db_session.flush()

        for i in range(3):
            db_session.add(
                sample_news_item(
                    source_id=source.id,
                    title=f"Purge {i}",
                    content_hash=f"purge-{i}",
                )
            )
        db_session.flush()

        response = test_client.post(f"/api/admin/sources/{source.id}/purge")
        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] == 3
        assert data["dry_run"] is False

    def test_purge_source_not_found(self, test_client):
        response = test_client.post("/api/admin/sources/9999/purge")
        assert response.status_code == 404

    def test_pattern_cleanup_dry_run(self, test_client, db_session):
        source = sample_source(name="Pattern Source")
        db_session.add(source)
        db_session.flush()

        db_session.add(
            sample_news_item(
                source_id=source.id,
                title="Staff Bio: John Doe",
                content_hash="pattern-1",
            )
        )
        db_session.add(
            sample_news_item(
                source_id=source.id,
                title="Real News Article",
                content_hash="pattern-2",
            )
        )
        db_session.flush()

        response = test_client.post(
            "/api/admin/cleanup/by-pattern",
            json={"field": "title", "pattern": "Staff Bio", "dry_run": True},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["matched"] == 1
        assert data["deleted"] == 0
        assert data["dry_run"] is True

    def test_pattern_cleanup_execute(self, test_client, db_session):
        source = sample_source(name="Pattern Exec Source")
        db_session.add(source)
        db_session.flush()

        db_session.add(
            sample_news_item(
                source_id=source.id,
                title="Unwanted: Staff Bio",
                content_hash="patexec-1",
            )
        )
        db_session.add(
            sample_news_item(
                source_id=source.id,
                title="Good Article",
                content_hash="patexec-2",
            )
        )
        db_session.flush()

        response = test_client.post(
            "/api/admin/cleanup/by-pattern",
            json={"field": "title", "pattern": "Staff Bio", "dry_run": False},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["matched"] == 1
        assert data["deleted"] == 1

    def test_pattern_cleanup_by_source(self, test_client, db_session):
        source1 = sample_source(name="Source A")
        source2 = sample_source(name="Source B")
        db_session.add_all([source1, source2])
        db_session.flush()

        db_session.add(
            sample_news_item(
                source_id=source1.id, title="Bio: Alice", content_hash="bysrc-1"
            )
        )
        db_session.add(
            sample_news_item(
                source_id=source2.id, title="Bio: Bob", content_hash="bysrc-2"
            )
        )
        db_session.flush()

        response = test_client.post(
            "/api/admin/cleanup/by-pattern",
            json={
                "field": "title",
                "pattern": "Bio:",
                "source_id": source1.id,
                "dry_run": True,
            },
        )
        data = response.json()
        assert data["matched"] == 1  # Only source1

    def test_html_residue_dry_run(self, test_client, db_session):
        source = sample_source(name="HTML Source")
        db_session.add(source)
        db_session.flush()

        db_session.add(
            sample_news_item(
                source_id=source.id,
                title="Dirty content",
                content="Clean text <div class='wrapper'><script>alert(1)</script>inside</div>",
                content_hash="html-1",
            )
        )
        db_session.add(
            sample_news_item(
                source_id=source.id,
                title="Clean content",
                content="No tags here",
                content_hash="html-2",
            )
        )
        db_session.flush()

        response = test_client.post("/api/admin/cleanup/html-residue?dry_run=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data["flagged"]) >= 1
        assert data["fixed"] == 0
        assert data["dry_run"] is True

    def test_orphan_cleanup(self, test_client, db_session):
        # Create article with non-existent source_id
        from backend.src.infrastructure.models import NewsItem

        orphan = NewsItem(
            source_id=99999,
            title="Orphan article",
            content="Lost content",
            published_at=datetime(2025, 1, 1),
            content_hash="orphan-1",
            verification_status="pending",
        )
        db_session.add(orphan)
        db_session.flush()

        response = test_client.post("/api/admin/cleanup/orphans")
        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] >= 1


class TestDiagnostics:
    """Tests for /api/admin/stats and quality-report."""

    def test_global_stats(self, test_client, db_session):
        source = sample_source(name="Stats Global Source")
        db_session.add(source)
        db_session.flush()

        db_session.add(
            sample_news_item(
                source_id=source.id,
                title="Stats article",
                content_hash="gstats-1",
            )
        )
        db_session.flush()

        response = test_client.get("/api/admin/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_articles"] >= 1
        assert data["total_sources"] >= 1
        assert len(data["per_source"]) >= 1

    def test_quality_report_short_content(self, test_client, db_session):
        source = sample_source(name="QR Source")
        db_session.add(source)
        db_session.flush()

        db_session.add(
            sample_news_item(
                source_id=source.id,
                title="Short one",
                content="tiny",
                content_hash="qr-short-1",
            )
        )
        db_session.flush()

        response = test_client.get("/api/admin/quality-report")
        assert response.status_code == 200
        data = response.json()
        assert len(data["short_content"]) >= 1

    def test_quality_report_duplicate_titles(self, test_client, db_session):
        source = sample_source(name="Dupe Source")
        db_session.add(source)
        db_session.flush()

        for i in range(2):
            db_session.add(
                sample_news_item(
                    source_id=source.id,
                    title="Duplicate Title",
                    content_hash=f"dupe-{i}",
                )
            )
        db_session.flush()

        response = test_client.get("/api/admin/quality-report")
        data = response.json()
        dupe_titles = [d["title"] for d in data["duplicate_titles"]]
        assert "Duplicate Title" in dupe_titles

    def test_quality_report_empty_sources(self, test_client, db_session):
        source = sample_source(name="Empty Source QR")
        db_session.add(source)
        db_session.flush()

        response = test_client.get("/api/admin/quality-report")
        data = response.json()
        empty_names = [s["name"] for s in data["empty_sources"]]
        assert "Empty Source QR" in empty_names

    def test_quality_report_html_residue(self, test_client, db_session):
        source = sample_source(name="HTML QR Source")
        db_session.add(source)
        db_session.flush()

        db_session.add(
            sample_news_item(
                source_id=source.id,
                title="HTML in summary",
                summary="Text <div>with tags</div>",
                content_hash="qr-html-1",
            )
        )
        db_session.flush()

        response = test_client.get("/api/admin/quality-report")
        data = response.json()
        html_fields = [(h["title"], h["field"]) for h in data["html_residue"]]
        assert ("HTML in summary", "summary") in html_fields
