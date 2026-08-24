import re
import json
import sys
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

PARSED_DIR = Path("output/parsed")

ANIME_KEYWORDS = re.compile(
    r"\b(manga|comic|anime|manhwa|manhua|light novel|webtoon|truyện tranh|truyện chữ|novel|"
    r"truyện tranh màu|hoạt hình|truyện dài|truyện ngắn|truyện)\b",
    re.IGNORECASE,
)

EXCLUDE_KEYWORDS = re.compile(
    r"\b(giáo dục|đố vui|khoa học|kiến thức|thiếu nhi|nhi đồng|mẫu giáo|tiểu học|"
    r"bé thông minh|bé ham hỏi|cổ tích|danh nhân|lịch sử|sử lược|"
    r"từ điển|hình ảnh|số đếm|quốc phòng|cảm xúc|tâm lý|kỹ năng|"
    r"kinh doanh|tiếng anh|tiếng nhật|ngoại ngữ|học ngoại ngữ|"
    r"sức khỏe|mang thai|sinh nở|nữ công|gia chánh|"
    r"tản văn|tiểu thuyết|thơ|truyện ngắn|văn học|"
    r"nhà trẻ|mẹ hỏi|bé trả lời|cẩm nang|"
    r"500 câu|câu đố|quiz|"
    r"lịch sử việt nam|danh nhân thế giới|who\?|"
    r"chuyện kể|truyện cổ|truyện cũ|truyện dân gian|"
    r"sách thiếu nhi|sách cho bé|sách mầm non)\b",
    re.IGNORECASE,
)

SERIES_ANIME_HINTS = re.compile(
    r"\b(doraemon|conan|one piece|black clover|naruto|bleach|"
    r"dragon ball|sailor moon|inuyasha|shin cậu bé bút chì|"
    r"pokemon|thám tử|lupin|detective|mickey|disney|"
    r"kính vạn hoa|thần đồng đất việt|trạng quỷnh|"
    r"nhóc miko|kill blue|wistoria|jojo|frieren|"
    r"chúa tể bóng tối|trở về chương|light novel|"
    r"orange|thế giới xe|thế giới|xung kích|freud|"
    r"bảy chú ếch|bé khỏe|càng chơi|tuổi thần tiên|"
    r"ren nhân cách|luyện tài năng|bác hồ|"
    r"vòng quanh thế giới|who\?|chuyện kể|"
    r"tuyển tập|kiệt tác|fujiko|artbook|art book|"
    r"movie story|hoạt hình màu|tuyển tập tranh|"
    r"boxset|combo|tập lẻ|tuyệt đỉnh|đỉnh cao)\b",
    re.IGNORECASE,
)


def is_anime_related(comic: dict) -> bool:
    title = comic.get("title", "") or ""
    series = comic.get("series", "") or ""
    desc = comic.get("description", "") or ""
    product_type = comic.get("product_type", "") or ""
    target = comic.get("target_audience", "") or ""
    text = f"{title} {series} {desc} {product_type} {target}"

    if SERIES_ANIME_HINTS.search(text):
        return True

    if ANIME_KEYWORDS.search(text):
        if not EXCLUDE_KEYWORDS.search(text):
            return True
        return False

    return False


def main():
    files = list(PARSED_DIR.glob("*.json"))
    files = [f for f in files if f.name not in ("summary.json", "summary_filtered.json")]

    kept = []
    removed = []

    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            comic = json.load(f)

        if is_anime_related(comic):
            kept.append(comic)
        else:
            removed.append(comic)
            path.unlink()

    summary_path = PARSED_DIR / "summary_filtered.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "total": len(kept),
                "removed": len(removed),
                "items": kept,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"[filter] Kept: {len(kept)}, Removed: {len(removed)}")
    if removed:
        print("[filter] Sample removed:")
        for c in removed[:10]:
            title = c.get("title", "")
            safe = title.encode("utf-8", errors="replace").decode("utf-8", errors="replace")
            print(f"  - {safe}")


if __name__ == "__main__":
    main()
