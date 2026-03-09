---
type: code-quality
priority: medium
status: resolved
discovered: 2026-03-07
related: []
related_decision: null
report: null
---

# Deprecated FastAPI and Pydantic APIs

## Problem

The codebase uses deprecated APIs that will be removed in future versions:

### 1. FastAPI `on_event` (main.py:39, 62)

```python
@app.on_event("startup")   # deprecated
@app.on_event("shutdown")  # deprecated
```

Should use the lifespan context manager pattern instead.

### 2. Pydantic class-based `Config` (schemas.py:31, 44)

```python
class SourceResponse(SourceBase):
    class Config:
        from_attributes = True
```

Should use `model_config = ConfigDict(from_attributes=True)` instead.

### 3. SQLAlchemy `declarative_base()` (database.py:11)

```python
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
```

Should use `from sqlalchemy.orm import DeclarativeBase` with class-based declaration.

## Recommended Approach

Fix all three in a single commit:
1. FastAPI: Convert to `@asynccontextmanager` lifespan
2. Pydantic: Use `ConfigDict`
3. SQLAlchemy: Use `DeclarativeBase` class pattern

All are straightforward, well-documented migrations with no logic changes.
