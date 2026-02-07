"""Unit tests for OllamaService (AI service)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.src.infrastructure.ai_service import OllamaService


class TestExtractSummary:
    """Tests for _extract_summary method."""

    def test_removes_think_block(self):
        service = OllamaService("http://localhost:11434", "test-model")
        text = "<think>Some reasoning here</think>Actual summary text."
        result = service._extract_summary(text)
        assert result == "Actual summary text."

    def test_no_think_block(self):
        service = OllamaService("http://localhost:11434", "test-model")
        text = "Just a plain summary."
        result = service._extract_summary(text)
        assert result == "Just a plain summary."

    def test_empty_string(self):
        service = OllamaService("http://localhost:11434", "test-model")
        assert service._extract_summary("") == ""

    def test_think_block_with_content_before(self):
        service = OllamaService("http://localhost:11434", "test-model")
        text = "Before <think>reasoning</think> After"
        result = service._extract_summary(text)
        assert result == "Before  After"


class TestStripHtml:
    """Tests for _strip_html method."""

    def test_removes_tags(self):
        service = OllamaService("http://localhost:11434", "test-model")
        assert service._strip_html("<p>Hello</p>") == "Hello"

    def test_empty_input(self):
        service = OllamaService("http://localhost:11434", "test-model")
        assert service._strip_html("") == ""
        assert service._strip_html(None) == ""


class TestSummarize:
    """Tests for summarize method."""

    @pytest.mark.asyncio
    async def test_successful_summarize(self):
        service = OllamaService("http://localhost:11434", "test-model")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Riassunto del testo."}

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("backend.src.infrastructure.ai_service.httpx.AsyncClient", return_value=mock_client):
            result = await service.summarize("Some content to summarize")

        assert result == "Riassunto del testo."

    @pytest.mark.asyncio
    async def test_summarize_truncates_long_content(self):
        service = OllamaService("http://localhost:11434", "test-model")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Short summary."}

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        long_content = "x" * 3000

        with patch("backend.src.infrastructure.ai_service.httpx.AsyncClient", return_value=mock_client):
            result = await service.summarize(long_content)

        # Verify the content was truncated in the request
        call_args = mock_client.post.call_args
        prompt = call_args.kwargs["json"]["prompt"]
        # 2000 chars + "..." = truncated
        assert "..." in prompt

    @pytest.mark.asyncio
    async def test_summarize_error_status(self):
        service = OllamaService("http://localhost:11434", "test-model")

        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("backend.src.infrastructure.ai_service.httpx.AsyncClient", return_value=mock_client):
            result = await service.summarize("content")

        assert "Errore AI" in result

    @pytest.mark.asyncio
    async def test_summarize_exception(self):
        service = OllamaService("http://localhost:11434", "test-model")

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(side_effect=Exception("connection refused"))

        with patch("backend.src.infrastructure.ai_service.httpx.AsyncClient", return_value=mock_client):
            result = await service.summarize("content")

        assert "Errore nella chiamata AI" in result


class TestFetchArticleContent:
    """Tests for fetch_article_content method."""

    @pytest.mark.asyncio
    async def test_successful_fetch(self):
        service = OllamaService("http://localhost:11434", "test-model")

        html = "<html><body><article><p>Article text here.</p></article></body></html>"
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("backend.src.infrastructure.ai_service.httpx.AsyncClient", return_value=mock_client):
            result = await service.fetch_article_content("https://example.com/article")

        assert "Article text here" in result

    @pytest.mark.asyncio
    async def test_fetch_error(self):
        service = OllamaService("http://localhost:11434", "test-model")

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=Exception("timeout"))

        with patch("backend.src.infrastructure.ai_service.httpx.AsyncClient", return_value=mock_client):
            result = await service.fetch_article_content("https://example.com/fail")

        assert "Impossibile recuperare" in result
