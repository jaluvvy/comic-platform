# Comic Crawler Project - Session Notes

## Project Info
- **Path**: `H:\My Drive\Work\comic-crawler`
- **Tech**: Python 3.14, requests, beautifulsoup4, lxml, pydantic, tenacity
- **Source**: NXB Kim Dong (`https://nxbkimdong.com.vn/sitemap_products_1.xml`)
- **Filter**: Chỉ giữ sách anime/manga/light novel, loại sách giáo khoa/thiếu nhi
- **Platform Goal**: Nền tảng thư viện + mua bán truyện tranh (Next.js + Supabase + Prisma)

## Current Progress

### Crawler v2 - Full Sitemap Coverage
- **Đã crawl toàn bộ sitemap Kim Đồng**: **5,325 / 5,326 URLs** (99.98%)
- **Crawler file**: `src/crawlers/kimdong_v2.py`
- **Output**: `output/parsed/*.json` (5,325 files) + `output/raw/*.html` (5,325 files)
- **Crawler cũ**: `src/crawlers/kimdong.py` (legacy, chỉ crawl 279 truyện)
- **Parser nâng cao**: `src/parsers/kimdong.py`
- **Speed**: ~6 workers × 0.7s delay ≈ 500 truyện/5 phút

### Data Quality Stats
- Có giá bán: 5,325 (100%)
- Có ISBN: ~5,000+ (94%)
- **Có quà tặng kèm**: **847 truyện** (↑ từ 8)
- **Tổng gift entries**: ~1,669 (sau cleanup HTML)
- **Có thông tin tái bản**: **49 truyện** (↑ từ 0)
- Duplicate URLs trong sitemap: 0

### Gift Extraction (Đã cải thiện)
- **Trước**: Regex linh tinh trên raw HTML → bắt cả HTML fragments (`<a>`, `class=`, `product-transition`...)
- **Sau**: 2 chiến lược có kiểm soát:
  1. **Title/Alt attributes**: Tìm `(Tặng kèm X)` trong `title` của `<a>` và `alt` của `<img>`
  2. **Page text fallback**: Regex trên text đã strip HTML
- **Cleanup script**: `clean_gifts3.py` - loại bỏ HTML entities, false positives
- **Kết quả**: 0 HTML fragments còn sót lại trong gift names

### Edition Detection
- Detect "Tái bản" + năm từ title/description/HTML
- Kết quả: 49 truyện có `edition_type: "tai_ban"`
- Ví dụ: Ghost Hunt 4 (2026), Đi tìm xứ Tu-Bo (2015), Dế Mèn phiêu lưu kí (2026)

### FES Gifts System
- **Goal**: Thu thập quà tặng FES từ fanpage Kim Đồng (fan meeting, hội sách, sự kiện)
- **Crawler**: `src/crawlers/fes.py` - crawl blog Kim Đồng (`/blogs/tin-tuc`) để tìm bài viết về sự kiện
- **Importer**: `src/utils/import_fes_gifts.py` - quản lý quà FES, import/export JSON
- **Data**: `data/fes_gifts.json` - nhập thủ công từ fanpage (Facebook scraping cần Graph API)
- **Schema**: Gift model trong Prisma đã sẵn sàng (`isFes`, `fesEvent`, `Event`, `EventGift`)
- Product pages đã extract được gift info (tên quà, hình ảnh)

### Web Platform (Next.js + TypeScript + Tailwind + Supabase + Prisma)
- Đã setup project trong `web/`
- **Schema**: Publisher, Comic, Gift, Event, EventGift, User, Listing
- **Pages**: Home (`/`), Comics (`/comics`), Comic detail (`/comics/[id]`)
- **API**: `/api/comics`, `/api/comics/[id]`
- **Components**: Header, ComicCard, ComicGrid, SearchBar
- **Seed script**: `web/scripts/seed.ts` - import comics + gifts từ parsed JSON
- **Build**: Đã build thành công (`npm run build` passed)
- **Node.js**: Đã cài portable Node.js 22 LTS tại `C:\Users\Nam.le\AppData\Local\Temp\kilo\nodejs\node-v22.15.0-win-x64`
- **Setup script**: `setup-node-env.ps1` - setup Node.js PATH + execution policy
- **Env**: `.env.local` đã cấu hình Supabase credentials

### Supabase Setup Status
- **Migration**: `web/prisma/migrations/20240101000000_init/migration.sql` - schema 7 tables + indexes + FKs
- **RLS**: `web/prisma/migrations/20240101000000_init/rls_policies.sql` - public read, admin write, users manage own
- **Credentials đã có**:
  - DATABASE_URL: `postgresql://postgres:ThanhVy2323%40@db.sxfoyzrqkeoqfuawdalw.supabase.co:5432/postgres`
  - NEXT_PUBLIC_SUPABASE_URL: `https://sxfoyzrqkeoqfuawdalw.supabase.co`
  - NEXT_PUBLIC_SUPABASE_ANON_KEY: `sb_publishable_ZUIOLrpmyQSph4F2SYLJfg_uMRAjKjV`
- **BLOCKER**: DNS resolve failed cho `db.sxfoyzrqkeoqfuawdalw.supabase.co` → không connect được database
- **Cần làm**: Kiểm tra lại project Supabase có đang active không, copy connection string mới từ dashboard

### Commands
```bash
cd "H:\My Drive\Work\comic-crawler"

# Crawl products (legacy)
python -m src.crawlers.kimdong --delay 1.5

# Crawl products v2 (full sitemap)
python src/crawlers/kimdong_v2.py --workers 6 --delay 0.7

# Filter anime-related comics (auto)
python -m src.utils.filter_comics

# View comics HTML
python view_comics.py

# Manual filter (review each comic)
python -m src.utils.manual_filter --review
python -m src.utils.manual_filter --apply
python -m src.utils.manual_filter --status

# Batch review (10 comics/lần)
python -m src.utils.batch_review

# Crawl FES/events from blog
python -m src.crawlers.fes --pages 5 --analyze

# Manage FES gifts
python -m src.utils.import_fes_gifts --list
python -m src.utils.import_fes_gifts --add
python -m src.utils.import_fes_gifts --export

# Web platform
cd web
npm install
npm run build
npm run dev
```

## Manual Filter Workflow
1. `python -m src.utils.manual_filter --review` → duyệt từng truyện, đánh dấu `k` (keep) / `r` (remove) / `s` (skip)
2. `python -m src.utils.manual_filter --status` → xem tiến độ
3. `python -m src.utils.manual_filter --apply` → xóa các truyện đã đánh dấu `remove`
4. `python -m src.utils.manual_filter --reset` → xóa tất cả decisions nếu muốn làm lại

### Batch Review Tool
- **Tool mới**: `src/utils/batch_review.py` - review 10 comics/lần, nhanh hơn manual_filter cũ
- **Commands**: `[k]eep`, `[r]emove`, `[s]kip`, `[n]ext` (skip trong batch), `[q]uit`
- **Chạy**: `python -m src.utils.batch_review`

### Auto Prefilter Status
- **Đã chạy auto-prefilter** với logic từ `filter_comics.py` (giữ anime/manga/light novel, loại giáo khoa/thiếu nhi)
- **Kết quả**: 1,772 truyện giữ lại, 1,952 truyện bị loại
- **Còn lại trong `output/parsed/`**: 1,772 files
- **Manual review còn lại**: ~1,700 truyện cần duyệt thủ công
- **Viewer file**: `output/viewer.html` - mở bằng browser để xem tất cả truyện còn lại
- **Stats remaining set**:
  - Có giá bán: 100%
  - Có quà tặng: 28% (507)
  - Có edition info: 84% (1,493)
  - Có ISBN: 62% (1,112)

## Next Steps
1. **Manual filter ~1,700 truyện còn lại** bằng `python -m src.utils.batch_review`
2. **Fix Supabase DNS** → kiểm tra project active → copy connection string mới từ dashboard
3. **Chạy migrate**: `cd web && npx prisma migrate dev`
4. **Seed comics**: `cd web && npm run db:seed`
5. **Chạy web dev server**: `cd web && npm run dev`
6. **Crawl thêm NXB khác** (Hồng Hạc, IPM, AZ Comics...)
7. **Deploy lên Vercel** + connect Supabase

## Known Issues
- Publisher field đã fix (fallback cố định)
- Authors split đã fix
- Gift extraction đã cải thiện (HTML cleanup)
- Facebook fanpage scraping cần Graph API access token (chưa implement)
- Một số URL trong sitemap có thể 404 (đã skip)
- Gift extraction vẫn có thể bỏ sót một số trường hợp phức tạp
- Supabase DNS resolve failed → cần kiểm tra lại project/credentials
- node_modules không sync về Drive (phải chạy npm install lại khi cần)
