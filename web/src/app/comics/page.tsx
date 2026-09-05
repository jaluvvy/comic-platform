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
      return { comics: data.data || [], error: null as string | null };
    }
    const text = await res.text();
    return { comics: [] as any[], error: `Failed to fetch comics (${res.status}): ${text}` };
  } catch (e: any) {
    return { comics: [] as any[], error: e?.message || "Failed to fetch comics" };
  }
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
  const [result, publishers] = await Promise.all([
    getComics(params),
    getPublishers(),
  ]);
  const comics = result.comics;
  const error = result.error;

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

        {error && (
          <div className="mb-6 rounded-md bg-red-50 p-4 text-sm text-red-800">
            {error}
          </div>
        )}

        <ComicGrid comics={comics} />
      </div>
    </div>
  );
}
