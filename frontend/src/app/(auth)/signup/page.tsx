/**
 * Sign Up Page
 * New user registration with email, name, and password
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { isValidEmail } from '@/lib/utils';
import { USER_NAME_MIN_LENGTH, USER_NAME_MAX_LENGTH, PASSWORD_MIN_LENGTH } from '@/types/task';

export default function SignUpPage() {
  const router = useRouter();
  const { signUp, isLoading } = useAuth();

  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!email || !name || !password) {
      setError('All fields are required');
      return;
    }

    if (!isValidEmail(email)) {
      setError('Invalid email format');
      return;
    }

    if (name.length < USER_NAME_MIN_LENGTH || name.length > USER_NAME_MAX_LENGTH) {
      setError(`Name must be between ${USER_NAME_MIN_LENGTH} and ${USER_NAME_MAX_LENGTH} characters`);
      return;
    }

    if (password.length < PASSWORD_MIN_LENGTH) {
      setError(`Password must be at least ${PASSWORD_MIN_LENGTH} characters`);
      return;
    }

    try {
      await signUp(email, name, password);
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sign up failed. Email may already be registered.');
    }
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden flex flex-col">
      {/* Background Orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
        <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-primary/10 rounded-full blur-[120px] animate-blob" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-500/10 rounded-full blur-[120px] animate-blob animation-delay-2000" />
      </div>

      {/* Header */}
      <header className="border-b border-border/40 bg-background/60 backdrop-blur-xl sticky top-0 z-50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-20 items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-modern-gradient rounded-xl flex items-center justify-center shadow-lg ring-1 ring-white/20">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <Link href="/" className="text-2xl font-black gradient-text tracking-tighter transition-opacity hover:opacity-80">
                TodoApp
              </Link>
            </div>
            <div className="flex items-center gap-6">
              <span className="text-xs font-bold text-muted-foreground uppercase tracking-widest hidden sm:block opacity-60">System Registry</span>
              <Link
                href="/signin"
                className="px-6 py-2.5 rounded-xl border border-border/60 text-foreground/70 hover:text-primary hover:border-primary/30 font-black text-xs uppercase tracking-widest transition-all duration-300 shadow-sm"
              >
                Sign In
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Sign Up Form */}
      <div className="flex-1 flex items-center justify-center px-4 py-20 relative">
        <div className="w-full max-w-[460px] animate-in fade-in zoom-in-95 duration-700">
          <div className="glass-card rounded-[2.5rem] shadow-premium p-10 relative overflow-hidden">
             {/* Visual accent */}
            <div className="absolute top-0 left-0 w-full h-1.5 bg-modern-gradient opacity-80" />

            <div className="text-center mb-10">
               <div className="inline-flex p-3 bg-primary/10 rounded-2xl mb-4">
                 <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                 </svg>
              </div>
              <h2 className="text-4xl font-black tracking-tighter text-foreground">
                Join the <span className="gradient-text">Network</span>
              </h2>
              <p className="mt-3 text-sm font-medium text-muted-foreground uppercase tracking-widest opacity-70">
                Register unique operator signature
              </p>
            </div>

            <form className="space-y-6" onSubmit={handleSubmit}>
              {error && (
                <div className="rounded-2xl bg-destructive/10 p-4 border border-destructive/20 animate-in slide-in-from-top-2">
                  <div className="flex items-center gap-3">
                     <div className="w-2 h-2 bg-destructive rounded-full" />
                     <p className="text-xs font-bold text-destructive uppercase tracking-tight">{error}</p>
                  </div>
                </div>
              )}

              <div className="space-y-5">
                <div>
                  <label htmlFor="email" className="block text-[10px] font-black text-muted-foreground uppercase tracking-[0.2em] mb-2 px-1">
                    Neural Identifier (Email)
                  </label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="modern-input block w-full rounded-2xl px-5 py-4 text-foreground placeholder-muted-foreground/40 outline-none h-14 font-medium"
                    placeholder="name@nexus.com"
                  />
                </div>

                <div>
                   <label htmlFor="name" className="block text-[10px] font-black text-muted-foreground uppercase tracking-[0.2em] mb-2 px-1">
                    Operator Designation (Name)
                  </label>
                  <input
                    id="name"
                    name="name"
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="modern-input block w-full rounded-2xl px-5 py-4 text-foreground placeholder-muted-foreground/40 outline-none h-14 font-medium"
                    placeholder="Alpha One"
                  />
                  <div className="mt-2 flex justify-end px-1">
                     <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest opacity-50">
                        REQ: {USER_NAME_MIN_LENGTH}-{USER_NAME_MAX_LENGTH} CHARS
                     </span>
                  </div>
                </div>

                <div>
                  <label htmlFor="password" className="block text-[10px] font-black text-muted-foreground uppercase tracking-[0.2em] mb-2 px-1">
                    Access Key (Password)
                  </label>
                  <input
                    id="password"
                    name="password"
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="modern-input block w-full rounded-2xl px-5 py-4 text-foreground placeholder-muted-foreground/40 outline-none h-14 font-medium"
                    placeholder="••••••••"
                  />
                   <div className="mt-2 flex justify-end px-1">
                     <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest opacity-50">
                        STR_MIN: {PASSWORD_MIN_LENGTH} CHARS
                     </span>
                  </div>
                </div>
              </div>

              <div className="flex items-start group cursor-pointer py-2">
                <input
                  id="terms"
                  name="terms"
                  type="checkbox"
                  required
                  className="h-5 w-5 mt-1 rounded-lg border-border bg-background text-primary focus:ring-primary/20 transition-all cursor-pointer"
                />
                <label htmlFor="terms" className="ml-3 block text-[10px] font-black text-muted-foreground uppercase tracking-widest cursor-pointer group-hover:text-foreground transition-colors leading-relaxed">
                  I accept the{' '}
                  <a href="#" className="text-primary hover:opacity-80 transition-opacity">Neural Protocols</a>
                  {' '}and{' '}
                  <a href="#" className="text-primary hover:opacity-80 transition-opacity">Data Ethics</a>
                </label>
              </div>

              <div>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="group relative flex w-full justify-center items-center h-14 rounded-2xl bg-modern-gradient text-sm font-black text-white hover:scale-[1.02] active:scale-95 transition-all duration-300 shadow-xl shadow-primary/20 hover:shadow-primary/40 disabled:opacity-50 disabled:scale-100 uppercase tracking-[0.2em]"
                >
                  {isLoading ? (
                    <div className="flex items-center gap-3">
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white"></div>
                      <span className="opacity-80">Initializing...</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-3">
                      <span>Register Identity</span>
                      <svg className="w-5 h-5 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 4v16m8-8H4" />
                      </svg>
                    </div>
                  )}
                </button>
              </div>
            </form>

            <div className="mt-10 pt-10 border-t border-border/40 text-center">
              <p className="text-[10px] font-black text-muted-foreground uppercase tracking-widest opacity-60">
                Already registered?{' '}
                <Link href="/signin" className="text-primary hover:opacity-80 transition-opacity ml-1">
                  Access Portal
                </Link>
              </p>
            </div>
          </div>

          {/* Back to Home */}
          <div className="mt-8 text-center animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-500 fill-mode-both">
            <Link href="/" className="inline-flex items-center gap-2 text-[10px] font-black text-muted-foreground uppercase tracking-widest hover:text-foreground transition-colors group">
              <svg className="w-3 h-3 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M15 19l-7-7 7-7" />
              </svg>
              Return to Surface
            </Link>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-auto border-t border-border/20 bg-background/40 backdrop-blur-sm py-8">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-[10px] font-black text-muted-foreground/60 uppercase tracking-widest">
              © 2026 TodoApp Core Runtime
            </p>
            <div className="flex gap-6">
                <span className="text-[10px] font-black text-primary/60 uppercase tracking-widest">v2.1.0-STABLE</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
