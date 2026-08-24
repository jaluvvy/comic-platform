import { NextResponse } from "next/server";
import prisma from "@/lib/prisma";

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  
  const comic = await prisma.comic.findUnique({
    where: { id },
    include: {
      publisher: true,
      gifts: {
        orderBy: { createdAt: "desc" },
      },
      eventGifts: {
        include: {
          event: true,
        },
      },
    },
  });

  if (!comic) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  return NextResponse.json({ data: comic });
}
