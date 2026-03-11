"""Unit tests for FeedParserService."""

from datetime import UTC, datetime
from time import struct_time
from unittest.mock import MagicMock, patch

import httpx
import pytest

from backend.src.infrastructure import feed_parser as feed_parser_module
from backend.src.infrastructure.feed_parser import FeedParserService
from backend.tests.conftest import sample_source


@pytest.fixture(autouse=True)
def _reset_circuit_breaker():
    """Reset feed fetch circuit breaker before each test."""
    feed_parser_module._cb_feed_fetch.reset()


class TestStripHtml:
    """Tests for _strip_html method."""

    def test_removes_tags(self, uow):
        parser = FeedParserService(uow)
        result = parser._strip_html("<p>Hello <b>world</b></p>")
        assert result == "Hello world"

    def test_removes_script_and_style(self, uow):
        parser = FeedParserService(uow)
        html = "<p>Text</p><script>alert('x')</script><style>.a{}</style>"
        result = parser._strip_html(html)
        assert "alert" not in result
        assert ".a" not in result
        assert "Text" in result

    def test_empty_input(self, uow):
        parser = FeedParserService(uow)
        assert parser._strip_html("") == ""
        assert parser._strip_html(None) == ""

    def test_collapses_whitespace(self, uow):
        parser = FeedParserService(uow)
        result = parser._strip_html("<p>Hello</p>   <p>world</p>")
        assert "  " not in result


class TestCreateHash:
    """Tests for _create_hash method."""

    def test_produces_sha256(self, uow):
        parser = FeedParserService(uow)
        h = parser._create_hash("title", "content", 1, datetime(2025, 1, 1))
        assert len(h) == 64  # SHA256 hex digest

    def test_is_deterministic(self, uow):
        parser = FeedParserService(uow)
        dt = datetime(2025, 1, 1)
        h1 = parser._create_hash("t", "c", 1, dt)
        h2 = parser._create_hash("t", "c", 1, dt)
        assert h1 == h2

    def test_different_inputs_different_hash(self, uow):
        parser = FeedParserService(uow)
        dt = datetime(2025, 1, 1)
        h1 = parser._create_hash("title_a", "c", 1, dt)
        h2 = parser._create_hash("title_b", "c", 1, dt)
        assert h1 != h2


class TestParseDate:
    """Tests for _parse_date method."""

    def test_published_parsed(self, uow):
        parser = FeedParserService(uow)
        entry = MagicMock()
        entry.published_parsed = struct_time((2025, 3, 15, 10, 0, 0, 0, 0, 0))
        result = parser._parse_date(entry)
        assert result == datetime(2025, 3, 15, 10, 0, 0)

    def test_updated_parsed_fallback(self, uow):
        parser = FeedParserService(uow)
        entry = type("Entry", (), {
            "published_parsed": None,
            "updated_parsed": struct_time((2025, 6, 1, 8, 0, 0, 0, 0, 0)),
        })()
        result = parser._parse_date(entry)
        assert result == datetime(2025, 6, 1, 8, 0, 0)

    def test_fallback_to_utcnow(self, uow):
        parser = FeedParserService(uow)
        entry = type("Entry", (), {})()
        result = parser._parse_date(entry)
        # Should be close to now
        assert (datetime.now(UTC) - result).total_seconds() < 5


class TestParseAndImport:
    """Tests for parse_and_import method."""

    @patch("backend.src.infrastructure.feed_parser.feedparser.parse")
    @patch("backend.src.infrastructure.feed_parser.httpx.Client")
    def test_imports_new_items(self, mock_httpx_client_cls, mock_parse, uow, db_session):
        # Setup httpx mock
        mock_response = MagicMock()
        mock_response.text = "<rss>mock feed xml</rss>"
        mock_response.raise_for_status = MagicMock()
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get = MagicMock(return_value=mock_response)
        mock_httpx_client_cls.return_value = mock_client

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

        parser = FeedParserService(uow)
        count = parser.parse_and_import(source)
        assert count == 1

    @patch("backend.src.infrastructure.feed_parser.feedparser.parse")
    @patch("backend.src.infrastructure.feed_parser.httpx.Client")
    def test_skips_duplicates(self, mock_httpx_client_cls, mock_parse, uow, db_session):
        # Setup httpx mock
        mock_response = MagicMock()
        mock_response.text = "<rss>mock</rss>"
        mock_response.raise_for_status = MagicMock()
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get = MagicMock(return_value=mock_response)
        mock_httpx_client_cls.return_value = mock_client

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

        parser = FeedParserService(uow)
        # First import
        parser.parse_and_import(source)
        # Second import — should skip duplicate
        count = parser.parse_and_import(source)
        assert count == 0

    @patch("backend.src.infrastructure.feed_parser.feedparser.parse")
    @patch("backend.src.infrastructure.feed_parser.httpx.Client")
    def test_bozo_feed_returns_zero(self, mock_httpx_client_cls, mock_parse, uow, db_session):
        # Setup httpx mock
        mock_response = MagicMock()
        mock_response.text = "<rss>bad xml</rss>"
        mock_response.raise_for_status = MagicMock()
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get = MagicMock(return_value=mock_response)
        mock_httpx_client_cls.return_value = mock_client

        source = sample_source(name="Bozo Source")
        db_session.add(source)
        db_session.flush()

        mock_parse.return_value = MagicMock(
            bozo=True,
            bozo_exception=Exception("malformed XML"),
        )

        parser = FeedParserService(uow)
        count = parser.parse_and_import(source)
        assert count == 0

    @patch("backend.src.infrastructure.feed_parser.httpx.Client")
    def test_retries_on_connect_error(self, mock_httpx_client_cls, uow, db_session):
        """Verify retry on transient connection errors."""
        mock_response = MagicMock()
        mock_response.text = "<rss>recovered</rss>"
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        # First call fails, second succeeds
        mock_client.get = MagicMock(
            side_effect=[httpx.ConnectError("refused"), mock_response]
        )
        mock_httpx_client_cls.return_value = mock_client

        source = sample_source(name="Retry Source")
        db_session.add(source)
        db_session.flush()

        parser = FeedParserService(uow)

        with patch("backend.src.infrastructure.feed_parser.feedparser.parse") as mock_parse:
            mock_parse.return_value = MagicMock(bozo=False, entries=[])
            count = parser.parse_and_import(source)

        assert count == 0  # no entries, but no crash
        assert mock_client.get.call_count == 2

    @patch("backend.src.infrastructure.feed_parser.httpx.Client")
    def test_cb_opens_after_repeated_failures(self, mock_httpx_client_cls, uow, db_session):
        """Circuit breaker opens after repeated fetch failures."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get = MagicMock(side_effect=Exception("always fails"))
        mock_httpx_client_cls.return_value = mock_client

        source = sample_source(name="CB Source")
        db_session.add(source)
        db_session.flush()

        parser = FeedParserService(uow)

        # Fail 5 times to open CB
        for _ in range(5):
            parser.parse_and_import(source)

        # Next call should be rejected by CB immediately
        count = parser.parse_and_import(source)
        assert count == 0
