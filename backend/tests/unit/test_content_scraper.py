"""Tests for ContentScraper service."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from bs4 import BeautifulSoup
from backend.src.infrastructure.content_scraper import (
    ContentScraper,
    _cb_scraping,
    _merge_citation_fragments,
)
from backend.src.infrastructure.resilience import CircuitState


def make_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


class TestMergeCitationFragments:
    """Unit tests for _merge_citation_fragments DOM post-processing."""

    def test_merges_comma_continuation(self):
        """A <p> starting with comma is merged into the previous <p>."""
        soup = make_soup("<div><p>Main text;</p><p>, CFTC Docket No. 21-09 (2021).</p></div>")
        _merge_citation_fragments(soup.div)
        paragraphs = soup.find_all("p")
        assert len(paragraphs) == 1
        assert "CFTC Docket No." in paragraphs[0].get_text()

    def test_merges_see_citation(self):
        """A <p> starting with 'see,' is merged into the previous <p>."""
        soup = make_soup("<div><p>Prohibited under Section 4c(a)(1);</p><p>see, e.g., In re Khorrami.</p></div>")
        _merge_citation_fragments(soup.div)
        paragraphs = soup.find_all("p")
        assert len(paragraphs) == 1
        assert "In re Khorrami" in paragraphs[0].get_text()

    def test_merges_civil_action_no(self):
        """A <p> starting with 'Civil Action No.' is merged."""
        soup = make_soup("<div><p>CFTC v. Clark,</p><p>Civil Action No. 4:22-cv-00365 (S.D. Tex. 2026).</p></div>")
        _merge_citation_fragments(soup.div)
        assert len(soup.find_all("p")) == 1

    def test_merges_in_re(self):
        """A <p> starting with 'In re ' is merged into the previous <p>."""
        soup = make_soup("<div><p>See also</p><p>In re Webb, et al., Docket No. 21-09.</p></div>")
        _merge_citation_fragments(soup.div)
        assert len(soup.find_all("p")) == 1

    def test_does_not_merge_long_paragraph(self):
        """A fragment longer than the threshold is left as a separate paragraph."""
        long_text = ", " + "x" * 200
        soup = make_soup(f"<div><p>Previous text.</p><p>{long_text}</p></div>")
        _merge_citation_fragments(soup.div)
        assert len(soup.find_all("p")) == 2

    def test_does_not_merge_normal_paragraph(self):
        """A normal paragraph not matching continuation patterns is left alone."""
        soup = make_soup("<div><p>First paragraph.</p><p>Second independent paragraph.</p></div>")
        _merge_citation_fragments(soup.div)
        assert len(soup.find_all("p")) == 2

    def test_does_not_merge_across_parents(self):
        """Fragments in different parent blocks are not merged across them."""
        soup = make_soup(
            "<div>"
            "<div><p>Block A text.</p></div>"
            "<div><p>, continuation that looks like citation.</p></div>"
            "</div>"
        )
        _merge_citation_fragments(soup.div)
        assert len(soup.find_all("p")) == 2

    def test_preserves_inline_tags_when_merging(self):
        """Inline tags inside the fragment are preserved after merging."""
        soup = make_soup("<div><p>Regulation violated;</p><p>see, e.g., <em>In re Smith</em>.</p></div>")
        _merge_citation_fragments(soup.div)
        paragraphs = soup.find_all("p")
        assert len(paragraphs) == 1
        assert soup.find("em") is not None
        assert "In re Smith" in paragraphs[0].get_text()

    def test_merges_agency_signoff(self):
        """A <p> starting with '-AGENCY-' sign-off pattern is merged."""
        soup = make_soup("<div><p>Final statement of the document.</p><p>-CFTC-</p></div>")
        _merge_citation_fragments(soup.div)
        assert len(soup.find_all("p")) == 1


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
