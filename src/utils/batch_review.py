import json
import os
import sys
from pathlib import Path

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


def get_pending_comics():
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
        pending.append({"file": f, "data": data, "pid": pid})
    return pending


def print_batch(comics, start_idx, total):
    print("\n" + "=" * 80)
    print(f"BATCH {start_idx//10 + 1} | comics {start_idx+1}-{min(start_idx+10, total)} of {total}")
    print("=" * 80)
    for i, comic in enumerate(comics):
        data = comic["data"]
        print(f"\n[{start_idx + i + 1}] ID: {comic['pid']}")
        print(f"  Title: {data.get('title', 'N/A')}")
        print(f"  Series: {data.get('series', 'N/A')}")
        print(f"  Type: {data.get('product_type', 'N/A')}")
        print(f"  Audience: {data.get('target_audience', 'N/A')}")
        print(f"  Genre: {data.get('genre', 'N/A')}")
        desc = data.get('description', '') or ''
        if desc:
            print(f"  Desc: {desc[:150]}{'...' if len(desc) > 150 else ''}")
        gifts = data.get('gifts', [])
        if gifts:
            print(f"  Gifts: {len(gifts)} item(s)")
            for g in gifts[:2]:
                print(f"    - {g.get('name', 'N/A')}")


def main():
    pending = get_pending_comics()
    if not pending:
        print("[batch] No comics left to review!")
        return

    decisions = load_decisions()
    total = len(pending)
    batch_size = 10
    i = 0

    print(f"[batch] Starting batch review: {total} comics pending")
    print("Commands per comic: [k]eep, [r]emove, [s]kip, [q]uit")
    print("Or batch commands: [a]ll-keep, [A]ll-remove, [n]ext, [p]rev")

    while i < total:
        batch = pending[i:i + batch_size]
        print_batch(batch, i, total)

        # Review each comic in batch
        for j, comic in enumerate(batch):
            pid = comic["pid"]
            while True:
                cmd = input(f"  [{i+j+1}] Decision (k/r/s/q/n): ").strip().lower()
                if cmd in ("k", "keep"):
                    decisions[pid] = "keep"
                    print(f"    -> KEPT")
                    break
                elif cmd in ("r", "remove"):
                    decisions[pid] = "remove"
                    print(f"    -> REMOVED")
                    break
                elif cmd in ("s", "skip"):
                    print(f"    -> SKIPPED")
                    break
                elif cmd in ("n", "next"):
                    print(f"    -> SKIPPED (batch next)")
                    break
                elif cmd in ("q", "quit"):
                    save_decisions(decisions)
                    print(f"\n[batch] Saved progress. {len(decisions)}/{total} reviewed.")
                    return
                else:
                    print("    Invalid. Use k/r/s/n/q")

        save_decisions(decisions)
        i += batch_size
        print(f"\n[batch] Batch complete. Progress: {len(decisions)}/{total} ({len(decisions)*100//total}%)")

        cont = input("Continue to next batch? (y/n): ").strip().lower()
        if cont != "y":
            print(f"\n[batch] Paused. {len(decisions)}/{total} reviewed.")
            return

    print(f"\n[batch] Complete! All {total} comics reviewed.")
    print("Run 'python -m src.utils.manual_filter --apply' to apply changes.")


if __name__ == "__main__":
    main()
