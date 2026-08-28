from typing import Optional

from src.crawlers.base import BaseCrawler
from src.parsers.kimdong import KimDongParser


class KimDongCrawler(BaseCrawler):
    publisher = "Nhà xuất bản Kim Đồng"

    @staticmethod
    def parse_sitemap(xml_content: str) -> list[dict]:
        return KimDongParser.parse_sitemap(xml_content)

    @staticmethod
    def parse_product(html: str, url: str, lastmod: Optional[str] = None) -> Optional[dict]:
        comic = KimDongParser.parse_product_page(html, url, lastmod)
        if comic is None:
            return None
        data = comic.model_dump()
        data["publisher"] = KimDongCrawler.publisher
        return data

    @staticmethod
    def normalize_publisher(raw_publisher: Optional[str]) -> str:
        if not raw_publisher:
            return KimDongCrawler.publisher
        if "kim đồng" in raw_publisher.lower() or "kimdong" in raw_publisher.lower():
            return KimDongCrawler.publisher
        return raw_publisher
