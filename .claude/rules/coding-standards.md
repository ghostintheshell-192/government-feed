# Coding Standards

## Naming Conventions

- **Classes**: `PascalCase` (e.g., `NewsItem`, `FeedParser`)
- **Functions/Methods**: `snake_case` (e.g., `get_recent_news`, `update_content_hash`)
- **Variables/Parameters**: `snake_case` (e.g., `content_hash`, `feed_url`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DATABASE_URL`, `MAX_RETRY`)
- **Private attributes**: `_snake_case` (e.g., `_session`, `_logger`)
- **Type aliases**: `PascalCase`

## Code Style

- **Enforced via**: ruff (linting + formatting)
- **Line length**: 100 characters
- **Target**: Python 3.13
- **Rules**: E, F, I, N, W, UP (pyupgrade for modern syntax)
- **Manual check**: `ruff check backend/src`

## Type Hints

- **mypy strict mode** enforced
- Use Python 3.13 union syntax: `str | None` (not `Optional[str]`)
- All functions must have return type annotations
- All parameters must have type annotations

## File Organization

- **One module per concern**: Separate files for entities, models, services
- **Import order** (enforced by ruff isort):
  1. Standard library
  2. Third-party packages
  3. Local imports
- **File structure**:
  1. Imports
  2. Constants
  3. Type definitions
  4. Classes/Functions
  5. Module-level code

## Documentation

- **Docstrings**: Required for public APIs and complex functions
- **Language**: English only
- **Focus**: Explain "why", not "what"
- **Style**: Google-style docstrings

## Dependency Injection

- **FastAPI Depends**: Use for request-scoped dependencies (database sessions)
- **Constructor injection**: For services with dependencies
- **Abstract base classes**: Define interfaces in core layer
- **Example**:

  ```python
  class NewsRepository(INewsRepository):
      def __init__(self, session: Session):
          self._session = session
          self._logger = logging.getLogger(__name__)
  ```
