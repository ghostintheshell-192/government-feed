# Project Overview

## Government Feed

**Government Feed** is a specialized news aggregator that centralizes, filters, and contextualizes information from official government and institutional sources. Privacy-first, with local AI processing.

- **Type**: Personal tool (potential open-source release)
- **Platform**: Web application (Python backend + React frontend)
- **Status**: MVP Backend complete, frontend basic

## Development Methodology

- **Functional minimalism**: Minimum complexity for current requirements
- **Incrementality**: One component at a time, test before proceeding
- **Privacy-first**: All AI processing happens locally via Ollama
- **Effective simplicity**: Simplest solution that works

## Architecture

- **Clean Architecture**: Core (domain) <- Infrastructure -> API
- **Repository Pattern + Unit of Work**: Data access abstraction
- **Dependency Injection**: Constructor injection via FastAPI dependencies
- **Async-first**: Non-blocking I/O with FastAPI and httpx

## Technology Stack

- **Python 3.13** with full type hints
- **FastAPI** - Async web framework with OpenAPI
- **SQLAlchemy 2.0** - ORM with declarative models
- **React 18 + TypeScript** - Frontend SPA
- **Ollama** - Local AI for summarization (DeepSeek-R1)
- **Pydantic** - Data validation and schemas
- **Testing**: pytest + pytest-asyncio + pytest-cov
- **Quality**: ruff (linting) + mypy (strict type checking)
