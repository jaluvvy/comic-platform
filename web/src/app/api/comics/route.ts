import { NextResponse } from "next/server";
import prisma from "@/lib/prisma";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const q = searchParams.get("q");
  const publisher = searchParams.get("publisher");
  const page = parseInt(searchParams.get("page") || "1");
  const limit = parseInt(searchParams.get("limit") || "20");

  const where: any = {};
  
  if (q) {
    where.OR = [
      { title: { contains: q, mode: "insensitive" } },
      { authors: { has: q } },
      { series: { contains: q, mode: "insensitive" } },
    ];
  }
  
  if (publisher) {
    where.publisher = { slug: publisher };
  }

  const [comics, total] = await Promise.all([
    prisma.comic.findMany({
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
      skip: (page - 1) * limit,
      take: limit,
    }),
    prisma.comic.count({ where }),
  ]);

  return NextResponse.json({
    data: comics,
    pagination: {
      page,
      limit,
      total,
      totalPages: Math.ceil(total / limit),
    },
  });
}
