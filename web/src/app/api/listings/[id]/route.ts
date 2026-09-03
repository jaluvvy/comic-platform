import prisma from "@/lib/prisma";
import { supabaseListing } from "@/lib/supabase-helpers";
import { NextResponse } from "next/server";

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;

  try {
    const listing = await prisma.listing.findUnique({
      where: { id },
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
            gifts: {
              select: { id: true, name: true, imageUrl: true, isFes: true },
            },
          },
        },
        gift: true,
      },
    });

    if (!listing) {
      return NextResponse.json({ error: "Not found" }, { status: 404 });
    }

    return NextResponse.json({ data: listing });
  } catch (error) {
    console.error("Prisma error, falling back to Supabase REST:", error);
    try {
      const listing = await supabaseListing(id);
      if (!listing) {
        return NextResponse.json({ error: "Not found" }, { status: 404 });
      }
      return NextResponse.json({ data: listing });
    } catch (supabaseError) {
      console.error("Supabase REST error:", supabaseError);
      return NextResponse.json({ error: "Failed to fetch listing" }, { status: 500 });
    }
  }
}

export async function DELETE(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;

  await prisma.listing.delete({
    where: { id },
  });

  return NextResponse.json({ success: true });
}

export async function PATCH(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const body = await request.json();

  const listing = await prisma.listing.update({
    where: { id },
    data: {
      ...(body.price && { price: body.price }),
      ...(body.condition && { condition: body.condition }),
      ...(body.editionInfo !== undefined && { editionInfo: body.editionInfo }),
      ...(body.giftsIncluded && { giftsIncluded: body.giftsIncluded }),
      ...(body.intro !== undefined && { intro: body.intro }),
      ...(body.outro !== undefined && { outro: body.outro }),
      ...(body.status && { status: body.status }),
    },
  });

  return NextResponse.json({ data: listing });
}
