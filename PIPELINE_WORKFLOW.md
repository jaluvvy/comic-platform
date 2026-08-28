# Pipeline Workflow - Từ Sơ Khai đến Production

## Mục tiêu
Chuẩn bị "vật liệu" data sạch, validate, export sẵn sàng import lên Supabase production trước khi build web lên.

---

## Phase 1: Data Pipeline

### 1. Crawl
```bash
python -m src.pipeline_runner --workers 6 --delay 0.7
# hoặc giới hạn test
python -m src.pipeline_runner --workers 6 --delay 0.7 --limit 20
```

**Output**:
- `output/raw/*.html` - HTML gốc
- `output/parsed/*.json` - Dữ liệu đã parse
- `output/parsed/summary.json` - Tổng kết crawl

### 2. Validate
```bash
python -m src.pipeline_runner --validate
# hoặc chỉ chạy validate trên data cũ
python -m src.validators
```

**Output**:
- `output/parsed/validation_report.json`

**Quality Gates**:
- `invalid_comics == 0`
- `invalid_volumes == 0`
- `invalid_gifts == 0`
- `warnings < 50`

### 3. Export
```bash
python -m src.pipeline_runner --export
# hoặc chỉ chạy export
python -m src.exporters
```

**Output**:
- `output/export/comics.json`
- `output/export/volumes.json`
- `output/export/gifts.json`
- `output/export/import_manifest.json`

### 4. Review / Filter
```bash
# Auto filter
python -m src.utils.filter_comics

# Manual review
python -m src.utils.batch_review
python -m src.utils.manual_filter --review
python -m src.utils.manual_filter --apply
```

**Output**:
- `output/parsed/` chỉ còn truyện cần giữ
- `output/manual_filter_decisions.json`

---

## Phase 2: Database Pipeline

### 1. Prisma Setup
```bash
cd web
npm run db:generate
npm run db:push
```

### 2. Seed via Prisma (ưu tiên)
```bash
npm run db:seed
```
Script: `web/scripts/seed.ts`

### 3. Seed via Direct SQL (fallback)
```bash
python scripts/import_supabase_direct.py \
  --url "postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres" \
  --input output/export/comics.json \
  --clear
```

### 4. Verify
```bash
python scripts/export_supabase.py --url "..." --output verify_export
```

---

## Phase 3: Web Platform

### 1. Local Dev
```bash
cd web
npm install
npm run dev
# http://localhost:3000
```

### 2. Build Check
```bash
npm run build
npm run lint
```

### 3. Deploy
```bash
git push origin master
# Vercel auto-deploy
```

---

## Phase 4: Expansion (khi Phase 1-3 ổn)

### Thêm NXB mới
1. Viết parser mới implement `BaseParser`
2. Viết crawler mới implement `BaseCrawler`
3. Chạy pipeline: `python -m src.pipeline_runner`
4. Seed lên DB

### Ví dụ: Hồng Hạc
```
src/parsers/honghac.py   -> BaseParser
src/crawlers/honghac.py  -> BaseCrawler
python -m src.pipeline_runner --parser honghac
```

---

## Architecture

```
BaseParser (interface)
  ├── KimDongParser
  ├── HongHaParser (future)
  └── ...

BaseCrawler (interface)
  ├── KimDongCrawler
  ├── HongHaCrawler (future)
  └── ...

CrawlPipeline (orchestrator)
  ├── fetch_text
  ├── parse_sitemap
  ├── parse_product
  ├── save JSON
  └── save summary

DataValidator
  ├── validate_comic
  ├── validate_volume
  └── validate_gift

DataExporter
  ├── export_comics
  ├── export_volumes
  ├── export_gifts
  └── export_manifest

import_supabase_direct.py
  └── Direct SQL import to Supabase
```

---

## Troubleshooting

### npm install lỗi trên Google Drive
**Fix**: Copy `web/` về local (C:\Projects\comic-platform\web), chạy npm install ở đó, sync code sau.

### Supabase connection fail
**Fix**: Dùng `import_supabase_direct.py` thay vì Prisma, hoặc kiểm tra IP whitelist.

### Validation có nhiều warnings
**Fix**: Xem `validation_report.json`, filter từng loại warning, update parser.
