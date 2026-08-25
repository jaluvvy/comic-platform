-- Create volumes table
CREATE TABLE "volumes" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid(),
    "comic_id" TEXT NOT NULL,
    "title" VARCHAR(500) NOT NULL,
    "slug" VARCHAR(500) NOT NULL,
    "product_id" TEXT UNIQUE,
    "sku" VARCHAR(100),
    "barcode" VARCHAR(100),
    "price" INTEGER,
    "original_price" INTEGER,
    "currency" VARCHAR(10) NOT NULL DEFAULT 'VND',
    "volume_number" INTEGER,
    "volume_label" VARCHAR(50),
    "pages" INTEGER,
    "format" VARCHAR(50),
    "dimensions" VARCHAR(50),
    "weight" VARCHAR(50),
    "cover_image" TEXT,
    "url" TEXT UNIQUE,
    "available" BOOLEAN NOT NULL DEFAULT true,
    "inventory_qty" INTEGER,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "volumes_pkey" PRIMARY KEY ("id")
);

-- Update gifts table: remove comic_id, add volume_id and event_id
ALTER TABLE "gifts" DROP COLUMN IF EXISTS "comic_id";
ALTER TABLE "gifts" ADD COLUMN "volume_id" TEXT;
ALTER TABLE "gifts" ADD COLUMN "event_id" TEXT;
ALTER TABLE "gifts" ADD COLUMN "gift_type" VARCHAR(50) NOT NULL DEFAULT 'combo';
ALTER TABLE "gifts" ADD COLUMN "rarity" VARCHAR(50) NOT NULL DEFAULT 'normal';

-- Update event_gifts table
ALTER TABLE "event_gifts" ADD COLUMN "volume_id" TEXT;
ALTER TABLE "event_gifts" ADD COLUMN "gift_id" TEXT;

-- Update listings table
ALTER TABLE "listings" ADD COLUMN "volume_id" TEXT;
ALTER TABLE "listings" ADD COLUMN "gift_id" TEXT;
ALTER TABLE "listings" ADD COLUMN "listing_type" VARCHAR(20) NOT NULL DEFAULT 'volume';

-- Create indexes
CREATE INDEX "volumes_comic_id_idx" ON "volumes"("comic_id");
CREATE INDEX "volumes_slug_idx" ON "volumes"("slug");
CREATE INDEX "volumes_product_id_idx" ON "volumes"("product_id");

CREATE INDEX "gifts_volume_id_idx" ON "gifts"("volume_id");
CREATE INDEX "gifts_event_id_idx" ON "gifts"("event_id");

CREATE INDEX "event_gifts_volume_id_idx" ON "event_gifts"("volume_id");
CREATE INDEX "event_gifts_gift_id_idx" ON "event_gifts"("gift_id");

CREATE INDEX "listings_volume_id_idx" ON "listings"("volume_id");
CREATE INDEX "listings_gift_id_idx" ON "listings"("gift_id");

-- Add foreign keys
ALTER TABLE "volumes" ADD CONSTRAINT "volumes_comic_id_fkey" FOREIGN KEY ("comic_id") REFERENCES "comics"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "gifts" ADD CONSTRAINT "gifts_volume_id_fkey" FOREIGN KEY ("volume_id") REFERENCES "volumes"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "gifts" ADD CONSTRAINT "gifts_event_id_fkey" FOREIGN KEY ("event_id") REFERENCES "events"("id") ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE "event_gifts" ADD CONSTRAINT "event_gifts_volume_id_fkey" FOREIGN KEY ("volume_id") REFERENCES "volumes"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "event_gifts" ADD CONSTRAINT "event_gifts_gift_id_fkey" FOREIGN KEY ("gift_id") REFERENCES "gifts"("id") ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE "listings" ADD CONSTRAINT "listings_volume_id_fkey" FOREIGN KEY ("volume_id") REFERENCES "volumes"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "listings" ADD CONSTRAINT "listings_gift_id_fkey" FOREIGN KEY ("gift_id") REFERENCES "gifts"("id") ON DELETE SET NULL ON UPDATE CASCADE;
