#!/usr/bin/env python3
"""Feed crawler: parse OPML directories, validate feeds, and prepare catalog entries.

Usage:
    # Validate all OPML files in a directory
    python scripts/crawl_feeds.py validate data/feed-sources/opml-raw/

    # Validate a single OPML file
    python scripts/crawl_feeds.py validate data/feed-sources/opml-raw/Italy.opml

    # Import validated feeds into the database
    python scripts/crawl_feeds.py import data/feed-sources/validated/Italy.json

    # Add EU institutional feeds
    python scripts/crawl_feeds.py validate data/feed-sources/eu-institutions/eu-institutions.opml
"""

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import feedparser
import httpx

# Country name -> ISO 3166-1 alpha-2 code
COUNTRY_CODES: dict[str, str] = {
    "Austria": "AT",
    "Belgium": "BE",
    "Bulgaria": "BG",
    "Croatia": "HR",
    "Cyprus": "CY",
    "Czech Republic": "CZ",
    "Denmark": "DK",
    "Estonia": "EE",
    "Finland": "FI",
    "France": "FR",
    "Germany": "DE",
    "Greece": "GR",
    "Hungary": "HU",
    "Iceland": "IS",
    "Ireland": "IE",
    "Italy": "IT",
    "Latvia": "LV",
    "Lithuania": "LT",
    "Luxembourg": "LU",
    "Malta": "MT",
    "Netherlands": "NL",
    "Norway": "NO",
    "Poland": "PL",
    "Portugal": "PT",
    "Romania": "RO",
    "Russia": "RU",
    "Serbia": "RS",
    "Slovakia": "SK",
    "Slovenia": "SI",
    "Spain": "ES",
    "Sweden": "SE",
    "Switzerland": "CH",
    "Ukraine": "UA",
    "United Kingdom": "GB",
}

# Domain patterns that suggest geographic level
CONTINENTAL_DOMAINS = {"europa.eu", "consilium.europa.eu", "europarl.europa.eu"}

# TLD -> country code (for feeds without a country context)
TLD_TO_COUNTRY: dict[str, str] = {
    ".it": "IT",
    ".fr": "FR",
    ".de": "DE",
    ".es": "ES",
    ".pl": "PL",
    ".uk": "GB",
    ".ie": "IE",
    ".nl": "NL",
    ".be": "BE",
    ".at": "AT",
    ".ch": "CH",
    ".se": "SE",
    ".no": "NO",
    ".dk": "DK",
    ".fi": "FI",
    ".pt": "PT",
    ".gr": "GR",
    ".cz": "CZ",
    ".ro": "RO",
    ".hu": "HU",
    ".bg": "BG",
    ".hr": "HR",
    ".sk": "SK",
    ".si": "SI",
    ".ee": "EE",
    ".lv": "LV",
    ".lt": "LT",
    ".ua": "UA",
    ".ru": "RU",
    ".rs": "RS",
    ".is": "IS",
    ".lu": "LU",
    ".mt": "MT",
    ".cy": "CY",
    ".gov.uk": "GB",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
}


def parse_opml(path: Path) -> list[dict[str, str]]:
    """Parse an OPML file and return a list of feed entries."""
    # Some OPML files have invalid XML entities — clean them up
    raw = path.read_text(encoding="utf-8", errors="replace")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        # Try fixing common issues: unescaped ampersands
        import re

        raw = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;|#)", "&amp;", raw)
        root = ET.fromstring(raw)
    feeds: list[dict[str, str]] = []

    for outline in root.iter("outline"):
        xml_url = outline.get("xmlUrl")
        if not xml_url:
            continue
        feeds.append({
            "name": outline.get("title") or outline.get("text") or "",
            "description": outline.get("description") or "",
            "feed_url": xml_url,
            "source_type": (outline.get("type") or "rss").upper(),
        })

    return feeds


def infer_geographic_level(feed_url: str) -> str:
    """Infer geographic level from the feed URL domain."""
    for domain in CONTINENTAL_DOMAINS:
        if domain in feed_url:
            return "CONTINENTAL"
    return "NATIONAL"


def infer_country_from_url(feed_url: str) -> str | None:
    """Try to infer country code from URL TLD."""
    # Check longest TLDs first (e.g., .gov.uk before .uk)
    for tld, code in sorted(TLD_TO_COUNTRY.items(), key=lambda x: -len(x[0])):
        # Check if TLD appears in the domain part
        from urllib.parse import urlparse

        hostname = urlparse(feed_url).hostname or ""
        if hostname.endswith(tld):
            return code
    return None


def infer_tags(name: str, description: str) -> list[str]:
    """Infer basic tags from feed name and description."""
    tags: list[str] = []
    text = (name + " " + description).lower()

    tag_keywords = {
        "news": ["news", "notizie", "nachrichten", "actualité", "nyheter"],
        "politics": ["politi", "governo", "government", "parliament", "parlamento"],
        "economy": ["econom", "finanz", "finance", "business", "market"],
        "law": ["law", "legal", "legislat", "lex", "giuridic", "recht"],
        "science": ["science", "scienz", "wissenschaft", "research"],
        "environment": ["environment", "ambiente", "climat", "energy", "energia"],
        "tech": ["tech", "digital", "cyber", "innovat"],
    }

    for tag, keywords in tag_keywords.items():
        if any(kw in text for kw in keywords):
            tags.append(tag)

    return tags


def validate_feed(feed_url: str, timeout: float = 15.0) -> dict[str, object]:
    """Validate a feed URL: check HTTP response and parse content."""
    result: dict[str, object] = {
        "url": feed_url,
        "valid": False,
        "status_code": None,
        "error": None,
        "entry_count": 0,
        "feed_title": None,
    }

    try:
        with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=timeout) as client:
            response = client.get(feed_url)
            result["status_code"] = response.status_code

            if response.status_code != 200:
                result["error"] = f"HTTP {response.status_code}"
                return result

            parsed = feedparser.parse(response.text)
            if parsed.bozo and not parsed.entries:
                result["error"] = f"Parse error: {parsed.bozo_exception}"
                return result

            result["valid"] = True
            result["entry_count"] = len(parsed.entries)
            result["feed_title"] = parsed.feed.get("title", "")

    except httpx.TimeoutException:
        result["error"] = "Timeout"
    except Exception as e:
        result["error"] = str(e)

    return result


def process_opml(
    opml_path: Path,
    country_name: str | None = None,
) -> list[dict[str, object]]:
    """Process an OPML file: parse, validate, and categorize all feeds."""
    feeds = parse_opml(opml_path)

    # Derive country from filename if not specified
    if country_name is None:
        country_name = opml_path.stem

    country_code = COUNTRY_CODES.get(country_name)

    print(f"\n{'=' * 60}")
    print(f"Processing: {country_name} ({len(feeds)} feeds)")
    print(f"{'=' * 60}")

    results: list[dict[str, object]] = []

    for i, feed in enumerate(feeds, 1):
        url = feed["feed_url"]
        print(f"  [{i}/{len(feeds)}] {feed['name'][:50]}... ", end="", flush=True)

        validation = validate_feed(url)

        if validation["valid"]:
            print(f"OK ({validation['entry_count']} entries)")
        else:
            print(f"FAIL ({validation['error']})")

        # Use parsed feed title if available and better than OPML title
        name = feed["name"]
        if validation.get("feed_title") and len(str(validation["feed_title"])) > len(name):
            name = str(validation["feed_title"])

        geo_level = infer_geographic_level(url)
        feed_country = country_code
        if geo_level == "CONTINENTAL":
            feed_country = None  # EU-level, no single country

        # Try to infer country from URL if we don't have one
        if not feed_country and geo_level != "CONTINENTAL":
            feed_country = infer_country_from_url(url)

        tags = infer_tags(name, feed.get("description", ""))

        results.append({
            "name": name,
            "description": feed.get("description", ""),
            "feed_url": url,
            "source_type": feed.get("source_type", "RSS"),
            "geographic_level": geo_level,
            "country_code": feed_country,
            "tags": tags,
            "validation": {
                "valid": validation["valid"],
                "status_code": validation["status_code"],
                "error": validation["error"],
                "entry_count": validation["entry_count"],
            },
        })

    # Summary
    valid = sum(1 for r in results if r["validation"]["valid"])
    print(f"\n  Summary: {valid}/{len(results)} valid feeds")

    return results


def cmd_validate(target: str) -> None:
    """Validate OPML file(s) and save results as JSON."""
    target_path = Path(target)

    if target_path.is_dir():
        opml_files = sorted(target_path.glob("*.opml"))
    elif target_path.is_file() and target_path.suffix == ".opml":
        opml_files = [target_path]
    else:
        print(f"Error: {target} is not a valid OPML file or directory")
        sys.exit(1)

    if not opml_files:
        print(f"No OPML files found in {target}")
        sys.exit(1)

    output_dir = Path("data/feed-sources/validated")
    output_dir.mkdir(parents=True, exist_ok=True)

    all_stats: dict[str, dict[str, int]] = {}

    for opml_file in opml_files:
        try:
            results = process_opml(opml_file)
        except ET.ParseError as e:
            print(f"\n  SKIPPED {opml_file.name}: XML parse error ({e})")
            all_stats[opml_file.stem] = {"total": 0, "valid": 0, "error": str(e)}
            continue

        output_file = output_dir / f"{opml_file.stem}.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        valid = sum(1 for r in results if r["validation"]["valid"])
        all_stats[opml_file.stem] = {"total": len(results), "valid": valid}
        print(f"  Saved to: {output_file}")

    # Final summary
    print(f"\n{'=' * 60}")
    print("FINAL SUMMARY")
    print(f"{'=' * 60}")
    total_feeds = 0
    total_valid = 0
    for name, stats in all_stats.items():
        total_feeds += stats["total"]
        total_valid += stats["valid"]
        print(f"  {name}: {stats['valid']}/{stats['total']} valid")
    print(f"  TOTAL: {total_valid}/{total_feeds} valid")


def cmd_import(target: str) -> None:
    """Import validated feeds from JSON into the database."""
    target_path = Path(target)

    if target_path.is_dir():
        json_files = sorted(target_path.glob("*.json"))
    elif target_path.is_file() and target_path.suffix == ".json":
        json_files = [target_path]
    else:
        print(f"Error: {target} is not a valid JSON file or directory")
        sys.exit(1)

    # Import here to avoid requiring DB setup for validate-only usage
    from backend.src.infrastructure.database import SessionLocal
    from backend.src.infrastructure.models import Source
    from backend.src.infrastructure.unit_of_work import UnitOfWork

    db = SessionLocal()
    uow = UnitOfWork(db)

    added = 0
    skipped = 0

    try:
        # Get existing feed URLs to avoid duplicates
        existing_urls = {s.feed_url for s in uow.source_repository.get_all()}

        for json_file in json_files:
            with open(json_file) as f:
                feeds = json.load(f)

            print(f"\nImporting from {json_file.name}...")

            for feed in feeds:
                if not feed["validation"]["valid"]:
                    continue

                if feed["feed_url"] in existing_urls:
                    skipped += 1
                    continue

                source = Source(
                    name=feed["name"],
                    description=feed.get("description", ""),
                    feed_url=feed["feed_url"],
                    source_type=feed.get("source_type", "RSS"),
                    geographic_level=feed.get("geographic_level"),
                    country_code=feed.get("country_code"),
                    tags=feed.get("tags", []),
                )
                db.add(source)
                existing_urls.add(feed["feed_url"])
                added += 1

        uow.commit()
        print(f"\nDone: {added} added, {skipped} skipped (duplicates)")

    except Exception as e:
        uow.rollback()
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        db.close()


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    target = sys.argv[2]

    if command == "validate":
        cmd_validate(target)
    elif command == "import":
        cmd_import(target)
    else:
        print(f"Unknown command: {command}")
        print("Usage: crawl_feeds.py [validate|import] <path>")
        sys.exit(1)


if __name__ == "__main__":
    main()
