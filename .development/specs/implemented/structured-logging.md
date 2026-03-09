# Structured Logging

**Status**: implemented
**Milestone**: M1-MVP
**Priority**: should-have
**Depends on**: —

## Summary

Centralized logging infrastructure with consistent structured format across all backend services, providing observability for feed processing, AI operations, and API requests.

## User Stories

- As a developer, I want consistent log format across all modules for easy debugging
- As an operator, I want structured logs that can be parsed by log aggregation tools

## Requirements

### Functional

- [x] Centralized logger configuration in `shared/logging/`
- [x] Consistent format: `[timestamp] [level] [module] message`
- [x] Log levels: DEBUG, INFO, WARNING, ERROR
- [x] Module name included for traceability
- [x] Context fields for structured data
- [x] Output to stdout (container-friendly)

### Non-Functional

- Performance: Minimal overhead on request processing
- Compatibility: Output format parseable by Loki/ELK (future)

## Technical Notes

- Implementation: `shared/logging/logger.py`
- Format: `[2025-10-25 19:05:08] [INFO] [module.name] Message with context`
- Used across all services: feed parser, AI service, API endpoints, repositories
- Replaces previous ad-hoc `print()` statements

## Acceptance Criteria

- [x] All backend modules use centralized logger
- [x] Log format is consistent across all modules
- [x] Log level is configurable
- [x] No print() statements remain in production code
