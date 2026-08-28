#!/usr/bin/env python3
"""
Import parsed comics into Supabase using psycopg2.
Handles schema: Publisher -> Comic -> Volume -> Gift/EventGift
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.stdout.reconfigure(encoding="utf-8")

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    print("Error: psycopg2-binary is required. Install: pip install psycopg2-binary")
    sys.exit(1)


def get_connection(db_url: str):
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)


def slugify(name: str) -> str:
    import re
    text = (name or "").lower()
    text = text.replace("à", "a").replace("á", "a").replace("ả", "a").replace("ã", "a").replace("ạ", "a")
    text = text.replace("è", "e").replace("é", "e").replace("ẻ", "e").replace("ẽ", "e").replace("ẹ", "e")
    text = text.replace("ì", "i").replace("í", "i").replace("ỉ", "i").replace("ĩ", "i").replace("ị", "i")
    text = text.replace("ò", "o").replace("ó", "o").replace("ỏ", "o").replace("õ", "o").replace("ọ", "o")
    text = text.replace("ù", "u").replace("ú", "u").replace("ủ", "u").replace("ũ", "u").replace("ụ", "u")
    text = text.replace("ỳ", "y").replace("ý", "y").replace("ỷ", "y").replace("ỹ", "y").replace("ỵ", "y")
    text = text.replace("đ", "d")
    text = re.sub(r"[^a-z0-9-]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text[:100] or "unknown"


def ensure_publisher(conn, publisher_name: str) -> str:
    if not publisher_name:
        publisher_name = "Nhà xuất bản Kim Đồng"
    slug = slugify(publisher_name)
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM publishers WHERE name = %s", (publisher_name,))
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute(
            "INSERT INTO publishers (name, slug, type, created_at, updated_at) VALUES (%s, %s, 'nxb', now(), now()) RETURNING id",
            (publisher_name, slug),
        )
        return cur.fetchone()[0]
    finally:
        cur.close()


def import_comics(conn, items: list[dict[str, Any]], clear: bool = False) -> dict[str, int]:
    cur = conn.cursor()
    try:
        if clear:
            cur.execute("DELETE FROM event_gifts")
            cur.execute("DELETE FROM gifts")
            cur.execute("DELETE FROM volumes")
            cur.execute("DELETE FROM comics")
            cur.execute("DELETE FROM publishers")
            print("[import] Cleared existing data")

        stats = {"publishers": 0, "comics": 0, "volumes": 0, "gifts": 0}
        publisher_cache: dict[str, str] = {}

        for item in items:
            publisher_name = item.get("publisher") or "Nhà xuất bản Kim Đồng"
            if publisher_name not in publisher_cache:
                publisher_cache[publisher_name] = ensure_publisher(conn, publisher_name)
                stats["publishers"] += 1
            publisher_id = publisher_cache[publisher_name]

            comic_slug = item.get("slug") or str(item.get("product_id") or "unknown")
            cur.execute(
                """
                INSERT INTO comics (
                    publisher_id, title, slug, product_id, price, original_price, currency,
                    sku, isbn, authors, target_audience, dimensions, pages, format, weight,
                    edition_type, edition_year, series, description, cover_image, product_type,
                    url, lastmod, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (slug) DO UPDATE SET
                    title = EXCLUDED.title,
                    price = EXCLUDED.price,
                    original_price = EXCLUDED.original_price,
                    sku = EXCLUDED.sku,
                    isbn = EXCLUDED.isbn,
                    authors = EXCLUDED.authors,
                    target_audience = EXCLUDED.target_audience,
                    dimensions = EXCLUDED.dimensions,
                    pages = EXCLUDED.pages,
                    format = EXCLUDED.format,
                    weight = EXCLUDED.weight,
                    edition_type = EXCLUDED.edition_type,
                    edition_year = EXCLUDED.edition_year,
                    series = EXCLUDED.series,
                    description = EXCLUDED.description,
                    cover_image = EXCLUDED.cover_image,
                    product_type = EXCLUDED.product_type,
                    url = EXCLUDED.url,
                    lastmod = EXCLUDED.lastmod,
                    updated_at = EXCLUDED.updated_at
                RETURNING id
                """,
                (
                    publisher_id,
                    item.get("title"),
                    comic_slug,
                    item.get("product_id"),
                    item.get("price"),
                    item.get("original_price"),
                    item.get("currency", "VND"),
                    item.get("sku"),
                    item.get("isbn"),
                    item.get("authors", []),
                    item.get("target_audience"),
                    item.get("dimensions"),
                    item.get("pages"),
                    item.get("format"),
                    item.get("weight"),
                    item.get("edition_type", "ban_in_dau"),
                    item.get("edition_year"),
                    item.get("series"),
                    item.get("description"),
                    item.get("cover_image"),
                    item.get("product_type"),
                    item.get("url"),
                    item.get("lastmod"),
                    datetime.now(timezone.utc).isoformat(),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            comic_id = cur.fetchone()[0]
            stats["comics"] += 1

            for volume in item.get("volumes", []) or []:
                vol_slug = volume.get("slug") or f"{comic_slug}-vol-{volume.get('volume_number') or 0}"
                cur.execute(
                    """
                    INSERT INTO volumes (
                        comic_id, publisher_id, title, slug, product_id, sku, barcode,
                        price, original_price, currency, volume_number, volume_label,
                        pages, format, dimensions, weight, cover_image, url,
                        available, inventory_qty, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (product_id) DO UPDATE SET
                        title = EXCLUDED.title,
                        price = EXCLUDED.price,
                        original_price = EXCLUDED.original_price,
                        available = EXCLUDED.available,
                        updated_at = EXCLUDED.updated_at
                    RETURNING id
                    """,
                    (
                        comic_id,
                        publisher_id,
                        volume.get("title"),
                        vol_slug,
                        volume.get("product_id"),
                        volume.get("sku"),
                        volume.get("barcode"),
                        volume.get("price"),
                        volume.get("original_price"),
                        volume.get("currency", "VND"),
                        volume.get("volume_number"),
                        volume.get("volume_label"),
                        volume.get("pages"),
                        volume.get("format"),
                        volume.get("dimensions"),
                        volume.get("weight"),
                        volume.get("cover_image"),
                        volume.get("url"),
                        volume.get("available", True),
                        volume.get("inventory_qty"),
                        datetime.now(timezone.utc).isoformat(),
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                volume_id = cur.fetchone()[0]
                stats["volumes"] += 1

                for gift in volume.get("gifts", []) or []:
                    cur.execute(
                        """
                        INSERT INTO gifts (
                            volume_id, name, description, image_url, is_fes, fes_event, gift_type, rarity, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            volume_id,
                            gift.get("name"),
                            gift.get("description"),
                            gift.get("image_url"),
                            gift.get("is_fes", False),
                            gift.get("fes_event"),
                            gift.get("gift_type", "combo"),
                            gift.get("rarity", "normal"),
                            datetime.now(timezone.utc).isoformat(),
                            datetime.now(timezone.utc).isoformat(),
                        ),
                    )
                    stats["gifts"] += 1

            for gift in item.get("gifts", []) or []:
                cur.execute(
                    """
                    INSERT INTO gifts (
                        name, description, image_url, is_fes, fes_event, gift_type, rarity, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        gift.get("name"),
                        gift.get("description"),
                        gift.get("image_url"),
                        gift.get("is_fes", False),
                        gift.get("fes_event"),
                        gift.get("gift_type", "combo"),
                        gift.get("rarity", "normal"),
                        datetime.now(timezone.utc).isoformat(),
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                stats["gifts"] += 1

        return stats
    finally:
        cur.close()


def write_manifest(path: Path, stats: dict[str, int], checksum: str) -> Path:
    manifest = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "stats": stats,
        "checksum": checksum,
    }
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main():
    parser = argparse.ArgumentParser(description="Import parsed comics into Supabase")
    parser.add_argument("--url", required=True, help="Postgres connection URL")
    parser.add_argument("--input", required=True, help="Input parsed directory or comics.json")
    parser.add_argument("--clear", action="store_true", help="Clear existing data before import")
    args = parser.parse_args()

    input_path = Path(args.input)
    print(f"[import] Input path: {input_path.resolve()}")
    print(f"[import] Input exists: {input_path.exists()}")
    if input_path.exists():
        print(f"[import] Input size: {input_path.stat().st_size}")
    if input_path.is_dir():
        items: list[dict[str, Any]] = []
        for file in input_path.glob("*.json"):
            if file.name in ("summary.json", "summary_filtered.json", "validation_report.json", "pipeline_manifest.json"):
                continue
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                items.append(data)
            except Exception:
                pass
    else:
        items = json.loads(input_path.read_text(encoding="utf-8"))

    checksum = hashlib.sha256(json.dumps(items, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    print(f"[import] Loaded {len(items)} comics, checksum={checksum[:16]}...")

    conn = get_connection(args.url)
    try:
        stats = import_comics(conn, items, clear=args.clear)
        print(f"[import] Done: {stats}")
        manifest_path = input_path.parent / "import_manifest.json" if input_path.is_file() else input_path / "import_manifest.json"
        write_manifest(manifest_path, stats, checksum)
        print(f"[import] Manifest -> {manifest_path}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
