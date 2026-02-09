/**
 * useAuth Hook
 * Custom hook for authentication with JWT tokens
 */

'use client';

import { useState, useEffect } from 'react';
import { getSession, setSession, clearSession } from '@/lib/auth';

export interface AuthUser {
  id: string;
  email: string;
  name: string;
}

export interface UseAuthReturn {
  user: AuthUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, name: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
}

const API_URL = (process.env.NEXT_PUBLIC_API_URL || 'https://todo-backend-wwws.onrender.com').replace(/\/$/, '');
console.log('[useAuth] API URL configured as:', API_URL);

/**
 * Hook for managing authentication state with JWT tokens
 */
export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing session on mount
    const checkSession = async () => {
      try {
        const session = getSession();

        if (session) {
          // Check if token is expired
          const expiresAt = new Date(session.expiresAt);
          const now = new Date();

          if (expiresAt > now) {
            setUser(session.user);
          } else {
            // Token expired, clear session
            clearSession();
            setUser(null);
          }
        } else {
          setUser(null);
        }
      } catch (error) {
        console.error('Session check failed:', error);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    checkSession();
  }, []);

  async function signIn(email: string, password: string) {
    try {
      setIsLoading(true);

      const response = await fetch(`${API_URL}/api/auth/signin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Sign in failed');
      }

      const data = await response.json();

      // Store session with JWT token
      const session = {
        user: data.user,
        token: data.token,
        expiresAt: data.expires_at,
      };

      setSession(session);
      setUser(data.user);
    } finally {
      setIsLoading(false);
    }
  }

  async function signUp(email: string, name: string, password: string) {
    try {
      setIsLoading(true);

      const response = await fetch(`${API_URL}/api/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, name, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Sign up failed');
      }

      const data = await response.json();

      // Store session with JWT token
      const session = {
        user: data.user,
        token: data.token,
        expiresAt: data.expires_at,
      };

      setSession(session);
      setUser(data.user);
    } finally {
      setIsLoading(false);
    }
  }

  async function signOut() {
    try {
      setIsLoading(true);

      // Call backend signout endpoint (optional, JWT is stateless)
      await fetch(`${API_URL}/api/auth/signout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      // Clear session and user state
      clearSession();
      setUser(null);

      // Redirect to signin page
      window.location.href = '/signin';
    } finally {
      setIsLoading(false);
    }
  }

  return {
    user,
    isLoading,
    isAuthenticated: !!user,
    signIn,
    signUp,
    signOut,
  };
}
