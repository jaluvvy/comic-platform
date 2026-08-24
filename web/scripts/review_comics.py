import sys
import psycopg2
import json
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

conn = psycopg2.connect("postgresql://postgres:ThanhVy2323%40@db.sxfoyzrqkeoqfuawdalw.supabase.co:5432/postgres")
cur = conn.cursor()

# Get all comics with publisher info
cur.execute("""
    SELECT c.id, c.title, c.slug, c.authors, c.product_type, p.name as publisher_name, p.type as publisher_type
    FROM comics c
    LEFT JOIN publishers p ON c.publisher_id = p.id
    ORDER BY c.title
""")
rows = cur.fetchall()

# More specific manga/anime indicators
MangaIndicators = {
    'explicit_manga': ['(manga)', '(truyện tranh nhật bản)', 'truyện tranh nhật'],
    'explicit_anime': ['(anime)', '(hoạt hình nhật bản)', 'hoạt hình nhật'],
    'explicit_ln': ['(light novel)', '(light-novel)', '(ln)'],
    'japanese_publishers': [
        'nhà xuất bản kang', 'nxb kang', 'nhà xuất bản izan', 'nxb izan',
        'nhà xuất bản sao', 'nxb sao', 'nhà xuất bản horizon', 'nxb horizon',
    ],
    'manga_series': [
        'naruto', 'one piece', 'dragon ball', 'bleach', 'death note',
        'attack on titan', 'shingeki no kyojin', 'tokyo ghoul',
        'demon slayer', 'kimetsu no yaiba', 'jujutsu kaisen',
        'jojo', 'fairy tail', 'hunter x hunter',
        'my hero academia', 'boku no hero', 'mha',
        'sword art online', 'sao', 'overlord',
        're:zero', 'konosuba',
        'fullmetal alchemist', 'fma',
        'cowboy bebop', 'evangelion',
        'spy x family', 'chainsaw man',
        'hells paradise', 'world trigger',
        'dr. stone', 'toradora',
        'ao ashi', '21emon',
        'cậu ma nhà xí hanako', 'cau ma nha xi hanako',
        'astro boy', 'cậu bé tay sắt',
        'bảng xếp hạng quân vương',
        'arya bàn bên',
    ]
}

def analyze_comic(title, authors, product_type, publisher_name):
    title_lower = (title or '').lower()
    authors_lower = ' '.join(authors or []).lower()
    product_lower = (product_type or '').lower()
    publisher_lower = (publisher_name or '').lower()
    
    is_manga = False
    reasons = []
    category = 'vietnamese'
    
    # Check explicit markers in title
    for indicator in MangaIndicators['explicit_manga']:
        if indicator in title_lower:
            is_manga = True
            reasons.append(f"title: '{indicator}'")
            category = 'manga'
            break
    
    if not is_manga:
        for indicator in MangaIndicators['explicit_anime']:
            if indicator in title_lower:
                is_manga = True
                reasons.append(f"title: '{indicator}'")
                category = 'anime'
                break
    
    if not is_manga:
        for indicator in MangaIndicators['explicit_ln']:
            if indicator in title_lower:
                is_manga = True
                reasons.append(f"title: '{indicator}'")
                category = 'light_novel'
                break
    
    # Check product_type field
    if not is_manga and product_type:
        if 'manga' in product_lower:
            is_manga = True
            reasons.append(f"product_type: '{product_type}'")
            category = 'manga'
        elif 'anime' in product_lower:
            is_manga = True
            reasons.append(f"product_type: '{product_type}'")
            category = 'anime'
    
    # Check Japanese publishers
    if not is_manga:
        for pub in MangaIndicators['japanese_publishers']:
            if pub in publisher_lower:
                is_manga = True
                reasons.append(f"publisher: '{publisher_name}'")
                category = 'manga'
                break
    
    # Check manga series names
    if not is_manga:
        for series in MangaIndicators['manga_series']:
            if series in title_lower:
                is_manga = True
                reasons.append(f"series: '{series}'")
                category = 'manga'
                break
    
    return {
        'is_manga': is_manga,
        'category': category,
        'reasons': reasons
    }

manga_count = 0
vietnamese_count = 0
light_novel_count = 0
anime_count = 0

manga_comics = []
vietnamese_comics = []
light_novel_comics = []
anime_comics = []

for row in rows:
    comic_id, title, slug, authors, product_type, publisher_name, publisher_type = row
    
    result = analyze_comic(title, authors, product_type, publisher_name)
    
    if result['is_manga']:
        if result['category'] == 'manga':
            manga_count += 1
            manga_comics.append({
                'id': comic_id,
                'title': title,
                'publisher': publisher_name,
                'reasons': result['reasons']
            })
        elif result['category'] == 'anime':
            anime_count += 1
            anime_comics.append({
                'id': comic_id,
                'title': title,
                'publisher': publisher_name,
                'reasons': result['reasons']
            })
        elif result['category'] == 'light_novel':
            light_novel_count += 1
            light_novel_comics.append({
                'id': comic_id,
                'title': title,
                'publisher': publisher_name,
                'reasons': result['reasons']
            })
    else:
        vietnamese_count += 1
        vietnamese_comics.append({
            'id': comic_id,
            'title': title,
            'publisher': publisher_name
        })

print(f"Total comics: {len(rows)}")
print(f"Vietnamese comics: {vietnamese_count}")
print(f"Manga: {manga_count}")
print(f"Anime: {anime_count}")
print(f"Light novels: {light_novel_count}")
print()

# Show some manga candidates
print("=== MANGA CANDIDATES (first 20) ===")
for comic in manga_comics[:20]:
    print(f"  - {comic['title']} | {comic['publisher']} | {', '.join(comic['reasons'])}")

print()
print("=== LIGHT NOVEL CANDIDATES (first 10) ===")
for comic in light_novel_comics[:10]:
    print(f"  - {comic['title']} | {comic['publisher']} | {', '.join(comic['reasons'])}")

print()
print("=== VIETNAMESE COMICS (first 10) ===")
for comic in vietnamese_comics[:10]:
    print(f"  - {comic['title']} | {comic['publisher']}")

# Save results
with open('G:/My Drive/Work/comic-crawler/web/scripts/comics_review.json', 'w', encoding='utf-8') as f:
    json.dump({
        'summary': {
            'total': len(rows),
            'vietnamese': vietnamese_count,
            'manga': manga_count,
            'anime': anime_count,
            'light_novel': light_novel_count
        },
        'vietnamese_comics': vietnamese_comics,
        'manga_comics': manga_comics,
        'anime_comics': anime_comics,
        'light_novel_comics': light_novel_comics
    }, f, ensure_ascii=False, indent=2)

print()
print("Results saved to comics_review.json")

cur.close()
conn.close()
