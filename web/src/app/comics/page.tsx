import { ComicGrid } from "@/components/ComicGrid";
import { SearchBar } from "@/components/SearchBar";

interface ComicsPageProps {
  searchParams: Promise<{ q?: string; publisher?: string; genre?: string }>;
}

async function getComics(searchParams: { q?: string; publisher?: string; genre?: string }) {
  try {
    const baseUrl = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";
    const params = new URLSearchParams();
    if (searchParams.q) params.set("q", searchParams.q);
    if (searchParams.publisher) params.set("publisher", searchParams.publisher);

    const res = await fetch(`${baseUrl}/api/comics?${params.toString()}`, {
      next: { revalidate: 30 },
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

async function getPublishers() {
  try {
    const baseUrl = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";
    const res = await fetch(`${baseUrl}/api/publishers`, {
      next: { revalidate: 60 },
    });
    if (res.ok) {
      const data = await res.json();
      return data.data || [];
    }
  } catch (e) {
    console.error("Failed to fetch publishers:", e);
  }
  return [];
}

export const dynamic = "force-dynamic";

export default async function ComicsPage({ searchParams }: ComicsPageProps) {
  const params = await searchParams;
  const [comics, publishers] = await Promise.all([
    getComics(params),
    getPublishers(),
  ]);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Thư viện truyện</h1>
          <p className="text-gray-600">
            Khám phá {comics.length} đầu truyện từ các nhà xuất bản
          </p>
        </div>

        <div className="mb-6">
          <SearchBar publishers={publishers} />
        </div>

        <ComicGrid comics={comics} />
      </div>
    </div>
  );
}
