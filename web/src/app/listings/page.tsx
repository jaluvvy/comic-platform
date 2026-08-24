import Link from "next/link";
import { Metadata } from "next";
import { BookOpen, Filter, Search } from "lucide-react";
import ListingFilters from "./ListingFilters";

export const metadata: Metadata = {
  title: "Danh sách bán | ComicPlatform",
  description: "Xem danh sách truyện tranh đang được bán",
};

async function getListings(searchParams: Record<string, string>) {
  try {
    const baseUrl = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";
    const params = new URLSearchParams();
    
    params.set("limit", "20");
    if (searchParams.q) params.set("q", searchParams.q);
    if (searchParams.condition) params.set("condition", searchParams.condition);
    if (searchParams.minPrice) params.set("minPrice", searchParams.minPrice);
    if (searchParams.maxPrice) params.set("maxPrice", searchParams.maxPrice);

    const res = await fetch(`${baseUrl}/api/listings?${params.toString()}`, {
      next: { revalidate: 30 },
    });
    if (res.ok) {
      const data = await res.json();
      return { listings: data.data || [], pagination: data.pagination };
    }
  } catch (e) {
    console.error("Failed to fetch listings:", e);
  }
  return { listings: [], pagination: null };
}

export default async function ListingsPage({
  searchParams,
}: {
  searchParams: Record<string, string>;
}) {
  const { listings, pagination } = await getListings(searchParams);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat("vi-VN").format(price) + " VND";
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
              Tìm và mua truyện tranh từ cộng đồng
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

        {listings.length === 0 ? (
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
                      {listing.comic.title}
                    </h3>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                      {getConditionLabel(listing.condition)}
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
                      <span className="font-medium">NXB:</span>{" "}
                      {listing.comic.publisher?.name || "N/A"}
                    </p>
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
