import json
import os
import sys
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

PARSED_DIR = Path("output/parsed")
DECISIONS_FILE = Path("output/manual_filter_decisions.json")
OUTPUT_FILE = Path("output/auto_filter_decisions.json")

MANGA_INDICATORS = {
    "explicit_manga": [
        "(manga)", "(truyện tranh nhật bản)", "truyện tranh nhật",
        "(truyện tranh)", "manga",
    ],
    "explicit_anime": [
        "(anime)", "(hoạt hình nhật bản)", "hoạt hình nhật", "anime",
    ],
    "explicit_ln": [
        "(light novel)", "(light-novel)", "(ln)", "light novel",
    ],
    "japanese_publishers": [
        "nhà xuất bản kang", "nxb kang", "nhà xuất bản izan", "nxb izan",
        "nhà xuất bản sao", "nxb sao", "nhà xuất bản horizon", "nxb horizon",
        "nhà xuất bản ipm", "nxb ipm",
    ],
    "manga_series": [
        "naruto", "one piece", "dragon ball", "bleach", "death note",
        "attack on titan", "shingeki no kyojin", "tokyo ghoul",
        "demon slayer", "kimetsu no yaiba", "jujutsu kaisen",
        "jojo", "fairy tail", "hunter x hunter",
        "my hero academia", "boku no hero", "mha",
        "sword art online", "overlord",
        "re:zero", "konosuba",
        "fullmetal alchemist", "fma",
        "cowboy bebop", "evangelion",
        "chainsaw man",
        "hells paradise", "world trigger",
        "dr. stone", "toradora",
        "ao ashi",
        "cậu ma nhà xí hanako", "cau ma nha xi hanako",
        "astro boy", "cậu bé tay sắt",
        "bảng xếp hạng quân vương",
    ],
}


def load_decisions():
    if DECISIONS_FILE.exists():
        with open(DECISIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_json(path, data):
    os.makedirs(path.parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def analyze_comic(data):
    title = (data.get("title") or "").lower()
    product_type = (data.get("product_type") or "").lower()
    publisher = data.get("publisher") or {}
    if isinstance(publisher, str):
        publisher_name = publisher.lower()
    else:
        publisher_name = (publisher.get("name") or "").lower()
    series = (data.get("series") or "").lower()

    haystack = title + " " + series + " " + product_type + " " + publisher_name

    for indicator in MANGA_INDICATORS["explicit_manga"]:
        if indicator in haystack:
            return "remove", f"manga marker: {indicator}"

    for indicator in MANGA_INDICATORS["explicit_anime"]:
        if indicator in haystack:
            return "remove", f"anime marker: {indicator}"

    for indicator in MANGA_INDICATORS["explicit_ln"]:
        if indicator in haystack:
            return "remove", f"light novel marker: {indicator}"

    for indicator in MANGA_INDICATORS["japanese_publishers"]:
        if indicator in haystack:
            return "remove", f"japanese publisher: {indicator}"

    for indicator in MANGA_INDICATORS["manga_series"]:
        if indicator in haystack:
            return "remove", f"manga series: {indicator}"

    return "keep", "no foreign markers"


def main():
    decisions = load_decisions()
    auto_decisions = {}
    pending = []
    skipped = 0

    files = sorted(PARSED_DIR.glob("*.json"))
    files = [f for f in files if f.name not in ("summary.json", "summary_filtered.json", ".crawled_urls.txt")]

    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception as e:
            print(f"[auto] Skipping invalid JSON: {f.name} ({e})")
            skipped += 1
            continue

        pid = data.get("product_id") or f.stem
        if pid in decisions:
            continue

        decision, reason = analyze_comic(data)
        auto_decisions[pid] = decision
        pending.append({
            "pid": pid,
            "file": f.name,
            "title": data.get("title"),
            "decision": decision,
            "reason": reason,
        })

    print(f"[auto] Skipped {skipped} invalid JSON files")
    print(f"[auto] Pending before auto-filter: {len(pending)}")

    auto_keep = sum(1 for d in auto_decisions.values() if d == "keep")
    auto_remove = sum(1 for d in auto_decisions.values() if d == "remove")
    print(f"[auto] Auto keep: {auto_keep}")
    print(f"[auto] Auto remove: {auto_remove}")

    save_json(OUTPUT_FILE, auto_decisions)
    print(f"[auto] Saved auto decisions to: {OUTPUT_FILE}")

    with open("output/auto_filter_report.txt", "w", encoding="utf-8") as f:
        f.write(f"Auto filter report\n")
        f.write(f"=================\n")
        f.write(f"Total pending: {len(pending)}\n")
        f.write(f"Auto keep: {auto_keep}\n")
        f.write(f"Auto remove: {auto_remove}\n\n")
        f.write("Removed comics:\n")
        for item in pending:
            if item["decision"] == "remove":
                f.write(f"- {item['pid']}: {item['title']} | {item['reason']}\n")

    print("[auto] Report saved to: output/auto_filter_report.txt")


if __name__ == "__main__":
    main()
