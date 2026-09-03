import { NextResponse } from "next/server";
import prisma from "@/lib/prisma";
import { supabasePublishers } from "@/lib/supabase-helpers";

export async function GET() {
  try {
    const publishers = await prisma.publisher.findMany({
      select: { id: true, name: true, slug: true },
      orderBy: { name: "asc" },
    });
    return NextResponse.json({ data: publishers });
  } catch (error) {
    console.error("Prisma error, falling back to Supabase REST:", error);
    try {
      const publishers = await supabasePublishers();
      return NextResponse.json({ data: publishers });
    } catch (supabaseError) {
      console.error("Supabase REST error:", supabaseError);
      return NextResponse.json({ error: "Failed to fetch publishers" }, { status: 500 });
    }
  }
}
