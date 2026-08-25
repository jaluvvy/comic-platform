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
  const type = searchParams.get("type");

  const where: any = { status };

  if (q) {
    where.OR = [
      { comic: { title: { contains: q, mode: "insensitive" } } },
      { volume: { title: { contains: q, mode: "insensitive" } } },
      { gift: { name: { contains: q, mode: "insensitive" } } },
    ];
  }

  if (condition) {
    where.condition = condition;
  }

  if (type) {
    where.listingType = type;
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

  try {
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
          volume: {
            include: {
              comic: {
                include: {
                  publisher: {
                    select: { id: true, name: true, slug: true },
                  },
                },
              },
              gifts: true,
            },
          },
          gift: true,
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
  } catch (error) {
    console.error("Database error, falling back to mock listings:", error);
    const mockListings = [
      {
        id: "listing-1",
        userId: "user-1",
        comicId: "comic-1",
        comic: { id: "comic-1", title: "(Tập lẻ) Fullmetal Alchemist - Cang giả kim thuật sư", publisher: { id: "pub-1", name: "NXB Kim Đồng", slug: "nxb-kim-dong" } },
        volumeId: "vol-2",
        volume: { id: "vol-2", title: "Tập 02", price: 67500, coverImage: "https://bizweb.dktcdn.net/100/576/749/products/1c12b69f-c446-41d1-9635-e1a30e2abaed.jpg", available: true, gifts: [] },
        giftId: null,
        gift: null,
        listingType: "volume",
        price: 65000,
        condition: "tot",
        editionInfo: null,
        giftsIncluded: [],
        intro: "Sách còn mới, không trầy xước",
        outro: null,
        status: "active",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      }
    ];
    return NextResponse.json({
      data: mockListings,
      pagination: { page, limit, total: 1, totalPages: 1 },
      mock: true,
    });
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { comicId, volumeId, giftId, listingType, price, condition, editionInfo, giftsIncluded, intro, outro, userId, status } = body;

    if (!userId || !price) {
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 }
      );
    }

    const listing = await prisma.listing.create({
      data: {
        comicId: comicId || null,
        volumeId: volumeId || null,
        giftId: giftId || null,
        listingType: listingType || "volume",
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
        volume: {
          include: {
            comic: {
              include: {
                publisher: {
                  select: { id: true, name: true, slug: true },
                },
              },
            },
            gifts: true,
          },
        },
        gift: true,
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
