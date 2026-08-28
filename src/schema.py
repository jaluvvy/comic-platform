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
    edition_type: Optional[str] = None
    edition_year: Optional[int] = None
    series: Optional[str] = None
    genre: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    product_type: Optional[str] = None
    url: Optional[str] = None
    lastmod: Optional[str] = None
    raw_html_path: Optional[str] = None
    gifts: list[dict] = []
    volumes: list[dict] = []


class Volume(BaseModel):
    comic_product_id: Optional[str] = None
    title: str
    slug: str
    product_id: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    price: Optional[int] = None
    original_price: Optional[int] = None
    currency: str = "VND"
    volume_number: Optional[int] = None
    volume_label: Optional[str] = None
    pages: Optional[int] = None
    format: Optional[str] = None
    dimensions: Optional[str] = None
    weight: Optional[str] = None
    cover_image: Optional[str] = None
    url: Optional[str] = None
    available: bool = True
    inventory_qty: Optional[int] = None
    gifts: list[dict] = []


class Gift(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_fes: bool = False
    fes_event: Optional[str] = None
    volume_id: Optional[str] = None
    event_id: Optional[str] = None
    gift_type: str = "combo"
    rarity: str = "normal"

