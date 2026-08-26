import { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { BookOpen, ArrowLeft, ShoppingCart, User, Tag, Gift, FileText } from "lucide-react";

export const metadata: Metadata = {
  title: "Chi tiết bài bán | ComicPlatform",
};

async function getListing(id: string) {
  try {
    const baseUrl = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";
    const res = await fetch(`${baseUrl}/api/listings/${id}`, {
      next: { revalidate: 30 },
    });
    if (res.ok) {
      const data = await res.json();
      return data.data;
    }
  } catch (e) {
    console.error("Failed to fetch listing:", e);
  }
  return null;
}

async function getComics() {
  try {
    const baseUrl = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";
    const res = await fetch(`${baseUrl}/api/comics?limit=100`, {
      next: { revalidate: 60 },
    });
    if (res.ok) {
      const data = await res.json();
      return data.data || [];
    }
  } catch (e) {
    console.error("Failed to fetch comics:", e);
  }
  return [];
}

export default async function ListingDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const listing = await getListing(id);

  if (!listing) {
    notFound();
  }

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
        <Link
          href="/listings"
          className="inline-flex items-center text-sm text-gray-600 hover:text-primary-600 mb-6"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Quay lại danh sách
        </Link>

        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <div className="p-6 md:p-8">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h1 className="text-2xl md:text-3xl font-bold text-gray-900">
                  {listing.volume?.title || listing.gift?.name || listing.comic?.title || "Không rõ"}
                </h1>
                <p className="text-gray-600 mt-1">
                  {(listing.volume?.comic?.publisher?.name || listing.comic?.publisher?.name || "Ẩn danh")}{" "}
                  {(listing.volume?.comic?.authors?.length || listing.comic?.authors?.length) ? (
                    <>• {(listing.volume?.comic?.authors || listing.comic?.authors || []).join(", ")}</>
                  ) : null}
                </p>
              </div>
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800">
                {getConditionLabel(listing.condition)}
              </span>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              <div className="md:col-span-2 space-y-6">
                {listing.intro && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center mb-2">
                      <FileText className="h-5 w-5 text-gray-400 mr-2" />
                      <h3 className="font-semibold text-gray-900">Giới thiệu</h3>
                    </div>
                    <p className="text-gray-700 whitespace-pre-wrap">
                      {listing.intro}
                    </p>
                  </div>
                )}

                {listing.giftsIncluded && listing.giftsIncluded.length > 0 && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center mb-2">
                      <Gift className="h-5 w-5 text-gray-400 mr-2" />
                      <h3 className="font-semibold text-gray-900">Quà tặng kèm</h3>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {listing.giftsIncluded.map((gift: string, idx: number) => (
                        <span
                          key={idx}
                          className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-primary-50 text-primary-700"
                        >
                          <Tag className="h-3 w-3 mr-1" />
                          {gift}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {listing.outro && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center mb-2">
                      <FileText className="h-5 w-5 text-gray-400 mr-2" />
                      <h3 className="font-semibold text-gray-900">Lời nhắn</h3>
                    </div>
                    <p className="text-gray-700 whitespace-pre-wrap">
                      {listing.outro}
                    </p>
                  </div>
                )}
              </div>

              <div className="space-y-4">
                <div className="bg-primary-50 rounded-lg p-6">
                  <p className="text-sm text-primary-600 font-medium mb-1">
                    Giá bán
                  </p>
                  <p className="text-3xl font-bold text-primary-900">
                    {formatPrice(listing.price)}
                  </p>
                </div>

                {listing.editionInfo && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600 mb-1">Phiên bản</p>
                    <p className="font-medium text-gray-900">
                      {listing.editionInfo}
                    </p>
                  </div>
                )}

                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <User className="h-4 w-4 text-gray-400 mr-2" />
                    <p className="text-sm text-gray-600">Người bán</p>
                  </div>
                  <p className="font-medium text-gray-900">
                    {listing.user?.name || "Ẩn danh"}
                  </p>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Ngày đăng</p>
                  <p className="font-medium text-gray-900">
                    {new Date(listing.createdAt).toLocaleDateString("vi-VN", {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                    })}
                  </p>
                </div>

                <button className="w-full flex items-center justify-center px-4 py-3 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700">
                  <ShoppingCart className="mr-2 h-4 w-4" />
                  Liên hệ người bán
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
