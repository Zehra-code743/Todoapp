"use client";

/**
 * ChatWindow Component - Phase III AI Chatbot
 *
 * Wrapper around OpenAI ChatKit for AI-powered task management.
 * Integrates with backend chat API and Better Auth for authentication.
 */

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { cn } from '@/lib/utils';
import { CheckCircle2, Circle, AlertCircle, Send, User, Bot, PlusCircle } from 'lucide-react';

interface ToolCall {
  tool_name: string;
  parameters: Record<string, any>;
  result: Record<string, any>;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  tool_calls?: ToolCall[];
}

interface ChatWindowProps {
  userId: string;
  conversationId?: number | null;
  onConversationCreated?: (conversationId: number) => void;
}

export default function ChatWindow({
  userId,
  conversationId = null,
  onConversationCreated
}: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(conversationId);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Helper to get JWT token from cookies
  const getAuthToken = (): string | null => {
    try {
      const sessionCookie = document.cookie
        .split('; ')
        .find((row) => row.startsWith('better-auth.session_token='));

      if (!sessionCookie) return null;

      const sessionData = sessionCookie.split('=')[1];
      const decoded = JSON.parse(decodeURIComponent(sessionData));
      return decoded.token;
    } catch {
      return null;
    }
  };

  // Load conversation history if conversationId provided
  useEffect(() => {
    if (conversationId) {
      loadConversationHistory(conversationId);
    }
  }, [conversationId]);

  const loadConversationHistory = async (convId: number) => {
    try {
      setIsLoading(true);
      const token = getAuthToken();

      if (!token) {
        router.push('/signin');
        return;
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/${userId}/conversations/${convId}/messages`,
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to load conversation history');
      }

      const data = await response.json();
      // Backend returns messages in a format that might need mapping to our ToolCall structure
      // but if saved correctly in DB it should already match.
      setMessages(data.messages || []);
    } catch (err) {
      console.error('Error loading conversation:', err);
      setError('Failed to load conversation history');
    } finally {
      setIsLoading(false);
    }
  };

  const ToolCallDisplay = ({ tool }: { tool: ToolCall }) => {
    if (tool.tool_name === 'add_task') {
      const { title, description } = tool.parameters;
      const { task_id, status } = tool.result;

      return (
        <Card className="mt-3 border-none bg-primary/5 dark:bg-primary/10 backdrop-blur-sm overflow-hidden shadow-sm">
          <div className="h-1 bg-primary/30 w-full" />
          <CardHeader className="p-4 pb-0">
            <div className="flex items-center space-x-2">
              <div className="p-1.5 bg-primary/10 rounded-lg">
                <PlusCircle className="w-4 h-4 text-primary" />
              </div>
              <CardTitle className="text-sm font-bold tracking-tight text-primary">Task Automated</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="p-4 pt-2">
            <p className="font-bold text-sm text-foreground">{title}</p>
            {description && <p className="text-xs text-muted-foreground mt-1 line-clamp-2 leading-relaxed">{description}</p>}
            <div className="mt-4 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="text-[10px] bg-background/50 border px-2 py-1 rounded-md font-mono font-bold text-muted-foreground uppercase">#{task_id}</span>
                <span className="flex items-center text-[10px] bg-green-500/10 text-green-600 dark:text-green-400 px-2 py-1 rounded-md font-bold uppercase tracking-wider">
                   <div className="w-1.5 h-1.5 bg-green-500 rounded-full mr-1.5 animate-pulse" />
                   {status}
                </span>
              </div>
              <Button variant="ghost" size="sm" className="h-7 text-[10px] font-bold uppercase tracking-widest px-2" onClick={() => router.push('/dashboard')}>
                 View Path
              </Button>
            </div>
          </CardContent>
        </Card>
      );
    }

    return (
      <Card className="mt-3 border border-border/50 bg-muted/30 backdrop-blur-sm overflow-hidden">
        <div className="bg-muted px-3 py-1.5 flex items-center justify-between">
           <CardTitle className="text-[10px] font-mono font-bold uppercase tracking-widest text-muted-foreground">DEBUG: {tool.tool_name}</CardTitle>
        </div>
        <CardContent className="p-3">
          <pre className="text-[10px] overflow-auto max-h-32 bg-background/50 p-2 rounded-lg font-mono leading-relaxed">
            {JSON.stringify(tool.result, null, 2)}
          </pre>
        </CardContent>
      </Card>
    );
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setError(null);

    // Optimistically add user message to UI
    const newUserMessage: Message = { role: 'user', content: userMessage };
    setMessages(prev => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      const token = getAuthToken();

      if (!token) {
        router.push('/signin');
        return;
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/${userId}/chat`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            conversation_id: currentConversationId,
            message: userMessage,
          }),
        }
      );

      if (response.status === 401) {
        router.push('/signin');
        return;
      }

      if (response.status === 429) {
        throw new Error('Rate limit exceeded. Please try again in a moment.');
      }

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to send message');
      }

      const data = await response.json();

      // Update conversation ID if this was first message
      if (!currentConversationId && data.conversation_id) {
        setCurrentConversationId(data.conversation_id);
        onConversationCreated?.(data.conversation_id);
      }

      // Add assistant response to messages
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        tool_calls: data.tool_calls,
      };
      setMessages(prev => [...prev, assistantMessage]);

    } catch (err) {
      console.error('Error sending message:', err);
      setError(err instanceof Error ? err.message : 'Failed to send message');

      // Remove optimistic user message on error
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="flex flex-col h-full bg-background/30 backdrop-blur-xl border-none shadow-premium overflow-hidden animate-in fade-in zoom-in-95 duration-700">
      {/* Header */}
      <CardHeader className="px-8 py-6 border-b border-border/40 bg-card/40 backdrop-blur-md sticky top-0 z-10 flex flex-row items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="relative">
            <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full animate-pulse-soft" />
            <div className="relative p-2.5 bg-modern-gradient rounded-2xl shadow-lg ring-1 ring-white/20">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 border-2 border-background rounded-full" title="AI is Online" />
          </div>
          <div>
            <CardTitle className="text-xl font-extrabold tracking-tight gradient-text">Neural Workspace</CardTitle>
            <div className="flex items-center mt-1">
              <div className="flex space-x-0.5 mr-2">
                <div className="w-1 h-1 bg-green-500 rounded-full" />
                <div className="w-1 h-1 bg-green-500 rounded-full animate-pulse" />
              </div>
              <p className="text-[10px] text-muted-foreground font-bold uppercase tracking-widest opacity-80">
                Active Inference Core
              </p>
            </div>
          </div>
        </div>
        <div className="hidden md:flex space-x-2">
           <Button variant="outline" size="sm" className="bg-background/50 hover:bg-background h-8 text-[10px] font-bold uppercase tracking-tighter" onClick={() => setMessages([])}>
              Clear History
           </Button>
        </div>
      </CardHeader>

      {/* Messages Area */}
      <CardContent className="flex-1 overflow-y-auto px-8 py-8 space-y-8 scrollbar-thin scrollbar-thumb-primary/10 hover:scrollbar-thumb-primary/20 transition-all">
        {messages.length === 0 && !isLoading && (
          <div className="text-center py-20 animate-in fade-in slide-in-from-bottom-8 duration-1000">
            <div className="relative inline-block">
              <div className="absolute inset-0 bg-primary/20 blur-3xl rounded-full scale-150" />
              <div className="relative bg-primary/5 w-24 h-24 rounded-3xl flex items-center justify-center mx-auto mb-8 border border-primary/10 transform rotate-12 hover:rotate-0 transition-transform duration-500">
                <Bot className="w-12 h-12 text-primary/40" />
              </div>
            </div>
            <h3 className="text-2xl font-black text-foreground tracking-tight">Initiate Sequence</h3>
            <p className="text-sm text-muted-foreground mt-3 max-w-[280px] mx-auto leading-relaxed">
              Your AI workstation is ready. Describe a goal or a set of tasks to begin the automation process.
            </p>
            <div className="flex flex-wrap justify-center gap-2 mt-8 max-w-sm mx-auto">
               {["Create project", "List today's tasks", "Summarize goals"].map((hint) => (
                 <button key={hint} onClick={() => setInputMessage(hint)} className="px-3 py-1.5 bg-muted/50 hover:bg-primary/10 hover:text-primary rounded-lg text-xs font-bold transition-all border border-border/40">
                    {hint}
                 </button>
               ))}
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={cn(
              "flex w-full animate-in slide-in-from-bottom-4 duration-500",
              message.role === 'user' ? 'justify-end' : 'justify-start'
            )}
            style={{ animationDelay: `${index * 50}ms` }}
          >
            <div className={cn(
              "flex flex-col max-w-[88%]",
              message.role === 'user' ? 'items-end' : 'items-start'
            )}>
              <div className="flex items-center space-x-2 mb-2 px-2">
                {message.role === 'assistant' ? (
                  <>
                    <div className="w-5 h-5 bg-primary/10 rounded-md flex items-center justify-center">
                       <Bot className="w-3 h-3 text-primary" />
                    </div>
                    <span className="text-[9px] font-black uppercase tracking-[0.2em] text-primary/70">System Identity</span>
                  </>
                ) : (
                  <>
                    <span className="text-[9px] font-black uppercase tracking-[0.2em] text-muted-foreground/70">Operator Authenticated</span>
                    <div className="w-5 h-5 bg-muted rounded-md flex items-center justify-center">
                       <User className="w-3 h-3 text-muted-foreground" />
                    </div>
                  </>
                )}
              </div>

              <div
                className={cn(
                  "rounded-3xl px-6 py-4 shadow-sm text-[15px] transition-all duration-300 relative group leading-relaxed",
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground rounded-tr-none shadow-primary/20 hover:shadow-lg hover:shadow-primary/30'
                    : 'glass-card text-foreground rounded-tl-none hover:shadow-xl hover:border-primary/20'
                )}
              >
                <div className="relative z-10">
                  <p className="whitespace-pre-wrap break-words font-medium">
                    {message.content}
                  </p>
                </div>

                {message.role === 'assistant' && (
                  <div className="absolute top-0 right-0 p-1 opacity-0 group-hover:opacity-100 transition-opacity">
                     <Button variant="ghost" size="icon" className="w-6 h-6 hover:bg-primary/10" onClick={() => navigator.clipboard.writeText(message.content)}>
                        <div className="w-1.5 h-1.5 rounded-full bg-primary/40" />
                     </Button>
                  </div>
                )}

                {/* Render Tool Calls if present */}
                {message.tool_calls && message.tool_calls.length > 0 && (
                  <div className="mt-4 space-y-3">
                    {message.tool_calls.map((tool, tIdx) => (
                      <ToolCallDisplay key={tIdx} tool={tool} />
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start animate-in fade-in duration-500">
            <div className="flex flex-col items-start max-w-[85%]">
               <div className="flex items-center space-x-2 mb-2 px-2 animate-pulse">
                  <div className="w-5 h-5 bg-primary/20 rounded-md flex items-center justify-center">
                     <Bot className="w-3 h-3 text-primary" />
                  </div>
                  <span className="text-[9px] font-black uppercase tracking-[0.2em] text-primary italic">Processing request...</span>
               </div>
               <div className="glass-card rounded-3xl rounded-tl-none px-6 py-5 border-primary/20 shadow-lg animate-pulse-soft">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                    <div className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                    <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
                  </div>
               </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </CardContent>

      {/* Error Display */}
      {error && (
        <div className="mx-8 mb-4 px-6 py-3 bg-destructive/10 border border-destructive/20 rounded-2xl flex items-center space-x-3 animate-in slide-in-from-top-4">
          <div className="p-1.5 bg-destructive/20 rounded-lg">
             <AlertCircle className="w-4 h-4 text-destructive" />
          </div>
          <p className="text-sm font-bold text-destructive tracking-tight">{error}</p>
        </div>
      )}

      {/* Input Area */}
      <CardFooter className="px-8 py-8 border-t border-border/40 bg-card/40 backdrop-blur-md">
        <form onSubmit={sendMessage} className="w-full">
          <div className="relative group">
            <div className="absolute -inset-1 bg-modern-gradient rounded-[22px] blur opacity-10 group-focus-within:opacity-25 transition-opacity duration-500" />
            <div className="relative flex items-center space-x-3 bg-background border border-border/60 rounded-[20px] p-2 pr-2.5 shadow-2xl focus-within:border-primary/50 transition-all duration-300">
              <div className="pl-4">
                 <div className="w-2 h-2 bg-primary rounded-full animate-pulse-soft" />
              </div>
              <Input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Submit command or inquiry..."
                maxLength={1000}
                disabled={isLoading}
                className="flex-1 border-none bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 text-base font-medium h-12 px-0"
              />
              <Button
                type="submit"
                disabled={!inputMessage.trim() || isLoading}
                className="h-11 w-11 p-0 rounded-xl shadow-lg shadow-primary/20 hover:shadow-primary/40 transition-all duration-300 transform active:scale-95 group/btn"
              >
                <Send className={cn("w-5 h-5 transition-all duration-300 group-hover/btn:rotate-12", isLoading && "animate-pulse")} />
              </Button>
            </div>
          </div>
          <div className="flex justify-between items-center mt-4 px-1">
             <div className="flex items-center">
                <div className="w-1.5 h-1.5 rounded-full bg-green-500 mr-2 shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
                <p className="text-[9px] text-muted-foreground font-black uppercase tracking-[0.15em] opacity-60">
                   Secure Channel Stabilized
                </p>
             </div>
             <p className={cn(
               "text-[10px] font-mono tracking-tighter font-bold px-2 py-0.5 rounded-md",
               inputMessage.length > 900 ? "bg-destructive/10 text-destructive" : "bg-muted/50 text-muted-foreground/80"
             )}>
                {inputMessage.length} / 1000
             </p>
          </div>
        </form>
      </CardFooter>
    </Card>
  );
}
