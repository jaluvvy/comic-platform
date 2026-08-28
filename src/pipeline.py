from __future__ import annotations

import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.schema import Comic
from src.parsers.base import BaseParser


HEADERS = {
    "User-Agent": "ComicCrawler/1.0 (contact: https://github.com/jaluvvy/comic-platform)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(requests.RequestException),
)
def fetch_text(url: str, params: Optional[dict] = None, timeout: int = 30) -> str:
    resp = SESSION.get(url, params=params, timeout=timeout)
    if resp.status_code in (502, 503, 504):
        raise requests.HTTPError(f"Server error {resp.status_code}", response=resp)
    resp.raise_for_status()
    return resp.text


class CrawlPipeline:
    def __init__(
        self,
        parser: type[BaseParser],
        raw_dir: Path,
        parsed_dir: Path,
        max_workers: int = 5,
        delay: float = 1.0,
        limit: Optional[int] = None,
        existing_urls: Optional[set[str]] = None,
        on_success: Optional[Callable[[dict], None]] = None,
    ) -> None:
        self.parser = parser
        self.raw_dir = raw_dir
        self.parsed_dir = parsed_dir
        self.max_workers = max_workers
        self.delay = delay
        self.limit = limit
        self.existing_urls = existing_urls or set()
        self.on_success = on_success
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.parsed_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _normalize_slug(parser: type[BaseParser], url: str) -> str:
        return parser.safe_filename(urlparse(url).path.strip("/"))

    def crawl(self, sitemap_xml: str) -> list[dict]:
        items = self.parser.parse_sitemap(sitemap_xml)
        to_crawl = []
        seen = set()
        for item in items:
            url = item.get("url")
            if not url:
                continue
            if url in self.existing_urls:
                continue
            if url in seen:
                continue
            seen.add(url)
            to_crawl.append(item)
            if self.limit is not None and len(to_crawl) >= self.limit:
                break

        print(f"[pipeline] Total to crawl: {len(to_crawl):,}")
        print(f"[pipeline] Workers: {self.max_workers}, Delay: {self.delay}s")

        results: list[dict] = []
        failed = 0
        start = time.time()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for item in to_crawl:
                future = executor.submit(self._process_item, item)
                futures[future] = item
                time.sleep(self.delay / max(self.max_workers, 1))

            for future in as_completed(futures):
                item = futures[future]
                try:
                    data = future.result()
                    if data:
                        results.append(data)
                        self.existing_urls.add(item.get("url", ""))
                        if self.on_success:
                            self.on_success(data)
                    else:
                        failed += 1
                except Exception as e:
                    failed += 1
                    print(f"[pipeline] Failed {item.get('url')}: {e}")

        elapsed = time.time() - start
        print(f"[pipeline] Done in {elapsed/60:.1f} min")
        print(f"[pipeline] Success: {len(results)}, Failed: {failed}")
        return results

    def _process_item(self, item: dict) -> Optional[dict]:
        url = item.get("url")
        if not url:
            return None
        path = urlparse(url).path
        if path in ("/", "/search", "/account", "/cart", "/checkout"):
            return None

        try:
            html = fetch_text(url)
        except Exception as e:
            print(f"[pipeline] Fetch failed {url}: {e}")
            return None

        slug = self._normalize_slug(self.parser, url)
        raw_path = self.raw_dir / f"{slug}.html"
        raw_path.write_text(html, encoding="utf-8")

        try:
            comic = self.parser.parse_product(html, url, item.get("lastmod"))
        except Exception as e:
            print(f"[pipeline] Parse failed {url}: {e}")
            return None

        if not comic:
            return None

        if hasattr(comic, "model_dump"):
            data = comic.model_dump()
        else:
            data = dict(comic)
        data["raw_html_path"] = str(raw_path)
        data["publisher"] = self.parser.normalize_publisher(data.get("publisher"))

        out_path = self.parsed_dir / f"{slug}.json"
        out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data

    def save_summary(self, items: list[dict]) -> Path:
        summary = {
            "total": len(items),
            "crawled_at": datetime.now(timezone.utc).isoformat(),
            "parser": self.parser.__name__ if hasattr(self.parser, "__name__") else type(self.parser).__name__,
            "items": items,
        }
        path = self.parsed_dir / "summary.json"
        path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[pipeline] Summary -> {path}")
        return path
