"use client";

import { ComicCard } from "@/components/ComicCard";

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
  gifts: {
    id: string;
    name: string;
    imageUrl: string | null;
    isFes: boolean;
  }[];
}

interface ComicGridProps {
  comics: Comic[];
}

export function ComicGrid({ comics }: ComicGridProps) {
  if (comics.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">Không tìm thấy truyện nào</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
      {comics.map((comic) => (
        <ComicCard key={comic.id} comic={comic} />
      ))}
    </div>
  );
}
