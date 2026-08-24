# ComicPlatform - Progress Notes

## Last Updated: 2026-08-24

## ✅ Completed

### Auth System
- Login page with email confirmation UI + resend button
- Register page with confirmation message
- Verify email callback page (/verify-email)
- Forgot password + Reset password pages
- Middleware protecting /listings/create, /listings/manage, /profile, /admin
- API routes: /api/auth/login, /api/auth/register, /api/auth/logout, /api/auth/me
- Header with user info when logged in

### Selling Module (Listings CRUD)
- /listings - List page with search/filter UI (condition, price range, title)
- /listings/[id] - Detail page with comic info, price, edition, gifts
- /listings/create - Create listing form (protected)
- /listings/manage - Manage listings table (protected)
- API: GET /api/listings, POST /api/listings
- API: GET /api/listings/[id], DELETE /api/listings/[id], PATCH /api/listings/[id]

### Database & Schema
- Prisma schema with all @map mappings fixed
- Schema synced to both dev and production Supabase
- Production DB: kfseqrvwvkjbdyywlobp.supabase.co
- Dev DB: sxfoyzrqkeoqfuawdalw.supabase.co

### Data Quality
- Script: scripts/review_comics.py
- Output: scripts/comics_review.json
- Results: 5089 Vietnamese comics, 219 manga, 13 light novels
- Admin review page: /admin/review-comics (protected)
- API: /api/admin/review-comics

### Deployment Prep
- vercel.json configured
- next.config.js with production optimizations
- .env.example template
- DEPLOY.md with full instructions
- scripts/deploy.sh, deploy.ps1
- scripts/production_schema.sql
- scripts/export_supabase.py - working
- scripts/import_supabase.py - working with batch insert
- scripts/setup_new_machine.py/.bat

### Exported Data
- supabase_export/ folder with all tables
- publishers.json: 1 row
- comics.json: 5,321 rows
- gifts.json: 1,669 rows
- users.json: 1 row

## 🔄 In Progress / Pending

### Git/GitHub Setup
- Git repo initialized locally but commit failed due to geometric repack error
- Need to: git config --global pack.threads 1, then retry
- Need to create GitHub repo and push

### Production Deployment
- Production Supabase project created: kfseqrvwvkjbdyywlobp
- Data imported successfully (5321 comics, 1669 gifts, 1 publisher)
- Need to:
  1. Get Supabase anon/public key from Project Settings → API
  2. Configure Auth redirect URLs
  3. Deploy to Vercel
  4. Set environment variables in Vercel
  5. Test production

### Buying Module Enhancements
- Search/filter UI added to /listings
- API supports q, condition, minPrice, maxPrice filters
- Could add: pagination UI, sort by price/date, save favorites

### Data Quality Review
- 232 items flagged for review (219 manga + 13 light novels)
- Admin page ready but needs auth check improvement
- Need to actually review and delete/keep items

## 📋 Next Steps Priority

1. **Fix Git commit and push to GitHub**
2. **Get Supabase credentials and deploy to Vercel**
3. **Test production deployment**
4. **Review flagged manga/light novels and clean data**
5. **Add more publishers (NXB Hồng Hạc, IPM, AZ Comics)**

## 🔑 Key Credentials (DO NOT COMMIT)

### Dev Supabase
- URL: https://sxfoyzrqkeoqfuawdalw.supabase.co
- Project: sxfoyzrqkeoqfuawdalw

### Production Supabase
- URL: https://kfseqrvwvkjbdyywlobp.supabase.co
- Project: kfseqrvwvkjbdyywlobp
- DB Password: @ThanhVy2323@

## 📁 Important Paths

- Project root: G:\My Drive\Work\comic-crawler
- Web app: G:\My Drive\Work\comic-crawler\web
- Exports: G:\My Drive\Work\comic-crawler\web\supabase_export
- Scripts: G:\My Drive\Work\comic-crawler\web\scripts

## 🚀 Quick Commands

```bash
# Start dev server
cd "G:\My Drive\Work\comic-crawler\web"
npm run dev

# Export dev DB
python scripts/export_supabase.py --url "postgresql://postgres:ThanhVy2323%40@db.sxfoyzrqkeoqfuawdalw.supabase.co:5432/postgres" --output supabase_export

# Import to production
python scripts/import_supabase.py --url "postgresql://postgres:%40ThanhVy2323%40@db.kfseqrvwvkjbdyywlobp.supabase.co:5432/postgres" --input supabase_export --clear --force

# Review comics
python scripts/review_comics.py
```
