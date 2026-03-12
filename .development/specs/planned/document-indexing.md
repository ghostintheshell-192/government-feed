# Document Indexing

status: planned
milestone: M4a (tentative)
priority: medium
created: 2026-03-10

## Summary

Extract, index, and expose document links (PDF, DOC, XLS, etc.) found in news articles.
Government feeds frequently link to official documents (decrees, reports, technical annexes)
that are valuable and hard to find through standard search.

## Motivation

- Institutional feeds often embed links to official documents in article content
- These links are lost if not explicitly extracted and indexed
- Documents are high-value content that users want to browse and search independently
- A document may appear across multiple articles from different sources

## Design

### Domain Entity

```python
class Document:
    id: int
    url: str                    # unique, canonical URL
    filename: str               # extracted from URL path
    file_extension: str         # pdf, docx, xlsx, etc.
    mime_type: str | None       # inferred from extension
    title: str                  # from <a> text or filename
    source_id: int | None       # source where first discovered
    first_seen: datetime        # when first extracted
    last_seen: datetime         # most recent article referencing it
```

Relationship: N:M with `NewsItem` via junction table `article_documents`.

### Target File Extensions

`.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`,
`.csv`, `.zip`, `.ods`, `.odt`, `.odp`, `.rtf`

### Extraction

- **When**: during feed import (FeedParserService) and content scraping (ContentScraper)
- **How**: parse `<a>` tags from content/summary, match `href` against target extensions
- **Function**: standalone `extract_document_links(html: str, base_url: str) -> list[DocumentLink]`
  usable from both import paths
- **Deduplication**: by normalized URL (strip query params, fragments)

### Storage

```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    file_extension TEXT NOT NULL,
    mime_type TEXT,
    title TEXT,
    source_id INTEGER REFERENCES sources(id),
    first_seen TIMESTAMP NOT NULL,
    last_seen TIMESTAMP NOT NULL
);

CREATE TABLE article_documents (
    news_item_id INTEGER REFERENCES news_items(id) ON DELETE CASCADE,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    PRIMARY KEY (news_item_id, document_id)
);
```

### API Endpoints

- `GET /api/documents` — list/search with pagination, filters (type, source, date range, keyword)
- `GET /api/documents/{id}` — document detail with linked articles
- `GET /api/admin/stats` — include document counts in existing stats

### Frontend

- Documents page/tab in UI
- Table with sortable columns (title, type, source, first seen, article count)
- Filters by file type, source
- Each document links to external URL and shows referencing articles
- Document count badge in admin overview

## Dependencies

- **HTML content preservation** — cleanup must not strip `<a>` tags (fixed in this branch)
- **Alembic migration** — new tables require a migration
- Content scraper already preserves `<a>` tags with href

## Open Questions

- Download/cache documents locally? (storage vs. availability tradeoff)
- AI indexing of PDF content? (M4b scope, requires text extraction)
- Handle relative URLs in document links? (need base_url from source)
- URL normalization strategy (query params, tracking suffixes, redirects)
