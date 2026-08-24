"use client";

import { useState, useEffect } from "react";
import { createClient } from "@/lib/supabase";
import { useRouter } from "next/navigation";
import Link from "next/link";

type Comic = {
  id: string;
  title: string;
  publisher: string;
  reasons?: string[];
};

type ReviewData = {
  summary: {
    total: number;
    vietnamese: number;
    manga: number;
    anime: number;
    light_novel: number;
  };
  vietnamese_comics: Comic[];
  manga_comics: Comic[];
  anime_comics: Comic[];
  light_novel_comics: Comic[];
};

export default function ReviewPage() {
  const [data, setData] = useState<ReviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [reviewing, setReviewing] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [action, setAction] = useState<"keep" | "remove" | null>(null);
  const [stats, setStats] = useState({ reviewed: 0, kept: 0, removed: 0 });
  const [isAdmin, setIsAdmin] = useState(false);
  const router = useRouter();

  useEffect(() => {
    checkAdmin();
  }, []);

  const checkAdmin = async () => {
    const supabase = createClient();
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) {
      router.push("/login");
      return;
    }
    setIsAdmin(true);
    loadData();
  };

  const loadData = async () => {
    try {
      const res = await fetch("/api/admin/review-comics");
      if (res.ok) {
        const data = await res.json();
        setData(data);
      }
    } catch (e) {
      console.error("Failed to load review data:", e);
    } finally {
      setLoading(false);
    }
  };

  const allCandidates = data ? [
    ...data.manga_comics.map(c => ({ ...c, category: "manga" })),
    ...data.light_novel_comics.map(c => ({ ...c, category: "light_novel" })),
  ] : [];

  const currentComic = allCandidates[currentIndex] || null;

  const handleReview = async (decision: "keep" | "remove") => {
    if (!currentComic) return;
    
    setAction(decision);
    setReviewing(true);

    try {
      const res = await fetch("/api/admin/review-comics", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          comicId: currentComic.id,
          decision,
          category: currentComic.category,
        }),
      });

      if (res.ok) {
        setStats(prev => ({
          reviewed: prev.reviewed + 1,
          kept: decision === "keep" ? prev.kept + 1 : prev.kept,
          removed: decision === "remove" ? prev.removed + 1 : prev.removed,
        }));
        setCurrentIndex(prev => prev + 1);
        setAction(null);
      }
    } catch (e) {
      console.error("Review failed:", e);
    } finally {
      setReviewing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">Đang tải...</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center text-red-600">Không thể tải dữ liệu review</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Review Comics</h1>
            <p className="text-gray-600 mt-1">
              Phân loại truyện tranh: Giữ lại (Vietnamese) hoặc Xóa (Manga/Anime/Light Novel)
            </p>
          </div>
          <Link
            href="/"
            className="text-sm text-primary-600 hover:text-primary-500"
          >
            ← Quay lại trang chủ
          </Link>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-sm border p-4">
            <p className="text-sm text-gray-600">Tổng cần review</p>
            <p className="text-2xl font-bold text-gray-900">{allCandidates.length}</p>
          </div>
          <div className="bg-white rounded-lg shadow-sm border p-4">
            <p className="text-sm text-gray-600">Đã review</p>
            <p className="text-2xl font-bold text-primary-600">{stats.reviewed}</p>
          </div>
          <div className="bg-white rounded-lg shadow-sm border p-4">
            <p className="text-sm text-gray-600">Giữ lại (Vietnamese)</p>
            <p className="text-2xl font-bold text-green-600">{stats.kept}</p>
          </div>
          <div className="bg-white rounded-lg shadow-sm border p-4">
            <p className="text-sm text-gray-600">Xóa (Manga/Anime/LN)</p>
            <p className="text-2xl font-bold text-red-600">{stats.removed}</p>
          </div>
        </div>

        {/* Progress */}
        <div className="bg-white rounded-lg shadow-sm border p-4 mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Tiến độ</span>
            <span className="text-sm text-gray-900">
              {currentIndex} / {allCandidates.length}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-primary-600 h-2 rounded-full transition-all"
              style={{ width: `${(currentIndex / allCandidates.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Review Card */}
        {currentComic ? (
          <div className="bg-white rounded-lg shadow-sm border p-6 md:p-8">
            <div className="mb-6">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800 mb-4">
                {currentComic.category === "manga" ? "Manga" : "Light Novel"}
              </span>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                {currentComic.title}
              </h2>
              <p className="text-gray-600">
                NXB: {currentComic.publisher || "N/A"}
              </p>
              {currentComic.reasons && currentComic.reasons.length > 0 && (
                <div className="mt-4">
                  <p className="text-sm text-gray-500 mb-2">Lý do được đánh giá:</p>
                  <ul className="list-disc list-inside text-sm text-gray-600">
                    {currentComic.reasons.map((reason, idx) => (
                      <li key={idx}>{reason}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={() => handleReview("keep")}
                disabled={reviewing}
                className="flex-1 inline-flex items-center justify-center px-6 py-3 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                {reviewing && action === "keep" ? "Đang xử lý..." : "✓ Giữ lại (Vietnamese)"}
              </button>
              <button
                onClick={() => handleReview("remove")}
                disabled={reviewing}
                className="flex-1 inline-flex items-center justify-center px-6 py-3 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                {reviewing && action === "remove" ? "Đang xử lý..." : "✗ Xóa (Manga/Anime/LN)"}
              </button>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm border p-12 text-center">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              🎉 Hoàn thành review!
            </h3>
            <p className="text-gray-600 mb-6">
              Bạn đã review tất cả {allCandidates.length} truyện.
            </p>
            <div className="grid grid-cols-3 gap-4 max-w-md mx-auto">
              <div className="bg-green-50 rounded-lg p-4">
                <p className="text-2xl font-bold text-green-600">{stats.kept}</p>
                <p className="text-sm text-gray-600">Giữ lại</p>
              </div>
              <div className="bg-red-50 rounded-lg p-4">
                <p className="text-2xl font-bold text-red-600">{stats.removed}</p>
                <p className="text-sm text-gray-600">Đã xóa</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-2xl font-bold text-gray-600">{stats.reviewed}</p>
                <p className="text-sm text-gray-600">Tổng cộng</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
