#!/bin/bash
set -e

echo "🚀 Deploying ComicPlatform to Production..."
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

# Check if user is logged in to Vercel
echo "🔐 Checking Vercel authentication..."
if ! vercel whoami &> /dev/null; then
    echo "Please log in to Vercel:"
    vercel login
fi

# Run database migrations
echo "🗄️  Running database migrations..."
cd web
npm run db:push

# Build the project
echo "🔨 Building project..."
npm run build

# Deploy to production
echo "🚀 Deploying to Vercel..."
vercel --prod

echo ""
echo "✅ Deployment complete!"
echo "Don't forget to:"
echo "1. Set environment variables in Vercel dashboard"
echo "2. Configure Supabase auth settings"
echo "3. Test the deployed site"
