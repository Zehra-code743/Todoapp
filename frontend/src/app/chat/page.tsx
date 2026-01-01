"use client";

/**
 * Chat Page - Phase III AI Chatbot
 *
 * Main chat interface page with authentication integration.
 * Uses Better Auth for user session management.
 */

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import ChatWindow from '@/components/ChatWindow';

interface User {
  id: string;
  email: string;
  name?: string;
}

export default function ChatPage() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      // Get JWT token from cookies
      const sessionCookie = document.cookie
        .split('; ')
        .find((row) => row.startsWith('better-auth.session_token='));

      if (!sessionCookie) {
        router.push('/signin');
        return;
      }

      const sessionData = sessionCookie.split('=')[1];
      const decoded = JSON.parse(decodeURIComponent(sessionData));
      const token = decoded.token;

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/auth/me`,
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        router.push('/signin');
        return;
      }

      const userData = await response.json();
      setUser(userData);
    } catch (error) {
      console.error('Auth check failed:', error);
      router.push('/signin');
    } finally {
      setIsLoading(false);
    }
  };

  const handleConversationCreated = (conversationId: number) => {
    console.log('New conversation created:', conversationId);
    // Could update URL with conversation ID for bookmarking
    // router.push(`/chat?conversation=${conversationId}`, { shallow: true });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null; // Will redirect to signin
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/dashboard')}
                className="text-gray-600 hover:text-gray-900"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">AI Chat</h1>
                <p className="text-sm text-gray-500">Manage your tasks with AI</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">{user.email}</span>
              <button
                onClick={() => router.push('/dashboard')}
                className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900 font-medium"
              >
                Dashboard
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="h-[calc(100vh-200px)]">
          <ChatWindow
            userId={user.id}
            onConversationCreated={handleConversationCreated}
          />
        </div>

        {/* Quick Tips */}
        <div className="mt-6 bg-blue-50 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-blue-900 mb-2">💡 Quick Tips</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• <strong>Create tasks:</strong> "I need to buy groceries tomorrow"</li>
            <li>• <strong>View tasks:</strong> "Show my pending tasks" or "What do I need to do?"</li>
            <li>• <strong>Be natural:</strong> Just describe what you want in plain language</li>
          </ul>
        </div>
      </main>
    </div>
  );
}
