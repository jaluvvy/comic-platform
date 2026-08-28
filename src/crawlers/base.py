import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class BaseCrawler(ABC):
    @abstractmethod
    def parse_sitemap(self, xml_content: str) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def parse_product(self, html: str, url: str, lastmod: Optional[str] = None) -> Optional[dict]:
        raise NotImplementedError

    @staticmethod
    def safe_filename(name: str) -> str:
        name = re.sub(r"[^a-zA-Z0-9_-]+", "_", name)
        return name[:80]

    @staticmethod
    def safe_slug(url: str, title: Optional[str] = None) -> str:
        from urllib.parse import urlparse
        path = urlparse(url).path.strip("/")
        slug = path or (title or "").lower()
        slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", slug)
        return slug[:120].strip("_") or "unknown"
