# Deploy ComicPlatform to Production
Write-Host "Deploying ComicPlatform to Production..." -ForegroundColor Green
Write-Host ""

# Check if Vercel CLI is installed
$vercel = Get-Command vercel -ErrorAction SilentlyContinue
if (-not $vercel) {
    Write-Host "Installing Vercel CLI..." -ForegroundColor Yellow
    npm install -g vercel
}

# Check if user is logged in to Vercel
Write-Host "Checking Vercel authentication..." -ForegroundColor Yellow
$vercelWhoami = vercel whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Please log in to Vercel:" -ForegroundColor Yellow
    vercel login
}

# Navigate to web directory
Set-Location "G:\My Drive\Work\comic-crawler\web"

# Run database migrations
Write-Host "Running database migrations..." -ForegroundColor Yellow
npm run db:push

# Build the project
Write-Host "Building project..." -ForegroundColor Yellow
npm run build

# Deploy to production
Write-Host "Deploying to Vercel..." -ForegroundColor Green
vercel --prod

Write-Host ""
Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "Don't forget to:" -ForegroundColor Yellow
Write-Host "1. Set environment variables in Vercel dashboard"
Write-Host "2. Configure Supabase auth settings"
Write-Host "3. Test the deployed site"
