import json, glob, os
from pathlib import Path

PARSED_DIR = Path("output/parsed")
files = sorted(glob.glob(str(PARSED_DIR / "*.json")))
files = [f for f in files if "summary" not in f]

comics = []
for f in files:
    with open(f, "r", encoding="utf-8") as fh:
        try:
            comics.append(json.load(fh))
        except Exception:
            pass

html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Comic Crawler - NXB Kim Dong</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
h1 {{ color: #333; }}
.info {{ background: #fff; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; }}
.card {{ background: #fff; border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
.card img {{ max-width: 100%; height: 180px; object-fit: contain; background: #f0f0f0; border-radius: 4px; }}
.card h3 {{ font-size: 14px; margin: 10px 0 5px; color: #222; }}
.card p {{ font-size: 12px; color: #666; margin: 3px 0; }}
.price {{ color: #e74c3c; font-weight: bold; font-size: 14px; }}
</style>
</head>
<body>
<h1>Comic Crawler - NXB Kim Dong</h1>
<div class="info">
<p><strong>Tong san pham:</strong> {total}</p>
<p><strong>Xuat ban:</strong> {crawled_at}</p>
</div>
<div class="grid">
""".format(total=len(comics), crawled_at=comics[0].get("crawled_at", "") if comics else "")

for c in comics:
    img = c.get("cover_image") or ""
    title = c.get("title") or "Khong co tieu de"
    price = c.get("price")
    price_str = f"{price:,} d" if price else "Lien he"
    authors = c.get("authors") or []
    author_str = ", ".join(authors) if authors else "N/A"
    series = c.get("series") or ""
    url = c.get("url") or "#"
    pages = c.get("pages") or ""
    format_ = c.get("format") or ""
    
    html += f"""
    <div class="card">
        <a href="{url}" target="_blank">
            <img src="{img}" onerror="this.src='https://via.placeholder.com/200x180?text=No+Image'" alt="{title}">
        </a>
        <h3><a href="{url}" target="_blank">{title}</a></h3>
        <p class="price">{price_str}</p>
        <p><strong>Tac gia:</strong> {author_str}</p>
        {f'<p><strong>Bo:</strong> {series}</p>' if series else ''}
        {f'<p><strong>Trang:</strong> {pages} | {format_}</p>' if pages else ''}
    </div>
    """

html += """
</div>
</body>
</html>
"""

out_path = Path("output/viewer.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Da tao viewer: {out_path}")
print(f"Mo file: {out_path.absolute()}")
