import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl


class Comic(BaseModel):
    publisher: str
    title: str
    slug: str
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
    series: Optional[str] = None
    genre: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    product_type: Optional[str] = None
    url: Optional[str] = None
    lastmod: Optional[str] = None
    raw_html_path: Optional[str] = None
    gifts: list[dict] = []
