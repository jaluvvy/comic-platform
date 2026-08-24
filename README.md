# Comic Crawler & Platform

Dự án gồm 2 phần:
1. **Crawler** (Python): Thu thập dữ liệu truyện từ NXB Kim Đồng
2. **Web Platform** (Next.js): Nền tảng thư viện, mua bán truyện tranh

## Phần 1: Crawler (Python)

### Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Usage

```bash
python src/crawlers/kimdong_v2.py --workers 6 --delay 0.7
```

Output:
- `output/raw/` - saved HTML / sitemap XML
- `output/parsed/` - parsed JSON per product + `summary.json`

### Notes

- Respect `robots.txt` and rate-limit with `--delay`.
- Sitemap URL: https://nxbkimdong.com.vn/sitemap_products_1.xml
- Dataset: 5,325/5,326 URLs crawled (99.98%)

## Phần 2: Web Platform (Next.js)

Xem hướng dẫn chi tiết tại [web/README.md](web/README.md).

### Quick Start

```bash
cd web
npm install
npm run dev
```

### Tech Stack

- Next.js 14 + TypeScript + Tailwind CSS
- PostgreSQL (Supabase) + Prisma ORM
- 1,772 comics Kim Đồng đã có sẵn, import qua `npm run db:seed`

## Roadmap

- [x] Phase 1: Foundation (Library, Database, Basic UI)
- [ ] Phase 2: Enhanced Crawler + Selling Module
- [ ] Phase 3: Buying Module + Polish
- [ ] Phase 4: Multi-publisher support + App

## License

Dự án cá nhân, không phân phối thương mại.
