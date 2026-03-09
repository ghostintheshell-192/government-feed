# Security Issue: Server-Side Request Forgery (SSRF) — Arbitrary URL Fetching

**Type**: Bug (Security)
**Priority**: High
**Status**: Open
**Severity**: HIGH (CVSS 7.8)
**Report**: `archive/analysis/2026-03-08_report_security-auditor.md`

---

## Issue Description

Multiple endpoints accept URLs from user input and fetch them without validation:
- `/api/news/{news_id}/fetch-content` — fetches from `news.external_id`
- `/api/sources/discover` — fetches from user-provided URL
- Feed parsing fetches feed URLs from user-created sources

**Attack scenarios:**
- Port scanning internal network (localhost:5432, 192.168.x.x:6379)
- Accessing cloud metadata services (AWS IMDSv2)
- Exfiltrating data via HTTP interactions
- DoS against third-party services

## Affected Code

1. **`backend/src/api/main.py:300-331`** — `fetch_news_content()`
2. **`backend/src/api/main.py:179-201`** — `discover_feeds()`
3. **`backend/src/infrastructure/content_scraper.py:20-36`** — `fetch_article_content()`
4. **`backend/src/infrastructure/feed_parser.py:105-111`** — `_fetch_feed_content_sync()`
5. **`backend/src/infrastructure/ai_service.py:27-44`** — `fetch_article_content()`
6. **`backend/src/infrastructure/feed_discovery.py:134-142`** — `_fetch_html()`

## Current Implementation

```python
async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
    response = await client.get(url)  # ← No URL validation!
    response.raise_for_status()
```

## Attack Vectors

### 1. Port Scanning Internal Network
```bash
# Attacker creates a source with feed_url = "http://127.0.0.1:5432"
# Backend connects to internal PostgreSQL, timing reveals if port is open
POST /api/sources
{
  "name": "Test",
  "feed_url": "http://127.0.0.1:5432",
  "source_type": "RSS"
}
POST /api/sources/1/process  # Tries to fetch, timing reveals open port
```

### 2. Cloud Metadata Service
```bash
# AWS EC2 metadata service
POST /api/sources/discover
{"query": "http://169.254.169.254/latest/meta-data/iam/security-credentials/"}

# Backend makes request, could leak IAM credentials
```

### 3. Gopher Protocol Attack (Redis)
```bash
# If httpx supports gopher:
external_id: "gopher://127.0.0.1:6379/_FLUSHDB"
# Can execute Redis commands
```

### 4. Response Size DoS
```bash
# Create news item with external_id = "http://attacker-target.com/huge-file.bin"
# Backend slowly downloads huge file, tying up resources
```

## Remediation Steps

### 1. Create URL Validation Helper

```python
# backend/src/infrastructure/url_validation.py
from urllib.parse import urlparse
import ipaddress
from shared.logging import get_logger

logger = get_logger(__name__)

# Define allowed domains (configurable from environment)
ALLOWED_DOMAINS = {
    "governo.it",
    "senato.it",
    "camera.it",
    "example.com",
    # Add government/news sources as needed
}

# Block private IP ranges
BLOCKED_CIDRS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Localhost
    ipaddress.ip_network("10.0.0.0/8"),       # Private Class A
    ipaddress.ip_network("172.16.0.0/12"),    # Private Class B
    ipaddress.ip_network("192.168.0.0/16"),   # Private Class C
    ipaddress.ip_network("169.254.0.0/16"),   # Link-local
    ipaddress.ip_network("224.0.0.0/4"),      # Multicast
    ipaddress.ip_network("::1/128"),          # IPv6 localhost
    ipaddress.ip_network("fc00::/7"),         # IPv6 private
    ipaddress.ip_network("fe80::/10"),        # IPv6 link-local
]

def is_url_safe(url: str, allow_private: bool = False) -> bool:
    """
    Validate that URL is safe to fetch.

    Args:
        url: URL to validate
        allow_private: If True, allow private IP ranges (for dev/testing)

    Returns:
        True if URL is safe, False otherwise
    """
    try:
        parsed = urlparse(url)

        # Only allow http/https (block gopher, file, etc.)
        if parsed.scheme not in ("http", "https"):
            logger.warning("Blocked URL with scheme: %s", parsed.scheme)
            return False

        # Must have a hostname
        if not parsed.hostname:
            logger.warning("Blocked URL with no hostname: %s", url)
            return False

        hostname = parsed.hostname.lower()

        # Check against private IP ranges (if not explicitly allowed)
        if not allow_private:
            try:
                ip = ipaddress.ip_address(hostname)
                for cidr in BLOCKED_CIDRS:
                    if ip in cidr:
                        logger.warning("Blocked private IP address: %s", ip)
                        return False
            except ValueError:
                # hostname is not an IP address, check domain whitelist
                domain_allowed = any(
                    hostname.endswith(allowed) or hostname == allowed
                    for allowed in ALLOWED_DOMAINS
                )
                if not domain_allowed:
                    logger.warning("Blocked domain not in whitelist: %s", hostname)
                    return False

        return True

    except Exception as e:
        logger.error("URL validation error: %s", e)
        return False

def validate_or_raise(url: str) -> None:
    """Validate URL or raise HTTPException."""
    if not is_url_safe(url):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail="URL is not authorized"
        )
```

### 2. Update Content Scraper

```python
# backend/src/infrastructure/content_scraper.py
from backend.src.infrastructure.url_validation import is_url_safe

async def fetch_article_content(self, url: str) -> str:
    """Fetch and extract text content from article URL."""
    if not is_url_safe(url):
        logger.warning("Blocked unsafe URL: %s", url)
        return "Impossibile recuperare: URL non autorizzato"

    try:
        return await _cb_scraping.call_async(self._fetch_impl, url)
    except CircuitBreakerOpenError:
        logger.warning("Content scraping circuit breaker is open")
        return "Servizio di scraping temporaneamente non disponibile"
    except Exception as e:
        logger.error("Error fetching article: %s", type(e).__name__)
        return f"Impossibile recuperare il contenuto"

@retry_web_scraping
async def _fetch_impl(self, url: str) -> str:
    """Fetch article with retry and extract main content."""
    async with httpx.AsyncClient(
        timeout=30.0,
        follow_redirects=False,  # Don't follow to prevent SSRF via redirect
        limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
    ) as client:
        response = await client.get(url)

        # Validate response size
        content_length = int(response.headers.get("content-length", 0))
        if content_length > 10_000_000:  # 10MB max
            logger.warning("Blocking response: too large (%d bytes)", content_length)
            return ""

        response.raise_for_status()
        # ... rest of parsing
```

### 3. Validate URLs in Pydantic Schemas

```python
# backend/src/api/schemas.py
from pydantic import BaseModel, Field, field_validator
from backend.src.infrastructure.url_validation import is_url_safe

class FeedDiscoveryRequest(BaseModel):
    """Request schema for feed discovery."""
    query: str = Field(..., min_length=1, max_length=500)

    @field_validator("query")
    @classmethod
    def validate_url_if_provided(cls, v: str) -> str:
        if v.startswith(("http://", "https://")):
            if not is_url_safe(v):
                raise ValueError("URL is not authorized")
        return v

class SourceCreate(BaseModel):
    """Schema for creating a Source."""
    feed_url: str = Field(..., min_length=1, max_length=500, pattern=r'^https?://')

    @field_validator("feed_url")
    @classmethod
    def validate_feed_url(cls, v: str) -> str:
        if not is_url_safe(v):
            raise ValueError("Feed URL is not authorized")
        return v
```

### 4. Update Feed Discovery

```python
# backend/src/infrastructure/feed_discovery.py
async def _fetch_html(self, url: str) -> str | None:
    """Fetch HTML content from a URL."""
    if not is_url_safe(url):
        logger.warning("Blocked unsafe URL in feed discovery: %s", url)
        return None

    async with httpx.AsyncClient(
        timeout=self._timeout,
        follow_redirects=False  # Don't follow redirects
    ) as client:
        response = await client.get(url)
        response.raise_for_status()
        # ... rest
```

### 5. Add Configuration for Allowed Domains

Create `.env.example`:
```
# Allowed domains for URL fetching (comma-separated)
ALLOWED_DOMAINS=governo.it,senato.it,camera.it,example.com
ALLOW_PRIVATE_IPS=false  # Set to true only in development
```

Update settings loader:
```python
import os
from backend.src.infrastructure.url_validation import ALLOWED_DOMAINS

def load_allowed_domains() -> set[str]:
    """Load allowed domains from environment."""
    domains_str = os.getenv(
        "ALLOWED_DOMAINS",
        "governo.it,senato.it,camera.it"
    )
    return {d.strip() for d in domains_str.split(",") if d.strip()}

ALLOWED_DOMAINS = load_allowed_domains()
```

## Testing

- [ ] Verify local URLs are blocked (127.0.0.1, localhost)
- [ ] Verify private IPs are blocked (10.x, 192.168.x, 172.16.x)
- [ ] Verify cloud metadata URLs are blocked (169.254.169.254)
- [ ] Verify whitelisted domains are allowed
- [ ] Verify non-whitelisted domains are blocked
- [ ] Verify non-http schemes are blocked (gopher, file, ftp)
- [ ] Verify oversized responses are truncated
- [ ] Verify redirects to private IPs are blocked

Example tests:
```python
def test_block_localhost(test_client):
    response = test_client.post("/api/sources", json={
        "name": "Test",
        "feed_url": "http://127.0.0.1:5432",
        "source_type": "RSS"
    })
    assert response.status_code == 422  # Validation error

def test_block_private_ip(test_client):
    response = test_client.post("/api/sources", json={
        "name": "Test",
        "feed_url": "http://192.168.1.1/feed",
        "source_type": "RSS"
    })
    assert response.status_code == 422

def test_allow_whitelisted_domain(test_client):
    response = test_client.post("/api/sources", json={
        "name": "Test",
        "feed_url": "https://governo.it/feed.xml",
        "source_type": "RSS"
    })
    assert response.status_code == 201
```

## Related Issues

- None (first SSRF finding)

## Timeline

- **Severity**: HIGH
- **Deadline**: Implement immediately (blocks external use)
- **Estimated Effort**: 4-6 hours
- **Blocks**: Any external deployment

## CWE References

- CWE-918: Server-Side Request Forgery (SSRF)
- CWE-399: Uncontrolled Resource Consumption ('Resource Exhaustion')
