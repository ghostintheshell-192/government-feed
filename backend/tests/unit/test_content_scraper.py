"""Tests for ContentScraper service."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from backend.src.infrastructure.content_scraper import ContentScraper, _cb_scraping
from backend.src.infrastructure.resilience import CircuitState


@pytest.fixture(autouse=True)
def reset_circuit_breaker():
    """Reset circuit breaker before each test."""
    _cb_scraping._state = CircuitState.CLOSED
    _cb_scraping._failure_count = 0


class TestFetchArticleContent:
    """Tests for ContentScraper.fetch_article_content()."""

    @pytest.mark.asyncio
    async def test_extracts_article_content(self):
        """Test extracting content from a page with <article> tag."""
        html = """
        <html>
        <body>
            <nav>Navigation</nav>
            <article>
                <h1>Test Article</h1>
                <p>First paragraph of the article.</p>
                <p>Second paragraph with more details.</p>
            </article>
            <footer>Footer content</footer>
        </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("backend.src.infrastructure.content_scraper.httpx.AsyncClient", return_value=mock_client):
            scraper = ContentScraper()
            result = await scraper.fetch_article_content("https://example.com/article")

        assert "Test Article" in result
        assert "First paragraph" in result
        assert "Navigation" not in result
        assert "Footer content" not in result

    @pytest.mark.asyncio
    async def test_removes_script_and_style(self):
        """Test that script and style elements are removed."""
        html = """
        <html>
        <body>
            <article>
                <script>alert('xss')</script>
                <style>.hidden { display: none; }</style>
                <p>Clean content here.</p>
            </article>
        </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("backend.src.infrastructure.content_scraper.httpx.AsyncClient", return_value=mock_client):
            scraper = ContentScraper()
            result = await scraper.fetch_article_content("https://example.com/article")

        assert "alert" not in result
        assert "display: none" not in result
        assert "Clean content here." in result

    @pytest.mark.asyncio
    async def test_falls_back_to_body(self):
        """Test fallback to body when no content selector matches."""
        html = """
        <html>
        <body>
            <div class="custom-layout">
                <p>Body content without article tag.</p>
            </div>
        </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("backend.src.infrastructure.content_scraper.httpx.AsyncClient", return_value=mock_client):
            scraper = ContentScraper()
            result = await scraper.fetch_article_content("https://example.com/article")

        assert "Body content without article tag." in result

    @pytest.mark.asyncio
    async def test_main_selector(self):
        """Test extraction using <main> selector."""
        html = """
        <html>
        <body>
            <header>Site Header</header>
            <main>
                <p>Main content here.</p>
            </main>
            <aside>Sidebar</aside>
        </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("backend.src.infrastructure.content_scraper.httpx.AsyncClient", return_value=mock_client):
            scraper = ContentScraper()
            result = await scraper.fetch_article_content("https://example.com/article")

        assert "Main content here." in result
        # Header and aside should be removed
        assert "Site Header" not in result

    @pytest.mark.asyncio
    async def test_removes_noise_within_content(self):
        """Test that noise elements within main content are removed."""
        html = """
        <html>
        <body>
            <article>
                <p>Article text.</p>
                <div class="breadcrumb">Home > News > Article</div>
                <div class="share-links">Share on Twitter</div>
                <p>More article text.</p>
            </article>
        </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("backend.src.infrastructure.content_scraper.httpx.AsyncClient", return_value=mock_client):
            scraper = ContentScraper()
            result = await scraper.fetch_article_content("https://example.com/article")

        assert "Article text." in result
        assert "More article text." in result
        assert "Share on Twitter" not in result

    @pytest.mark.asyncio
    async def test_returns_empty_for_no_body(self):
        """Test returns empty string when no body element exists."""
        html = "<html></html>"
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("backend.src.infrastructure.content_scraper.httpx.AsyncClient", return_value=mock_client):
            scraper = ContentScraper()
            result = await scraper.fetch_article_content("https://example.com/article")

        assert result == ""

    @pytest.mark.asyncio
    async def test_http_error_returns_message(self):
        """Test that HTTP errors return an error message."""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "404", request=MagicMock(), response=MagicMock(status_code=404)
            )
        )
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("backend.src.infrastructure.content_scraper.httpx.AsyncClient", return_value=mock_client):
            scraper = ContentScraper()
            result = await scraper.fetch_article_content("https://example.com/missing")

        assert "Impossibile recuperare" in result

    @pytest.mark.asyncio
    async def test_circuit_breaker_open_returns_message(self):
        """Test circuit breaker open state returns appropriate message."""
        _cb_scraping._state = CircuitState.OPEN
        _cb_scraping._last_failure_time = 9999999999.0  # Far future to prevent recovery
        scraper = ContentScraper()
        result = await scraper.fetch_article_content("https://example.com/article")

        assert "temporaneamente non disponibile" in result

    @pytest.mark.asyncio
    async def test_preserves_paragraph_structure(self):
        """Test that paragraph separation is maintained."""
        html = """
        <html>
        <body>
            <article>
                <p>First paragraph.</p>
                <p>Second paragraph.</p>
                <p>Third paragraph.</p>
            </article>
        </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("backend.src.infrastructure.content_scraper.httpx.AsyncClient", return_value=mock_client):
            scraper = ContentScraper()
            result = await scraper.fetch_article_content("https://example.com/article")

        # Content should preserve semantic HTML paragraph tags
        assert "<p>" in result
        assert "First paragraph." in result
        assert "Second paragraph." in result
        assert "Third paragraph." in result
