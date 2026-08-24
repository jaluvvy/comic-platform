# ComicPlatform

Thư viện truyện tranh toàn diện - nền tảng mua bán trao đổi truyện tranh Việt Nam.

## Tech Stack

- **Frontend**: Next.js 14, React, Tailwind CSS
- **Backend**: Next.js API Routes
- **Database**: Supabase (PostgreSQL)
- **Auth**: Supabase Auth
- **ORM**: Prisma

## Quick Start

### 1. Clone repository
```bash
git clone https://github.com/[your-username]/comic-platform.git
cd comic-platform/web
```

### 2. Install dependencies
```bash
npm install
```

### 3. Set up environment variables
```bash
# Copy example env file
cp .env.example .env.local

# Edit .env.local with your Supabase credentials
# - NEXT_PUBLIC_APP_URL
# - DATABASE_URL
# - NEXT_PUBLIC_SUPABASE_URL
# - NEXT_PUBLIC_SUPABASE_ANON_KEY
```

### 4. Set up database
```bash
# Generate Prisma client
npm run db:generate

# Push schema to database
npm run db:push
```

### 5. Import data (optional)
```bash
# If you have export data from another environment
python scripts/import_supabase.py \
  --url "postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres" \
  --input ../supabase_export \
  --clear --force
```

### 6. Run development server
```bash
npm run dev
```

Visit [http://localhost:3001](http://localhost:3001)

## Project Structure

```
web/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── api/               # API routes
│   │   ├── comics/            # Comics pages
│   │   ├── listings/          # Listings pages
│   │   ├── login/             # Auth pages
│   │   └── admin/             # Admin pages
│   ├── components/            # Reusable components
│   └── lib/                   # Utilities
├── scripts/                   # Database scripts
├── prisma/                    # Prisma schema
├── supabase_export/           # Data exports (not committed)
└── .env.example               # Environment template
```

## Available Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start development server on port 3001 |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm run db:generate` | Generate Prisma client |
| `npm run db:push` | Push schema to database |
| `npm run db:migrate` | Run Prisma migrations |
| `npm run db:seed` | Seed database |

## Environment Variables

See `.env.example` for required variables.

## Deployment

See [DEPLOY.md](DEPLOY.md) for production deployment instructions.

## Contributing

1. Create feature branch
2. Commit changes
3. Push to branch
4. Open Pull Request

## License

MIT
