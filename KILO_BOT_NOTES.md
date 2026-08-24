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

3. **Database** - Production Supabase ready
   - Project: `kfseqrvwvkjbdyywlobp.supabase.co`
   - 5,321 comics + 1,669 gifts imported
   - Schema synced with Prisma

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

### 🔄 IN PROGRESS
1. **Git sync** - Master repo pushed to GitHub
   - Repo: https://github.com/jaluvvy/comic-platform
   - Setup script for new machines ready

2. **Data cleanup** - 232 items flagged for review
   - 219 manga, 13 light novels
   - Admin page ready for keep/remove decisions

### ⚠️ BLOCKERS / TODO
1. **Supabase DNS** - Some machines can't resolve `db.sxfoyzrqkeoqfuawdalw.supabase.co`
   - Fix: Use production project `kfseqrvwvkjbdyywlobp` instead

2. **Production deploy** - Not yet deployed to Vercel
   - Need: Vercel account, env vars configured
   - See `web/DEPLOY.md`

3. **Manual review** - ~1,700 comics need manual filtering
   - Tool: `python -m src.utils.batch_review`
   - Keep Vietnamese comics, remove manga/LN

4. **Expand publishers** - Only Kim Đồng crawled
   - Next: Hồng Hạc, IPM, AZ Comics

## 🔑 Credentials (DO NOT COMMIT)

### Production Supabase
- URL: `https://kfseqrvwvkjbdyywlobp.supabase.co`
- DB: `postgresql://postgres:@ThanhVy2323@@db.kfseqrvwvkjbdyywlobp.supabase.co:5432/postgres`
- Anon key: In `web/.env.local` (not in git)

### Dev Supabase
- URL: `https://sxfoyzrqkeoqfuawdalw.supabase.co`
- DB: `postgresql://postgres:ThanhVy2323%40@db.sxfoyzrqkeoqfuawdalw.supabase.co:5432/postgres`

## 🛠 Tech Stack
- **Crawler**: Python 3.14, requests, beautifulsoup4, lxml, pydantic, tenacity
- **Web**: Next.js 14, React, TypeScript, Tailwind CSS
- **Database**: Supabase (PostgreSQL)
- **Auth**: Supabase Auth
- **ORM**: Prisma 5.x
- **Hosting**: Vercel (planned)

## 📁 Important Paths
- Project: `G:\My Drive\Work\comic-crawler`
- Web app: `G:\My Drive\Work\comic-crawler\web`
- Scripts: `G:\My Drive\Work\comic-crawler\web\scripts`
- Crawler: `G:\My Drive\Work\comic-crawler\src`
- Output: `G:\My Drive\Work\comic-crawler\output` (gitignored)
- Data: `G:\My Drive\Work\comic-crawler\data` (gitignored)

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
npm run dev          # http://localhost:3001
npm run build        # production build
npm run db:generate  # Prisma client
npm run db:push      # sync schema
```

### Crawler
```bash
python -m src.crawlers.kimdong_v2.py --workers 6 --delay 0.7
python -m src.utils.batch_review
python -m src.utils.filter_comics
python scripts/review_comics.py
```

### Database
```bash
# Export dev
python scripts/export_supabase.py --url "postgresql://postgres:ThanhVy2323%40@db.sxfoyzrqkeoqfuawdalw.supabase.co:5432/postgres" --output supabase_export

# Import prod
python scripts/import_supabase.py --url "postgresql://postgres:%40ThanhVy2323%40@db.kfseqrvwvkjbdyywlobp.supabase.co:5432/postgres" --input supabase_export --clear --force
```

## 📋 Next Steps Priority
1. Deploy to Vercel (see `web/DEPLOY.md`)
2. Manual review of ~1,700 remaining comics
3. Expand to other publishers (Hồng Hạc, IPM, AZ)
4. Add more listing filters (publisher, author, ISBN)
5. Implement favorites/saved searches
6. Add publisher management page
7. Auto-generate Facebook sell templates
8. Mobile app or PWA

## 🤖 For Kilo Bot
When user asks to continue work:
1. Read `web/scripts/PROGRESS_NOTES.md` for detailed state
2. Check `git log --oneline -5` for recent commits
3. Check `git status` for uncommitted work
4. Ask user which module to work on next
5. Always work in `G:\My Drive\Work\comic-crawler\web\` for web code
6. Never commit `.env.local` or `output/` or `data/`
7. Use `git pull` before starting new work on any machine
8. Database is already populated - no need to re-import unless requested
