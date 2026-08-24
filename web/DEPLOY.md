# Deploy ComicPlatform to Production

## Prerequisites
- [Vercel](https://vercel.com) account
- [Supabase](https://supabase.com) account
- [GitHub](https://github.com) repository

## Step 1: Prepare Supabase Production

1. Create a new Supabase project (production)
2. Go to **Project Settings → Database**
3. Copy the **Connection string** (URI format)
4. Run migrations to sync schema:

```bash
cd web
npm run db:push
```

5. Go to **Authentication → Providers**
   - Enable Email provider
   - Disable "Confirm email" for production (or keep enabled for security)
   - Configure email templates

6. Copy the following from **Project Settings → API**:
   - `Project URL` → `NEXT_PUBLIC_SUPABASE_URL`
   - `anon/public` key → `NEXT_PUBLIC_SUPABASE_ANON_KEY`

## Step 2: Deploy to Vercel

### Option A: Deploy via Vercel Dashboard
1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repository
3. Configure environment variables:
   - `NEXT_PUBLIC_APP_URL`: your production URL
   - `DATABASE_URL`: Supabase connection string
   - `NEXT_PUBLIC_SUPABASE_URL`: Supabase project URL
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Supabase anon key
4. Click **Deploy**

### Option B: Deploy via Vercel CLI
```bash
npm i -g vercel
vercel login
vercel --prod
```

## Step 3: Configure Domain (Optional)
1. In Vercel Dashboard → Your Project → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed

## Step 4: Post-Deployment

### Verify Deployment
```bash
# Check homepage
curl https://your-domain.vercel.app/

# Check API
curl https://your-domain.vercel.app/api/comics?limit=1
```

### Create Admin User
1. Register a user via `/register`
2. In Supabase Dashboard → Authentication → Users
3. Copy the user ID
4. Update middleware or create admin check

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
