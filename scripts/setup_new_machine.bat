@echo off
chcp 65001 >nul
echo ============================================
echo ComicPlatform - New Machine Setup
echo ============================================
echo.

echo Checking prerequisites...
echo.

node --version >nul 2>&1
if errorlevel 1 (
    echo [ERR] Node.js not found. Please install from https://nodejs.org/
    pause
    exit /b 1
) else (
    echo [OK] Node.js found
)

npm --version >nul 2>&1
if errorlevel 1 (
    echo [ERR] npm not found
    pause
    exit /b 1
) else (
    echo [OK] npm found
)

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERR] Python not found. Please install from https://python.org/
    pause
    exit /b 1
) else (
    echo [OK] Python found
)

echo.
echo Installing dependencies...
cd web
call npm install
if errorlevel 1 (
    echo [ERR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Generating Prisma client...
call npm run db:generate
if errorlevel 1 (
    echo [ERR] Failed to generate Prisma client
    pause
    exit /b 1
)

echo.
if not exist ".env.local" (
    echo [WARN] .env.local not found!
    echo.
    echo Please create .env.local with your Supabase credentials:
    echo   1. Copy .env.example to .env.local
    echo   2. Fill in your Supabase project credentials
    echo.
    echo Get credentials from:
    echo   - Project Settings ^> Database ^> Connection string
    echo   - Project Settings ^> API ^> Project URL ^> anon key
) else (
    echo [OK] .env.local found
    echo.
    echo Pushing schema to database...
    call npm run db:push
    if errorlevel 1 (
        echo [WARN] Failed to push schema. Check DATABASE_URL in .env.local
    ) else (
        echo [OK] Database schema synced
    )
)

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next steps:
echo   1. Ensure .env.local is configured
echo   2. Run: npm run db:push
echo   3. Run: npm run dev
echo   4. Visit: http://localhost:3001
echo.
pause
