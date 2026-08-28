from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.schema import Comic, Volume, Gift


EXPORT_DIR = Path(__file__).resolve().parent.parent / "output" / "export"


def escape_sql(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, int):
        return str(value)
    text = str(value)
    text = text.replace("'", "''")
    return f"'{text}'"


def comic_insert(item: dict[str, Any]) -> str:
    comic = Comic(**{k: v for k, v in item.items() if k in Comic.model_fields})
    now = datetime.now(timezone.utc).isoformat()
    gifts_sql = "ARRAY["
    parts = []
    for g in comic.gifts or []:
        gift = Gift(**{k: v for k, v in g.items() if k in Gift.model_fields})
        parts.append(
            f"ROW({escape_sql(gift.name)},{escape_sql(gift.description)},{escape_sql(gift.image_url)},"
            f"{escape_sql(gift.is_fes)},{escape_sql(gift.fes_event)},{escape_sql('combo')},{escape_sql(gift.rarity)})::gift"
        )
    gifts_sql += ",".join(parts) + "]"
    if not parts:
        gifts_sql = "ARRAY[]::gift[]"

    volumes_sql = "ARRAY["
    parts = []
    for v in (comic.volumes or []):
        vol = Volume(**{k: v for k, v in v.items() if k in Volume.model_fields})
        parts.append(
            f"ROW({escape_sql(vol.title)},{escape_sql(vol.slug)},{escape_sql(vol.product_id)},"
            f"{escape_sql(vol.sku)},{escape_sql(vol.barcode)},{escape_sql(vol.price)},{escape_sql(vol.original_price)},"
            f"'VND',{escape_sql(vol.volume_number)},{escape_sql(vol.volume_label)},{escape_sql(vol.pages)},"
            f"{escape_sql(vol.format)},{escape_sql(vol.dimensions)},{escape_sql(vol.weight)},"
            f"{escape_sql(vol.cover_image)},{escape_sql(vol.url)},{escape_sql(vol.available)},{escape_sql(vol.inventory_qty)},"
            f"ARRAY[]::gift[])"
        )
    volumes_sql += ",".join(parts) + "]"
    if not parts:
        volumes_sql = "ARRAY[]::volume[]"

    return (
        f"INSERT INTO comics (publisher, title, slug, product_id, price, original_price, currency, sku, isbn, "
        f"authors, target_audience, dimensions, pages, format, weight, edition_type, edition_year, series, "
        f"description, cover_image, product_type, url, lastmod, gifts, volumes, created_at, updated_at) "
        f"VALUES ({escape_sql(comic.publisher)},{escape_sql(comic.title)},{escape_sql(comic.slug)},"
        f"{escape_sql(comic.product_id)},{escape_sql(comic.price)},{escape_sql(comic.original_price)},"
        f"'VND',{escape_sql(comic.sku)},{escape_sql(comic.isbn)},"
        f"ARRAY{escape_sql(comic.authors)},{escape_sql(comic.target_audience)},{escape_sql(comic.dimensions)},"
        f"{escape_sql(comic.pages)},{escape_sql(comic.format)},{escape_sql(comic.weight)},"
        f"{escape_sql(comic.edition_type)},{escape_sql(comic.edition_year)},{escape_sql(comic.series)},"
        f"{escape_sql(comic.description)},{escape_sql(comic.cover_image)},{escape_sql(comic.product_type)},"
        f"{escape_sql(comic.url)},{escape_sql(comic.lastmod)},{gifts_sql},{volumes_sql},"
        f"'{now}','{now}') "
        f"ON CONFLICT (slug) DO NOTHING;"
    )


def export_sql(source: Path | None = None, output: Path | None = None) -> Path:
    source = source or EXPORT_DIR / "comics.json"
    output = output or EXPORT_DIR / "comics.sql"
    data = json.loads(source.read_text(encoding="utf-8"))
    lines = ["BEGIN;"]
    for item in data:
        try:
            lines.append(comic_insert(item))
        except Exception as e:
            print(f"[export] Skipped {item.get('slug')}: {e}")
    lines.append("COMMIT;")
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"[export] SQL -> {output}")
    return output


if __name__ == "__main__":
    export_sql()
