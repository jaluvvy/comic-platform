import re
import time
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import BaseModel, Field


class Comic(BaseModel):
    publisher: str = "Nhà xuất bản Kim Đồng"
    title: Optional[str] = None
    slug: str = ""
    product_id: Optional[str] = None
    price: Optional[int] = None
    original_price: Optional[int] = None
    currency: str = "VND"
    sku: Optional[str] = None
    isbn: Optional[str] = None
    authors: list[str] = []
    target_audience: Optional[str] = None
    dimensions: Optional[str] = None
    pages: Optional[int] = None
    format: Optional[str] = None
    weight: Optional[str] = None
    edition_type: Optional[str] = "ban_in_dau"
    edition_year: Optional[int] = None
    series: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    product_type: Optional[str] = None
    url: Optional[str] = None
    lastmod: Optional[str] = None
    raw_html_path: Optional[str] = None
    gifts: list[dict] = []
    volumes: list[dict] = []


RAW_DIR = Path("output/raw")
PARSED_DIR = Path("output/parsed")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PARSED_DIR, exist_ok=True)

SITEMAP_URL = "https://nxbkimdong.com.vn/sitemap_products_1.xml"
BASE_URL = "https://nxbkimdong.com.vn"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def safe_filename(name: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9_-]+", "_", name)
    return name[:80]


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


def parse_sitemap(xml_content: str) -> list[dict]:
    root = BeautifulSoup(xml_content, "xml")
    items = []
    for url_tag in root.find_all("url"):
        loc = url_tag.find("loc")
        lastmod = url_tag.find("lastmod")
        if loc and loc.text:
            items.append({
                "url": loc.text.strip(),
                "lastmod": lastmod.text.strip() if lastmod and lastmod.text else None,
            })
    return items


def detect_edition(title: str, desc: str, html: str = "") -> tuple[str, Optional[int]]:
    text = f"{title or ''} {desc or ''} {html or ''}"
    edition_type = "ban_in_dau"
    edition_year = None

    reprint = re.search(
        r"Tái bản\s*(?:lần\s*)?(\d+)?(?:\s*\(?\s*(\d{4})\s*\)?)?",
        text,
        re.IGNORECASE,
    )
    if reprint:
        edition_type = "tai_ban"
        if reprint.group(2):
            edition_year = int(reprint.group(2))
        elif reprint.group(1):
            edition_year = int(reprint.group(1))

    first = re.search(r"Bản in đầu|Bản đẹp|Bản đặc biệt|Bản Collector", text, re.IGNORECASE)
    if first:
        edition_type = "ban_in_dau"

    year_match = re.search(r"\b(20\d{2})\b", text)
    if year_match and not edition_year:
        possible_year = int(year_match.group(1))
        if 2000 <= possible_year <= 2030:
            edition_year = possible_year

    return edition_type, edition_year


def extract_gifts(soup: BeautifulSoup, html: str = "") -> list[dict]:
    gifts = []
    seen = set()

    gift_patterns = [
        r"\(Tặng\s+kèm\s+([^)]+)\)",
        r"\(Tặng\s+kèm\s+([^)]+)\)",
        r"Tặng\s+kèm\s+([^<]{3,80})",
        r"Quà\s+tặng\s+([^<]{3,80})",
        r"Tặng\s+kèm\s+(\d+\s*[^<]{3,80})",
    ]

    bad_patterns = [
        r"dành\s+cho\s+bản\s+in\s+đầu\s+tiên",
        r"dành\s+cho\s+mỗi\s+tập",
        r"dànhcho\s+bản\s+in\s+đầu\s+tiên",
        r"chỉ\s+có\s+trong\s+lần\s+in\s+đầu\s+tiên",
        r"hãy\s+cùng\s+đón\s+chào",
        r"class\s*=",
        r"product-transition",
        r"item-product-name",
        r"<[^>]+>",
    ]

    html_tag_re = re.compile(r"<[^>]+>")
    html_entity_re = re.compile(r"&[a-zA-Z0-9#]+;")
    extra_space_re = re.compile(r"\s+")

    def clean_text(text: str) -> str:
        if not text:
            return ""
        text = html_tag_re.sub("", text)
        text = html_entity_re.sub("", text)
        text = extra_space_re.sub(" ", text).strip()
        return text

    def is_bad(name: str) -> bool:
        lower = name.lower()
        for pat in bad_patterns:
            if re.search(pat, lower):
                return True
        return False

    # Strategy 1: title/alt attributes
    for tag in soup.find_all(["a", "img"]):
        text = ""
        if tag.name == "a" and tag.get("title"):
            text = tag.get("title", "")
        elif tag.name == "img" and tag.get("alt"):
            text = tag.get("alt", "")
        if not text:
            continue
        text = clean_text(text)
        for pat in gift_patterns[:3]:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                name = clean_text(m.group(1))
                if name and len(name) >= 3 and not is_bad(name) and name.lower() not in seen:
                    seen.add(name.lower())
                    gifts.append({"name": name, "description": None, "image_url": None})
                break

    # Strategy 2: page text fallback
    if not gifts:
        page_text = soup.get_text(separator="\n", strip=True)
        for pat in gift_patterns:
            matches = re.findall(pat, page_text, re.IGNORECASE)
            for m in matches:
                name = clean_text(" ".join(m) if isinstance(m, tuple) else m)
                if name and len(name) >= 3 and not is_bad(name) and name.lower() not in seen:
                    seen.add(name.lower())
                    gifts.append({"name": name, "description": None, "image_url": None})

    return gifts


def parse_product(html: str, url: str, lastmod: Optional[str] = None) -> Optional[Comic]:
    soup = BeautifulSoup(html, "lxml")

    title_tag = soup.select_one("h1.title-head")
    title = title_tag.get_text(strip=True) if title_tag else None
    if not title:
        return None

    slug = urlparse(url).path.strip("/")
    product_id = None
    mpn = soup.select_one("meta[itemprop='mpn']")
    if mpn:
        product_id = mpn.get("content")

    price = original_price = None
    price_box = soup.select_one(".price-box")
    if price_box:
        special = price_box.select_one(".price.product-price")
        old = price_box.select_one(".price.product-price-old del")
        if special:
            raw = special.get_text(strip=True).replace("₫", "").replace(".", "").replace(",", "")
            try:
                price = int(raw)
            except ValueError:
                pass
        if old:
            raw = old.get_text(strip=True).replace("₫", "").replace(".", "").replace(",", "")
            try:
                original_price = int(raw)
            except ValueError:
                pass

    sku = None
    sku_tag = soup.select_one(".variant-sku")
    if sku_tag:
        content = sku_tag.get("content")
        if content:
            sku = content.strip()
        else:
            text = sku_tag.get_text(strip=True)
            m = re.search(r"Mã sản phẩm:\s*(\S+)", text)
            if m:
                sku = m.group(1)

    description = None
    desc_meta = soup.select_one("meta[itemprop='description']")
    if desc_meta:
        description = desc_meta.get("content", "").strip() or None

    cover_image = None
    img_meta = soup.select_one("meta[itemprop='image']")
    if img_meta:
        cover_image = img_meta.get("content", "").strip() or None

    seller = None
    seller_elem = soup.select_one('div[itemprop="seller"]')
    if seller_elem:
        seller_meta = seller_elem.select_one('meta[itemprop="name"]')
        if seller_meta:
            seller = seller_meta.get("content", "").strip() or None
    if not seller:
        seller_meta = soup.select_one('meta[itemprop="name"]')
        if seller_meta:
            seller = seller_meta.get("content", "").strip() or None

    product_type = None
    type_meta = soup.select_one("meta[property='og:type']")
    if type_meta:
        product_type = type_meta.get("content", "").strip() or None

    summary_text = ""
    summary = soup.select_one(".summary")
    if summary:
        summary_text = summary.get_text("\n", strip=True)

    isbn = dimensions = pages = fmt = weight = series = target_audience = None
    authors = []

    if summary:
        for li in summary.find_all("li"):
            text = li.get_text(" ", strip=True)
            if "ISBN:" in text:
                m = re.search(r"ISBN:\s*([\d\-\s]+)", text)
                if m:
                    isbn = m.group(1).strip()
            elif text.startswith("Tác giả:"):
                raw = text.replace("Tác giả:", "").strip()
                parts = [p.strip() for p in re.split(r"\s{2,}", raw) if p.strip()]
                authors = [p for p in parts if p and not re.search(r"\(\d", p)]
            elif text.startswith("Đối tượng:"):
                target_audience = text.replace("Đối tượng:", "").strip()
            elif text.startswith("Khuôn Khổ:"):
                dimensions = text.replace("Khuôn Khổ:", "").strip()
            elif text.startswith("Số trang:"):
                m = re.search(r"Số trang:\s*(\d+)", text)
                if m:
                    try:
                        pages = int(m.group(1))
                    except ValueError:
                        pass
            elif text.startswith("Định dạng:"):
                fmt = text.replace("Định dạng:", "").strip()
            elif text.startswith("Trọng lượng:"):
                weight = text.replace("Trọng lượng:", "").strip()
            elif text.startswith("Bộ sách:"):
                series = text.replace("Bộ sách:", "").strip()

    if not authors:
        m = re.search(r"Tác giả:\s*(.+?)(?:\n|$)", summary_text)
        if m:
            raw = m.group(1)
            parts = [p.strip() for p in re.split(r"\s{2,}", raw) if p.strip()]
            authors = [p for p in parts if p and not re.search(r"\(\d", p)]

    edition_type, edition_year = detect_edition(title, description or "", html)
    gifts = extract_gifts(soup, html)

    volumes = []
    script_tags = soup.find_all("script")
    for script in script_tags:
        script_text = script.get_text()
        if "variants" in script_text and "product" in script_text:
            match = re.search(r"product\s*=\s*({.*?});", script_text, re.DOTALL)
            if match:
                try:
                    product_data = json.loads(match.group(1))
                    variants = product_data.get("variants", [])
                    if len(variants) > 1:
                        for variant in variants:
                            volume_number = None
                            volume_label = None
                            option_title = variant.get("title", "")
                            m = re.search(r"Tập\s+(\d+)", option_title)
                            if m:
                                volume_number = int(m.group(1))
                                volume_label = f"Tập {volume_number:02d}"
                            elif option_title:
                                volume_label = option_title

                            image_url = None
                            image_data = variant.get("image")
                            if isinstance(image_data, dict):
                                image_url = image_data.get("src")

                            volumes.append({
                                "product_id": str(variant.get("id")) if variant.get("id") else None,
                                "sku": variant.get("sku"),
                                "barcode": variant.get("barcode"),
                                "title": option_title or title,
                                "slug": f"{slug}-tap-{volume_number:02d}" if volume_number else slug,
                                "price": int(variant.get("price", 0)) if variant.get("price") else None,
                                "original_price": int(variant.get("compare_at_price", 0)) if variant.get("compare_at_price") else None,
                                "volume_number": volume_number,
                                "volume_label": volume_label,
                                "cover_image": image_url,
                                "url": url,
                                "available": bool(variant.get("available", True)),
                                "inventory_qty": variant.get("inventory_quantity"),
                                "gifts": [],
                            })
                        break
                except json.JSONDecodeError:
                    continue

    return Comic(
        publisher=seller or "Nhà xuất bản Kim Đồng",
        title=title,
        slug=slug,
        product_id=product_id,
        price=price,
        original_price=original_price,
        sku=sku,
        isbn=isbn,
        authors=authors,
        target_audience=target_audience,
        dimensions=dimensions,
        pages=pages,
        format=fmt,
        weight=weight,
        edition_type=edition_type,
        edition_year=edition_year,
        series=series,
        description=description,
        cover_image=cover_image,
        product_type=product_type,
        url=url,
        lastmod=lastmod,
        gifts=gifts,
        volumes=volumes,
    )


def save_comic(comic: Comic):
    pid = comic.product_id or safe_filename(comic.slug or comic.title or "unknown")
    path = PARSED_DIR / f"{pid}.json"
    data = comic.model_dump()
    if data.get("raw_html_path"):
        data["raw_html_path"] = str(data["raw_html_path"])
    data["raw_html_path"] = str(data.get("raw_html_path") or "")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def crawl_one(item: dict) -> Optional[Comic]:
    url = item.get("url")
    if not url:
        return None
    path = urlparse(url).path
    if path in ("/", "/search", "/account", "/cart", "/checkout"):
        return None

    try:
        html = fetch_text(url)
    except Exception as e:
        print(f"[skip] Failed {url}: {e}")
        return None

    slug = safe_filename(path.strip("/"))
    raw_path = RAW_DIR / f"{slug}.html"
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(html)

    try:
        comic = parse_product(html, url, item.get("lastmod"))
    except Exception as e:
        print(f"[skip] Parse failed {url}: {e}")
        return None

    if comic:
        comic.raw_html_path = str(raw_path)
    return comic


def main(max_workers: int = 5, limit: Optional[int] = None, delay: float = 1.0):
    print("[crawl] Fetching sitemap...")
    xml = fetch_text(SITEMAP_URL)
    items = parse_sitemap(xml)
    print(f"[crawl] Total URLs in sitemap: {len(items):,}")

    existing = set()
    for f in PARSED_DIR.glob("*.json"):
        if "summary" in f.name:
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if data.get("url"):
                existing.add(data["url"])
        except Exception:
            pass

    to_crawl = [item for item in items if item.get("url") not in existing]
    if limit is not None:
        to_crawl = to_crawl[:limit]

    print(f"[crawl] Already crawled: {len(existing):,}")
    print(f"[crawl] To crawl: {len(to_crawl):,}")
    print(f"[crawl] Workers: {max_workers}, Delay: {delay}s")

    comics = []
    failed = 0
    start = time.time()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for item in to_crawl:
            future = executor.submit(crawl_one, item)
            futures[future] = item
            time.sleep(delay / max_workers)

        for future in as_completed(futures):
            comic = future.result()
            if comic:
                comics.append(comic)
                save_comic(comic)
            else:
                failed += 1

    elapsed = time.time() - start
    print(f"\n[crawl] Done in {elapsed/60:.1f} min")
    print(f"[crawl] Success: {len(comics)}, Failed: {failed}")

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
    print(f"[save] Summary -> {summary_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Crawl NXB Kim Đồng products v2")
    parser.add_argument("--limit", type=int, default=None, help="Max products to crawl")
    parser.add_argument("--delay", type=float, default=1.0, help="Base delay between requests (seconds)")
    parser.add_argument("--workers", type=int, default=5, help="Concurrent workers")
    args = parser.parse_args()

    main(max_workers=args.workers, limit=args.limit, delay=args.delay)
