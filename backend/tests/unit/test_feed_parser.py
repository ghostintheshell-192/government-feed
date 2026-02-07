"""Unit tests for FeedParserService."""

from datetime import datetime
from time import struct_time
from unittest.mock import MagicMock, patch

from backend.src.infrastructure.feed_parser import FeedParserService
from backend.tests.conftest import sample_source


class TestStripHtml:
    """Tests for _strip_html method."""

    def test_removes_tags(self, db_session):
        parser = FeedParserService(db_session)
        result = parser._strip_html("<p>Hello <b>world</b></p>")
        assert result == "Hello world"

    def test_removes_script_and_style(self, db_session):
        parser = FeedParserService(db_session)
        html = "<p>Text</p><script>alert('x')</script><style>.a{}</style>"
        result = parser._strip_html(html)
        assert "alert" not in result
        assert ".a" not in result
        assert "Text" in result

    def test_empty_input(self, db_session):
        parser = FeedParserService(db_session)
        assert parser._strip_html("") == ""
        assert parser._strip_html(None) == ""

    def test_collapses_whitespace(self, db_session):
        parser = FeedParserService(db_session)
        result = parser._strip_html("<p>Hello</p>   <p>world</p>")
        assert "  " not in result


class TestCreateHash:
    """Tests for _create_hash method."""

    def test_produces_sha256(self, db_session):
        parser = FeedParserService(db_session)
        h = parser._create_hash("title", "content", 1, datetime(2025, 1, 1))
        assert len(h) == 64  # SHA256 hex digest

    def test_is_deterministic(self, db_session):
        parser = FeedParserService(db_session)
        dt = datetime(2025, 1, 1)
        h1 = parser._create_hash("t", "c", 1, dt)
        h2 = parser._create_hash("t", "c", 1, dt)
        assert h1 == h2

    def test_different_inputs_different_hash(self, db_session):
        parser = FeedParserService(db_session)
        dt = datetime(2025, 1, 1)
        h1 = parser._create_hash("title_a", "c", 1, dt)
        h2 = parser._create_hash("title_b", "c", 1, dt)
        assert h1 != h2


class TestParseDate:
    """Tests for _parse_date method."""

    def test_published_parsed(self, db_session):
        parser = FeedParserService(db_session)
        entry = MagicMock()
        entry.published_parsed = struct_time((2025, 3, 15, 10, 0, 0, 0, 0, 0))
        result = parser._parse_date(entry)
        assert result == datetime(2025, 3, 15, 10, 0, 0)

    def test_updated_parsed_fallback(self, db_session):
        parser = FeedParserService(db_session)
        entry = MagicMock(spec=[])
        entry.published_parsed = None
        entry.updated_parsed = struct_time((2025, 6, 1, 8, 0, 0, 0, 0, 0))
        # Make hasattr work
        entry = type("Entry", (), {
            "published_parsed": None,
            "updated_parsed": struct_time((2025, 6, 1, 8, 0, 0, 0, 0, 0)),
        })()
        result = parser._parse_date(entry)
        assert result == datetime(2025, 6, 1, 8, 0, 0)

    def test_fallback_to_utcnow(self, db_session):
        parser = FeedParserService(db_session)
        entry = type("Entry", (), {})()
        result = parser._parse_date(entry)
        # Should be close to now
        assert (datetime.utcnow() - result).total_seconds() < 5


class TestParseAndImport:
    """Tests for parse_and_import method."""

    @patch("backend.src.infrastructure.feed_parser.feedparser.parse")
    def test_imports_new_items(self, mock_parse, db_session):
        # Add a source first
        source = sample_source(name="Feed Source")
        db_session.add(source)
        db_session.flush()

        # Mock feed data
        entry = MagicMock()
        entry.get.side_effect = lambda key, default="": {
            "title": "New Article",
            "link": "https://example.com/1",
            "summary": "A summary",
        }.get(key, default)
        entry.content = None
        entry.description = "Article content"
        entry.published_parsed = struct_time((2025, 3, 1, 0, 0, 0, 0, 0, 0))

        mock_parse.return_value = MagicMock(
            bozo=False,
            entries=[entry],
        )

        parser = FeedParserService(db_session)
        count = parser.parse_and_import(source)
        assert count == 1

    @patch("backend.src.infrastructure.feed_parser.feedparser.parse")
    def test_skips_duplicates(self, mock_parse, db_session):
        source = sample_source(name="Dup Source")
        db_session.add(source)
        db_session.flush()

        entry = MagicMock()
        entry.get.side_effect = lambda key, default="": {
            "title": "Dup Article",
            "link": "https://example.com/dup",
            "summary": "",
        }.get(key, default)
        entry.content = None
        entry.description = "Content"
        entry.published_parsed = struct_time((2025, 3, 1, 0, 0, 0, 0, 0, 0))

        mock_parse.return_value = MagicMock(bozo=False, entries=[entry])

        parser = FeedParserService(db_session)
        # First import
        parser.parse_and_import(source)
        # Second import — should skip duplicate
        count = parser.parse_and_import(source)
        assert count == 0

    @patch("backend.src.infrastructure.feed_parser.feedparser.parse")
    def test_bozo_feed_returns_zero(self, mock_parse, db_session):
        source = sample_source(name="Bozo Source")
        db_session.add(source)
        db_session.flush()

        mock_parse.return_value = MagicMock(
            bozo=True,
            bozo_exception=Exception("malformed XML"),
        )

        parser = FeedParserService(db_session)
        count = parser.parse_and_import(source)
        assert count == 0
