import re
import time
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.parsers.kimdong import KimDongParser
from src.schema import Comic


RAW_DIR = Path("output/raw")
PARSED_DIR = Path("output/parsed")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PARSED_DIR, exist_ok=True)

SITEMAP_URL = "https://nxbkimdong.com.vn/sitemap_products_1.xml"
BASE_URL = "https://nxbkimdong.com.vn"
ROBOTS_URL = f"{BASE_URL}/robots.txt"

HEADERS = {
    "User-Agent": "ComicCrawler/1.0 (contact: https://github.com/your-repo)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def safe_filename(name: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9_-]+", "_", name)
    return name[:80]


def check_robots_txt() -> dict:
    try:
        resp = SESSION.get(ROBOTS_URL, timeout=10)
        resp.raise_for_status()
        print(f"[crawl] robots.txt fetched from {ROBOTS_URL}")
        return {"allowed": True, "content": resp.text}
    except Exception as e:
        print(f"[crawl] robots.txt fetch failed: {e}")
        return {"allowed": True, "content": ""}


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(requests.RequestException),
)
def fetch_text(url: str, params: Optional[dict] = None) -> str:
    resp = SESSION.get(url, params=params, timeout=30)
    if resp.status_code in (502, 503, 504):
        raise requests.HTTPError(f"Server error {resp.status_code}", response=resp)
    resp.raise_for_status()
    return resp.text


def crawl_sitemap() -> list[dict]:
    print("[crawl] Fetching sitemap...")
    xml = fetch_text(SITEMAP_URL)
    path = PARSED_DIR / "sitemap_products_1.xml"
    with open(path, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"[crawl] Saved sitemap to {path}")

    items = KimDongParser.parse_sitemap(xml)
    print(f"[crawl] Parsed {len(items)} URLs from sitemap")
    return items


def crawl_product(url: str, lastmod: Optional[str] = None) -> Optional[Comic]:
    print(f"[crawl] Fetching product: {url}")
    try:
        html = fetch_text(url)
    except Exception as e:
        print(f"[crawl] Failed to fetch {url}: {e}")
        return None

    slug = urlparse(url).path.strip("/")
    raw_path = RAW_DIR / f"{safe_filename(slug)}.html"
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(html)

    try:
        comic = KimDongParser.parse_product_page(html, url, lastmod)
    except Exception as e:
        print(f"[crawl] Parse failed for {url}: {e}")
        return None

    if comic:
        comic.raw_html_path = str(raw_path)
    return comic


def save_comic(comic: Comic):
    slug = safe_filename(comic.slug or comic.title or "unknown")
    pid = comic.product_id or slug
    path = PARSED_DIR / f"{pid}.json"
    data = comic.model_dump()
    if data.get("raw_html_path"):
        data["raw_html_path"] = str(data["raw_html_path"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[save] {path}")


def main(limit: Optional[int] = None, delay: float = 1.5, new_only: bool = True):
    robots = check_robots_txt()
    if not robots.get("allowed", True):
        print("[crawl] Blocked by robots.txt")
        return

    items = crawl_sitemap()
    seen_urls = set()
    existing_files = {p.stem for p in PARSED_DIR.glob("*.json") if p.name not in ("summary.json", "summary_filtered.json")}
    index_path = PARSED_DIR / ".crawled_urls.txt"
    existing_urls = set()
    if index_path.exists():
        try:
            existing_urls = set(index_path.read_text(encoding="utf-8").splitlines())
        except Exception:
            existing_urls = set()
    comics = []
    count = 0

    for item in items:
        if limit is not None and count >= limit:
            break
        url = item.get("url")
        if not url:
            continue
        path = urlparse(url).path
        if path in ("/", "/search", "/account", "/cart", "/checkout"):
            continue
        if url in seen_urls:
            continue
        seen_urls.add(url)

        slug = safe_filename(path.strip("/").split("-")[-1] if path else "unknown")
        pid = slug

        if new_only:
            if url in existing_urls:
                print(f"[skip] Already crawled: {url}")
                count += 1
                continue

        comic = crawl_product(url, item.get("lastmod"))
        if comic:
            comics.append(comic)
            save_comic(comic)
            existing_urls.add(url)
            try:
                with open(index_path, "a", encoding="utf-8") as f:
                    f.write(url + "\n")
            except Exception:
                pass
            count += 1
        time.sleep(delay)

    summary_path = PARSED_DIR / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "total": len(comics),
                "crawled_at": datetime.now(timezone.utc).isoformat(),
                "items": [c.model_dump() for c in comics],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"[done] Total comics crawled: {len(comics)} -> {summary_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Crawl NXB Kim Đồng products")
    parser.add_argument("--limit", type=int, default=None, help="Max products to crawl")
    parser.add_argument("--delay", type=float, default=1.5, help="Delay between requests (seconds)")
    parser.add_argument("--all", dest="new_only", action="store_false", help="Crawl all products, including already crawled")
    parser.set_defaults(new_only=True)
    args = parser.parse_args()

    main(limit=args.limit, delay=args.delay, new_only=args.new_only)
