import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup

PARSED_DIR = Path("output/parsed")
RAW_DIR = Path("output/raw")


def extract_volumes_from_html(html: str, url: str) -> list[dict]:
    volumes = []
    soup = BeautifulSoup(html, "lxml")
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
                        title = product_data.get("name", "")
                        slug = Path(urlparse(url).path).stem if url else ""
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
    return volumes


def main():
    json_files = sorted(PARSED_DIR.glob("*.json"))
    json_files = [f for f in json_files if f.name not in ("summary.json", "summary_filtered.json", ".crawled_urls.txt")]
    print(f"[reparse] Found {len(json_files)} JSON files")

    updated = 0
    skipped = 0
    errors = 0

    for json_file in json_files:
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            if "volumes" in data:
                skipped += 1
                continue

            raw_path = data.get("raw_html_path")
            if not raw_path:
                skipped += 1
                continue

            html_path = Path(raw_path)
            if not html_path.is_absolute():
                html_path = Path.cwd() / raw_path

            if not html_path.exists():
                skipped += 1
                continue

            html = html_path.read_text(encoding="utf-8", errors="ignore")
            url = data.get("url") or f"https://nxbkimdong.com.vn/{json_file.stem}"
            volumes = extract_volumes_from_html(html, url)

            if volumes:
                data["volumes"] = volumes
                json_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                updated += 1
                if updated % 200 == 0:
                    print(f"[reparse] Updated {updated} files...", flush=True)
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"[reparse] Error {json_file.name}: {e}")

    print(f"\n[reparse] Done!")
    print(f"[reparse] Updated: {updated}")
    print(f"[reparse] Skipped: {skipped}")
    print(f"[reparse] Errors: {errors}")


if __name__ == "__main__":
    main()
