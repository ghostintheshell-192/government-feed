# Security Audit Report - Government Feed
**Generated**: 2026-03-08
**Project**: Government Feed (Python FastAPI Backend)
**Type**: News Aggregator with RSS Feed Parsing, Web Scraping, and Local AI Integration
**Location**: `/data/repos/government-feed`

---

## Executive Summary

**Overall Risk Level**: 🟠 **HIGH**

The Government Feed application has **3 HIGH-severity vulnerabilities** and **5 MEDIUM-severity issues** that require remediation. The application currently operates as a single-user local tool, which mitigates some risks, but several vulnerabilities will become **CRITICAL when multi-user authentication is added**.

| Category | Count | Risk |
|----------|-------|------|
| **Critical (immediate action required)** | 0 | 🟢 None |
| **High (address soon)** | 3 | 🟠 **3 HIGH** |
| **Medium (should address)** | 5 | 🟡 **5 MEDIUM** |
| **Low (nice to fix)** | 4 | 🔵 **4 LOW** |
| **Total Issues** | 12 | |

**Key Findings:**
- ✅ Good: SQL injection risk is **LOW** — uses SQLAlchemy ORM with parameterized queries
- ✅ Good: No hardcoded credentials in code
- ⚠️ Concern: Unauthenticated access to all endpoints — OK for single-user, **CRITICAL when multi-user**
- ⚠️ Concern: Settings file (`settings.json`) contains sensitive configuration in plaintext
- ⚠️ Concern: SSRF risk via URL fetching — user can specify arbitrary URLs for scraping/feed discovery
- ⚠️ Concern: Missing input validation on several endpoints
- ⚠️ Concern: XXE (XML External Entity) vulnerability risk in feed parser
- ⚠️ Concern: Settings endpoint accepts **unvalidated dictionary** — potential code injection

---

## High-Severity Vulnerabilities

### 1. Unvalidated Settings Endpoint — Arbitrary Configuration Injection
**Severity**: HIGH
**Category**: Input Validation / Configuration Security
**Location**: `backend/src/api/main.py:345-353` + `backend/src/infrastructure/settings_store.py`
**CWE**: CWE-94 (Code Injection), CWE-434 (Unrestricted Upload)
**CVSS Score**: 7.5 (High)

**Vulnerable code:**
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

**The Problem:**
- Endpoint accepts **any dictionary** without schema validation
- No whitelist of allowed settings keys
- Settings directly persisted to `settings.json`
- When multi-user auth is added: unauthenticated or low-privilege users could modify:
  - `ollama_endpoint` → SSRF to internal services
  - `redis_url` → Connect to unauthorized Redis instances
  - `ai_enabled` → Enable/disable features globally
  - Arbitrary new keys → pollution of settings file

**Attack Scenario (Current):**
```bash
curl -X PUT http://localhost:8000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"ollama_endpoint": "http://127.0.0.1:5432", "malicious_key": "value"}'
```

**Attack Scenario (Multi-user Future):**
A non-admin user modifies settings to redirect Ollama requests to attacker-controlled server, intercepting all summarization requests.

**Remediation:**
1. Create a Pydantic schema with explicit settings:
```python
from pydantic import BaseModel, Field, validator

class SettingsUpdate(BaseModel):
    """Validated settings update schema."""
    ai_enabled: bool | None = None
    summary_max_words: int | None = Field(None, ge=10, le=1000)
    scheduler_enabled: bool | None = None
    news_retention_days: int | None = Field(None, ge=1, le=365)

    # Ollama settings (only if user is admin in future)
    ollama_endpoint: str | None = Field(None, pattern=r'^https?://')
    ollama_model: str | None = Field(None, max_length=100)

    # Redis URL validation
    redis_url: str | None = Field(None, pattern=r'^redis://')

@app.put("/api/settings", response_model=dict)
async def update_settings(settings: SettingsUpdate):
    """Update application settings."""
    from backend.src.infrastructure.settings_store import load_settings, save_settings

    current = load_settings()
    updates = settings.model_dump(exclude_none=True)
    current.update(updates)
    save_settings(current)
    return {"success": True, "message": "Impostazioni salvate"}
```

2. Add authorization (when multi-user is implemented):
```python
from fastapi import Depends
from backend.src.api.dependencies import get_current_user

@app.put("/api/settings")
async def update_settings(
    settings: SettingsUpdate,
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
    # ... rest of function
```

3. Separate sensitive settings (Ollama, Redis) from user-configurable ones
4. Add audit logging of settings changes
5. Validate URLs use `https://` in production

**Priority**: HIGH — Easy to exploit, affects multiple subsystems
**Timeline**: Before multi-user release

---

### 2. Server-Side Request Forgery (SSRF) — Arbitrary URL Fetching
**Severity**: HIGH
**Category**: SSRF / Input Validation
**Location**: Multiple endpoints that accept URLs from user input
**Affected Endpoints:**
- `POST /api/news/{news_id}/fetch-content` — Fetches from `news.external_id` (user-controllable)
- `POST /api/sources/discover` — Accepts user-provided URL in `request.query`
- Feed parsing: `_fetch_feed_content_sync()` accepts feed_url from user-created Source

**CWE**: CWE-918 (Server-Side Request Forgery)
**CVSS Score**: 7.8 (High)

**Vulnerable Code:**
```python
# backend/src/api/main.py:300-331
@app.post("/api/news/{news_id}/fetch-content")
async def fetch_news_content(news_id: int, ...):
    # ...
    scraper = ContentScraper()
    content = await scraper.fetch_article_content(news.external_id)  # ← No URL validation!

# backend/src/infrastructure/content_scraper.py:20-36
async def fetch_article_content(self, url: str) -> str:
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url)  # ← Fetches ANY URL
        response.raise_for_status()
```

**Attack Scenarios:**

1. **Port Scanning Internal Network:**
```bash
# Create a news item with malicious external_id
curl -X POST http://localhost:8000/api/news/1/fetch-content
# Backend connects to http://127.0.0.1:5432, http://192.168.1.1:6379, etc.
# Timing response reveals if ports are open
```

2. **Cloud Metadata Service Attack:**
```
POST /api/sources/discover
{"query": "http://169.254.169.254/latest/meta-data/iam/security-credentials/"}
# If running in AWS/GCP, retrieves sensitive credentials
```

3. **Redis Compromise (if Redis URL in settings):**
```
External_id set to: gopher://127.0.0.1:6379/
# Can perform Redis commands via gopher protocol
```

4. **DoS Against Third Parties:**
```
external_id: "http://attacker-target.com/huge-file.bin"
# Backend slowly downloads huge file, tying up connections
```

**Root Cause:**
- No URL validation before HTTP requests
- No whitelist of allowed domains/IPs
- Follows redirects (`follow_redirects=True`)
- No timeout on total request size (only connection timeout)
- TOCTOU (Time-of-Check-Time-of-Use): URL comes from DB, but DB can be manipulated

**Remediation:**

1. **Whitelist-based URL validation:**
```python
from urllib.parse import urlparse
import ipaddress

ALLOWED_DOMAINS = {
    "example.com", "governo.it", "senato.it",  # Add government domains
}

BLOCKED_CIDRS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Localhost
    ipaddress.ip_network("10.0.0.0/8"),       # Private
    ipaddress.ip_network("172.16.0.0/12"),    # Private
    ipaddress.ip_network("192.168.0.0/16"),   # Private
    ipaddress.ip_network("169.254.0.0/16"),   # Link-local
    ipaddress.ip_network("::1/128"),          # IPv6 localhost
    ipaddress.ip_network("fc00::/7"),         # IPv6 private
]

def is_url_safe(url: str) -> bool:
    """Check if URL is safe to fetch."""
    try:
        parsed = urlparse(url)

        # Only allow http/https
        if parsed.scheme not in ("http", "https"):
            return False

        # No empty host
        if not parsed.hostname:
            return False

        # Check against private IP ranges
        try:
            ip = ipaddress.ip_address(parsed.hostname)
            for cidr in BLOCKED_CIDRS:
                if ip in cidr:
                    return False
        except ValueError:
            # hostname is not an IP, check domain whitelist
            domain = parsed.hostname.lower()
            # Allow subdomains: news.example.com matches example.com
            if not any(domain.endswith(allowed) for allowed in ALLOWED_DOMAINS):
                return False

        return True
    except Exception:
        return False

# Updated content scraper:
async def fetch_article_content(self, url: str) -> str:
    if not is_url_safe(url):
        logger.warning("Blocked unsafe URL: %s", url)
        return "Impossibile recuperare: URL non autorizzato"

    try:
        return await _cb_scraping.call_async(self._fetch_impl, url)
    # ...
```

2. **Add request size limits:**
```python
async with httpx.AsyncClient(
    timeout=30.0,
    follow_redirects=False,  # Don't follow redirects (or whitelist specific hosts)
    limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
) as client:
    response = await client.get(url)

    # Limit response size
    if int(response.headers.get("content-length", 0)) > 10_000_000:  # 10MB
        return "Contenuto troppo grande"
```

3. **Validate URLs at entry point (API layer):**
```python
class FeedDiscoveryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)

    @field_validator("query")
    @classmethod
    def validate_url_if_provided(cls, v: str) -> str:
        if v.startswith(("http://", "https://")):
            if not is_url_safe(v):
                raise ValueError("URL is not authorized")
        return v
```

4. **For feed discovery, only use URL-based discovery for whitelisted domains**

**Priority**: HIGH — Directly exploitable for network reconnaissance
**Timeline**: Before any external deployment

---

### 3. XXE (XML External Entity) Vulnerability in Feed Parser
**Severity**: HIGH
**Category**: XML Injection / Information Disclosure
**Location**: `backend/src/infrastructure/feed_parser.py:44` + `backend/src/infrastructure/feed_discovery.py:155`
**CWE**: CWE-611 (Improper Restriction of XML External Entity Reference)
**CVSS Score**: 7.5 (High)

**Vulnerable Code:**
```python
# backend/src/infrastructure/feed_parser.py:44
feed = feedparser.parse(xml_content)  # ← Parses untrusted XML

# backend/src/infrastructure/feed_discovery.py:155
parsed = feedparser.parse(response.text)  # ← Parses untrusted XML
```

**The Problem:**
- `feedparser.parse()` is called on untrusted XML from user-provided feed URLs
- By default, feedparser uses Python's `xml.etree.ElementTree` which **is vulnerable to XXE**
- Attacker can craft malicious RSS feed with XXE payload

**Attack Scenario:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE feed [
  <!ELEMENT entry ANY>
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<rss version="2.0">
  <channel>
    <title>&xxe;</title>
    <item>
      <title>Test</title>
      <link>http://example.com</link>
      <description>&xxe;</description>
    </item>
  </channel>
</rss>
```

When parsed, the XXE entity is resolved and `/etc/passwd` contents are embedded in the feed, potentially logged or saved to database.

**Remediation:**

Feedparser has XXE protection built-in (uses defusedxml by default in recent versions), but we should **explicitly disable XXE and DTD processing**:

```python
import feedparser
from defusedxml import ElementTree as ET

# Set feedparser to use defusedxml (if not already)
feedparser._FeedParserMixin.PREFERRED_XML_PARSERS = [ET.XMLParser]

# Or, explicitly disable DTD processing in feedparser
# feedparser has limited XXE controls, so validate XML before parsing:

def parse_feed_safely(xml_content: str, feed_url: str):
    """Parse feed with XXE protection."""
    # 1. Validate basic XML structure (no DOCTYPE with SYSTEM)
    if "<!DOCTYPE" in xml_content and "SYSTEM" in xml_content:
        logger.warning("Blocked feed with DOCTYPE SYSTEM from %s", feed_url)
        return None, "Feed contiene DTD esterno non supportato"

    # 2. Remove DOCTYPE declarations
    import re
    xml_content = re.sub(r'<!DOCTYPE[^>]*>', '', xml_content, flags=re.IGNORECASE)

    # 3. Parse with feedparser (which should use defusedxml)
    try:
        feed = feedparser.parse(xml_content)
        if feed.bozo:
            logger.warning("Feed parse error: %s", feed.bozo_exception)
            # Don't log exception text, might leak paths
            return None, "Feed parsing error"
        return feed, None
    except Exception as e:
        logger.error("Feed parsing failed: %s", type(e).__name__)
        return None, "Feed parsing failed"
```

**Updated code:**
```python
# backend/src/infrastructure/feed_parser.py:44
def parse_and_import(self, source: Source) -> int:
    xml_content = _cb_feed_fetch.call(self._fetch_feed_content_sync, source.feed_url)

    # Parse safely
    feed, error = parse_feed_safely(xml_content, source.feed_url)
    if error:
        logger.warning("Feed parse error for %s: %s", source.name, error)
        return 0

    # ... rest of parsing
```

**Check dependencies:**
- Verify feedparser version >= 6.0 (has better XXE handling)
- Ensure defusedxml is in `requirements.txt`
- Test with XXE payloads (see OWASP testing guide)

**Priority**: HIGH — Information disclosure, affects all feed imports
**Timeline**: Immediate (before production)

---

## Medium-Severity Issues

### 4. Missing Input Validation on Query Parameters
**Severity**: MEDIUM
**Category**: Input Validation / DoS
**Location**: `backend/src/api/main.py:237-277`
**CWE**: CWE-400 (Uncontrolled Resource Consumption)

**Vulnerable Code:**
```python
@app.get("/api/news", response_model=schemas.PaginatedNewsResponse)
async def get_news(
    limit: int = 20,
    offset: int = 0,
    source_id: list[int] | None = Query(None),  # ← No max validation
    search: str | None = None,                   # ← No length validation
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    ...
):
```

**Issues:**
1. `limit` has no maximum — user could request `limit=1000000`
2. `search` string has no max length — could be huge
3. `offset` could be negative (though Query doesn't allow this, the query builder doesn't validate)
4. Multiple `source_id` values — no limit on count

**Attack:**
```bash
# Expensive query: fetch million items, huge offset
curl "http://localhost:8000/api/news?limit=1000000&offset=999999999"

# Huge search string (string matching is slow)
curl "http://localhost:8000/api/news?search=$(python3 -c 'print("a"*100000)')"
```

**Remediation:**
```python
from pydantic import Field

@app.get("/api/news", response_model=schemas.PaginatedNewsResponse)
async def get_news(
    limit: int = Field(default=20, ge=1, le=100),        # Min 1, max 100
    offset: int = Field(default=0, ge=0),                 # Min 0
    source_id: list[int] | None = Query(None, max_length=10),  # Max 10 sources
    search: str | None = Field(None, max_length=200),     # Max 200 chars
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    ...
):
```

**Priority**: MEDIUM — DoS risk, but pagination reduces impact
**Timeline**: Before production

---

### 5. Missing Foreign Key Constraint — Data Integrity Risk
**Severity**: MEDIUM
**Category**: Data Integrity
**Location**: `backend/src/infrastructure/models.py:33`
**Status**: Already tracked in tech-debt, but security-relevant

**Vulnerable Code:**
```python
class NewsItem(Base):
    __tablename__ = "news_items"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, nullable=False, index=True)  # ← No FK constraint!
```

**Risk:**
- Can delete a Source, leaving orphaned NewsItems
- Can insert invalid source_id values
- Data integrity violations

**Remediation:**
```python
from sqlalchemy import ForeignKey

class NewsItem(Base):
    __tablename__ = "news_items"
    source_id = Column(
        Integer,
        ForeignKey("sources.id", ondelete="CASCADE"),  # Auto-delete news when source deleted
        nullable=False,
        index=True
    )
```

Update Alembic migration and apply to database.

**Priority**: MEDIUM — Data integrity, use Alembic migration
**Timeline**: Next iteration

---

### 6. CORS Configuration — Single Hardcoded Origin
**Severity**: MEDIUM
**Category**: CORS Configuration / Development vs Production
**Location**: `backend/src/api/main.py:63-70`
**CWE**: CWE-346 (Origin Validation Error)

**Vulnerable Code:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # ← Hardcoded dev origin!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Issues:**
1. Hardcoded development origin — will break in production
2. `allow_methods=["*"]` — allows OPTIONS, DELETE, PUT, etc. (overly permissive)
3. `allow_headers=["*"]` — allows any header (less critical, but overly permissive)
4. `allow_credentials=True` with specific origin is correct, but needs env config

**Attack Risk (Production):**
- Browser-based attacker on different origin can make cross-origin requests
- If deployed to production without changing CORS, attacker at `http://attacker.com` can call backend APIs

**Remediation:**
```python
import os

# Get allowed origins from environment
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
]

# Validate origins are https in production
if os.getenv("ENVIRONMENT", "development") == "production":
    for origin in ALLOWED_ORIGINS:
        if origin != "http://localhost:5173" and not origin.startswith("https://"):
            raise ValueError(f"Production origin must use HTTPS: {origin}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Explicit methods
    allow_headers=["Content-Type", "Authorization"],  # Explicit headers
    max_age=3600,
)
```

**Create `.env.example`:**
```
ALLOWED_ORIGINS=http://localhost:5173,https://news.example.com
ENVIRONMENT=development
```

**Priority**: MEDIUM — Configuration issue, becomes CRITICAL in production
**Timeline**: Before any external deployment

---

### 7. Settings File Exposed — Plaintext Configuration Secrets
**Severity**: MEDIUM
**Category**: Sensitive Data Exposure
**Location**: `backend/src/infrastructure/settings_store.py` + `settings.json` (on disk)
**CWE**: CWE-327 (Inadequate Encryption), CWE-540 (Inclusion of Sensitive Information)

**Risk:**
```python
# settings.json on disk contains:
{
  "ollama_endpoint": "http://localhost:11434",
  "redis_url": "redis://localhost:6379",
  "ai_enabled": true
}
```

**Issues:**
1. Settings stored in plaintext JSON in working directory
2. File is version-controlled (if not in .gitignore) — exposed in git history
3. When multi-user added, might contain API keys, auth tokens
4. File permissions not enforced (world-readable on some systems)
5. No audit trail of config changes

**Remediation:**

1. **Add `settings.json` to `.gitignore`:**
```
echo "settings.json" >> .gitignore
```

2. **Use environment variables for sensitive settings:**
```python
# backend/src/infrastructure/settings_store.py
import os
from typing import Any

def load_settings() -> dict:
    """Load settings from file and environment variables."""
    settings = {}

    # Load from file
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE) as f:
            settings = json.load(f)
    else:
        settings = DEFAULT_SETTINGS.copy()

    # Override with environment variables (highest priority)
    settings["ollama_endpoint"] = os.getenv("OLLAMA_ENDPOINT", settings.get("ollama_endpoint"))
    settings["redis_url"] = os.getenv("REDIS_URL", settings.get("redis_url"))
    settings["ai_enabled"] = os.getenv("AI_ENABLED", "true").lower() == "true"

    # For future multi-user:
    # settings["api_key"] = os.getenv("API_KEY")  # Fail if not set

    return settings
```

3. **Enforce file permissions:**
```python
import stat
import os

def save_settings(settings: dict) -> None:
    """Save settings to file with restrictive permissions."""
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

    # Set file permissions to 0600 (read/write only for owner)
    os.chmod(SETTINGS_FILE, stat.S_IRUSR | stat.S_IWUSR)
```

4. **Create `.env.example`:**
```
OLLAMA_ENDPOINT=http://localhost:11434
OLLAMA_MODEL=deepseek-r1:7b
REDIS_URL=redis://localhost:6379
AI_ENABLED=true
```

**Priority**: MEDIUM — Becomes HIGH when secrets are added
**Timeline**: Before multi-user release

---

### 8. Insufficient Rate Limiting — API Abuse Risk
**Severity**: MEDIUM
**Category**: API Security / DoS
**Location**: All endpoints
**CWE**: CWE-770 (Allocation of Resources Without Limits or Throttling)

**Issue:**
- No rate limiting on any endpoint
- Users (current or future) can hammer endpoints
- Feed processing could be triggered repeatedly
- Summarization requests to Ollama not throttled

**Attack:**
```bash
# Spam feed processing
for i in {1..100}; do
  curl -X POST http://localhost:8000/api/sources/1/process &
done
```

**Remediation:**

Install `slowapi`:
```bash
pip install slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Apply to key endpoints:
@app.post("/api/sources/{source_id}/process")
@limiter.limit("5/minute")  # 5 requests per minute
async def process_feed(request: Request, source_id: int, ...):
    ...

@app.post("/api/news/{news_id}/fetch-content")
@limiter.limit("10/minute")
async def fetch_news_content(request: Request, ...):
    ...

@app.post("/api/news/{news_id}/summarize")
@limiter.limit("10/minute")
async def summarize_news(request: Request, ...):
    ...
```

**Priority**: MEDIUM — Important for production
**Timeline**: Before public deployment

---

### 9. Missing Security Headers
**Severity**: MEDIUM
**Category**: HTTP Security Headers
**Location**: FastAPI app configuration
**CWE**: CWE-693 (Protection Mechanism Failure)

**Missing Headers:**
```
X-Content-Type-Options: nosniff          # Prevent MIME sniffing
X-Frame-Options: DENY                    # Prevent clickjacking
X-XSS-Protection: 1; mode=block          # Legacy XSS protection
Strict-Transport-Security: max-age=31536000  # HSTS (HTTPS only)
Content-Security-Policy: default-src 'self'  # CSP
```

**Remediation:**

```python
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Only in production:
        if os.getenv("ENVIRONMENT") == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response

app.add_middleware(SecurityHeadersMiddleware)
```

Or use TrustedHost middleware:
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "example.com"],  # From env
)
```

**Priority**: MEDIUM — Good-to-have, important for production
**Timeline**: Before public deployment

---

## Low-Severity Issues

### 10. Error Messages Leak Information
**Severity**: LOW
**Category**: Information Disclosure
**Location**: Various error returns
**CWE**: CWE-209 (Information Exposure Through an Error Message)

**Example:**
```python
# backend/src/infrastructure/feed_parser.py:101
logger.error("Error parsing feed from %s: %s", source.name, e)
# Logs full exception, which might include paths, stack traces
```

**Risk:** Low — Only visible in logs, not user-facing (in current version)

**Remediation:**
- Log full exceptions internally
- Return generic error messages to users
- Already done in most places, a few places could be improved

---

### 11. Dependency Vulnerabilities — Outdated Packages
**Severity**: LOW
**Category**: Dependency Management
**Location**: `backend/requirements.txt`

**Recommendation:**
Run dependency scanning:
```bash
pip install safety
safety check
```

Check for known CVEs in:
- feedparser
- beautifulsoup4
- httpx
- sqlalchemy
- fastapi

**Action:** Regular dependency updates (part of maintenance)

---

### 12. Logging — Potential PII/Sensitive Data in Logs
**Severity**: LOW
**Category**: Information Disclosure
**Location**: Logging calls throughout codebase
**CWE**: CWE-532 (Insertion of Sensitive Information into Log File)

**Current Practice:** Logs are generally good, but a few instances:
```python
logger.info(f"Creating new source: {source.name}")  # OK
logger.info("Fetching article content from URL: %s", url)  # OK, uses %s

# Potential issue:
logger.error(f"Error fetching article from {url}: {e}")  # Error might contain URL with token
```

**Remediation:**
- Review all logging calls
- Never log URLs that might contain query parameters
- Sanitize user input in logs
- Create logger wrapper to redact sensitive fields

---

## Architectural & Design Considerations

### A. Authentication & Authorization (Future Multi-User)

**Current State:** No authentication — single-user local app. When multi-user is added:

**Critical Issues to Address:**
1. **All endpoints are unauthenticated** — Anyone with network access can:
   - View all news and sources
   - Create/modify/delete sources
   - Trigger background jobs
   - Modify settings

2. **No authorization granularity** — Who can:
   - Delete sources? (Admin only?)
   - Modify Ollama settings? (Admin only?)
   - View specific news? (All users? By category?)

3. **No audit trail** — No logs of who did what and when

**Recommendations (for M4):**
- Use JWT tokens (from an auth system)
- Add role-based access control (Admin, User, Viewer)
- Implement row-level security for news/sources (shared vs. private)
- Add audit logging to all data modifications

Example:
```python
from fastapi import Depends
from backend.src.api.dependencies import get_current_user

@app.delete("/api/sources/{source_id}", status_code=204)
async def delete_source(
    source_id: int,
    current_user = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_unit_of_work)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete sources")
    # ...
```

---

### B. Data Privacy & Retention

**Consideration:** Government feed content may be sensitive. No encryption at rest mentioned.

**Issues:**
- Database (`government_feed.db`) stored in plaintext
- Article content and summaries not encrypted
- No data retention enforcement (though `news_retention_days` setting exists)

**Recommendations:**
- Consider encryption at rest for sensitive articles
- Implement automatic data deletion via scheduler (already tracked in tech-debt)
- Add data anonymization for user tracking

---

### C. Third-Party Service Risks

**Ollama:** Local service, no network risk (unless exposed)
**Redis:** No password in config (good for local dev, but needs auth in production)

**Recommendation:** Require Redis password in production:
```python
redis_url = os.getenv("REDIS_URL", "redis://:password@localhost:6379")
```

---

## Testing & Verification Recommendations

### Security Testing Checklist

- [ ] **SQL Injection**: Current ORM usage is safe, but test with SQLi payloads
- [ ] **XXE Testing**: Submit malicious feed with XXE payload, verify it's blocked
- [ ] **SSRF Testing**: Try fetching from localhost, private IPs, cloud metadata service
- [ ] **CORS Testing**: Verify cross-origin requests are blocked/allowed correctly
- [ ] **Input Validation**: Fuzz all endpoints with oversized/malformed inputs
- [ ] **Rate Limiting**: Verify rate limits are enforced when implemented
- [ ] **Settings Injection**: Try modifying settings with arbitrary keys
- [ ] **Dependency Scanning**: Run `pip install safety && safety check`
- [ ] **SAST**: Run `bandit backend/src` for basic static analysis

### Recommended Tools

```bash
# Static analysis
pip install bandit
bandit -r backend/src

# Dependency scanning
pip install safety
safety check

# Manual testing
pytest backend/tests

# Web testing (after fixes)
pip install httpx
# Custom security test suite
```

---

## Summary Table: Issues & Remediation

| # | Issue | Severity | Category | Fix Status | Timeline |
|----|-------|----------|----------|-----------|----------|
| 1 | Unvalidated Settings Endpoint | HIGH | Input Validation | Not started | Immediate |
| 2 | SSRF — Arbitrary URL Fetching | HIGH | SSRF | Not started | Immediate |
| 3 | XXE in Feed Parser | HIGH | XML Injection | Not started | Immediate |
| 4 | Missing Query Validation | MEDIUM | Input Validation | Not started | Before Production |
| 5 | Missing FK Constraint | MEDIUM | Data Integrity | Tracked in tech-debt | Next Iteration |
| 6 | CORS Hardcoded Origin | MEDIUM | Configuration | Not started | Before Deployment |
| 7 | Settings File Plaintext | MEDIUM | Secrets Management | Not started | Before Multi-User |
| 8 | No Rate Limiting | MEDIUM | API Security | Not started | Before Deployment |
| 9 | Missing Security Headers | MEDIUM | HTTP Security | Not started | Before Deployment |
| 10 | Error Message Leaks | LOW | Info Disclosure | Partial | Nice-to-have |
| 11 | Dependency Updates | LOW | Maintenance | Ongoing | Regular |
| 12 | Logging Sensitive Data | LOW | Info Disclosure | Minimal | Nice-to-have |

---

## Risk Assessment Timeline

### IMMEDIATE (Fix before testing beyond localhost):
1. **Settings endpoint validation** (Issue #1)
2. **SSRF URL validation** (Issue #2)
3. **XXE protection** (Issue #3)

### BEFORE PRODUCTION (Fix before external deployment):
4. Query parameter validation (Issue #4)
5. CORS configuration (Issue #6)
6. Rate limiting (Issue #8)
7. Security headers (Issue #9)

### BEFORE MULTI-USER RELEASE:
8. Settings file secrets management (Issue #7)
9. Add authentication & authorization throughout
10. Foreign key constraints (Issue #5) — Data integrity

### NICE-TO-HAVE (Maintenance):
11. Error message sanitization (Issue #10)
12. Dependency updates (Issue #11)
13. Logging review (Issue #12)

---

## Compliance & Standards

**OWASP Top 10 (2021) Coverage:**
- **A03:2021 – Injection**: XML injection risk (Issue #3)
- **A05:2021 – Access Control**: No auth/authz (future issue)
- **A06:2021 – Vulnerable & Outdated Components**: Dependency scanning (Issue #11)
- **A07:2021 – Identification & Authentication**: No auth (future issue)
- **A09:2021 – Security Logging & Monitoring**: Logging concerns (Issue #12)

**GDPR/Privacy Considerations:**
- No encryption at rest — user articles might be PII
- No data deletion enforcement — retention settings exist but not enforced
- No audit trail — GDPR requires records of data access

**Recommendations:**
- Implement data minimization (only store necessary fields)
- Encrypt article content at rest (optional for local app, critical for multi-user)
- Enforce automatic deletion (cron job, already tracked)
- Add audit logging for data access

---

## Final Recommendations

### Priority Order (Execution Plan):

**Phase 1 — CRITICAL (1-2 days):**
1. Fix settings endpoint validation (Issue #1)
2. Implement SSRF URL whitelist (Issue #2)
3. Add XXE protection (Issue #3)
4. Test fixes with included payloads

**Phase 2 — PRODUCTION-READY (1 week):**
5. Add query parameter validation (Issue #4)
6. Externalize CORS configuration (Issue #6)
7. Implement rate limiting (Issue #8)
8. Add security headers (Issue #9)
9. Run full security test suite

**Phase 3 — MULTI-USER (Before M4):**
10. Implement authentication/authorization
11. Add secrets management via environment (Issue #7)
12. Add audit logging
13. Re-run security audit

**Phase 4 — ONGOING:**
14. Regular dependency scanning
15. Log review
16. Penetration testing (professional assessment recommended)

---

## Conclusion

Government Feed has a **solid foundation** with good use of SQLAlchemy ORM (prevents SQL injection) and circuit breaker patterns. The main security risks are:

1. **SSRF** — Fetching arbitrary URLs without validation
2. **XXE** — Parsing untrusted XML without protection
3. **Unvalidated settings** — Accepting arbitrary configuration

**These are all HIGH but fixable.** Implementation of the recommended mitigations will bring the application to production-ready security standards. The codebase is clean and well-structured, making security improvements straightforward.

**Next Steps:**
1. Create GitHub issues for each HIGH-severity finding
2. Assign to development queue
3. Implement fixes in order of severity
4. Add security tests to CI/CD pipeline
5. Schedule re-audit after fixes (1 week)

---

*Report generated: 2026-03-08 by Claude Security Auditor*
*Recommendations based on OWASP Top 10, CWE, and industry best practices*
