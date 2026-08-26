# Comic Crawler - Progress Note

## Tổng quan
- Nguồn: NXB Kim Đồng (`https://nxbkimdong.com.vn/sitemap_products_1.xml`)
- Mục tiêu: Nền tảng thư viện + mua bán truyện tranh (Next.js + Supabase + Prisma)
- Trạng thái hiện tại: Đã crawl xong dataset Kim Đồng, đang chuẩn bị seed lên Supabase

## Tiến độ chính
1. **Crawler v2** - Đã crawl toàn bộ sitemap Kim Đồng: **5,325 / 5,326 URLs** (99.98%)
   - Output: `output/parsed/*.json` + `output/raw/*.html`
   - Parser: `src/parsers/kimdong.py`
   - Speed: ~6 workers × 0.7s delay

2. **Data Quality**
   - Có giá bán: 100%
   - Có ISBN: ~94%
   - Có quà tặng kèm: 847 truyện / ~1,669 gift entries
   - Có thông tin tái bản: 49 truyện
   - Gift extraction đã cleanup HTML, không còn HTML fragments

3. **Auto Prefilter**
   - Đã chạy auto-prefilter: giữ **1,772** truyện, loại **1,952** truyện
   - Còn ~1,700 truyện cần manual review bằng `batch_review.py`
   - Viewer file: `output/viewer.html`

4. **Web Platform**
   - Next.js 14 + TypeScript + Tailwind + Prisma + Supabase
   - Build đã thành công (`npm run build` passed)
   - Node.js 22 LTS portable đã cài
   - `.env.local` đã cấu hình Supabase credentials
   - Migration SQL + RLS policies đã tạo sẵn trong `web/prisma/migrations/`
   - Seed script đã update: `web/scripts/seed.ts`
   - Đã thêm `error.tsx` + `loading.tsx` + `dynamic = 'force-dynamic'` cho DB pages
   - Đã push lên GitHub: `https://github.com/jaluvvy/comic-platform`
   - **New schema**: Comic (bộ) → Volume (tập) → Gift (quà tặng độc lập) + Event/EventGift
   - **Mock data**: `src/lib/mock-data.ts` cho testing local khi không có DB

5. **Supabase / Vercel**
   - Project: `kfseqrvwvkjbdyywlobp.supabase.co`
   - Pooled connection tested: `pooler.kfseqrvwvkjbdyywlobp.supabase.co:6543`
   - **Local**: TCP connect fails from this machine (firewall/IP restriction likely)
   - **Vercel**: Deployed successfully to `https://comic-platform-ch9idp10x-jaluvvy.vercel.app`
   - Envs: DATABASE_URL, NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY
   - Workaround: web app has mock data fallback if DB unreachable

## Công cụ đã tạo
- `src/utils/batch_review.py` - review 10 comics/lần
- `src/utils/manual_filter.py` - review từng truyện
- `src/utils/filter_comics.py` - auto prefilter
- `view_comics.py` - HTML viewer
- `web/test-connect.js` - test Prisma connection
- `setup-node-env.ps1` - setup Node.js PATH
- `web/prisma/migrations/20240101000000_init/migration.sql`
- `web/prisma/migrations/20240101000000_init/rls_policies.sql`

## Next Steps
1. Kiểm tra lại Supabase project active + lấy connection string mới từ dashboard
2. Chạy `npx prisma migrate dev`
3. Seed comics: `npm run db:seed`
4. Manual filter ~1,700 truyện còn lại
5. Deploy lên Vercel

## Blockers
- Supabase DNS resolve failed → cần connection string mới từ dashboard

## Cập nhật lần cuối
- Thời gian: 2026-08-25 15:36 ICT
- Người cập nhật: Kilo

## Latest Updates (2026-08-25)
- **New schema**: Comic (bộ) → Volume (tập) → Gift (quà tặng độc lập) + Event/EventGift
  - `Comic`: bộ truyện chung
  - `Volume`: từng tập riêng (Tập 01, Tập 02...)
  - `Gift`: quà tặng độc lập, có thể gắn vào `volumeId` (quà combo) hoặc `eventId` (quà FES/fan meeting)
  - `Listing`: có thể bán `comic`, `volume`, `gift`, hoặc `combo`
- **Migration**: `web/prisma/migrations/20250101000000_add_volume_and_separate_gifts/`
- **Mock data**: `src/lib/mock-data.ts` cho testing local khi không có DB
- **API updates**: 
  - `/api/comics` - support fallback to mock data
  - `/api/comics/[id]` - include volumes + gifts + eventGifts
  - `/api/listings` - support listing type filter, include volume/gift relations
- **UI updates**:
  - Comic detail page hiển thị volumes grid + event gifts section
  - Listings page support filtering by type (comic/volume/gift/event)
  - ComicCard hiển thị số tập + số quà
- **Build**: Passed với schema mới
- **Git**: Đã push lên `https://github.com/jaluvvy/comic-platform` (branch `master`)
