"""Tests for ContentScraper service."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from backend.src.infrastructure.content_scraper import (
    ContentScraper,
    _cb_scraping,
    _clean_html,
    _is_continuation_fragment,
    _merge_citation_fragments,
)
from backend.src.infrastructure.resilience import CircuitState
from bs4 import BeautifulSoup


def make_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


class TestIsContinuationFragment:
    """Unit tests for the structural continuation detection heuristic."""

    def test_comma_start(self):
        assert _is_continuation_fragment(", Docket No. 21-09", "Main text") is True

    def test_semicolon_start(self):
        assert _is_continuation_fragment("; see also", "Main text") is True

    def test_paren_start(self):
        assert _is_continuation_fragment("(S.D. Tex. 2026)", "Main text") is True

    def test_lowercase_start(self):
        assert _is_continuation_fragment("see, e.g., Smith v. Jones", "Main text") is True

    def test_signoff_pattern(self):
        assert _is_continuation_fragment("-CFTC-", "Final statement.") is True

    def test_prev_ends_with_comma(self):
        assert _is_continuation_fragment("Civil Action No. 4:22", "CFTC v. Clark,") is True

    def test_prev_ends_with_semicolon(self):
        assert _is_continuation_fragment("In re Webb, et al.", "Section 4c(a)(1);") is True

    def test_prev_ends_with_colon(self):
        assert _is_continuation_fragment("Section 5(d) of the Act", "See:") is True

    def test_normal_paragraph_not_detected(self):
        assert _is_continuation_fragment("Second independent paragraph.", "First paragraph.") is False

    def test_too_long_not_detected(self):
        assert _is_continuation_fragment(", " + "x" * 200, "Previous.") is False

    def test_empty_text_not_detected(self):
        assert _is_continuation_fragment("", "Previous.") is False


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
        """A <p> starting with lowercase 'see' is merged (mid-sentence)."""
        soup = make_soup("<div><p>Prohibited under Section 4c(a)(1);</p><p>see, e.g., In re Khorrami.</p></div>")
        _merge_citation_fragments(soup.div)
        paragraphs = soup.find_all("p")
        assert len(paragraphs) == 1
        assert "In re Khorrami" in paragraphs[0].get_text()

    def test_merges_when_prev_ends_with_comma(self):
        """A <p> after a paragraph ending with comma is merged (continuation)."""
        soup = make_soup("<div><p>CFTC v. Clark,</p><p>Civil Action No. 4:22-cv-00365 (S.D. Tex. 2026).</p></div>")
        _merge_citation_fragments(soup.div)
        assert len(soup.find_all("p")) == 1

    def test_merges_when_prev_ends_with_semicolon(self):
        """A <p> after a paragraph ending with semicolon is merged."""
        soup = make_soup("<div><p>Regulation 180.1(a)(1) and (3);</p><p>In re Webb, et al., Docket No. 21-09.</p></div>")
        _merge_citation_fragments(soup.div)
        assert len(soup.find_all("p")) == 1

    def test_merges_chain_of_fragments(self):
        """Multiple consecutive fragments are all merged into the first <p>."""
        soup = make_soup(
            "<div>"
            "<p>Section 4c(a)(1);</p>"
            "<p>see, e.g., CFTC v. Clark,</p>"
            "<p>Civil Action No. 4:22-cv-00365.</p>"
            "</div>"
        )
        _merge_citation_fragments(soup.div)
        paragraphs = soup.find_all("p")
        assert len(paragraphs) == 1
        text = paragraphs[0].get_text()
        assert "Section 4c" in text
        assert "CFTC v. Clark" in text
        assert "Civil Action No." in text

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


class TestCleanHtmlNoiseRemoval:
    """Tests for noise element removal in _clean_html."""

    def test_removes_related_content(self):
        """Sections with 'related' in class name are removed."""
        soup = make_soup(
            "<article>"
            "<p>Article text.</p>"
            '<div class="related-articles"><p>Other article</p></div>'
            "</article>"
        )
        result = _clean_html(soup.article)
        assert "Article text." in result
        assert "Other article" not in result

    def test_removes_more_on_topic(self):
        """Sections with 'more-on' in class name are removed (e.g. ESMA)."""
        soup = make_soup(
            "<article>"
            "<p>Main content.</p>"
            '<div class="more-on-same-topic"><p>Related news</p></div>'
            "</article>"
        )
        result = _clean_html(soup.article)
        assert "Main content." in result
        assert "Related news" not in result

    def test_removes_teaser_blocks(self):
        """Teaser blocks (e.g. Drupal document teasers) are removed."""
        soup = make_soup(
            "<article>"
            "<p>Article body.</p>"
            '<div class="teaser--library-documents"><table><tr><td>Doc</td></tr></table></div>'
            "</article>"
        )
        result = _clean_html(soup.article)
        assert "Article body." in result
        assert "Doc" not in result

    def test_removes_aside_elements(self):
        """Aside elements within content are removed."""
        soup = make_soup(
            "<article>"
            "<p>Core content.</p>"
            "<aside><p>Sidebar info</p></aside>"
            "</article>"
        )
        result = _clean_html(soup.article)
        assert "Core content." in result
        assert "Sidebar info" not in result

    def test_removes_complementary_role(self):
        """Elements with role=complementary are removed."""
        soup = make_soup(
            "<article>"
            "<p>Main text.</p>"
            '<div role="complementary"><p>Extra info</p></div>'
            "</article>"
        )
        result = _clean_html(soup.article)
        assert "Main text." in result
        assert "Extra info" not in result


class TestTrailingBoilerplateRemoval:
    """Tests for heading-based boilerplate trimming."""

    def test_removes_further_information_section(self):
        """'Further information' heading and everything after it is removed."""
        soup = make_soup(
            "<article>"
            "<p>Article content.</p>"
            "<h4>Further information</h4>"
            "<p>press@esma.europa.eu</p>"
            "<h6>Author Name</h6>"
            "</article>"
        )
        result = _clean_html(soup.article)
        assert "Article content." in result
        assert "press@esma" not in result
        assert "Author Name" not in result

    def test_removes_related_documents_heading(self):
        """'Related Documents' heading and table after it are removed."""
        soup = make_soup(
            "<article>"
            "<p>Main text here.</p>"
            "<h5>Related Documents</h5>"
            "<table><tr><td>Document.pdf</td></tr></table>"
            "</article>"
        )
        result = _clean_html(soup.article)
        assert "Main text here." in result
        assert "Document.pdf" not in result

    def test_removes_more_on_same_topic_heading(self):
        """'More on the same topic' heading and links are removed."""
        soup = make_soup(
            "<article>"
            "<p>Core article.</p>"
            "<h4>More on the same topic</h4>"
            '<a href="/other">Other article</a>'
            "<p>Some other news snippet</p>"
            "</article>"
        )
        result = _clean_html(soup.article)
        assert "Core article." in result
        assert "Other article" not in result

    def test_removes_italian_ulteriori_informazioni(self):
        """Italian 'Ulteriori informazioni' heading is detected."""
        soup = make_soup(
            "<article>"
            "<p>Contenuto articolo.</p>"
            "<h4>Ulteriori informazioni</h4>"
            "<p>Ufficio stampa: press@example.it</p>"
            "</article>"
        )
        result = _clean_html(soup.article)
        assert "Contenuto articolo." in result
        assert "press@example" not in result

    def test_removes_italian_contatti(self):
        """Italian 'Contatti' heading is detected."""
        soup = make_soup(
            "<article>"
            "<p>Testo principale.</p>"
            "<h3>Contatti</h3>"
            "<p>Tel: 06 12345</p>"
            "</article>"
        )
        result = _clean_html(soup.article)
        assert "Testo principale." in result
        assert "06 12345" not in result

    def test_preserves_content_before_boilerplate(self):
        """All content before the boilerplate heading is preserved."""
        soup = make_soup(
            "<article>"
            "<h2>Introduction</h2>"
            "<p>First paragraph.</p>"
            "<h3>Next steps</h3>"
            "<p>Second paragraph.</p>"
            "<h4>Further information</h4>"
            "<p>Contact info</p>"
            "</article>"
        )
        result = _clean_html(soup.article)
        assert "Introduction" in result
        assert "First paragraph." in result
        assert "Next steps" in result
        assert "Second paragraph." in result
        assert "Contact info" not in result

    def test_no_boilerplate_heading_preserves_all(self):
        """Without boilerplate headings, all content is preserved."""
        soup = make_soup(
            "<article>"
            "<p>Full article text.</p>"
            "<h4>Conclusion</h4>"
            "<p>Final thoughts.</p>"
            "</article>"
        )
        result = _clean_html(soup.article)
        assert "Full article text." in result
        assert "Conclusion" in result
        assert "Final thoughts." in result


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
