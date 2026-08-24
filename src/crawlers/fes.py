import re
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


BASE_URL = "https://nxbkimdong.com.vn"
BLOG_URL = f"{BASE_URL}/blogs/tin-tuc"
NEWS_URL = f"{BASE_URL}/tin-tuc"

HEADERS = {
    "User-Agent": "ComicCrawler/1.0 (contact: https://github.com/your-repo)",
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
def fetch_text(url: str, params: Optional[dict] = None) -> str:
    resp = SESSION.get(url, params=params, timeout=30)
    if resp.status_code in (502, 503, 504):
        raise requests.HTTPError(f"Server error {resp.status_code}", response=resp)
    resp.raise_for_status()
    return resp.text


def parse_blog_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    items = []
    
    for news_item in soup.select(".news-item"):
        a = news_item.find("a", href=True)
        if not a:
            continue
        
        href = a.get("href", "")
        title = a.get_text(strip=True)
        
        # Try img alt as title fallback
        img = a.find("img")
        if not title and img:
            title = img.get("alt", "").strip()
        
        if not title or not href:
            continue
        
        # Make absolute URL
        if href.startswith("/"):
            href = BASE_URL + href
        elif not href.startswith("http"):
            continue
        
        # Extract date if available
        date_elem = news_item.select_one(".date, .time, time, .post-date")
        published_at = None
        if date_elem:
            published_at = date_elem.get_text(strip=True)
        
        # Extract excerpt/snippet
        excerpt_elem = news_item.select_one(".excerpt, .summary, .description, p")
        excerpt = None
        if excerpt_elem:
            excerpt = excerpt_elem.get_text(strip=True)[:500]
        
        items.append({
            "title": title,
            "url": href,
            "published_at": published_at,
            "excerpt": excerpt,
        })
    
    return items


def crawl_blog(page: int = 1) -> list[dict]:
    url = f"{BLOG_URL}?page={page}" if page > 1 else BLOG_URL
    print(f"[fes] Fetching blog page {page}: {url}")
    html = fetch_text(url)
    items = parse_blog_page(html)
    print(f"[fes] Found {len(items)} news items on page {page}")
    return items


def analyze_article_for_fes(html: str, url: str) -> Optional[dict]:
    soup = BeautifulSoup(html, "lxml")
    
    title = soup.select_one("h1, h2.article-title, .blog-title")
    title_text = title.get_text(strip=True) if title else ""
    
    content = soup.select_one(".article-content, .blog-content, .post-content, .summary")
    if not content:
        content = soup.select_one("article")
    if not content:
        content = soup
    
    text = content.get_text("\n", strip=True)
    
    # Check if article mentions FES/events/gifts
    fes_keywords = ["fes", "fan meeting", "hội sách", "sự kiện", "quà tặng", "tặng kèm", 
                    "standee", "poster", "event", "fanmeeting", "tặng quà", "quà fes"]
    
    is_fes_related = any(k in text.lower() for k in fes_keywords)
    
    if not is_fes_related:
        return None
    
    # Extract event name
    event_name = None
    event_match = re.search(r"sự kiện[:\s]+([^\n]+)", text, re.IGNORECASE)
    if event_match:
        event_name = event_match.group(1).strip()
    
    # Extract gifts mentioned
    gifts = []
    for p in content.select("p"):
        p_text = p.get_text(strip=True)
        if "Tặng kèm" in p_text or "Quà tặng" in p_text or "tặng" in p_text.lower():
            gifts.append(p_text)
    
    # Extract date
    date_match = re.search(r"(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})", text)
    event_date = date_match.group(1) if date_match else None
    
    return {
        "title": title_text,
        "url": url,
        "event_name": event_name,
        "event_date": event_date,
        "gifts": gifts,
        "content_snippet": text[:1000],
        "is_fes_related": True,
    }


def save_json(data: dict, path: Path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main(max_pages: int = 5, analyze_articles: bool = False):
    output_dir = Path("output/fes")
    os.makedirs(output_dir, exist_ok=True)
    
    all_items = []
    for page in range(1, max_pages + 1):
        try:
            items = crawl_blog(page)
            all_items.extend(items)
        except Exception as e:
            print(f"[fes] Error crawling page {page}: {e}")
            break
    
    # Save blog posts
    save_json({
        "total": len(all_items),
        "crawled_at": datetime.now(timezone.utc).isoformat(),
        "items": all_items,
    }, output_dir / "blog_posts.json")
    
    print(f"[fes] Saved {len(all_items)} blog posts to {output_dir / 'blog_posts.json'}")
    
    # Optionally analyze articles for FES content
    if analyze_articles:
        fes_items = []
        for item in all_items:
            try:
                html = fetch_text(item["url"])
                analyzed = analyze_article_for_fes(html, item["url"])
                if analyzed:
                    fes_items.append(analyzed)
            except Exception as e:
                print(f"[fes] Error analyzing {item['url']}: {e}")
        
        save_json({
            "total": len(fes_items),
            "crawled_at": datetime.now(timezone.utc).isoformat(),
            "items": fes_items,
        }, output_dir / "fes_gifts_from_blog.json")
        
        print(f"[fes] Found {len(fes_items)} FES-related articles")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Crawl FES/Events from Kim Dong blog")
    parser.add_argument("--pages", type=int, default=5, help="Max blog pages to crawl")
    parser.add_argument("--analyze", action="store_true", help="Analyze articles for FES content")
    args = parser.parse_args()
    
    main(max_pages=args.pages, analyze_articles=args.analyze)
