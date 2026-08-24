import { ComicGrid } from "@/components/ComicGrid";
import { SearchBar } from "@/components/SearchBar";
import prisma from "@/lib/prisma";

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

  return prisma.comic.findMany({
    where,
    include: {
      publisher: true,
      gifts: true,
    },
    orderBy: { updatedAt: "desc" },
    take: 50,
  });
}

async function getPublishers() {
  return prisma.publisher.findMany({
    select: { id: true, name: true, slug: true },
    orderBy: { name: "asc" },
  });
}

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
