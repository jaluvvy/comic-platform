import prisma from "@/lib/prisma";
import { NextResponse } from "next/server";

export async function GET() {
  try {
    const fs = await import("fs");
    const path = require("path");
    
    const reviewDataPath = path.join(process.cwd(), "scripts", "comics_review.json");
    
    if (!fs.existsSync(reviewDataPath)) {
      return NextResponse.json(
        { error: "Review data not found. Run scripts/review_comics.py first." },
        { status: 404 }
      );
    }

    const data = JSON.parse(fs.readFileSync(reviewDataPath, "utf-8"));
    return NextResponse.json(data);
  } catch (e) {
    console.error("Error loading review data:", e);
    return NextResponse.json(
      { error: "Failed to load review data" },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { comicId, decision, category } = body;

    if (!comicId || !decision) {
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 }
      );
    }

    if (decision === "remove") {
      // Delete related listings and comic
      await prisma.listing.deleteMany({
        where: { comicId }
      });
      
      await prisma.comic.delete({
        where: { id: comicId }
      });
      
      console.log(`Removed comic: ${comicId} (${category})`);
    } else if (decision === "keep") {
      // Mark as reviewed and kept
      console.log(`Kept comic: ${comicId} (${category})`);
    }

    return NextResponse.json({ success: true });
  } catch (e) {
    console.error("Error processing review:", e);
    return NextResponse.json(
      { error: "Failed to process review", details: String(e) },
      { status: 500 }
    );
  }
}
