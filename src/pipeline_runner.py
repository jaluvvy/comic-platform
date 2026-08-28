from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline import CrawlPipeline
from src.exporters import DataExporter
from src.validators import DataValidator
from src.crawlers.kimdong_v2 import fetch_text, parse_sitemap
from src.crawlers import KimDongCrawler

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "output" / "raw"
PARSED_DIR = BASE_DIR / "output" / "parsed"
EXPORT_DIR = BASE_DIR / "output" / "export"


def load_existing_urls(parsed_dir: Path) -> set[str]:
    urls: set[str] = set()
    for path in parsed_dir.glob("*.json"):
        if path.name in ("summary.json", "summary_filtered.json", "validation_report.json", "pipeline_manifest.json"):
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("url"):
                urls.add(data["url"])
        except Exception:
            pass
    return urls


def main():
    parser = argparse.ArgumentParser(description="Run Kim Dong crawl -> validate -> export pipeline")
    parser.add_argument("--workers", type=int, default=6, help="Concurrent workers")
    parser.add_argument("--delay", type=float, default=0.7, help="Base delay between requests (seconds)")
    parser.add_argument("--limit", type=int, default=None, help="Max products to crawl")
    parser.add_argument("--validate", action="store_true", help="Run validation after crawl")
    parser.add_argument("--export", action="store_true", help="Export JSON/SQL after crawl")
    args = parser.parse_args()

    sitemap_xml = fetch_text("https://nxbkimdong.com.vn/sitemap_products_1.xml")
    items = parse_sitemap(sitemap_xml)
    print(f"[pipeline] Sitemap URLs: {len(items):,}")

    existing_urls = load_existing_urls(PARSED_DIR)
    print(f"[pipeline] Existing parsed: {len(existing_urls):,}")

    pipeline = CrawlPipeline(
        parser=KimDongCrawler,
        raw_dir=RAW_DIR,
        parsed_dir=PARSED_DIR,
        max_workers=args.workers,
        delay=args.delay,
        limit=args.limit,
        existing_urls=existing_urls,
    )
    results = pipeline.crawl(sitemap_xml)
    pipeline.save_summary(results)

    if args.validate:
        print("[pipeline] Validating...")
        validator = DataValidator(PARSED_DIR)
        report = validator.run()
        report_path = PARSED_DIR / "validation_report.json"
        validator.write_report(report, report_path)
        print(f"[pipeline] Validation report -> {report_path}")
        print(f"[pipeline] Invalid comics: {report['summary']['invalid_comics']}")
        print(f"[pipeline] Warnings: {report['summary']['warnings']}")

    if args.export:
        print("[pipeline] Exporting...")
        exporter = DataExporter(PARSED_DIR, EXPORT_DIR)
        paths = exporter.export_all(results)
        for name, path in paths.items():
            print(f"[pipeline] Exported {name} -> {path}")


if __name__ == "__main__":
    main()
