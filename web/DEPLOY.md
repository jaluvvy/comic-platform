# Deploy ComicPlatform to Production

## Prerequisites
- [Vercel](https://vercel.com) account
- [Supabase](https://supabase.com) account
- [GitHub](https://github.com) repository

## Step 1: Prepare Supabase Production

### Option A: New Project (Recommended)
1. Create a new Supabase project (production)
2. Go to **Project Settings → Database**
3. Copy the **Connection string** (URI format)

### Option B: Use Existing Project
1. Go to **Project Settings → Database**
2. Copy the **Connection string**
3. Backup current data first:
   ```bash
   python scripts/export_supabase.py --url "postgresql://..." --output backup_before_deploy
   ```

### Sync Schema
```bash
cd web
npm run db:push
```

### Configure Auth
1. Go to **Authentication → Providers → Email**
2. Configure email settings:
   - Enable "Confirm email" for security
   - Set up email templates
   - Add redirect URLs (your production domain)

### Copy Credentials
From **Project Settings → API**:
- `Project URL` → `NEXT_PUBLIC_SUPABASE_URL`
- `anon/public` key → `NEXT_PUBLIC_SUPABASE_ANON_KEY`

## Step 2: Export/Import Data (if using new project)

### Export from Dev
```bash
python scripts/export_supabase.py \
  --url "postgresql://postgres:ThanhVy2323%40@db.sxfoyzrqkeoqfuawdalw.supabase.co:5432/postgres" \
  --output supabase_export
```

### Import to Production
```bash
python scripts/import_supabase.py \
  --url "postgresql://postgres:[PASSWORD]@[NEW-PROJECT-REF].supabase.co:5432/postgres" \
  --input supabase_export \
  --clear
```

### Verify Import
```bash
python scripts/export_supabase.py \
  --url "postgresql://postgres:[PASSWORD]@[NEW-PROJECT-REF].supabase.co:5432/postgres" \
  --output supabase_verify
```

## Step 3: Deploy to Vercel

### Option A: Deploy via Vercel Dashboard
1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repository
3. Configure environment variables:
   - `NEXT_PUBLIC_APP_URL`: `https://your-domain.vercel.app`
   - `DATABASE_URL`: Production Supabase connection string
   - `NEXT_PUBLIC_SUPABASE_URL`: Production Supabase URL
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Production Supabase anon key
4. Click **Deploy**

### Option B: Deploy via Vercel CLI
```bash
npm i -g vercel
vercel login
vercel --prod
```

## Step 4: Configure Domain (Optional)
1. In Vercel Dashboard → Your Project → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. Update `NEXT_PUBLIC_APP_URL` environment variable

## Step 5: Post-Deployment

### Verify Deployment
```bash
# Check homepage
curl https://your-domain.vercel.app/

# Check API
curl https://your-domain.vercel.app/api/comics?limit=1
```

### Create First User
1. Visit `/register` on your production site
2. Create an account
3. Verify in Supabase Dashboard → Authentication → Users

### Set up Monitoring
- Enable Vercel Analytics
- Set up error tracking (Sentry, LogRocket, etc.)

## Environment Variables Summary

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_APP_URL` | Production URL | Yes |
| `DATABASE_URL` | Supabase PostgreSQL URL | Yes |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | Yes |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key | Yes |

## Troubleshooting

### Build Fails
- Check Vercel build logs
- Ensure all environment variables are set
- Run `npm run build` locally first

### Database Connection Issues
- Verify `DATABASE_URL` is correct
- Check Supabase project is not paused
- Ensure IP allowlist includes Vercel

### Auth Not Working
- Verify Supabase URL and anon key
- Check email templates are configured
- Ensure redirect URLs are set in Supabase

### Data Not Showing
- Verify import completed successfully
- Check `supabase_export/import_summary.json`
- Verify database connection in Vercel logs

## Useful Commands

```bash
# Export dev database
python scripts/export_supabase.py --url "postgresql://..." --output supabase_export

# Import to production
python scripts/import_supabase.py --url "postgresql://..." --input supabase_export --clear

# Run Prisma migrations
npm run db:push

# Build locally
npm run build

# Deploy to Vercel
vercel --prod
```

## Checklist

- [ ] Create/configure Supabase production project
- [ ] Export data from dev database
- [ ] Import data to production database
- [ ] Verify data import success
- [ ] Set up Vercel project
- [ ] Configure environment variables
- [ ] Deploy to Vercel
- [ ] Configure custom domain (optional)
- [ ] Test production deployment
- [ ] Create first admin user
- [ ] Set up monitoring
- [ ] Configure email templates in Supabase
