"use client";

import { useRouter, usePathname, useSearchParams } from "next/navigation";
import { Search, X } from "lucide-react";
import { FormEvent } from "react";

interface Publisher {
  id: string;
  name: string;
  slug: string;
}

interface SearchBarProps {
  publishers: Publisher[];
}

export function SearchBar({ publishers }: SearchBarProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const q = formData.get("q") as string;
    const publisher = formData.get("publisher") as string;
    
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (publisher) params.set("publisher", publisher);
    
    router.push(`${pathname}?${params.toString()}`);
  };

  const clearFilters = () => {
    router.push(pathname);
  };

  const hasFilters = searchParams.has("q") || searchParams.has("publisher");

  return (
    <form onSubmit={handleSubmit} className="bg-white p-4 rounded-lg shadow-sm border">
      <div className="flex flex-col md:flex-row gap-3">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            name="q"
            defaultValue={searchParams.get("q") || ""}
            placeholder="Tìm kiếm truyện, tác giả, bộ sách..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          />
        </div>
        
        <select
          name="publisher"
          defaultValue={searchParams.get("publisher") || ""}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none bg-white"
        >
          <option value="">Tất cả NXB</option>
          {publishers.map((pub) => (
            <option key={pub.id} value={pub.slug}>
              {pub.name}
            </option>
          ))}
        </select>

        <button
          type="submit"
          className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Tìm kiếm
        </button>

        {hasFilters && (
          <button
            type="button"
            onClick={clearFilters}
            className="px-4 py-2 text-gray-600 hover:text-gray-900 flex items-center gap-1"
          >
            <X className="h-4 w-4" />
            Xóa lọc
          </button>
        )}
      </div>
    </form>
  );
}
