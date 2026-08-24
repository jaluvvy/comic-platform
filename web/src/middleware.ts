import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export async function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname;
  
  const protectedRoutes = ['/listings/create', '/listings/manage', '/profile', '/admin'];
  const authRoutes = ['/login', '/register', '/forgot-password', '/reset-password'];
  
  const isProtectedRoute = protectedRoutes.some(route => path.startsWith(route));
  const isAuthRoute = authRoutes.some(route => path.startsWith(route));
  
  const token = request.cookies.get('sb-token')?.value;
  
  if (isProtectedRoute && !token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  
  if (isAuthRoute && token) {
    return NextResponse.redirect(new URL('/comics', request.url));
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
