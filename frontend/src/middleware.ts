/**
 * Next.js Middleware
 * Route protection - redirect unauthenticated users to signin
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Get session token from cookies
  const sessionToken = request.cookies.get('better-auth.session_token');

  // Public routes that don't require authentication
  const publicRoutes = ['/', '/signin', '/signup'];
  const isPublicRoute = publicRoutes.includes(pathname);

  // If user is not authenticated and trying to access protected route
  if (!sessionToken && !isPublicRoute) {
    const signInUrl = new URL('/signin', request.url);
    return NextResponse.redirect(signInUrl);
  }

  // If user is authenticated and trying to access auth pages, redirect to dashboard
  if (sessionToken && (pathname === '/signin' || pathname === '/signup')) {
    const dashboardUrl = new URL('/dashboard', request.url);
    return NextResponse.redirect(dashboardUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
};
