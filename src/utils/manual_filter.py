import json
import os
import sys
from pathlib import Path
from datetime import datetime

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

PARSED_DIR = Path("output/parsed")
DECISIONS_FILE = Path("output/manual_filter_decisions.json")


def load_decisions():
    if DECISIONS_FILE.exists():
        with open(DECISIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_decisions(decisions):
    os.makedirs(DECISIONS_FILE.parent, exist_ok=True)
    with open(DECISIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(decisions, f, ensure_ascii=False, indent=2)


def get_comics_to_review():
    files = sorted(PARSED_DIR.glob("*.json"))
    files = [f for f in files if f.name not in ("summary.json", "summary_filtered.json", ".crawled_urls.txt")]
    
    decisions = load_decisions()
    pending = []
    
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        
        pid = data.get("product_id") or f.stem
        if pid in decisions:
            continue
        
        pending.append({
            "file": f,
            "data": data,
            "pid": pid,
        })
    
    return pending


def print_comic_info(comic, index, total):
    data = comic["data"]
    print("\n" + "="*80)
    print(f"[{index}/{total}] ID: {comic['pid']}")
    print(f"Title: {data.get('title', 'N/A')}")
    print(f"Series: {data.get('series', 'N/A')}")
    print(f"Publisher: {data.get('publisher', 'N/A')}")
    print(f"Authors: {', '.join(data.get('authors', []))}")
    print(f"Genre: {data.get('genre', 'N/A')}")
    print(f"Target Audience: {data.get('target_audience', 'N/A')}")
    print(f"Price: {data.get('price', 'N/A')}")
    print(f"Product Type: {data.get('product_type', 'N/A')}")
    print(f"URL: {data.get('url', 'N/A')}")
    
    desc = data.get('description', '') or ''
    if desc:
        print(f"Description: {desc[:300]}{'...' if len(desc) > 300 else ''}")
    
    gifts = data.get('gifts', [])
    if gifts:
        print(f"Gifts: {len(gifts)} item(s)")
        for g in gifts[:3]:
            print(f"  - {g.get('name', 'N/A')}")
    
    print("="*80)


def apply_decisions():
    decisions = load_decisions()
    removed = 0
    kept = 0
    errors = 0
    
    for pid, decision in decisions.items():
        # Find the file
        target = None
        for f in PARSED_DIR.glob("*.json"):
            if f.stem == pid or f.name == f"{pid}.json":
                target = f
                break
        
        if not target:
            errors += 1
            continue
        
        if decision == "remove":
            try:
                target.unlink()
                removed += 1
            except Exception:
                errors += 1
        elif decision == "keep":
            kept += 1
    
    print(f"[apply] Kept: {kept}, Removed: {removed}, Errors: {errors}")
    return kept, removed, errors


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Manual filter comics")
    parser.add_argument("--review", action="store_true", help="Start interactive review")
    parser.add_argument("--apply", action="store_true", help="Apply saved decisions")
    parser.add_argument("--reset", action="store_true", help="Reset all decisions")
    parser.add_argument("--status", action="store_true", help="Show review status")
    args = parser.parse_args()
    
    if args.status:
        decisions = load_decisions()
        total = len(list(PARSED_DIR.glob("*.json")))
        total = sum(1 for f in PARSED_DIR.glob("*.json") if f.name not in ("summary.json", "summary_filtered.json", ".crawled_urls.txt"))
        reviewed = len(decisions)
        kept = sum(1 for v in decisions.values() if v == "keep")
        removed = sum(1 for v in decisions.values() if v == "remove")
        print(f"Total comics: {total}")
        print(f"Reviewed: {reviewed} ({reviewed*100//max(total,1)}%)")
        print(f"Kept: {kept}, Removed: {removed}")
        return
    
    if args.reset:
        if DECISIONS_FILE.exists():
            DECISIONS_FILE.unlink()
        print("[reset] All decisions cleared")
        return
    
    if args.apply:
        apply_decisions()
        return
    
    if args.review:
        pending = get_comics_to_review()
        if not pending:
            print("[review] No comics left to review!")
            return
        
        decisions = load_decisions()
        total = len(pending)
        
        print(f"[review] Starting manual review: {total} comics pending")
        print("Commands: [k]eep, [r]emove, [s]kip, [q]uit")
        
        for i, comic in enumerate(pending):
            print_comic_info(comic, i + 1, total)
            
            while True:
                cmd = input("Decision (k/r/s/q): ").strip().lower()
                if cmd in ("k", "keep"):
                    decisions[comic["pid"]] = "keep"
                    save_decisions(decisions)
                    print(f"  -> KEPT: {comic['data'].get('title', '')}")
                    break
                elif cmd in ("r", "remove"):
                    decisions[comic["pid"]] = "remove"
                    save_decisions(decisions)
                    print(f"  -> REMOVED: {comic['data'].get('title', '')}")
                    break
                elif cmd in ("s", "skip"):
                    print("  -> SKIPPED")
                    break
                elif cmd in ("q", "quit"):
                    print(f"\n[review] Saved progress. {len(decisions)}/{total} reviewed.")
                    return
                else:
                    print("Invalid command. Use k/r/s/q")
        
        print(f"\n[review] Complete! All {total} comics reviewed.")
        print(f"Run 'python -m src.utils.manual_filter --apply' to apply changes.")
        return
    
    parser.print_help()


if __name__ == "__main__":
    main()
