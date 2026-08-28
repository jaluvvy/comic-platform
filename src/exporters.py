from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.schema import Comic, Volume, Gift


class DataExporter:
    def __init__(self, parsed_dir: Path, export_dir: Path) -> None:
        self.parsed_dir = parsed_dir
        self.export_dir = export_dir
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def load_parsed(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for path in self.parsed_dir.glob("*.json"):
            if path.name in ("summary.json", "summary_filtered.json", "pipeline_manifest.json"):
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                items.append(data)
            except Exception:
                pass
        return items

    def export_comics(self, items: list[dict[str, Any]]) -> Path:
        seen = set()
        comics: list[dict[str, Any]] = []
        dup_count = 0
        for item in items:
            if not item.get("title") or not item.get("slug"):
                continue
            key = item.get("product_id") or item.get("url") or item.get("slug")
            if not key:
                continue
            if key in seen:
                dup_count += 1
                continue
            seen.add(key)
            try:
                comic = Comic(**{k: v for k, v in item.items() if k in Comic.model_fields})
                comics.append(comic.model_dump())
            except Exception as e:
                print(f"[export] Skipped comic {item.get('slug')}: {e}")
        path = self.export_dir / "comics.json"
        payload = json.dumps(comics, ensure_ascii=False, indent=2)
        path.write_text(payload, encoding="utf-8")
        print(f"[export] Wrote {len(comics)} comics to {path} (size={len(payload)})")
        return path

    def export_volumes(self, items: list[dict[str, Any]]) -> Path:
        seen = set()
        volumes: list[dict[str, Any]] = []
        for item in items:
            for v in item.get("volumes", []) or []:
                if not v.get("title") or not v.get("slug"):
                    continue
                key = (item.get("slug"), v.get("slug") or v.get("title"), v.get("product_id"))
                if key in seen:
                    continue
                seen.add(key)
                try:
                    volume = Volume(**{k: v for k, v in v.items() if k in Volume.model_fields})
                    volumes.append(volume.model_dump())
                except Exception as e:
                    print(f"[export] Skipped volume {v.get('slug')}: {e}")
        path = self.export_dir / "volumes.json"
        path.write_text(json.dumps(volumes, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def export_gifts(self, items: list[dict[str, Any]]) -> Path:
        seen = set()
        gifts: list[dict[str, Any]] = []
        for item in items:
            for g in item.get("gifts", []) or []:
                if not g.get("name"):
                    continue
                key = (item.get("slug"), g.get("name"))
                if key in seen:
                    continue
                seen.add(key)
                try:
                    gift = Gift(**{k: v for k, v in g.items() if k in Gift.model_fields})
                    gifts.append(gift.model_dump())
                except Exception as e:
                    print(f"[export] Skipped gift {g.get('name')}: {e}")
        path = self.export_dir / "gifts.json"
        path.write_text(json.dumps(gifts, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def export_manifest(self, comics: list[dict[str, Any]], volumes: list[dict[str, Any]], gifts: list[dict[str, Any]], source: str = "parsed") -> Path:
        prices = [int(x["price"]) for x in comics if isinstance(x.get("price"), int)]
        originals = [int(x["original_price"]) for x in comics if isinstance(x.get("original_price"), int)]
        manifest = {
            "source": source,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "total_comics": len(comics),
            "total_volumes": len(volumes),
            "total_gifts": len(gifts),
            "price_stats": {
                "min_price": min(prices) if prices else None,
                "max_price": max(prices) if prices else None,
            },
            "checksum": hashlib.sha256(
                json.dumps(comics, ensure_ascii=False, sort_keys=True).encode("utf-8")
            ).hexdigest(),
        }
        path = self.export_dir / "import_manifest.json"
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def export_all(self, items: list[dict[str, Any]], source: str = "parsed") -> dict[str, Path]:
        comics = self.export_comics(items)
        volumes = self.export_volumes(items)
        gifts = self.export_gifts(items)
        manifest_path = self.export_manifest(
            json.loads(comics.read_text(encoding="utf-8")),
            json.loads(volumes.read_text(encoding="utf-8")),
            json.loads(gifts.read_text(encoding="utf-8")),
            source,
        )
        return {
            "comics": comics,
            "volumes": volumes,
            "gifts": gifts,
            "manifest": manifest_path,
        }
