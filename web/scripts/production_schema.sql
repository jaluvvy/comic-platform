-- Production database schema for ComicPlatform
-- Run this in Supabase SQL Editor or via psql

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Publishers table
CREATE TABLE IF NOT EXISTS publishers (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  name TEXT NOT NULL UNIQUE,
  slug TEXT NOT NULL UNIQUE,
  website TEXT,
  type TEXT NOT NULL DEFAULT 'nxb',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Comics table
CREATE TABLE IF NOT EXISTS comics (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  publisher_id TEXT NOT NULL REFERENCES publishers(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  slug TEXT NOT NULL,
  product_id TEXT UNIQUE,
  sku TEXT,
  isbn TEXT,
  price INT,
  original_price INT,
  currency TEXT DEFAULT 'VND',
  authors TEXT[],
  target_audience TEXT,
  dimensions TEXT,
  pages INT,
  format TEXT,
  weight TEXT,
  edition_type TEXT DEFAULT 'ban_in_dau',
  edition_year INT,
  series TEXT,
  description TEXT,
  cover_image TEXT,
  product_type TEXT,
  url TEXT UNIQUE,
  lastmod TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Gifts table
CREATE TABLE IF NOT EXISTS gifts (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  comic_id TEXT NOT NULL REFERENCES comics(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  image_url TEXT,
  is_fes BOOLEAN DEFAULT FALSE,
  fes_event TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Events table
CREATE TABLE IF NOT EXISTS events (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  publisher_id TEXT NOT NULL REFERENCES publishers(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  event_type TEXT DEFAULT 'hoc_sach',
  start_date TIMESTAMP,
  end_date TIMESTAMP,
  description TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Event gifts table
CREATE TABLE IF NOT EXISTS event_gifts (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  event_id TEXT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  comic_id TEXT REFERENCES comics(id) ON DELETE SET NULL,
  gift_name TEXT NOT NULL,
  condition TEXT,
  image_url TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Users table (for app users, not auth.users)
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  email TEXT UNIQUE,
  name TEXT,
  image TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Listings table
CREATE TABLE IF NOT EXISTS listings (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  comic_id TEXT NOT NULL REFERENCES comics(id) ON DELETE CASCADE,
  price INT NOT NULL,
  condition TEXT DEFAULT 'tot',
  edition_info TEXT,
  gifts_included TEXT[],
  intro TEXT,
  outro TEXT,
  status TEXT DEFAULT 'active',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_comics_publisher_id ON comics(publisher_id);
CREATE INDEX IF NOT EXISTS idx_comics_slug ON comics(slug);
CREATE INDEX IF NOT EXISTS idx_comics_title ON comics(title);
CREATE INDEX IF NOT EXISTS idx_comics_product_id ON comics(product_id);
CREATE INDEX IF NOT EXISTS idx_gifts_comic_id ON gifts(comic_id);
CREATE INDEX IF NOT EXISTS idx_events_publisher_id ON events(publisher_id);
CREATE INDEX IF NOT EXISTS idx_event_gifts_event_id ON event_gifts(event_id);
CREATE INDEX IF NOT EXISTS idx_event_gifts_comic_id ON event_gifts(comic_id);
CREATE INDEX IF NOT EXISTS idx_listings_user_id ON listings(user_id);
CREATE INDEX IF NOT EXISTS idx_listings_comic_id ON listings(comic_id);
CREATE INDEX IF NOT EXISTS idx_listings_status ON listings(status);

-- Insert default publisher
INSERT INTO publishers (id, name, slug, type)
VALUES ('publisher-kim-dong', 'Nhà xuất bản Kim Đồng', 'nxb-kim-dong', 'nxb')
ON CONFLICT (id) DO NOTHING;
