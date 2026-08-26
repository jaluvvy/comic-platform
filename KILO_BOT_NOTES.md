# ComicPlatform - Kilo Bot Context

## 🎯 Project Goal
Nền tảng thư viện + mua bán truyện tranh Việt Nam.

## 📊 Current State

### ✅ COMPLETED
1. **Crawler v2** - Full Kim Đồng sitemap crawl
   - 5,325/5,326 URLs crawled (99.98%)
   - Output: `output/parsed/*.json` + `output/raw/*.html`
   - Gift extraction cleaned, edition detection working

2. **Web Platform** - Next.js 14 + TypeScript + Tailwind + Supabase + Prisma
   - Build passing (`npm run build`)
   - Code on GitHub: https://github.com/jaluvvy/comic-platform
   - Branch: `master`
   - Schema: Comic (bộ) → Volume (tập) → Gift (quà tặng độc lập) + Event/EventGift
   - Mock data available for local testing: `src/lib/mock-data.ts`

3. **Database** - Production Supabase ready
   - Project: `kfseqrvwvkjbdyywlobp.supabase.co`
   - 5,321 comics + 1,669 gifts imported
   - Schema synced with Prisma
   - Migration + RLS policies ready in `web/prisma/migrations/`

4. **Auth System**
   - Login/Register with email confirmation
   - Forgot/Reset password
   - Middleware protecting routes
   - Header with user state

5. **Selling Module**
   - /listings - browse with filters (title, condition, price)
   - /listings/[id] - detail page
   - /listings/create - create listing (protected)
   - /listings/manage - user's listings (protected)
   - API CRUD for listings

6. **Data Quality Tools**
   - `scripts/review_comics.py` - flags manga/LN (219 manga, 13 LN)
   - `/admin/review-comics` - protected admin review page
   - Batch review, manual filter tools

7. **GitHub Ready**
   - Repo: https://github.com/jaluvvy/comic-platform
   - `.gitignore` configured (`.env.local`, `node_modules`, `.venv`, `output/`, `data/`, `__pycache__/`)
   - Setup script: `scripts/setup_new_machine.py/.bat`
   - Portable Node.js setup: `setup-node-env.ps1`

### 🔄 IN PROGRESS
1. **Manual review** - ~1,700 comics need filtering
    - Tool: `python -m src.utils.batch_review`
    - Viewer: `output/viewer.html`

2. **Database connection** - Supabase connection failing from this machine
    - Production project: `kfseqrvwvkjbdyywlobp.supabase.co`
    - Pooled connection tested: `pooler.kfseqrvwvkjbdyywlobp.supabase.co:6543` resolves but TCP fails
    - Likely cause: firewall / IP restriction on Supabase project
    - Current workaround: web app uses mock data fallback
    - **Deployed to Vercel**: https://web-oi3xq4ax9-jaluvvy.vercel.app
    - Vercel project: jaluvvy/web
    - Envs configured: DATABASE_URL, NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY

### ⚠️ BLOCKERS / TODO
1. **Supabase DNS** - Some machines can't resolve `db.sxfoyzrqkeoqfuawdalw.supabase.co`
    - Fix: Use direct connection string from dashboard or pooled connection
    - Production project ref: `kfseqrvwvkjbdyywlobp`

2. **Production deploy** - Not yet deployed to Vercel
    - Need: Vercel account, env vars configured
    - See `web/DEPLOY.md`

3. **Manual review** - ~1,700 comics need manual filtering
    - Tool: `python -m src.utils.batch_review`
    - Keep Vietnamese comics, remove manga/LN

4. **Expand publishers** - Only Kim Đồng crawled
    - Next: Hồng Hạc, IPM, AZ Comics

5. **Volume extraction from aggregated pages**
    - Some product pages contain multiple volumes in one URL
    - Need to parse `product.variants[]` to create separate Volume entries
    - See `output/raw/sample_aggregated.html` for example

## 🔑 Credentials (DO NOT COMMIT)

### Production Supabase
- URL: `https://kfseqrvwvkjbdyywlobp.supabase.co`
- DB: `postgresql://postgres:[PASSWORD]@db.kfseqrvwvkjbdyywlobp.supabase.co:5432/postgres`
- Anon key: In `web/.env.local` (not in git)

### Dev Supabase
- URL: `https://sxfoyzrqkeoqfuawdalw.supabase.co`
- DB: `postgresql://postgres:[PASSWORD]@db.sxfoyzrqkeoqfuawdalw.supabase.co:5432/postgres`
- Anon key: In `web/.env.local` (not in git)

## 🛠 Tech Stack
- **Crawler**: Python 3.14, requests, beautifulsoup4, lxml, pydantic, tenacity
- **Web**: Next.js 14, React, TypeScript, Tailwind CSS
- **Database**: Supabase (PostgreSQL)
- **Auth**: Supabase Auth
- **ORM**: Prisma 5.x
- **Hosting**: Vercel (planned)

## 📁 Important Paths
- Project: `H:\My Drive\Work\comic-crawler`
- Web app: `H:\My Drive\Work\comic-crawler\web`
- Scripts: `H:\My Drive\Work\comic-crawler\web\scripts`
- Crawler: `H:\My Drive\Work\comic-crawler\src`
- Output: `H:\My Drive\Work\comic-crawler\output` (gitignored)
- Data: `H:\My Drive\Work\comic-crawler\data` (gitignored)

## 🚀 Quick Commands

### Git
```bash
git status
git add .
git commit -m "message"
git push origin master
git pull origin master
```

### Web Dev
```bash
cd web
npm install
npm run dev          # http://localhost:3000
npm run build        # production build
npm run db:generate  # Prisma client
npm run db:push      # sync schema
```

### Crawler
```bash
python src/crawlers/kimdong_v2.py --workers 6 --delay 0.7
python -m src.utils.batch_review
python -m src.utils.filter_comics
python scripts/review_comics.py
```

### Database
```bash
# Export dev
python scripts/export_supabase.py --url "postgresql://postgres:[PASSWORD]@db.sxfoyzrqkeoqfuawdalw.supabase.co:5432/postgres" --output supabase_export

# Import prod
python scripts/import_supabase.py --url "postgresql://postgres:[PASSWORD]@db.kfseqrvwvkjbdyywlobp.supabase.co:5432/postgres" --input supabase_export --clear --force
```

## 📋 Next Steps Priority
1. Fix Supabase connection / deploy to Vercel (see `web/DEPLOY.md`)
2. Manual review of ~1,700 remaining comics
3. Expand to other publishers (Hồng Hạc, IPM, AZ)
4. Add more listing filters (publisher, author, ISBN)
5. Implement favorites/saved searches
6. Add publisher management page
7. Auto-generate Facebook sell templates
8. Mobile app or PWA

## 🆕 Latest Updates (2026-08-26)
- Schema changed: Comic (bộ) → Volume (tập) → Gift (quà tặng độc lập)
- New migration: `20250101000000_add_volume_and_separate_gifts`
- Mock data added: `src/lib/mock-data.ts` for local testing without DB
- Web pages updated: comics, comic detail, listings support new schema
- API routes updated with DB error fallback to mock data
- Build passed with new schema
- Git repo pushed to GitHub: `https://github.com/jaluvvy/comic-platform`
- Production DB populated: 5,321 comics + 1,669 gifts
- Project path updated to `H:\My Drive\Work\comic-crawler`

## 🤖 For Kilo Bot
When user asks to continue work:
1. Read `SESSION_NOTES.md` and `progress_note.md` for detailed state
2. Check `git log --oneline -5` for recent commits
3. Check `git status` for uncommitted work
4. Ask user which module to work on next
5. Always work in `H:\My Drive\Work\comic-crawler\web\` for web code
6. Never commit `.env.local` or `output/` or `data/`
7. Use `git pull` before starting new work on any machine
8. Database is already populated - no need to re-import unless requested
