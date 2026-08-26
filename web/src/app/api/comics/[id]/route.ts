import { NextResponse } from "next/server";
import prisma from "@/lib/prisma";
import { mockComics } from "@/lib/mock-data";

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  
  try {
    const comic = await prisma.comic.findUnique({
      where: { id },
      include: {
        publisher: true,
        volumes: {
          include: {
            gifts: {
              orderBy: { createdAt: "desc" },
            },
          },
        },
      },
    });

    if (!comic) {
      return NextResponse.json({ error: "Not found" }, { status: 404 });
    }

    return NextResponse.json({ data: comic });
  } catch (error) {
    console.error("Database error, falling back to mock comic:", error);
    const mock = mockComics.find(c => c.id === id);
    if (!mock) {
      return NextResponse.json({ error: "Not found" }, { status: 404 });
    }
    return NextResponse.json({ data: mock, mock: true });
  }
}
