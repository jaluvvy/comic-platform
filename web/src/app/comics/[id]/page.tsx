import { notFound } from "next/navigation";
import Image from "next/image";
import prisma from "@/lib/prisma";
import { MapPin, Calendar, Package, Tag, ExternalLink } from "lucide-react";

interface ComicDetailPageProps {
  params: Promise<{ id: string }>;
}

async function getComic(id: string) {
  const comic = await prisma.comic.findUnique({
    where: { id },
    include: {
      publisher: true,
      volumes: {
        include: {
          gifts: {
            orderBy: { createdAt: "desc" },
          },
        },
      },
    },
  });
  
  if (!comic) return null;
  return comic;
}

export async function generateMetadata({ params }: ComicDetailPageProps) {
  const comic = await getComic((await params).id);
  if (!comic) return {};
  
  return {
    title: `${comic.title} - ComicPlatform`,
    description: comic.description || comic.title,
  };
}

export default async function ComicDetailPage({ params }: ComicDetailPageProps) {
  const { id } = await params;
  const comic = await getComic(id);
  
  if (!comic) {
    notFound();
  }

  const priceFormatted = comic.price 
    ? new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(comic.price)
    : "Liên hệ";

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <div className="md:flex">
            {/* Cover Image */}
            <div className="md:w-1/3 lg:w-1/4">
              <div className="relative aspect-[3/4] bg-gray-100">
                {comic.coverImage ? (
                  <Image
                    src={comic.coverImage}
                    alt={comic.title}
                    fill
                    className="object-cover"
                    sizes="(max-width: 768px) 100vw, 33vw"
                    priority
                  />
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <Package className="h-24 w-24 text-gray-400" />
                  </div>
                )}
              </div>
            </div>

            {/* Details */}
            <div className="md:w-2/3 lg:w-3/4 p-6 md:p-8">
              <div className="mb-4">
                <span className="inline-block bg-primary-100 text-primary-800 text-sm font-medium px-3 py-1 rounded-full">
                  {comic.publisher.name}
                </span>
              </div>

              <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-4">
                {comic.title}
              </h1>

              <div className="flex flex-wrap items-center gap-4 mb-6">
                <div>
                  <p className="text-sm text-gray-500">Giá bán</p>
                  <p className="text-2xl font-bold text-red-600">{priceFormatted}</p>
                  {comic.originalPrice && comic.originalPrice > comic.price! && (
                    <p className="text-sm text-gray-400 line-through">
                      {new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(comic.originalPrice)}
                    </p>
                  )}
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6 mb-6">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Thông tin cơ bản</h3>
                  <dl className="space-y-2 text-sm">
                    {comic.isbn && (
                      <div className="flex">
                        <dt className="w-24 text-gray-500">ISBN:</dt>
                        <dd className="text-gray-900">{comic.isbn}</dd>
                      </div>
                    )}
                    {comic.sku && (
                      <div className="flex">
                        <dt className="w-24 text-gray-500">SKU:</dt>
                        <dd className="text-gray-900">{comic.sku}</dd>
                      </div>
                    )}
                    {comic.pages && (
                      <div className="flex">
                        <dt className="w-24 text-gray-500">Số trang:</dt>
                        <dd className="text-gray-900">{comic.pages}</dd>
                      </div>
                    )}
                    {comic.format && (
                      <div className="flex">
                        <dt className="w-24 text-gray-500">Định dạng:</dt>
                        <dd className="text-gray-900">{comic.format}</dd>
                      </div>
                    )}
                    {comic.dimensions && (
                      <div className="flex">
                        <dt className="w-24 text-gray-500">Kích thước:</dt>
                        <dd className="text-gray-900">{comic.dimensions}</dd>
                      </div>
                    )}
                    {comic.weight && (
                      <div className="flex">
                        <dt className="w-24 text-gray-500">Trọng lượng:</dt>
                        <dd className="text-gray-900">{comic.weight}</dd>
                      </div>
                    )}
                    {comic.editionType && (
                      <div className="flex">
                        <dt className="w-24 text-gray-500">Phiên bản:</dt>
                        <dd className="text-gray-900">
                          {comic.editionType === "tai_ban" 
                            ? `Tái bản ${comic.editionYear ? `(${comic.editionYear})` : ""}`
                            : "Bản in đầu"}
                        </dd>
                      </div>
                    )}
                  </dl>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Chi tiết khác</h3>
                  <dl className="space-y-2 text-sm">
                    {comic.targetAudience && (
                      <div className="flex">
                        <dt className="w-24 text-gray-500">Đối tượng:</dt>
                        <dd className="text-gray-900">{comic.targetAudience}</dd>
                      </div>
                    )}
                    {comic.series && (
                      <div className="flex">
                        <dt className="w-24 text-gray-500">Bộ sách:</dt>
                        <dd className="text-gray-900">{comic.series}</dd>
                      </div>
                    )}
                    {comic.authors.length > 0 && (
                      <div className="flex">
                        <dt className="w-24 text-gray-500">Tác giả:</dt>
                        <dd className="text-gray-900">{comic.authors.join(", ")}</dd>
                      </div>
                    )}
                  </dl>
                </div>
              </div>

              {comic.description && (
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-2">Mô tả</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{comic.description}</p>
                </div>
              )}

              {/* Gifts Section */}
              {comic.volumes.some(v => v.gifts.length > 0) && (
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <Tag className="h-5 w-5 text-yellow-500" />
                    Quà tặng kèm
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {comic.volumes.flatMap(v => v.gifts).map((gift) => (
                      <div key={gift.id} className="border rounded-lg p-3 bg-gray-50">
                        {gift.imageUrl && (
                          <div className="relative aspect-square bg-white rounded mb-2 overflow-hidden">
                            <Image
                              src={gift.imageUrl}
                              alt={gift.name}
                              fill
                              className="object-contain"
                              sizes="150px"
                            />
                          </div>
                        )}
                        <p className="text-sm font-medium text-gray-900">{gift.name}</p>
                        {gift.isFes && (
                          <span className="inline-block mt-1 text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded">
                            FES/Event
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {comic.url && (
                <div className="pt-4 border-t">
                  <a
                    href={comic.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-primary-600 hover:text-primary-700"
                  >
                    Xem trên NXB Kim Đồng
                    <ExternalLink className="ml-2 h-4 w-4" />
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
