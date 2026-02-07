# AI Summarization

**Status**: implemented
**Milestone**: M1-MVP
**Priority**: must-have
**Depends on**: feed-parsing.md

## Summary

Local AI-powered summarization service that generates concise Italian-language summaries of institutional news using Ollama, with web scraping for full-text content retrieval.

## User Stories

- As a user, I want each news item to have an AI-generated summary so I can quickly understand its content
- As a user, I want summaries in Italian so they are immediately readable
- As a user, I want summaries to focus on practical impact for citizens

## Requirements

### Functional

- [x] Integrate with Ollama API for local LLM inference
- [x] Web scrape original article URL for full-text content
- [x] Fall back to feed content when scraping fails
- [x] Clean and truncate content before sending to AI (2000 char limit)
- [x] Generate summaries in Italian language
- [x] Remove DeepSeek-R1 `<think>` reasoning blocks from output
- [x] Support configurable model, endpoint, and max words via settings
- [x] Support manual summarization trigger via `POST /api/news/{id}/summarize`

### Non-Functional

- Privacy: All processing happens locally via Ollama, no cloud AI services
- Performance: 2-10s per summary depending on model and hardware
- Reliability: Graceful degradation when Ollama is unavailable

## Technical Notes

- Implementation: `backend/src/infrastructure/ai_service.py`
- Uses `httpx` async client for Ollama API calls
- Ollama endpoint: `http://localhost:11434` (configurable)
- Default model: `deepseek-r1:7b`
- Temperature: 0.3 for deterministic output
- Content truncated to 2000 characters for model context limits
- Prompt engineering: Italian language, clear style, focus on citizen impact
- See [ADR-002](../../reference/decisions/002-privacy-first-ai.md) for privacy-first decision

## Acceptance Criteria

- [x] Summaries are generated in Italian
- [x] Full article content is fetched via web scraping when possible
- [x] Feed content is used as fallback when scraping fails
- [x] DeepSeek-R1 think blocks are cleaned from output
- [x] System degrades gracefully when Ollama is down (news saved without summary)
- [x] AI model and endpoint are configurable via settings
