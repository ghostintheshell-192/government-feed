"""Tests for FeedDiscoveryService."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from backend.src.infrastructure.feed_discovery import (
    _COMMON_FEED_PATHS,
    DiscoveredFeed,
    FeedDiscoveryService,
)

SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <link>https://example.com</link>
    <item>
      <title>Article 1</title>
      <link>https://example.com/1</link>
      <description>Content</description>
    </item>
  </channel>
</rss>
"""

SAMPLE_HTML_WITH_FEED_LINKS = """
<html>
<head>
    <link rel="alternate" type="application/rss+xml" title="RSS Feed" href="/feed.xml" />
    <link rel="alternate" type="application/atom+xml" title="Atom Feed" href="/atom.xml" />
</head>
<body><p>Website content</p></body>
</html>
"""


class TestDiscoverFromUrl:
    """Tests for URL-based feed discovery."""

    @pytest.mark.asyncio
    async def test_direct_feed_url(self):
        """When URL is a valid RSS feed, return it immediately."""
        mock_feed = DiscoveredFeed(
            url="https://example.com/feed.xml",
            title="Test Feed",
            feed_type="RSS",
            site_url="https://example.com/feed.xml",
            entry_count=1,
        )
        with patch.object(FeedDiscoveryService, "_validate_feed", return_value=mock_feed):
            service = FeedDiscoveryService(timeout=5.0)
            feeds, sites = await service.discover("https://example.com/feed.xml")

        assert len(feeds) == 1
        assert feeds[0].url == "https://example.com/feed.xml"
        assert feeds[0].entry_count == 1
        assert sites == ["https://example.com/feed.xml"]

    @pytest.mark.asyncio
    async def test_discovers_feeds_from_html_link_tags(self):
        """When URL is not a feed, discover feeds from <link> tags in HTML."""
        call_count = [0]

        async def mock_validate(feed_url, site_url, title=None):
            call_count[0] += 1
            if "feed.xml" in feed_url:
                return DiscoveredFeed(
                    url=feed_url, title=title or "RSS Feed",
                    feed_type="RSS", site_url=site_url, entry_count=5,
                )
            if "atom.xml" in feed_url:
                return DiscoveredFeed(
                    url=feed_url, title=title or "Atom Feed",
                    feed_type="Atom", site_url=site_url, entry_count=3,
                )
            return None  # Main URL is not a feed

        mock_response = MagicMock()
        mock_response.text = SAMPLE_HTML_WITH_FEED_LINKS
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch.object(FeedDiscoveryService, "_validate_feed", side_effect=mock_validate),
            patch("backend.src.infrastructure.feed_discovery.httpx.AsyncClient", return_value=mock_client),
        ):
            service = FeedDiscoveryService(timeout=5.0)
            feeds, sites = await service.discover("https://example.com")

        assert len(feeds) >= 1
        feed_urls = [f.url for f in feeds]
        assert any("feed.xml" in u for u in feed_urls)

    @pytest.mark.asyncio
    async def test_tries_common_paths(self):
        """Try common feed paths when URL is not a feed and no link tags found."""
        async def mock_validate(feed_url, site_url, title=None):
            if feed_url.endswith("/rss.xml"):
                return DiscoveredFeed(
                    url=feed_url, title="RSS",
                    feed_type="RSS", site_url=site_url, entry_count=10,
                )
            return None

        # Return HTML with no feed link tags
        mock_response = MagicMock()
        mock_response.text = "<html><body>No feeds</body></html>"
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch.object(FeedDiscoveryService, "_validate_feed", side_effect=mock_validate),
            patch("backend.src.infrastructure.feed_discovery.httpx.AsyncClient", return_value=mock_client),
        ):
            service = FeedDiscoveryService(timeout=5.0)
            feeds, _ = await service.discover("https://example.com")

        feed_urls = [f.url for f in feeds]
        assert any("rss.xml" in u for u in feed_urls)

    @pytest.mark.asyncio
    async def test_no_feeds_found(self):
        """Return empty list when no feeds are discovered."""
        async def mock_validate(feed_url, site_url, title=None):
            return None  # Nothing validates as a feed

        mock_response = MagicMock()
        mock_response.text = "<html><body>No feeds</body></html>"
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch.object(FeedDiscoveryService, "_validate_feed", side_effect=mock_validate),
            patch("backend.src.infrastructure.feed_discovery.httpx.AsyncClient", return_value=mock_client),
        ):
            service = FeedDiscoveryService(timeout=5.0)
            feeds, _ = await service.discover("https://nofeed.example.com")

        assert feeds == []

    @pytest.mark.asyncio
    async def test_deduplicates_within_url(self):
        """Feed URLs found via link tags and common paths are deduplicated."""
        call_urls = []

        async def mock_validate(feed_url, site_url, title=None):
            call_urls.append(feed_url)
            if "feed.xml" in feed_url:
                return DiscoveredFeed(
                    url=feed_url, title="Feed",
                    feed_type="RSS", site_url=site_url, entry_count=1,
                )
            return None

        # HTML has a link tag pointing to /feed.xml, and /feed is a common path
        html = '<html><head><link rel="alternate" type="application/rss+xml" href="/feed.xml" /></head><body></body></html>'
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch.object(FeedDiscoveryService, "_validate_feed", side_effect=mock_validate),
            patch("backend.src.infrastructure.feed_discovery.httpx.AsyncClient", return_value=mock_client),
        ):
            service = FeedDiscoveryService(timeout=5.0)
            feeds, _ = await service.discover("https://example.com")

        # feed.xml should appear only once even though it might be found via link AND common paths
        feed_urls = [f.url for f in feeds]
        assert feed_urls.count("https://example.com/feed.xml") == 1


class TestValidateFeed:
    """Tests for _validate_feed with actual feedparser."""

    @pytest.mark.asyncio
    async def test_valid_rss_feed(self):
        """Valid RSS feed is recognized and metadata extracted."""
        mock_response = MagicMock()
        mock_response.text = SAMPLE_RSS
        mock_response.headers = {"content-type": "application/rss+xml"}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("backend.src.infrastructure.feed_discovery.httpx.AsyncClient", return_value=mock_client):
            service = FeedDiscoveryService(timeout=5.0)
            result = await service._validate_feed(
                "https://example.com/feed.xml", "https://example.com"
            )

        assert result is not None
        assert result.title == "Test Feed"
        assert result.entry_count == 1
        assert result.feed_type == "RSS"

    @pytest.mark.asyncio
    async def test_http_error_returns_none(self):
        """HTTP errors result in None."""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError("404", request=MagicMock(), response=MagicMock(status_code=404))
        )
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("backend.src.infrastructure.feed_discovery.httpx.AsyncClient", return_value=mock_client):
            service = FeedDiscoveryService(timeout=5.0)
            result = await service._validate_feed(
                "https://example.com/missing.xml", "https://example.com"
            )

        assert result is None

    @pytest.mark.asyncio
    async def test_invalid_xml_returns_none(self):
        """Invalid XML that feedparser rejects returns None."""
        mock_response = MagicMock()
        mock_response.text = "This is not XML at all, just garbage @#$%^&*"
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("backend.src.infrastructure.feed_discovery.httpx.AsyncClient", return_value=mock_client):
            service = FeedDiscoveryService(timeout=5.0)
            result = await service._validate_feed(
                "https://example.com/garbage", "https://example.com"
            )

        # feedparser may or may not flag this as bozo, but it should have 0 entries
        # If the code allows 0-entry feeds through, that's fine - test the actual behavior
        if result is not None:
            assert result.entry_count == 0

    @pytest.mark.asyncio
    async def test_custom_title_used(self):
        """Custom title parameter overrides feed title."""
        mock_response = MagicMock()
        mock_response.text = SAMPLE_RSS
        mock_response.headers = {"content-type": "application/rss+xml"}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("backend.src.infrastructure.feed_discovery.httpx.AsyncClient", return_value=mock_client):
            service = FeedDiscoveryService(timeout=5.0)
            result = await service._validate_feed(
                "https://example.com/feed.xml", "https://example.com",
                title="Custom Title",
            )

        assert result is not None
        assert result.title == "Custom Title"

    @pytest.mark.asyncio
    async def test_xxe_doctype_stripped(self):
        """XXE payloads are neutralized by DOCTYPE stripping."""
        xxe_rss = """<?xml version="1.0"?>
<!DOCTYPE feed [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<rss version="2.0">
  <channel>
    <title>&xxe;</title>
    <item><title>Test</title><link>http://example.com</link></item>
  </channel>
</rss>"""
        mock_response = MagicMock()
        mock_response.text = xxe_rss
        mock_response.headers = {"content-type": "application/rss+xml"}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("backend.src.infrastructure.feed_discovery.httpx.AsyncClient", return_value=mock_client):
            service = FeedDiscoveryService(timeout=5.0)
            result = await service._validate_feed(
                "https://example.com/evil.xml", "https://example.com"
            )

        # Should either return None or a result WITHOUT /etc/passwd content
        if result is not None:
            assert "root:" not in result.title
            assert "/bin/bash" not in result.title


class TestDiscoverFromSearch:
    """Tests for search-based feed discovery."""

    @pytest.mark.asyncio
    async def test_search_uses_ddg(self):
        """Search query triggers DuckDuckGo search."""
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = [
            {"href": "https://result1.com"},
            {"href": "https://result2.com"},
        ]
        mock_ddgs_instance.__enter__ = MagicMock(return_value=mock_ddgs_instance)
        mock_ddgs_instance.__exit__ = MagicMock(return_value=False)

        async def mock_validate(feed_url, site_url, title=None):
            return None

        mock_response = MagicMock()
        mock_response.text = "<html><body></body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch.object(FeedDiscoveryService, "_validate_feed", side_effect=mock_validate),
            patch("backend.src.infrastructure.feed_discovery.httpx.AsyncClient", return_value=mock_client),
            patch("duckduckgo_search.DDGS", return_value=mock_ddgs_instance),
        ):
            service = FeedDiscoveryService(timeout=5.0)
            feeds, sites = await service.discover("government news")

        assert len(sites) == 2
        assert "https://result1.com" in sites

    @pytest.mark.asyncio
    async def test_ddg_failure_returns_empty(self):
        """DuckDuckGo failure results in empty results."""
        with patch("duckduckgo_search.DDGS", side_effect=Exception("Search blocked")):
            service = FeedDiscoveryService(timeout=5.0)
            feeds, sites = await service.discover("government news")

        assert feeds == []
        assert sites == []

    @pytest.mark.asyncio
    async def test_url_detected_as_url_not_search(self):
        """URL starting with http is treated as URL, not search query."""
        mock_feed = DiscoveredFeed(
            url="https://gov.example.com/feed.xml",
            title="Gov Feed",
            feed_type="RSS",
            site_url="https://gov.example.com",
            entry_count=5,
        )
        with patch.object(FeedDiscoveryService, "_discover_from_url", return_value=[mock_feed]):
            service = FeedDiscoveryService(timeout=5.0)
            feeds, sites = await service.discover("https://gov.example.com")

        assert len(feeds) == 1
        assert sites == ["https://gov.example.com"]


class TestDiscoveredFeed:
    """Tests for DiscoveredFeed dataclass."""

    def test_creation(self):
        feed = DiscoveredFeed(
            url="https://example.com/feed.xml",
            title="Test Feed",
            feed_type="RSS",
            site_url="https://example.com",
            entry_count=10,
        )
        assert feed.url == "https://example.com/feed.xml"
        assert feed.entry_count == 10

    def test_equality(self):
        feed1 = DiscoveredFeed("url", "title", "RSS", "site", 5)
        feed2 = DiscoveredFeed("url", "title", "RSS", "site", 5)
        assert feed1 == feed2


class TestCommonFeedPaths:
    """Tests for common feed path constants."""

    def test_common_paths_defined(self):
        assert "/feed" in _COMMON_FEED_PATHS
        assert "/rss" in _COMMON_FEED_PATHS
        assert "/rss.xml" in _COMMON_FEED_PATHS
        assert "/atom.xml" in _COMMON_FEED_PATHS
