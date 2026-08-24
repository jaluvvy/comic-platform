# Comic Platform - Web Application

Frontend cho nền tảng thư viện truyện tranh, mua bán và quản lý dữ liệu.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Database**: PostgreSQL qua Supabase
- **ORM**: Prisma 5
- **Auth**: Supabase Auth (sẵn có, chưa dùng trong Phase 1)

## Cấu trúc thư mục

```
web/
├── prisma/
│   └── schema.prisma          # Database schema
├── scripts/
│   └── seed.ts                # Import dữ liệu JSON cũ vào DB
├── src/
│   ├── app/
│   │   ├── layout.tsx         # Root layout + Header
│   │   ├── page.tsx           # Trang chủ
│   │   ├── globals.css        # Tailwind + custom styles
│   │   ├── not-found.tsx      # Trang 404
│   │   ├── comics/
│   │   │   ├── page.tsx       # Danh sách truyện + search/filter
│   │   │   └── [id]/page.tsx  # Chi tiết truyện
│   │   └── api/
│   │       └── comics/
│   │           ├── route.ts   # API: GET /api/comics
│   │           └── [id]/route.ts # API: GET /api/comics/[id]
│   ├── components/
│   │   ├── Header.tsx         # Navigation header
│   │   ├── ComicCard.tsx      # Card hiển thị 1 truyện
│   │   ├── ComicGrid.tsx      # Grid layout cho danh sách
│   │   └── SearchBar.tsx      # Search + filter theo NXB
│   └── lib/
│       ├── prisma.ts          # Prisma client instance
│       ├── supabase.ts        # Supabase client
│       └── utils.ts           # Utility functions (cn)
└── .env.local                 # Environment variables
```

## Setup nhanh

### 1. Clone/Copy project về local

```bash
# Copy toàn bộ thư mục web về một đường dẫn local (không dùng Google Drive)
# Vì npm/node_modules chạy rất chậm trên Google Drive
```

### 2. Cài đặt dependencies

```bash
cd web
npm install
```

### 3. Setup Database (Supabase)

1. Tạo project mới trên [Supabase](https://supabase.com)
2. Lấy `DATABASE_URL` từ Settings → Database → Connection string (URI mode)
3. Tạo `.env.local`:

```env
DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres"
NEXT_PUBLIC_SUPABASE_URL="https://[PROJECT_REF].supabase.co"
NEXT_PUBLIC_SUPABASE_ANON_KEY="[ANON_KEY]"
NEXT_PUBLIC_APP_URL="http://localhost:3000"
```

### 4. Push schema lên Supabase

```bash
npx prisma db push
```

Hoặc tạo migration:

```bash
npx prisma migrate dev --name init
```

### 5. Seed dữ liệu cũ (745 comics Kim Đồng)

```bash
npx prisma generate
npm run db:seed
```

### 6. Chạy dev server

```bash
npm run dev
```

Mở http://localhost:3000

## Deploy lên Vercel (Miễn phí)

1. Push code lên GitHub
2. Connect repo với Vercel
3. Thêm Environment Variables trong Vercel Dashboard:
   - `DATABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `NEXT_PUBLIC_APP_URL`
4. Deploy

## Lưu ý quan trọng

### Về Google Drive
**KHÔNG** chạy `npm install` hay `npm run dev` trực tiếp trên thư mục Google Drive. npm/node_modules chạy rất chậm và dễ lỗi trên GDrive.

**Cách làm việc đề xuất:**
- Copy thư mục `web/` về local (C:\Projects\comic-platform\web)
- Làm việc và test local
- Sync code lên Google Drive sau khi hoàn thành

### Về Prisma
- Prisma Client đã được generate sẵn trong `node_modules/@prisma/client`
- Nếu thay đổi `schema.prisma`, chạy `npx prisma generate` lại
- Khi deploy lên Vercel, Prisma Client sẽ được generate tự động qua postinstall script

### Về dữ liệu hiện tại
- 745 comics Kim Đồng đã có sẵn trong `output/parsed/*.json`
- Chạy `npm run db:seed` để import vào PostgreSQL
- Sau khi import xong, có thể xóa thư mục `output/` nếu muốn tiết kiệm dung lượng

## Tính năng Phase 1

- [x] Trang chủ với hero section + features
- [x] Thư viện truyện: Grid view, responsive
- [x] Chi tiết truyện: ISBN, giá, tác giả, bộ sách, quà tặng
- [x] Search: Tìm theo tên, tác giả, bộ sách
- [x] Filter: Theo NXB
- [x] API: `/api/comics`, `/api/comics/[id]`
- [x] Database schema cho Publishers, Comics, Gifts, Events, Listings, Users
- [x] Seed script import dữ liệu JSON cũ

## Tính năng Phase 2 (Sắp tới)

- Auth (Đăng nhập/Đăng ký)
- Selling: Tạo listing từ thư viện
- Buying: Search listings, filter tình trạng sách
- Event/Gift tracking từ NXB
- Image upload cho gifts
