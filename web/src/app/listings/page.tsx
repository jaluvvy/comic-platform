import Link from "next/link";
import { Metadata } from "next";
import { BookOpen, Filter, Search, Gift } from "lucide-react";
import ListingFilters from "./ListingFilters";
import prisma from "@/lib/prisma";
import { supabaseListings } from "@/lib/supabase-helpers";

export const metadata: Metadata = {
  title: "Danh sách bán | ComicPlatform",
  description: "Xem danh sách truyện tranh, tập, quà tặng đang được bán",
};

async function getListings(searchParams: Record<string, string>) {
  const status = searchParams.status || "active";
  const where: any = { status };

  if (searchParams.q) {
    where.OR = [
      { comic: { title: { contains: searchParams.q, mode: "insensitive" } } },
      { volume: { title: { contains: searchParams.q, mode: "insensitive" } } },
      { gift: { name: { contains: searchParams.q, mode: "insensitive" } } },
    ];
  }

  if (searchParams.condition) {
    where.condition = searchParams.condition;
  }

  if (searchParams.type) {
    where.listingType = searchParams.type;
  }

  if (searchParams.minPrice) {
    where.price = { ...where.price, gte: parseInt(searchParams.minPrice) };
  }

  if (searchParams.maxPrice) {
    where.price = { ...where.price, lte: parseInt(searchParams.maxPrice) };
  }

  try {
    const [listings, total] = await Promise.all([
      prisma.listing.findMany({
        where,
        include: {
          user: {
            select: { id: true, name: true, email: true },
          },
          comic: {
            include: {
              publisher: {
                select: { id: true, name: true, slug: true },
              },
            },
          },
          volume: {
            include: {
              comic: {
                include: {
                  publisher: {
                    select: { id: true, name: true, slug: true },
                  },
                },
              },
              gifts: true,
            },
          },
          gift: true,
        },
        orderBy: { createdAt: "desc" },
        skip: 0,
        take: 20,
      }),
      prisma.listing.count({ where }),
    ]);

    return { listings, pagination: { page: 1, limit: 20, total, totalPages: Math.ceil(total / 20) }, error: null as string | null };
  } catch (error) {
    console.error("Prisma error, falling back to Supabase REST:", error);
    try {
      const result = await supabaseListings({
        q: searchParams.q || undefined,
        condition: searchParams.condition || undefined,
        minPrice: searchParams.minPrice || undefined,
        maxPrice: searchParams.maxPrice || undefined,
        type: searchParams.type || undefined,
        status,
        page: 1,
        limit: 20,
      });
      return { listings: result.data || [], pagination: result.pagination, error: null as string | null };
    } catch (supabaseError: any) {
      console.error("Supabase REST error:", supabaseError);
      return { listings: [], pagination: null, error: supabaseError?.message || "Failed to fetch listings" };
    }
  }
}

function getListingTitle(listing: any): string {
  if (listing.volume) return listing.volume.title;
  if (listing.gift) return listing.gift.name;
  if (listing.comic) return listing.comic.title;
  return "Không rõ";
}

function getListingImage(listing: any): string | null {
  if (listing.volume?.coverImage) return listing.volume.coverImage;
  if (listing.gift?.imageUrl) return listing.gift.imageUrl;
  if (listing.comic?.coverImage) return listing.comic.coverImage;
  return null;
}

function getListingTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    comic: "Bộ truyện",
    volume: "Tập",
    gift: "Quà tặng",
    combo: "Combo",
  };
  return labels[type] || type;
}

export const dynamic = "force-dynamic";

export default async function ListingsPage({
  searchParams,
}: {
  searchParams: Record<string, string>;
}) {
  const { listings, pagination, error } = await getListings(searchParams);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(price);
  };

  const getConditionLabel = (condition: string) => {
    const labels: Record<string, string> = {
      moi: "Mới",
      tot: "Tốt",
      binh_thuong: "Bình thường",
      cu: "Cũ",
    };
    return labels[condition] || condition;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Danh sách bán</h1>
            <p className="text-gray-600 mt-1">
              Tìm và mua truyện tranh, tập, quà tặng từ cộng đồng
            </p>
          </div>
          <Link
            href="/listings/create"
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700"
          >
            <BookOpen className="mr-2 h-4 w-4" />
            Tạo bài bán
          </Link>
        </div>

        <ListingFilters />

        {error && (
          <div className="mb-6 rounded-md bg-red-50 p-4 text-sm text-red-800">
            {error}
          </div>
        )}

        {listings.length === 0 && !error ? (
          <div className="text-center py-16 bg-white rounded-lg border">
            <BookOpen className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-4 text-lg font-semibold text-gray-900">
              Không tìm thấy bài bán nào
            </h3>
            <p className="text-gray-600 mt-2">
              Thử thay đổi bộ lọc hoặc tạo bài bán mới
            </p>
            <Link
              href="/listings/create"
              className="mt-6 inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700"
            >
              Tạo bài bán ngay
            </Link>
          </div>
        ) : (
          <>
            <div className="mb-4 text-sm text-gray-600">
              {pagination && (
                <span>
                  Hiển thị {listings.length} / {pagination.total} bài bán
                </span>
              )}
            </div>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {listings.map((listing: any) => (
                <Link
                  key={listing.id}
                  href={`/listings/${listing.id}`}
                  className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
                      {getListingTitle(listing)}
                    </h3>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                      {getListingTypeLabel(listing.listingType)}
                    </span>
                  </div>

                  <div className="space-y-2 text-sm text-gray-600">
                    <p>
                      <span className="font-medium">Giá:</span>{" "}
                      <span className="text-primary-600 font-semibold">
                        {formatPrice(listing.price)}
                      </span>
                    </p>
                    <p>
                      <span className="font-medium">Tình trạng:</span>{" "}
                      {getConditionLabel(listing.condition)}
                    </p>
                    {listing.comic?.publisher && (
                      <p>
                        <span className="font-medium">NXB:</span>{" "}
                        {listing.comic.publisher.name}
                      </p>
                    )}
                    {listing.editionInfo && (
                      <p>
                        <span className="font-medium">Phiên bản:</span>{" "}
                        {listing.editionInfo}
                      </p>
                    )}
                    {listing.giftsIncluded && listing.giftsIncluded.length > 0 && (
                      <p>
                        <span className="font-medium">Quà tặng:</span>{" "}
                        {listing.giftsIncluded.join(", ")}
                      </p>
                    )}
                    {listing.volume?.gifts && listing.volume.gifts.length > 0 && (
                      <p className="flex items-center gap-1">
                        <Gift className="h-4 w-4 text-yellow-500" />
                        <span className="font-medium">Quà kèm tập:</span>{" "}
                        {listing.volume.gifts.map((g: any) => g.name).join(", ")}
                      </p>
                    )}
                  </div>

                  <div className="mt-4 pt-4 border-t flex items-center justify-between">
                    <span className="text-xs text-gray-500">
                      {new Date(listing.createdAt).toLocaleDateString("vi-VN")}
                    </span>
                    <span className="text-sm text-primary-600 font-medium">
                      Xem chi tiết →
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
