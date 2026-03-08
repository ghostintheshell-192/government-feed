# Security Issue: Unvalidated Settings Endpoint — Arbitrary Configuration Injection

**Type**: Bug (Security)
**Priority**: High
**Status**: Resolved
**Severity**: HIGH (CVSS 7.5)
**Report**: `archive/analysis/2026-03-08_report_security-auditor.md`

---

## Issue Description

The `/api/settings` endpoint accepts **any dictionary** without schema validation or authorization. This allows:
- Injection of arbitrary keys into settings file
- Modification of sensitive configuration (Ollama endpoint, Redis URL)
- When multi-user auth is added: privilege escalation risk

## Affected Code

- **File**: `backend/src/api/main.py:345-353`
- **Function**: `update_settings()`
- **Related**: `backend/src/infrastructure/settings_store.py`

## Current Implementation

```python
@app.put("/api/settings")
async def update_settings(settings: dict):
    """Update application settings."""
    from backend.src.infrastructure.settings_store import save_settings

    logger.info("Updating application settings")
    save_settings(settings)  # ← Accepts ANY dict, no validation!
    logger.info("Settings updated successfully")
    return {"success": True, "message": "Impostazioni salvate"}
```

## Attack Vector

```bash
curl -X PUT http://localhost:8000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"ollama_endpoint": "http://attacker.com:9999", "malicious_key": "value"}'
```

Result: `settings.json` is corrupted with arbitrary keys and attacker-controlled Ollama endpoint.

## Remediation Steps

1. **Create Pydantic schema** for allowed settings:
```python
from pydantic import BaseModel, Field

class SettingsUpdate(BaseModel):
    """Validated settings update schema."""
    ai_enabled: bool | None = None
    summary_max_words: int | None = Field(None, ge=10, le=1000)
    scheduler_enabled: bool | None = None
    news_retention_days: int | None = Field(None, ge=1, le=365)
    ollama_endpoint: str | None = Field(None, pattern=r'^https?://')
    ollama_model: str | None = Field(None, max_length=100)
    redis_url: str | None = Field(None, pattern=r'^redis://')
```

2. **Add validation to endpoint**:
```python
@app.put("/api/settings", response_model=dict)
async def update_settings(settings: SettingsUpdate):
    from backend.src.infrastructure.settings_store import load_settings, save_settings

    current = load_settings()
    updates = settings.model_dump(exclude_none=True)
    current.update(updates)
    save_settings(current)
    return {"success": True}
```

3. **Add authorization** (when multi-user is implemented):
```python
@app.put("/api/settings")
async def update_settings(
    settings: SettingsUpdate,
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
    # ... rest
```

4. **Add audit logging**:
```python
logger.info(f"User {current_user.id} modified settings: {updates.keys()}")
```

## Testing

- [ ] Verify valid settings are accepted
- [ ] Verify invalid settings are rejected (400 response)
- [ ] Verify arbitrary keys are rejected
- [ ] Verify settings file is not corrupted

Example test:
```python
def test_settings_validation():
    response = client.put("/api/settings", json={"invalid_key": "value"})
    assert response.status_code == 422  # Validation error
```

## Related Issues

- None (first security finding in this area)

## Timeline

- **Severity**: HIGH
- **Deadline**: Implement before multi-user release
- **Estimated Effort**: 2 hours
- **Blocks**: M4 (Multi-user) milestone

## CWE References

- CWE-94: Improper Control of Generation of Code
- CWE-434: Unrestricted Upload of File with Dangerous Type
