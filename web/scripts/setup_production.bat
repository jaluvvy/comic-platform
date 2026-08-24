@echo off
chcp 65001 >nul
echo ============================================
echo ComicPlatform Production Setup
echo ============================================
echo.

echo Step 1: Supabase Project Setup
echo --------------------------------------------
echo 1. Go to https://supabase.com/dashboard
echo 2. Create a new project:
echo    - Name: comic-platform-prod
echo    - Password: [choose a strong password]
echo    - Region: [choose closest to your users]
echo 3. Wait for project to be ready (1-2 minutes)
echo.

echo Step 2: Get Production Connection String
echo --------------------------------------------
echo 1. In Supabase Dashboard, go to:
echo    Project Settings ^> Database
echo 2. Copy the "Connection string" (URI format)
echo 3. It looks like:
echo    postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
echo.

echo Step 3: Update Prisma Schema
echo --------------------------------------------
echo Running: npm run db:push
echo This will sync your Prisma schema with the production database.
echo.
npm run db:push
echo.

echo Step 4: Import Data from Dev
echo --------------------------------------------
echo Run this command with your production connection string:
echo.
echo   python scripts/import_supabase.py ^
echo     --url "postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres" ^
echo     --input supabase_export ^
echo     --clear
echo.

echo Step 5: Configure Auth in Supabase
echo --------------------------------------------
echo 1. Go to Authentication ^> Providers ^> Email
echo 2. Enable Email provider
echo 3. Set "Confirm email" to true (recommended)
echo 4. Configure email templates
echo 5. Go to Authentication ^> URL Configuration
echo 6. Add your production URL to "Redirect URLs"
echo.

echo Step 6: Get API Credentials
echo --------------------------------------------
echo 1. Go to Project Settings ^> API
echo 2. Copy:
echo    - Project URL ^> NEXT_PUBLIC_SUPABASE_URL
echo    - anon/public key ^> NEXT_PUBLIC_SUPABASE_ANON_KEY
echo.

echo Step 7: Deploy to Vercel
echo --------------------------------------------
echo 1. Push code to GitHub:
echo    git add .
echo    git commit -m "Prepare for production"
echo    git push origin main
echo.
echo 2. Go to https://vercel.com/new
echo 3. Import your repository
echo 4. Add environment variables:
echo    - NEXT_PUBLIC_APP_URL=https://your-app.vercel.app
echo    - DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
echo    - NEXT_PUBLIC_SUPABASE_URL=https://[PROJECT-REF].supabase.co
echo    - NEXT_PUBLIC_SUPABASE_ANON_KEY=[YOUR-ANON-KEY]
echo 5. Click Deploy
echo.

echo ============================================
echo Setup Complete!
echo ============================================
pause
