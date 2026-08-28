from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class BaseParser(ABC):
    publisher: str = "Unknown"
    sitemap_url: Optional[str] = None
    base_url: Optional[str] = None

    @staticmethod
    @abstractmethod
    def parse_sitemap(xml_content: str) -> list[dict]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def parse_product(html: str, url: str, lastmod: Optional[str] = None) -> Optional[dict]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def normalize_publisher(raw_publisher: Optional[str]) -> str:
        raise NotImplementedError

    @staticmethod
    def safe_slug(url: str, title: Optional[str] = None) -> str:
        from urllib.parse import urlparse
        import re
        path = urlparse(url).path.strip("/")
        slug = path or (title or "").lower()
        slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", slug)
        return slug[:120].strip("_") or "unknown"

    @staticmethod
    def safe_filename(name: str) -> str:
        import re
        name = re.sub(r"[^a-zA-Z0-9_-]+", "_", name)
        return name[:80]
