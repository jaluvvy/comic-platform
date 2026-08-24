import prisma from "@/lib/prisma";
import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const q = searchParams.get("q");
  const condition = searchParams.get("condition");
  const minPrice = searchParams.get("minPrice");
  const maxPrice = searchParams.get("maxPrice");
  const page = parseInt(searchParams.get("page") || "1");
  const limit = parseInt(searchParams.get("limit") || "20");
  const status = searchParams.get("status") || "active";
  const userId = searchParams.get("userId");

  const where: any = { status };

  if (q) {
    where.comic = {
      title: { contains: q, mode: "insensitive" },
    };
  }

  if (condition) {
    where.condition = condition;
  }

  if (minPrice) {
    where.price = { ...where.price, gte: parseInt(minPrice) };
  }

  if (maxPrice) {
    where.price = { ...where.price, lte: parseInt(maxPrice) };
  }

  if (userId) {
    where.userId = userId;
  }

  const [listings, total] = await Promise.all([
    prisma.listing.findMany({
      where,
      include: {
        user: {
          select: { id: true, name: true, email: true },
        },
        comic: {
          include: {
            publisher: {
              select: { id: true, name: true, slug: true },
            },
          },
        },
      },
      orderBy: { createdAt: "desc" },
      skip: (page - 1) * limit,
      take: limit,
    }),
    prisma.listing.count({ where }),
  ]);

  return NextResponse.json({
    data: listings,
    pagination: {
      page,
      limit,
      total,
      totalPages: Math.ceil(total / limit),
    },
  });
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { comicId, price, condition, editionInfo, giftsIncluded, intro, outro, userId, status } = body;

    if (!comicId || !price || !userId) {
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 }
      );
    }

    const listing = await prisma.listing.create({
      data: {
        comicId,
        price,
        condition: condition || "tot",
        editionInfo,
        giftsIncluded: giftsIncluded || [],
        intro,
        outro,
        userId,
        status: status || "active",
      },
      include: {
        user: {
          select: { id: true, name: true, email: true },
        },
        comic: {
          include: {
            publisher: {
              select: { id: true, name: true, slug: true },
            },
          },
        },
      },
    });

    return NextResponse.json({ data: listing }, { status: 201 });
  } catch (e) {
    console.error("Error creating listing:", e);
    return NextResponse.json(
      { error: "Failed to create listing", details: String(e) },
      { status: 500 }
    );
  }
}
