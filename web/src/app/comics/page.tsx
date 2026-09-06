import { ComicGrid } from "@/components/ComicGrid";
import { SearchBar } from "@/components/SearchBar";
import prisma from "@/lib/prisma";
import { supabaseComics, supabasePublishers } from "@/lib/supabase-helpers";

interface ComicsPageProps {
  searchParams: Promise<{ q?: string; publisher?: string; genre?: string }>;
}

async function getComics(searchParams: { q?: string; publisher?: string; genre?: string }) {
  const where: any = {};
  
  if (searchParams.q) {
    where.OR = [
      { title: { contains: searchParams.q, mode: "insensitive" } },
      { authors: { has: searchParams.q } },
      { series: { contains: searchParams.q, mode: "insensitive" } },
    ];
  }
  
  if (searchParams.publisher) {
    where.publisher = { slug: searchParams.publisher };
  }

  try {
    return await prisma.comic.findMany({
      where,
      include: {
        publisher: {
          select: { id: true, name: true, slug: true },
        },
        volumes: {
          include: {
            gifts: {
              select: { id: true, name: true, imageUrl: true, isFes: true },
            },
          },
        },
      },
      orderBy: { updatedAt: "desc" },
      take: 50,
    });
  } catch (error) {
    console.error("Prisma error, falling back to Supabase REST:", error);
    const result = await supabaseComics({ q: searchParams.q, publisher: searchParams.publisher, page: 1, limit: 50 });
    return result.data || [];
  }
}

async function getPublishers() {
  try {
    return await prisma.publisher.findMany({
      select: { id: true, name: true, slug: true },
      orderBy: { name: "asc" },
    });
  } catch (error) {
    console.error("Prisma error, falling back to Supabase REST:", error);
    return await supabasePublishers();
  }
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
