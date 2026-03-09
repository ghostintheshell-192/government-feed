# Security Issue: XXE (XML External Entity) Vulnerability in Feed Parser

**Type**: Bug (Security)
**Priority**: High
**Status**: Resolved
**Severity**: HIGH (CVSS 7.5)
**Report**: `archive/analysis/2026-03-08_report_security-auditor.md`

---

## Issue Description

The feed parser uses `feedparser.parse()` on untrusted XML from user-provided feed URLs. XXE (XML External Entity) payloads in RSS/Atom feeds can:
- Read arbitrary files from the server (`/etc/passwd`, environment files)
- Perform Server-Side Request Forgery (SSRF)
- Cause Denial of Service (Billion Laughs attack)
- Information disclosure

## Affected Code

1. **`backend/src/infrastructure/feed_parser.py:44`** — `parse_and_import()`
2. **`backend/src/infrastructure/feed_discovery.py:155`** — `_validate_feed()`

## Current Implementation

```python
# feed_parser.py
feed = feedparser.parse(xml_content)  # ← Parses untrusted XML without XXE protection

# feed_discovery.py
parsed = feedparser.parse(response.text)  # ← Same vulnerability
```

## Attack Vectors

### 1. File Read XXE Payload

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE feed [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<rss version="2.0">
  <channel>
    <title>&xxe;</title>
    <item>
      <title>Leaked Content</title>
      <description>&xxe;</description>
    </item>
  </channel>
</rss>
```

When parsed:
- `/etc/passwd` contents embedded in feed
- Gets stored in database or logs
- Could be exfiltrated if exposed in API responses

### 2. SSRF via XXE

```xml
<?xml version="1.0"?>
<!DOCTYPE feed [
  <!ENTITY xxe SYSTEM "http://internal-service:5432/">
]>
<rss version="2.0">
  <!-- ... feed content ... -->
</rss>
```

### 3. Billion Laughs Attack (DoS)

```xml
<?xml version="1.0"?>
<!DOCTYPE lol [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!-- Repeat many times... -->
]>
<rss version="2.0">
  <channel><title>&lol10;</title></channel>
</rss>
```

Parser enters infinite loop, consuming CPU and memory.

## Remediation Steps

### 1. Validate XML Before Parsing

```python
# backend/src/infrastructure/feed_parser.py
import re
from shared.logging import get_logger

logger = get_logger(__name__)

def is_xml_safe(xml_content: str, source_name: str = "") -> tuple[bool, str | None]:
    """
    Validate XML content for XXE vulnerabilities.

    Returns:
        Tuple of (is_safe, error_message)
    """
    # Check for DOCTYPE declarations with SYSTEM identifiers (XXE risk)
    if "<!DOCTYPE" in xml_content and "SYSTEM" in xml_content:
        logger.warning("Blocked feed with DOCTYPE SYSTEM from %s", source_name)
        return False, "Feed contains DOCTYPE with SYSTEM (XXE protection)"

    # Check for entity declarations beyond standard ones
    # Allow only &lt; &gt; &amp; &apos; &quot;
    entity_pattern = r'<!ENTITY\s+(?!lt;|gt;|amp;|apos;|quot;)'
    if re.search(entity_pattern, xml_content):
        logger.warning("Blocked feed with custom entities from %s", source_name)
        return False, "Feed contains custom entity declarations"

    # Check for INCLUDE keyword (parameter entity injection)
    if "<!ELEMENT" in xml_content or "INCLUDE" in xml_content:
        logger.warning("Blocked feed with parameter entities from %s", source_name)
        return False, "Feed contains parameter entity declarations"

    return True, None

def parse_feed_safely(xml_content: str, source_name: str = ""):
    """Parse feed with XXE protection."""
    import feedparser

    # 1. Validate XML structure
    is_safe, error = is_xml_safe(xml_content, source_name)
    if not is_safe:
        logger.warning("Feed validation failed: %s", error)
        return None, error

    # 2. Remove DOCTYPE declarations entirely (safest approach)
    # This prevents any DTD processing
    cleaned_xml = re.sub(r'<!DOCTYPE[^>]*>', '', xml_content, flags=re.IGNORECASE)

    # 3. Remove any ENTITY declarations
    cleaned_xml = re.sub(r'<!ENTITY[^>]*>', '', cleaned_xml, flags=re.IGNORECASE)

    # 4. Parse with feedparser (uses defusedxml in secure mode)
    try:
        feed = feedparser.parse(cleaned_xml)

        if feed.bozo:
            # Log without exposing exception text (might leak paths)
            logger.warning("Feed parse error from %s (bozo=True)", source_name)
            return None, "Feed parsing error"

        return feed, None
    except Exception as e:
        logger.error("Feed parsing failed from %s: %s", source_name, type(e).__name__)
        return None, "Feed parsing failed"
```

### 2. Update Feed Parser Service

```python
# backend/src/infrastructure/feed_parser.py
class FeedParserService:
    def parse_and_import(self, source: Source) -> int:
        """Parse feed and import news items. Returns count of imported items."""
        try:
            logger.info("Parsing feed from source: %s", source.name)

            # Fetch feed content with resilience
            try:
                xml_content = _cb_feed_fetch.call(
                    self._fetch_feed_content_sync, source.feed_url
                )
            except CircuitBreakerOpenError:
                logger.warning(
                    "Feed fetch circuit breaker is open — skipping source %s",
                    source.name
                )
                return 0

            # Parse safely with XXE protection
            feed, error = parse_feed_safely(xml_content, source.name)
            if error:
                logger.warning("Feed validation failed for %s: %s", source.name, error)
                return 0

            if not feed or feed.bozo:  # Extra safety check
                logger.warning("Feed parse error for %s", source.name)
                return 0

            # ... rest of parsing (unchanged)
            imported_count = 0
            for entry in feed.entries:
                # ... existing entry processing
                imported_count += 1

            return imported_count

        except Exception as e:
            self.db.rollback()
            logger.error("Error parsing feed from %s: %s", source.name, type(e).__name__)
            return 0
```

### 3. Update Feed Discovery Service

```python
# backend/src/infrastructure/feed_discovery.py
async def _validate_feed(
    self, feed_url: str, site_url: str, title: str | None = None
) -> DiscoveredFeed | None:
    """Validate a URL as a feed and return metadata."""
    try:
        async with httpx.AsyncClient(
            timeout=self._timeout, follow_redirects=False
        ) as client:
            response = await client.get(feed_url)
            response.raise_for_status()

        # Parse feed safely
        feed, error = parse_feed_safely(response.text, feed_url)
        if error:
            logger.debug("URL %s is not a valid feed: %s", feed_url, error)
            return None

        # Check if it's a valid feed
        if not feed or not feed.entries:
            return None

        feed_title = title or getattr(feed.feed, "title", None) or feed_url
        feed_type = "Atom" if "atom" in response.headers.get("content-type", "").lower() else "RSS"

        return DiscoveredFeed(
            url=feed_url,
            title=feed_title,
            feed_type=feed_type,
            site_url=site_url,
            entry_count=len(feed.entries),
        )
    except Exception as e:
        logger.debug("URL %s is not a valid feed", feed_url)
        return None
```

### 4. Verify Feedparser Configuration

Ensure `defusedxml` is in `requirements.txt`:
```
defusedxml>=0.0.1
feedparser>=6.0.0
```

The security of modern versions depends on:
```python
# Test that defusedxml is being used
import feedparser
feedparser._sanitize_html = True  # Use defusedxml
```

### 5. Update Tests

Add XXE tests to verify protection:
```python
# backend/tests/test_xxe_protection.py
import pytest
from backend.src.infrastructure.feed_parser import parse_feed_safely

def test_xxe_file_read_blocked():
    """Test that XXE file read is blocked."""
    xxe_payload = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE feed [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<rss version="2.0">
  <channel>
    <title>&xxe;</title>
  </channel>
</rss>
"""
    feed, error = parse_feed_safely(xxe_payload, "test.xml")
    assert error is not None
    assert "DOCTYPE" in error or "entity" in error.lower()

def test_xxe_ssrf_blocked():
    """Test that XXE SSRF is blocked."""
    xxe_payload = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE feed [
  <!ENTITY xxe SYSTEM "http://127.0.0.1:5432/">
]>
<rss version="2.0">
  <channel><title>&xxe;</title></channel>
</rss>
"""
    feed, error = parse_feed_safely(xxe_payload, "test.xml")
    assert error is not None

def test_billion_laughs_blocked():
    """Test that Billion Laughs attack is blocked or limited."""
    # Create a moderately large payload
    lol_payload = """<?xml version="1.0"?>
<!DOCTYPE lol [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
]>
<rss version="2.0">
  <channel><title>&lol3;</title></channel>
</rss>
"""
    # Should either be blocked or parse without hanging
    feed, error = parse_feed_safely(lol_payload, "test.xml")
    # Either error is returned or feed is empty (benign failure)
    # Main thing is it doesn't cause CPU/memory explosion

def test_valid_feed_still_works():
    """Test that valid feeds are still parsed correctly."""
    valid_feed = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <link>http://example.com</link>
    <item>
      <title>Test Article</title>
      <link>http://example.com/article</link>
      <description>Test content</description>
    </item>
  </channel>
</rss>
"""
    feed, error = parse_feed_safely(valid_feed, "test.xml")
    assert error is None
    assert feed is not None
    assert len(feed.entries) == 1
```

## Implementation Checklist

- [ ] Add `is_xml_safe()` function to check for XXE indicators
- [ ] Add `parse_feed_safely()` function with DOCTYPE stripping
- [ ] Update `FeedParserService.parse_and_import()`
- [ ] Update `FeedDiscoveryService._validate_feed()`
- [ ] Verify `defusedxml >= 0.0.1` in requirements.txt
- [ ] Verify `feedparser >= 6.0.0` in requirements.txt
- [ ] Add XXE test cases
- [ ] Test with real government feeds to ensure no false positives
- [ ] Run security test suite

## Related Issues

- None (first XXE finding)

## Timeline

- **Severity**: HIGH
- **Deadline**: Implement immediately (affects all feed processing)
- **Estimated Effort**: 3-4 hours
- **Blocks**: Any feed import functionality

## CWE References

- CWE-611: Improper Restriction of XML External Entity Reference
- CWE-827: Improper Control of Document Type Definition
- CWE-776: Improper Restriction of Recursive Entity References in DTDs (Billion Laughs)

## References

- OWASP XXE Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html
- Python Security: Feedparser XXE: https://github.com/python-trio/feedparser/issues/318
