import json
import os
from pathlib import Path
from datetime import datetime, timezone


DEFAULT_FES_FILE = Path("data/fes_gifts.json")
OUTPUT_DIR = Path("output/fes")


def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(DEFAULT_FES_FILE.parent, exist_ok=True)


def load_fes_gifts(path: Path = DEFAULT_FES_FILE) -> list[dict]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("items", data.get("gifts", []))
    return []


def save_fes_gifts(gifts: list[dict], path: Path = DEFAULT_FES_FILE):
    ensure_dirs()
    data = {
        "total": len(gifts),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "items": gifts,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[fes] Saved {len(gifts)} gifts to {path}")


def add_fes_gift(
    comic_product_id: str,
    comic_title: str,
    event_name: str,
    event_date: str,
    gift_name: str,
    description: str = None,
    image_url: str = None,
    condition: str = None,
    source: str = "manual",
    source_url: str = None,
):
    gifts = load_fes_gifts()
    
    gift = {
        "id": f"fes_{len(gifts) + 1}",
        "comic_product_id": comic_product_id,
        "comic_title": comic_title,
        "event_name": event_name,
        "event_date": event_date,
        "gift_name": gift_name,
        "description": description,
        "image_url": image_url,
        "condition": condition,
        "is_fes": True,
        "source": source,
        "source_url": source_url,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    
    gifts.append(gift)
    save_fes_gifts(gifts)
    return gift


def import_from_json(path: Path):
    if not path.exists():
        print(f"[fes] File not found: {path}")
        return
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    items = data if isinstance(data, list) else data.get("items", data.get("gifts", []))
    existing = load_fes_gifts()
    
    # Merge without duplicates by id
    existing_ids = {g.get("id") for g in existing}
    new_gifts = [g for g in items if g.get("id") not in existing_ids]
    
    merged = existing + new_gifts
    save_fes_gifts(merged)
    print(f"[fes] Imported {len(new_gifts)} new gifts from {path}")


def export_for_db(path: Path = OUTPUT_DIR / "fes_gifts_for_db.json"):
    ensure_dirs()
    gifts = load_fes_gifts()
    
    # Transform to DB-ready format matching Prisma Gift/Event/EventGift models
    db_format = {
        "gifts": [],
        "events": [],
        "event_gifts": [],
    }
    
    events_seen = {}
    
    for g in gifts:
        # Add to gifts table
        db_format["gifts"].append({
            "comic_product_id": g.get("comic_product_id"),
            "name": g.get("gift_name"),
            "description": g.get("description"),
            "imageUrl": g.get("image_url"),
            "isFes": True,
            "fesEvent": g.get("event_name"),
        })
        
        # Add to events table (deduplicated)
        event_key = g.get("event_name")
        if event_key and event_key not in events_seen:
            events_seen[event_key] = {
                "name": event_key,
                "eventType": "fes",
                "startDate": g.get("event_date"),
                "description": f"FES event: {event_key}",
                "publisherId": "kimdong",
            }
            db_format["events"].append(events_seen[event_key])
        
        # Add to event_gifts table
        db_format["event_gifts"].append({
            "giftName": g.get("gift_name"),
            "condition": g.get("condition"),
            "imageUrl": g.get("image_url"),
            "comic_product_id": g.get("comic_product_id"),
            "event_name": event_key,
        })
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(db_format, f, ensure_ascii=False, indent=2)
    
    print(f"[fes] Exported DB format to {path}")
    return db_format


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage FES gifts data")
    parser.add_argument("--import", dest="import_path", help="Import FES gifts from JSON file")
    parser.add_argument("--export", action="store_true", help="Export to DB-ready format")
    parser.add_argument("--list", action="store_true", help="List existing FES gifts")
    parser.add_argument("--add", action="store_true", help="Add a new FES gift interactively")
    args = parser.parse_args()
    
    ensure_dirs()
    
    if args.import_path:
        import_from_json(Path(args.import_path))
    elif args.export:
        export_for_db()
    elif args.list:
        gifts = load_fes_gifts()
        print(f"[fes] Total gifts: {len(gifts)}")
        for g in gifts:
            print(f"  - {g.get('gift_name')} ({g.get('event_name')}) - {g.get('comic_title')}")
    elif args.add:
        print("Add FES gift (interactive mode)")
        # Simple interactive add
        comic_product_id = input("Comic product ID: ")
        comic_title = input("Comic title: ")
        event_name = input("Event name: ")
        event_date = input("Event date (YYYY-MM-DD): ")
        gift_name = input("Gift name: ")
        description = input("Description: ")
        image_url = input("Image URL: ")
        
        add_fes_gift(
            comic_product_id=comic_product_id,
            comic_title=comic_title,
            event_name=event_name,
            event_date=event_date,
            gift_name=gift_name,
            description=description or None,
            image_url=image_url or None,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
