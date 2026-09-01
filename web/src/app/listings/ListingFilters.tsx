"use client";

import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { Search, Filter } from "lucide-react";

export default function ListingFilters() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const params = new URLSearchParams(searchParams.toString());

    const q = formData.get("q") as string;
    if (q) {
      params.set("q", q);
    } else {
      params.delete("q");
    }

    const condition = formData.get("condition") as string;
    if (condition) {
      params.set("condition", condition);
    } else {
      params.delete("condition");
    }

    const minPrice = formData.get("minPrice") as string;
    const maxPrice = formData.get("maxPrice") as string;
    if (minPrice) params.set("minPrice", minPrice); else params.delete("minPrice");
    if (maxPrice) params.set("maxPrice", maxPrice); else params.delete("maxPrice");

    router.push(`${pathname}?${params.toString()}`);
  };

  const handleReset = () => {
    router.push(pathname);
  };

  return (
    <form onSubmit={handleSearch} className="bg-white rounded-lg shadow-sm border p-4 mb-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="md:col-span-2">
          <label htmlFor="q" className="block text-sm font-medium text-gray-700 mb-1">
            Tìm kiếm
          </label>
          <div className="relative">
            <input
              type="text"
              id="q"
              name="q"
              defaultValue={searchParams.get("q") || ""}
              placeholder="Tên truyện, tác giả..."
              className="block w-full px-3 py-2 pl-10 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            />
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
          </div>
        </div>

        <div>
          <label htmlFor="condition" className="block text-sm font-medium text-gray-700 mb-1">
            Tình trạng
          </label>
          <select
            id="condition"
            name="condition"
            defaultValue={searchParams.get("condition") || ""}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">Tất cả</option>
            <option value="moi">Mới</option>
            <option value="tot">Tốt</option>
            <option value="binh_thuong">Bình thường</option>
            <option value="cu">Cũ</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Khoảng giá (VNĐ)
          </label>
          <div className="flex items-center gap-2">
            <input
              type="number"
              name="minPrice"
              defaultValue={searchParams.get("minPrice") || ""}
              placeholder="Từ"
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            />
            <span className="text-gray-500">-</span>
            <input
              type="number"
              name="maxPrice"
              defaultValue={searchParams.get("maxPrice") || ""}
              placeholder="Đến"
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between">
        <button
          type="submit"
          className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700"
        >
          <Filter className="mr-2 h-4 w-4" />
          Lọc
        </button>
        <button
          type="button"
          onClick={handleReset}
          className="text-sm text-gray-600 hover:text-gray-900"
        >
          Xóa bộ lọc
        </button>
      </div>
    </form>
  );
}
