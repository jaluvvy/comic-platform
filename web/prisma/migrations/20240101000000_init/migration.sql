-- CreateEnum
CREATE TYPE "Role" AS ENUM ('USER', 'SELLER', 'ADMIN');

-- CreateTable
CREATE TABLE "publishers" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid(),
    "name" TEXT NOT NULL,
    "slug" VARCHAR(100) NOT NULL,
    "website" TEXT,
    "type" VARCHAR(20) NOT NULL DEFAULT 'nxb',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "publishers_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "comics" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid(),
    "publisher_id" TEXT NOT NULL,
    "title" VARCHAR(500) NOT NULL,
    "slug" VARCHAR(500) NOT NULL,
    "product_id" TEXT,
    "sku" VARCHAR(100),
    "isbn" VARCHAR(50),
    "price" INTEGER,
    "original_price" INTEGER,
    "currency" VARCHAR(10) NOT NULL DEFAULT 'VND',
    "authors" TEXT[],
    "target_audience" TEXT,
    "dimensions" TEXT,
    "pages" INTEGER,
    "format" TEXT,
    "weight" TEXT,
    "edition_type" VARCHAR(50) NOT NULL DEFAULT 'ban_in_dau',
    "edition_year" INTEGER,
    "series" TEXT,
    "description" TEXT,
    "cover_image" TEXT,
    "product_type" VARCHAR(50),
    "url" TEXT UNIQUE,
    "lastmod" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "comics_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "gifts" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid(),
    "comic_id" TEXT NOT NULL,
    "name" VARCHAR(200) NOT NULL,
    "description" TEXT,
    "image_url" TEXT,
    "is_fes" BOOLEAN NOT NULL DEFAULT false,
    "fes_event" VARCHAR(200),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "gifts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "events" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid(),
    "publisher_id" TEXT NOT NULL,
    "name" VARCHAR(200) NOT NULL,
    "event_type" VARCHAR(50) NOT NULL DEFAULT 'hoc_sach',
    "start_date" TIMESTAMP(3),
    "end_date" TIMESTAMP(3),
    "description" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "events_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "event_gifts" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid(),
    "event_id" TEXT NOT NULL,
    "comic_id" TEXT,
    "gift_name" VARCHAR(200) NOT NULL,
    "condition" TEXT,
    "image_url" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "event_gifts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "users" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid(),
    "email" TEXT UNIQUE,
    "name" TEXT,
    "image" TEXT,
    "role" "Role" NOT NULL DEFAULT 'USER',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "listings" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid(),
    "user_id" TEXT NOT NULL,
    "comic_id" TEXT NOT NULL,
    "price" INTEGER NOT NULL,
    "condition" VARCHAR(50) NOT NULL DEFAULT 'tot',
    "edition_info" TEXT,
    "gifts_included" TEXT[],
    "intro" TEXT,
    "outro" TEXT,
    "status" VARCHAR(20) NOT NULL DEFAULT 'active',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "listings_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "publishers_name_key" ON "publishers"("name");

CREATE UNIQUE INDEX "publishers_slug_key" ON "publishers"("slug");

CREATE INDEX "comics_publisher_id_idx" ON "comics"("publisher_id");

CREATE INDEX "comics_slug_idx" ON "comics"("slug");

CREATE INDEX "comics_title_idx" ON "comics"("title");

CREATE UNIQUE INDEX "comics_product_id_key" ON "comics"("product_id");

CREATE UNIQUE INDEX "comics_url_key" ON "comics"("url");

CREATE INDEX "gifts_comic_id_idx" ON "gifts"("comic_id");

CREATE INDEX "events_publisher_id_idx" ON "events"("publisher_id");

CREATE INDEX "event_gifts_event_id_idx" ON "event_gifts"("event_id");

CREATE INDEX "event_gifts_comic_id_idx" ON "event_gifts"("comic_id");

CREATE INDEX "listings_user_id_idx" ON "listings"("user_id");

CREATE INDEX "listings_comic_id_idx" ON "listings"("comic_id");

CREATE INDEX "listings_status_idx" ON "listings"("status");

-- AddForeignKey
ALTER TABLE "comics" ADD CONSTRAINT "comics_publisher_id_fkey" FOREIGN KEY ("publisher_id") REFERENCES "publishers"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "gifts" ADD CONSTRAINT "gifts_comic_id_fkey" FOREIGN KEY ("comic_id") REFERENCES "comics"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "events" ADD CONSTRAINT "events_publisher_id_fkey" FOREIGN KEY ("publisher_id") REFERENCES "publishers"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "event_gifts" ADD CONSTRAINT "event_gifts_event_id_fkey" FOREIGN KEY ("event_id") REFERENCES "events"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "event_gifts" ADD CONSTRAINT "event_gifts_comic_id_fkey" FOREIGN KEY ("comic_id") REFERENCES "comics"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "listings" ADD CONSTRAINT "listings_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "listings" ADD CONSTRAINT "listings_comic_id_fkey" FOREIGN KEY ("comic_id") REFERENCES "comics"("id") ON DELETE CASCADE ON UPDATE CASCADE;
