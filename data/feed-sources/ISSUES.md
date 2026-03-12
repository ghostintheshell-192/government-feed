# Feed Sources — Issues Log

## Malformed OPML files

| File | Issue | Fix |
|------|-------|-----|
| `Russia.opml` | Unescaped `"` inside XML attributes (Коммерсантъ) | Manually removed inner quotes |

## Failed feeds (by country)

### Germany
- **FOCUS Online** — HTTP 404 (dead feed URL)

### Italy
- **Fanpage** — HTTP 403 (blocks RSS scrapers)
- **Il Post** — HTTP 403 (blocks RSS scrapers)

### Poland
- **Polska Agencja Prasowa** — Invalid XML in feed content

### Spain
- **Agencia EFE** — Invalid XML in feed content

### Ukraine
- **ТЕЛЕГРАФ** — HTTP 404 (dead feed URL)
- **Вести.ua** — DNS resolution failure (domain down)

### Russia
- **Вести.Ru** — HTTP 404 (dead feed URL)

### EU Institutions
- **EEA - Press Releases** — Response is not valid RSS/Atom (possibly JSON API)
- **EEA - Publications** — Response is not valid RSS/Atom (possibly JSON API)
- **ECHR - Judgments** — HTTP 403 (blocks scrapers)

## Sources

| OPML file | Origin | Notes |
|-----------|--------|-------|
| `France.opml` | awesome-rss-feeds | Mostly newspapers |
| `Germany.opml` | awesome-rss-feeds | Mostly newspapers |
| `Ireland.opml` | awesome-rss-feeds | Mostly newspapers |
| `Italy.opml` | awesome-rss-feeds | Mostly newspapers |
| `Poland.opml` | awesome-rss-feeds | Mostly newspapers |
| `Russia.opml` | awesome-rss-feeds | Mostly newspapers (manually fixed XML) |
| `Spain.opml` | awesome-rss-feeds | Mostly newspapers |
| `Ukraine.opml` | awesome-rss-feeds | Mostly newspapers |
| `United Kingdom.opml` | awesome-rss-feeds | Mostly newspapers |
| `EU-Institutions.opml` | Manually curated | EP, EUR-Lex, ECB, Eurostat, EEA |

## Summary

- **Total feeds**: 97
- **Valid**: 86 (89%)
- **Failed**: 11 (11%)
- **Skipped OPML files**: 0 (after manual fix)
- **Country OPMLs**: 9 (mostly European newspapers)
- **EU Institutions**: 1 (government/institutional sources)
