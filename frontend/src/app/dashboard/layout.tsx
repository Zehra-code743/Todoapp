/**
 * Dashboard Layout
 * Includes header with logout button and auth protection
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, isAuthenticated, isLoading, signOut } = useAuth();

  // Redirect unauthenticated users to signin
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace('/signin');
    }
  }, [isAuthenticated, isLoading, router]);

  // Show loading while checking auth
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-blue-50 to-white">
        <div className="text-center">
          <div className="inline-block h-10 w-10 animate-spin rounded-full border-4 border-solid border-current border-r-transparent">
            <span className="sr-only">Loading...</span>
          </div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render children if not authenticated (will redirect)
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Dynamic background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl animate-blob" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-blob animation-delay-2000" />
      </div>

      {/* Header */}
      <header className="border-b border-border/40 bg-background/60 backdrop-blur-xl sticky top-0 z-50 transition-all duration-300">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-11 h-11 bg-modern-gradient rounded-2xl flex items-center justify-center shadow-lg transform hover:rotate-3 transition-transform duration-300 ring-1 ring-white/20">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <div className="leading-tight">
                <Link href="/dashboard" className="text-2xl font-black gradient-text tracking-tighter">
                  TodoApp
                </Link>
                <p className="text-[10px] text-muted-foreground font-bold uppercase tracking-widest hidden sm:block opacity-60">
                   {user?.name}'s Workspace
                </p>
              </div>
            </div>

            <div className="flex items-center gap-8">
              {/* Navigation Links */}
              <nav className="hidden md:flex items-center gap-1">
                <Link
                  href="/dashboard"
                  className="px-4 py-2 rounded-xl text-sm font-bold text-foreground/70 hover:text-foreground hover:bg-primary/5 transition-all relative group"
                >
                  Tasks
                  <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-1 h-1 bg-primary rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
                </Link>
                <Link
                  href="/chat"
                  className="px-4 py-2 rounded-xl text-sm font-bold text-foreground/70 hover:text-foreground hover:bg-primary/5 transition-all flex items-center gap-2 group relative"
                >
                  <svg className="w-4 h-4 font-bold" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                  Neural Chat
                  <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-1 h-1 bg-primary rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
                </Link>
              </nav>

              <div className="h-8 w-px bg-border/40 hidden md:block" />

              {/* User Avatar */}
              <div className="flex items-center gap-4">
                <div className="relative group cursor-help">
                   <div className="absolute -inset-1 bg-modern-gradient rounded-full blur opacity-25 group-hover:opacity-50 transition-opacity duration-300" />
                   <div className="relative w-10 h-10 bg-background border border-border/60 rounded-full flex items-center justify-center text-primary font-black text-sm shadow-sm">
                     {user?.name?.charAt(0).toUpperCase() || 'U'}
                   </div>
                </div>

                {/* Logout Button */}
                <button
                  onClick={signOut}
                  className="flex items-center gap-2.5 px-5 py-2.5 rounded-2xl border border-border/60 text-foreground/70 hover:border-destructive/30 hover:text-destructive hover:bg-destructive/5 transition-all duration-300 text-xs font-black uppercase tracking-widest shadow-sm"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  <span className="hidden sm:inline">Terminate</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t bg-white/60 backdrop-blur-sm mt-auto">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            © 2025 TodoApp. Built with Next.js and FastAPI.
          </p>
        </div>
      </footer>
    </div>
  );
}
