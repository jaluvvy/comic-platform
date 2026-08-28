import { PrismaClient } from '@prisma/client';
import { readdirSync, readFileSync } from 'fs';
import { join } from 'path';

const prisma = new PrismaClient();

interface VolumeJson {
  title: string;
  slug: string;
  product_id?: string;
  sku?: string;
  barcode?: string;
  price?: number;
  original_price?: number;
  volume_number?: number;
  volume_label?: string;
  pages?: number;
  format?: string;
  dimensions?: string;
  weight?: string;
  cover_image?: string;
  url?: string;
  available?: boolean;
  inventory_qty?: number;
  gifts?: Array<{
    name: string;
    description?: string | null;
    image_url?: string | null;
    is_fes?: boolean;
    fes_event?: string | null;
    gift_type?: string;
    rarity?: string;
  }>;
}

interface ComicJson {
  publisher: string;
  title: string;
  slug: string;
  product_id?: string;
  price?: number;
  original_price?: number;
  sku?: string;
  isbn?: string;
  authors?: string[];
  target_audience?: string;
  dimensions?: string;
  pages?: number;
  format?: string;
  weight?: string;
  series?: string;
  description?: string;
  cover_image?: string;
  product_type?: string;
  url?: string;
  lastmod?: string;
  edition_type?: string;
  edition_year?: number;
  volumes?: VolumeJson[];
  gifts?: Array<{
    name: string;
    description?: string | null;
    image_url?: string | null;
    is_fes?: boolean;
    fes_event?: string | null;
    gift_type?: string;
    rarity?: string;
  }>;
}

async function main() {
  const parsedDir = join(process.cwd(), '..', 'output', 'parsed');

  console.log('Reading JSON files...');
  const files = readdirSync(parsedDir).filter((f) => f.endsWith('.json') && !f.includes('summary'));
  console.log(`Found ${files.length} files`);

  let publishersMap = new Map<string, string>();
  let importedComics = 0;
  let importedVolumes = 0;
  let importedGifts = 0;

  for (const file of files) {
    const filePath = join(parsedDir, file);
    const content = readFileSync(filePath, 'utf-8');
    const data: ComicJson = JSON.parse(content);

    if (!data.publisher || !data.title) continue;

    const pub = data.publisher as string;
    let publisherId = publishersMap.get(pub);
    if (!publisherId) {
      const publisher = await prisma.publisher.upsert({
        where: { name: pub },
        update: {},
        create: {
          name: pub,
          slug: pub.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-'),
          type: 'nxb',
        },
      });
      publisherId = publisher.id;
      publishersMap.set(pub, publisherId);
    }

    const editionType = data.edition_type || 'ban_in_dau';

    const comic = await prisma.comic.upsert({
      where: {
        productId: data.product_id || undefined,
      },
      update: {
        title: data.title,
        price: data.price || 0,
        originalPrice: data.original_price || null,
        sku: data.sku,
        isbn: data.isbn,
        authors: data.authors || [],
        targetAudience: data.target_audience,
        dimensions: data.dimensions,
        pages: data.pages,
        format: data.format,
        weight: data.weight,
        series: data.series,
        description: data.description,
        coverImage: data.cover_image,
        productType: data.product_type,
        url: data.url,
        lastmod: data.lastmod,
        editionType,
        editionYear: data.edition_year || null,
        updatedAt: new Date(),
      },
      create: {
        publisherId,
        title: data.title,
        slug: data.slug || data.product_id || file.replace('.json', ''),
        productId: data.product_id,
        price: data.price || 0,
        originalPrice: data.original_price || null,
        sku: data.sku,
        isbn: data.isbn,
        authors: data.authors || [],
        targetAudience: data.target_audience,
        dimensions: data.dimensions,
        pages: data.pages,
        format: data.format,
        weight: data.weight,
        series: data.series,
        description: data.description,
        coverImage: data.cover_image,
        productType: data.product_type,
        url: data.url,
        lastmod: data.lastmod,
        editionType,
        editionYear: data.edition_year || null,
      },
    });

    importedComics += 1;

    const volumes = data.volumes || [];
    for (const volume of volumes) {
      const createdVolume = await prisma.volume.upsert({
        where: { productId: volume.product_id || undefined },
        update: {
          title: volume.title,
          slug: volume.slug,
          price: volume.price || 0,
          originalPrice: volume.original_price || null,
          sku: volume.sku,
          barcode: volume.barcode,
          volumeNumber: volume.volume_number,
          volumeLabel: volume.volume_label,
          pages: volume.pages,
          format: volume.format,
          dimensions: volume.dimensions,
          weight: volume.weight,
          coverImage: volume.cover_image,
          url: volume.url,
          available: volume.available ?? true,
          inventoryQty: volume.inventory_qty || null,
          updatedAt: new Date(),
        },
        create: {
          comicId: comic.id,
          publisherId,
          title: volume.title,
          slug: volume.slug,
          productId: volume.product_id,
          price: volume.price || 0,
          originalPrice: volume.original_price || null,
          sku: volume.sku,
          barcode: volume.barcode,
          volumeNumber: volume.volume_number,
          volumeLabel: volume.volume_label,
          pages: volume.pages,
          format: volume.format,
          dimensions: volume.dimensions,
          weight: volume.weight,
          coverImage: volume.cover_image,
          url: volume.url,
          available: volume.available ?? true,
          inventoryQty: volume.inventory_qty || null,
        },
      });

      importedVolumes += 1;

      const gifts = volume.gifts || [];
      if (gifts.length > 0) {
        await prisma.gift.deleteMany({
          where: { volumeId: createdVolume.id },
        });

        for (const gift of gifts) {
          await prisma.gift.create({
            data: {
              volumeId: createdVolume.id,
              name: gift.name,
              description: gift.description || null,
              imageUrl: gift.image_url || null,
              isFes: gift.is_fes || false,
              fesEvent: gift.fes_event || null,
              giftType: gift.gift_type || 'combo',
              rarity: gift.rarity || 'normal',
            },
          });
          importedGifts += 1;
        }
      }
    }

    console.log(`Imported: ${data.title} (+${volumes.length} volumes, +${importedGifts} gifts)`);
  }

  console.log(`\nDone! Imported ${importedComics} comics, ${importedVolumes} volumes, ${importedGifts} gifts.`);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
