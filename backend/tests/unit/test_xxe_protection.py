"""Tests for XXE protection in feed parser."""

from backend.src.infrastructure.feed_parser import _DOCTYPE_RE


class TestDoctypeStripping:
    """Tests for DOCTYPE removal regex."""

    def test_strips_simple_doctype(self):
        xml = '<!DOCTYPE feed SYSTEM "http://evil.com/xxe.dtd"><rss><channel></channel></rss>'
        result = _DOCTYPE_RE.sub("", xml)
        assert "<!DOCTYPE" not in result
        assert "<rss>" in result

    def test_strips_xxe_doctype(self):
        xml = """<?xml version="1.0"?>
<!DOCTYPE feed [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<rss version="2.0">
  <channel><title>&xxe;</title></channel>
</rss>"""
        result = _DOCTYPE_RE.sub("", xml)
        assert "<!DOCTYPE" not in result
        assert "<rss" in result

    def test_preserves_valid_xml(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <item>
      <title>Article</title>
      <link>https://example.com/1</link>
    </item>
  </channel>
</rss>"""
        result = _DOCTYPE_RE.sub("", xml)
        assert result == xml  # No change needed

    def test_case_insensitive(self):
        xml = '<!doctype foo><rss></rss>'
        result = _DOCTYPE_RE.sub("", xml)
        assert "doctype" not in result.lower()

    def test_billion_laughs_stripped(self):
        xml = """<?xml version="1.0"?>
<!DOCTYPE lol [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
]>
<rss><channel><title>&lol2;</title></channel></rss>"""
        result = _DOCTYPE_RE.sub("", xml)
        assert "<!DOCTYPE" not in result


class TestFeedParserXxeIntegration:
    """Integration tests for XXE protection in feed parsing."""

    def test_parse_valid_feed_with_doctype_stripping(self):
        """Valid feed should parse correctly after DOCTYPE stripping."""
        import feedparser

        xml = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <link>https://example.com</link>
    <item>
      <title>Test Article</title>
      <link>https://example.com/article</link>
      <description>Test content</description>
    </item>
  </channel>
</rss>"""
        cleaned = _DOCTYPE_RE.sub("", xml)
        feed = feedparser.parse(cleaned)

        assert not feed.bozo
        assert len(feed.entries) == 1
        assert feed.entries[0].title == "Test Article"

    def test_xxe_payload_neutralized(self):
        """XXE payload should be neutralized by DOCTYPE stripping."""
        import feedparser

        xxe_xml = """<?xml version="1.0"?>
<!DOCTYPE feed [
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
</rss>"""
        cleaned = _DOCTYPE_RE.sub("", xxe_xml)
        feed = feedparser.parse(cleaned)

        # After stripping DOCTYPE, &xxe; is an undefined entity
        # feedparser should either error or leave it as-is
        if feed.entries:
            # Content should NOT contain /etc/passwd contents
            for entry in feed.entries:
                desc = entry.get("description", "")
                assert "root:" not in desc
                assert "/bin/bash" not in desc
