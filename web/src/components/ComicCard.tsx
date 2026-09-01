"use client";

import Link from "next/link";
import Image from "next/image";
import { ExternalLink, Package } from "lucide-react";

interface Comic {
  id: string;
  title: string;
  slug: string;
  price: number | null;
  originalPrice: number | null;
  coverImage: string | null;
  authors: string[];
  series: string | null;
  pages: number | null;
  format: string | null;
  publisher: {
    name: string;
    slug: string;
  };
  volumes: {
    gifts: {
      id: string;
    }[];
  }[];
}

interface ComicCardProps {
  comic: Comic;
}

export function ComicCard({ comic }: ComicCardProps) {
  const priceFormatted = comic.price 
    ? new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(comic.price)
    : "Liên hệ";

  return (
    <Link href={`/comics/${comic.id}`} className="group">
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden hover:shadow-md transition-shadow">
        <div className="relative aspect-[3/4] bg-gray-100">
          {comic.coverImage ? (
            <Image
              src={comic.coverImage}
              alt={comic.title}
              fill
              className="object-cover group-hover:scale-105 transition-transform duration-300"
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 25vw"
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <Package className="h-12 w-12 text-gray-400" />
            </div>
          )}
          {comic.volumes.some(v => v.gifts.length > 0) && (
            <div className="absolute top-2 right-2 bg-yellow-400 text-yellow-900 text-xs font-bold px-2 py-1 rounded-full">
              Quà tặng
            </div>
          )}
        </div>
        
        <div className="p-4">
          <h3 className="font-semibold text-gray-900 line-clamp-2 mb-1 group-hover:text-primary-600 transition-colors">
            {comic.title}
          </h3>
          
          <p className="text-sm text-gray-500 mb-2">
            {comic.publisher.name}
          </p>
          
          {comic.series && (
            <p className="text-xs text-gray-400 mb-2">
              Bộ: {comic.series}
            </p>
          )}
          
          <div className="flex items-center justify-between">
            <div>
              <p className="text-lg font-bold text-red-600">{priceFormatted}</p>
              {comic.originalPrice && comic.originalPrice > comic.price! && (
                <p className="text-xs text-gray-400 line-through">
                  {new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(comic.originalPrice)}
                </p>
              )}
            </div>
            
            {comic.authors.length > 0 && (
              <p className="text-xs text-gray-500 text-right max-w-[100px] truncate">
                {comic.authors[0]}
              </p>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}
