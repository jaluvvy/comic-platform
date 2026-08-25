import os
import re
import json
import hashlib
from datetime import datetime
from typing import Optional
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.schema import Comic


HEADERS = {
    "User-Agent": "ComicCrawler/1.0 (contact: https://github.com/your-repo)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


class KimDongParser:
    @staticmethod
    def parse_sitemap(xml_content: str) -> list[dict]:
        urls = []
        try:
            root = ET.fromstring(xml_content)
            for url_elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
                loc = url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
                lastmod = url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
                img = url_elem.find("{http://www.google.com/schemas/sitemap/image/1.1}image")
                if loc is not None:
                    item = {
                        "url": loc.text.strip() if loc.text else None,
                        "lastmod": lastmod.text.strip() if lastmod is not None and lastmod.text else None,
                    }
                    if img is not None:
                        img_loc = img.find("{http://www.google.com/schemas/sitemap/image/1.1}loc")
                        if img_loc is not None and img_loc.text:
                            item["image_url"] = img_loc.text.strip()
                    urls.append(item)
        except ET.ParseError as e:
            print(f"[sitemap] Parse error: {e}")
        return urls

    @staticmethod
    def _extract_text_after_label(soup, label: str) -> Optional[str]:
        for li in soup.select(".summary li"):
            text = li.get_text(" ", strip=True)
            if text.startswith(label):
                return text[len(label):].strip()
        return None

    @staticmethod
    def _parse_price(text: str) -> Optional[int]:
        if not text:
            return None
        raw = text.replace("₫", "").replace(".", "").replace(",", "").strip()
        try:
            return int(raw)
        except ValueError:
            return None

    @staticmethod
    def parse_product_page(html: str, url: str, lastmod: Optional[str] = None) -> Optional[Comic]:
        soup = BeautifulSoup(html, "lxml")

        title_tag = soup.select_one("h1.title-head")
        title = title_tag.get_text(strip=True) if title_tag else None
        if not title:
            return None

        slug = urlparse(url).path.strip("/").split("-")[-1] if url else None
        product_id = None
        mpn = soup.select_one("meta[itemprop='mpn']")
        if mpn:
            product_id = mpn.get("content")

        price = None
        original_price = None
        price_box = soup.select_one(".price-box")
        if price_box:
            special = price_box.select_one(".price.product-price")
            old = price_box.select_one(".price.product-price-old del")
            if special:
                price = KimDongParser._parse_price(special.get_text(strip=True))
            if old:
                original_price = KimDongParser._parse_price(old.get_text(strip=True))

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

        genre = None
        genre = KimDongParser._extract_text_after_label(soup, "Thể loại:")
        if not genre:
            breadcrumb = soup.select_one(".breadcrumb")
            if breadcrumb:
                crumbs = [c.get_text(strip=True) for c in breadcrumb.find_all("a")]
                if crumbs:
                    genre = crumbs[-1] if crumbs else None

        summary_text = ""
        summary = soup.select_one(".summary")
        if summary:
            summary_text = summary.get_text("\n", strip=True)

        isbn = None
        dimensions = None
        pages = None
        fmt = None
        weight = None
        series = None
        target_audience = None
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

        if not authors and title:
            authors = [title]

        publisher = seller if seller and seller != title else "Nhà xuất bản Kim Đồng"

        gifts = []
        for p in soup.select("p"):
            strong = p.find("strong")
            if strong and "Tặng kèm" in strong.get_text():
                gift_name = strong.get_text(strip=True).replace("Tặng kèm", "").strip()
                img = None
                next_p = p.find_next_sibling("p")
                if next_p:
                    img = next_p.find("img")
                if not img:
                    img = p.find("img")
                image_url = img.get("src") if img else None
                if image_url and image_url.startswith("//"):
                    image_url = "https:" + image_url
                gifts.append({
                    "name": gift_name,
                    "description": None,
                    "image_url": image_url,
                    "is_fes": False,
                    "fes_event": None,
                })

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
            publisher=publisher,
            title=title,
            slug=slug or "",
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
            series=series,
            description=description,
            cover_image=cover_image,
            product_type=product_type,
            genre=genre,
            gifts=gifts,
            volumes=volumes,
            url=url,
            lastmod=lastmod,
        )
