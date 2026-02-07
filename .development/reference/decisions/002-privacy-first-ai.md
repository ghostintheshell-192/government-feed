# ADR-002: Privacy-First AI Processing

**Date**: 2025-10-25
**Status**: Active
**Impact**: critical

## Context

The application needs AI capabilities for summarizing government news articles. Government data may be sensitive, and users should not be required to send content to external cloud services.

## Decision

All AI processing happens locally via Ollama. The application connects to a local Ollama instance (default: `http://localhost:11434`) running DeepSeek-R1:7b model. No data is ever sent to external AI services.

## Rationale

- Government publications may contain sensitive information
- GDPR compliance is simpler with local processing
- Users maintain full control over their data
- Ollama is free, open-source, and supports many models
- DeepSeek-R1:7b provides good quality summaries at reasonable hardware requirements

## Consequences

- **Positive**: Full data privacy, no API costs, no rate limits, works offline
- **Negative**: Requires local hardware capable of running LLMs, quality depends on model choice
- **Trade-off**: Summarization speed depends on user's hardware (GPU recommended)
