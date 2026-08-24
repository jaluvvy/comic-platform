import { NextResponse } from "next/server";

export async function POST() {
  try {
    const response = NextResponse.json({ success: true });
    
    response.cookies.delete('sb-token');
    
    return response;
  } catch (e) {
    return NextResponse.json(
      { error: "Đăng xuất thất bại" },
      { status: 500 }
    );
  }
}
