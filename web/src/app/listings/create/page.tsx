"use client";

import { useState } from "react";
import { supabase } from "@/lib/supabase";
import { useRouter } from "next/navigation";
import Header from "@/components/Header";

export default function CreateListingPage() {
  const [comicId, setComicId] = useState("");
  const [price, setPrice] = useState("");
  const [condition, setCondition] = useState("tot");
  const [editionInfo, setEditionInfo] = useState("");
  const [giftsIncluded, setGiftsIncluded] = useState("");
  const [intro, setIntro] = useState("");
  const [outro, setOutro] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        router.push("/login");
        return;
      }

      const { data, error } = await supabase
        .from("listings")
        .insert({
          comic_id: comicId,
          price: parseInt(price),
          condition,
          edition_info: editionInfo || null,
          gifts_included: giftsIncluded ? giftsIncluded.split(",").map(g => g.trim()) : [],
          intro: intro || null,
          outro: outro || null,
          user_id: session.user.id,
        })
        .select()
        .single();

      if (error) {
        setError(error.message);
        return;
      }

      router.push("/listings");
    } catch (e) {
      setError("Tạo bài bán thất bại");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Tạo bài bán mới</h1>

          <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-sm border p-6 space-y-6">
            {error && (
              <div className="rounded-md bg-red-50 p-4">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            <div>
              <label htmlFor="comicId" className="block text-sm font-medium text-gray-700">
                Comic ID
              </label>
              <input
                id="comicId"
                type="text"
                required
                value={comicId}
                onChange={(e) => setComicId(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                placeholder="Nhập Comic ID từ thư viện"
              />
            </div>

            <div>
              <label htmlFor="price" className="block text-sm font-medium text-gray-700">
                Giá bán (VNĐ)
              </label>
              <input
                id="price"
                type="number"
                required
                min="0"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <div>
              <label htmlFor="condition" className="block text-sm font-medium text-gray-700">
                Tình trạng sách
              </label>
              <select
                id="condition"
                value={condition}
                onChange={(e) => setCondition(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="moi">Mới</option>
                <option value="tot">Tốt</option>
                <option value="binh_thuong">Bình thường</option>
                <option value="cu">Cũ</option>
              </select>
            </div>

            <div>
              <label htmlFor="editionInfo" className="block text-sm font-medium text-gray-700">
                Thông tin phiên bản (tùy chọn)
              </label>
              <input
                id="editionInfo"
                type="text"
                value={editionInfo}
                onChange={(e) => setEditionInfo(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                placeholder="Ví dụ: Tái bản 2024, Bản in đầu..."
              />
            </div>

            <div>
              <label htmlFor="giftsIncluded" className="block text-sm font-medium text-gray-700">
                Quà tặng kèm (phân cách bằng dấu phẩy)
              </label>
              <input
                id="giftsIncluded"
                type="text"
                value={giftsIncluded}
                onChange={(e) => setGiftsIncluded(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                placeholder="Ví dụ: Postcard, Sticker, Bookmark"
              />
            </div>

            <div>
              <label htmlFor="intro" className="block text-sm font-medium text-gray-700">
                Giới thiệu (tùy chọn)
              </label>
              <textarea
                id="intro"
                rows={3}
                value={intro}
                onChange={(e) => setIntro(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                placeholder="Mô tả thêm về tình trạng sách..."
              />
            </div>

            <div>
              <label htmlFor="outro" className="block text-sm font-medium text-gray-700">
                Kết thúc (tùy chọn)
              </label>
              <textarea
                id="outro"
                rows={3}
                value={outro}
                onChange={(e) => setOutro(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                placeholder="Lời nhắn cuối cùng..."
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
            >
              {loading ? "Đang tạo..." : "Tạo bài bán"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
