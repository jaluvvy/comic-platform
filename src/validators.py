from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from src.schema import Comic, Volume, Gift


class ValidationError(Exception):
    pass


class DataValidator:
    def __init__(self, parsed_dir: Path) -> None:
        self.parsed_dir = parsed_dir

    def load_parsed(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for path in self.parsed_dir.glob("*.json"):
            if path.name in ("summary.json", "summary_filtered.json", "pipeline_manifest.json", "validation_report.json", "import_manifest.json"):
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                items.append(data)
            except Exception:
                pass
        return items

    def validate_comic(self, item: dict[str, Any]) -> dict[str, Any]:
        result = {
            "slug": item.get("slug"),
            "valid": True,
            "errors": [],
            "warnings": [],
        }

        try:
            comic = Comic(**{k: v for k, v in item.items() if k in Comic.model_fields})
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"schema_error:{e}")
            return result

        if not comic.title:
            result["warnings"].append("missing_title")
        if not comic.url:
            result["warnings"].append("missing_url")
        if not comic.slug:
            result["warnings"].append("missing_slug")
        if not isinstance(comic.price, int) and not isinstance(comic.original_price, int):
            result["warnings"].append("missing_price")
        if comic.isbn and not re.search(r"[\d\-]{10,}", comic.isbn):
            result["warnings"].append("invalid_isbn_format")

        html_fragment_patterns = [
            r"class\s*=",
            r"product-transition",
            r"item-product-name",
            r"<[^>]+>",
        ]
        for gift in comic.gifts or []:
            name = gift.get("name") or ""
            for pat in html_fragment_patterns:
                if re.search(pat, name, re.IGNORECASE):
                    result["warnings"].append(f"gift_html_fragment:{name[:40]}")
                    break

        return result

    def validate_volume(self, volume: dict[str, Any]) -> dict[str, Any]:
        result = {
            "title": volume.get("title"),
            "valid": True,
            "errors": [],
            "warnings": [],
        }
        try:
            Volume(**{k: v for k, v in volume.items() if k in Volume.model_fields})
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"schema_error:{e}")
        return result

    def validate_gift(self, gift: dict[str, Any]) -> dict[str, Any]:
        result = {
            "name": gift.get("name"),
            "valid": True,
            "errors": [],
            "warnings": [],
        }
        try:
            Gift(**{k: v for k, v in gift.items() if k in Gift.model_fields})
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"schema_error:{e}")
        return result

    def run(self) -> dict[str, Any]:
        items = self.load_parsed()
        comics = []
        volumes = []
        gifts = []
        for item in items:
            comics.append(self.validate_comic(item))
            for v in item.get("volumes", []) or []:
                volumes.append(self.validate_volume(v))
            for g in item.get("gifts", []) or []:
                gifts.append(self.validate_gift(g))

        invalid_comics = [c for c in comics if not c["valid"]]
        summary = {
            "total_comics": len(comics),
            "invalid_comics": len(invalid_comics),
            "invalid_volumes": len([v for v in volumes if not v["valid"]]),
            "invalid_gifts": len([g for g in gifts if not g["valid"]]),
            "warnings": sum(len(c.get("warnings", [])) for c in comics),
        }
        return {"summary": summary, "comics": comics, "volumes": volumes, "gifts": gifts}

    def write_report(self, report: dict[str, Any], path: Path) -> Path:
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return path
