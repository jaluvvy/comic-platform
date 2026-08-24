import { createBrowserClient } from "@/lib/supabase";
import { NextResponse } from "next/server";

export async function GET() {
  try {
    const supabase = createBrowserClient();
    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session) {
      return NextResponse.json({ user: null });
    }
    
    return NextResponse.json({ user: session.user });
  } catch (e) {
    return NextResponse.json({ user: null });
  }
}
