import { NextResponse } from "next/server";
import prisma from "@/lib/prisma";
import { supabaseComic } from "@/lib/supabase-helpers";

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
    console.error("Prisma error, falling back to Supabase REST:", error);
    try {
      const comic = await supabaseComic(id);
      if (!comic) {
        return NextResponse.json({ error: "Not found" }, { status: 404 });
      }
      return NextResponse.json({ data: comic });
    } catch (supabaseError) {
      console.error("Supabase REST error:", supabaseError);
      return NextResponse.json({ error: "Failed to fetch comic" }, { status: 500 });
    }
  }
}
