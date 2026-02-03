'use client';

import { useEffect, useState, useRef } from 'react';
import Image from 'next/image';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';
import { advisorApi, feedbackApi } from '@/lib/api';
import type { AdvisorStatus } from '@/lib/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  source?: 'rules' | 'ai';
  conversationId?: string;
  timestamp: Date;
  rated?: 'up' | 'down' | null;
  showFeedbackForm?: boolean;
  isFavorite?: boolean;
}

interface ChatHistory {
  SK: string;
  conversation_id: string;
  question: string;
  answer: string;
  routed_to: string;
  created_at: string;
  is_favorite: boolean;
  thread_id?: string | null;
}

interface ThreadGroup {
  thread_id: string;
  title: string;
  conversations: ChatHistory[];
  last_date: string;
}

// Storage key for localStorage
const CHAT_STORAGE_KEY = 'bears_den_advisor_chat';

export default function AIAdvisorPage() {
  const { token } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([]);
  const [favorites, setFavorites] = useState<ChatHistory[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [historyTab, setHistoryTab] = useState<'recent' | 'favorites'>('recent');
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackType, setFeedbackType] = useState<'bug' | 'feature' | 'bad_recommendation'>('bad_recommendation');
  const [feedbackMessage, setFeedbackMessage] = useState('');
  const [feedbackSubmitting, setFeedbackSubmitting] = useState(false);
  const [feedbackSuccess, setFeedbackSuccess] = useState(false);
  const [inlineFeedbackId, setInlineFeedbackId] = useState<string | null>(null);
  const [inlineFeedbackText, setInlineFeedbackText] = useState('');
  const [aiStatus, setAiStatus] = useState<AdvisorStatus | null>(null);
  const [currentThreadId, setCurrentThreadId] = useState<string | null>(null);
  const [expandedThreads, setExpandedThreads] = useState<Set<string>>(new Set());
  const [bearPawLoaded, setBearPawLoaded] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load messages from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(CHAT_STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        // Restore dates as Date objects
        const restored = parsed.map((m: any) => ({
          ...m,
          timestamp: new Date(m.timestamp),
        }));
        setMessages(restored);
      }
    } catch (error) {
      console.error('Failed to restore chat from localStorage:', error);
    }
  }, []);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      try {
        localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messages));
      } catch (error) {
        console.error('Failed to save chat to localStorage:', error);
      }
    }
  }, [messages]);

  useEffect(() => {
    fetchChatHistory();
    fetchFavorites();
    fetchAiStatus();
  }, [token]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchAiStatus = async () => {
    if (!token) return;
    try {
      const data = await advisorApi.getStatus(token);
      setAiStatus(data);
    } catch (error) {
      console.error('Failed to fetch AI status:', error);
    }
  };

  const fetchChatHistory = async () => {
    if (!token) return;
    try {
      const data = await advisorApi.getHistory(token, 30);
      setChatHistory(Array.isArray(data.conversations) ? data.conversations : []);
    } catch (error) {
      console.error('Failed to fetch chat history:', error);
    }
  };

  const fetchFavorites = async () => {
    if (!token) return;
    try {
      const data = await advisorApi.getFavorites(token, 20);
      setFavorites(Array.isArray(data.favorites) ? data.favorites : []);
    } catch (error) {
      console.error('Failed to fetch favorites:', error);
    }
  };

  const toggleFavorite = async (chat: ChatHistory, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!token) return;

    try {
      const data = await advisorApi.toggleFavorite(token, chat.SK);
      setChatHistory((prev) =>
        prev.map((c) =>
          c.SK === chat.SK ? { ...c, is_favorite: data.is_favorite } : c
        )
      );
      fetchFavorites();
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  const toggleMessageFavorite = async (messageId: string, conversationId: string) => {
    if (!token) return;

    try {
      const data = await advisorApi.toggleFavorite(token, conversationId);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === messageId ? { ...m, isFavorite: data.is_favorite } : m
        )
      );
      fetchChatHistory();
      fetchFavorites();
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  // Toggle the current conversation's favorite status (top-level button)
  const toggleCurrentChatFavorite = async () => {
    if (!token) return;
    // Find the last assistant message with a conversationId
    const lastAssistant = [...messages].reverse().find(
      (m) => m.role === 'assistant' && m.conversationId
    );
    if (!lastAssistant?.conversationId) return;

    try {
      const data = await advisorApi.toggleFavorite(token, lastAssistant.conversationId);
      setMessages((prev) =>
        prev.map((m) =>
          m.conversationId === lastAssistant.conversationId
            ? { ...m, isFavorite: data.is_favorite }
            : m
        )
      );
      fetchChatHistory();
      fetchFavorites();
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  const loadChatFromHistory = (chat: ChatHistory, continueChat: boolean = false) => {
    // Load a past conversation into the chat
    const userMsg: Message = {
      id: `hist-user-${chat.conversation_id}`,
      role: 'user',
      content: chat.question,
      timestamp: new Date(chat.created_at),
    };
    const assistantMsg: Message = {
      id: `hist-asst-${chat.conversation_id}`,
      role: 'assistant',
      content: chat.answer,
      source: chat.routed_to as 'rules' | 'ai',
      conversationId: chat.SK,
      timestamp: new Date(chat.created_at),
      rated: null, // Allow re-rating from history
      isFavorite: chat.is_favorite,
    };

    if (continueChat && messages.length > 0) {
      // Append to existing conversation
      setMessages((prev) => [...prev, userMsg, assistantMsg]);
    } else {
      // Replace current conversation
      setMessages([userMsg, assistantMsg]);
      setCurrentThreadId(chat.thread_id || null);
    }
    setShowHistory(false);
  };

  // Load an entire thread into the chat
  const loadThreadFromHistory = async (threadGroup: ThreadGroup) => {
    const newMessages: Message[] = [];
    for (const chat of threadGroup.conversations) {
      newMessages.push({
        id: `hist-user-${chat.conversation_id}`,
        role: 'user',
        content: chat.question,
        timestamp: new Date(chat.created_at),
      });
      newMessages.push({
        id: `hist-asst-${chat.conversation_id}`,
        role: 'assistant',
        content: chat.answer,
        source: chat.routed_to as 'rules' | 'ai',
        conversationId: chat.SK,
        timestamp: new Date(chat.created_at),
        rated: null,
        isFavorite: chat.is_favorite,
      });
    }
    setMessages(newMessages);
    setCurrentThreadId(threadGroup.thread_id);
    setShowHistory(false);
  };

  const submitFeedback = async () => {
    if (!feedbackMessage.trim()) return;
    setFeedbackSubmitting(true);
    try {
      await feedbackApi.submit(token!, {
        category: feedbackType,
        description: feedbackMessage,
      });
      setFeedbackSuccess(true);
      setFeedbackMessage('');
      setTimeout(() => {
        setShowFeedback(false);
        setFeedbackSuccess(false);
      }, 2000);
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    } finally {
      setFeedbackSubmitting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const data = await advisorApi.ask(token!, userMessage.content, currentThreadId || undefined);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer || 'Sorry, I could not process your request.',
        source: data.source as 'rules' | 'ai',
        conversationId: data.conversation_id || undefined,
        timestamp: new Date(),
        rated: null,
      };

      // Track thread from response
      if (data.thread_id) {
        setCurrentThreadId(data.thread_id);
      }

      setMessages((prev) => [...prev, assistantMessage]);
      fetchChatHistory();

      // Refresh AI status to update remaining requests
      fetchAiStatus();
    } catch (error) {
      console.error('Failed to get response:', error);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: 'Sorry, something went wrong. Please try again.',
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setCurrentThreadId(null);
    localStorage.removeItem(CHAT_STORAGE_KEY);
  };

  const handleRating = async (messageId: string, conversationId: string | undefined, isHelpful: boolean) => {
    if (!conversationId) return;

    if (isHelpful) {
      // Thumbs up - submit immediately
      setMessages((prev) =>
        prev.map((m) =>
          m.id === messageId ? { ...m, rated: 'up' } : m
        )
      );

      try {
        await advisorApi.rate(token!, conversationId, { is_helpful: true });
      } catch (error) {
        console.error('Failed to submit rating:', error);
      }
    } else {
      // Thumbs down - show inline feedback form
      setInlineFeedbackId(messageId);
      setInlineFeedbackText('');
    }
  };

  const submitInlineFeedback = async (messageId: string, conversationId: string) => {
    if (!inlineFeedbackText.trim()) return;

    // Update local state to show rating
    setMessages((prev) =>
      prev.map((m) =>
        m.id === messageId ? { ...m, rated: 'down' } : m
      )
    );

    try {
      await advisorApi.rate(token!, conversationId, {
        is_helpful: false,
        user_feedback: inlineFeedbackText,
      });
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }

    setInlineFeedbackId(null);
    setInlineFeedbackText('');
  };

  const cancelInlineFeedback = () => {
    setInlineFeedbackId(null);
    setInlineFeedbackText('');
  };

  // Group chat history by thread_id for the history panel
  const groupedHistory = (() => {
    const threads: ThreadGroup[] = [];
    const standalone: ChatHistory[] = [];
    const threadMap = new Map<string, ChatHistory[]>();

    for (const chat of chatHistory) {
      if (chat.thread_id) {
        if (!threadMap.has(chat.thread_id)) {
          threadMap.set(chat.thread_id, []);
        }
        threadMap.get(chat.thread_id)!.push(chat);
      } else {
        standalone.push(chat);
      }
    }

    for (const [threadId, convos] of threadMap) {
      // Sort conversations within thread by date
      convos.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
      const firstQ = convos[0].question;
      const title = firstQ.length > 40 ? firstQ.substring(0, 40) + '...' : firstQ;
      threads.push({
        thread_id: threadId,
        title,
        conversations: convos,
        last_date: convos[convos.length - 1].created_at,
      });
    }

    // Sort threads by most recent activity
    threads.sort((a, b) => new Date(b.last_date).getTime() - new Date(a.last_date).getTime());

    return { threads, standalone };
  })();

  const toggleThreadExpanded = (threadId: string) => {
    setExpandedThreads((prev) => {
      const next = new Set(prev);
      if (next.has(threadId)) {
        next.delete(threadId);
      } else {
        next.add(threadId);
      }
      return next;
    });
  };

  // Determine if current chat is favorited
  const currentChatIsFavorite = (() => {
    const lastAssistant = [...messages].reverse().find(
      (m) => m.role === 'assistant' && m.conversationId
    );
    return lastAssistant?.isFavorite || false;
  })();

  const hasCurrentConversation = messages.some(
    (m) => m.role === 'assistant' && m.conversationId
  );

  const suggestedQuestions = [
    'What hero should I upgrade next?',
    'Best lineup for Bear Trap?',
    'How do I prepare for SvS?',
    'What chief gear should I focus on?',
  ];

  // AI status display helpers
  const aiModeLabel = aiStatus?.mode === 'unlimited' ? 'Unlimited' : aiStatus?.mode === 'on' ? 'On' : 'Off';
  const aiModeColor = aiStatus?.mode === 'unlimited'
    ? 'text-success'
    : aiStatus?.mode === 'on'
    ? 'text-ice'
    : 'text-frost-muted';

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto h-[calc(100vh-8rem)] flex flex-col animate-fadeIn">
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <div>
            <h1 className="text-2xl font-bold text-frost">AI Advisor</h1>
            <p className="text-sm text-frost-muted">Get personalized recommendations</p>
          </div>
          <div className="flex gap-2 items-center">
            {/* Top-level Favorite Toggle */}
            {hasCurrentConversation && (
              <button
                onClick={toggleCurrentChatFavorite}
                className={`text-sm px-3 py-1.5 rounded font-medium transition-colors ${
                  currentChatIsFavorite
                    ? 'bg-fire/20 text-fire ring-1 ring-fire'
                    : 'btn-ghost'
                }`}
                title={currentChatIsFavorite ? 'Remove from favorites' : 'Mark as favorite'}
              >
                {currentChatIsFavorite ? 'Favorited \u2605' : '\u2606 Favorite'}
              </button>
            )}
            <button
              onClick={() => setShowFeedback(!showFeedback)}
              className="btn-ghost text-sm"
            >
              Feedback
            </button>
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="btn-secondary text-sm"
            >
              {showHistory ? 'Hide' : 'History'}
            </button>
            <button onClick={handleNewChat} className="btn-secondary text-sm">
              New Chat
            </button>
          </div>
        </div>

        {/* AI Status Banner */}
        {aiStatus && (
          <div className="mb-3">
            {!aiStatus.ai_enabled ? (
              <div className="rounded-lg bg-surface border border-frost-muted/20 px-4 py-2.5">
                <p className="text-sm text-frost-muted">
                  AI is currently disabled. Questions will be answered by the rules engine only.
                </p>
              </div>
            ) : aiStatus.requests_remaining <= 3 && aiStatus.mode !== 'unlimited' ? (
              <div className="rounded-lg bg-fire/10 border border-fire/30 px-4 py-2.5 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-fire text-sm font-medium">Low AI requests</span>
                  <span className="text-xs text-frost-muted">
                    {aiStatus.requests_remaining} of {aiStatus.daily_limit} remaining today
                  </span>
                </div>
                <span className={`text-xs font-medium ${aiModeColor}`}>
                  Mode: {aiModeLabel}
                </span>
              </div>
            ) : (
              <div className="flex items-center justify-between px-1">
                <span className="text-xs text-frost-muted">
                  AI Mode: <span className={`font-medium ${aiModeColor}`}>{aiModeLabel}</span>
                  {aiStatus.mode !== 'unlimited' && (
                    <> &middot; {aiStatus.requests_remaining}/{aiStatus.daily_limit} requests remaining</>
                  )}
                </span>
                {aiStatus.primary_provider && (
                  <span className="text-xs text-frost-muted">
                    Provider: {aiStatus.primary_provider}
                  </span>
                )}
              </div>
            )}
          </div>
        )}

        {/* Feedback Form */}
        {showFeedback && (
          <div className="card mb-4 border-fire/30">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-frost">Send Feedback</h3>
              <button
                onClick={() => setShowFeedback(false)}
                className="text-frost-muted hover:text-frost"
              >
                ✕
              </button>
            </div>
            {feedbackSuccess ? (
              <div className="text-center py-4">
                <span className="text-2xl">{'\u2713'}</span>
                <p className="text-success mt-2">Thank you for your feedback!</p>
              </div>
            ) : (
              <>
                <div className="flex gap-2 mb-3">
                  {[
                    { value: 'bad_recommendation', label: 'Bad Recommendation' },
                    { value: 'bug', label: 'Bug Report' },
                    { value: 'feature', label: 'Feature Request' },
                  ].map((type) => (
                    <button
                      key={type.value}
                      onClick={() => setFeedbackType(type.value as typeof feedbackType)}
                      className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                        feedbackType === type.value
                          ? 'bg-fire/20 text-fire ring-1 ring-fire'
                          : 'bg-surface text-frost-muted hover:text-frost'
                      }`}
                    >
                      {type.label}
                    </button>
                  ))}
                </div>
                <textarea
                  value={feedbackMessage}
                  onChange={(e) => setFeedbackMessage(e.target.value)}
                  placeholder={
                    feedbackType === 'bad_recommendation'
                      ? "What was wrong with the recommendation? Include your question and what you expected..."
                      : feedbackType === 'bug'
                      ? "Describe the bug and steps to reproduce it..."
                      : "Describe the feature you'd like to see..."
                  }
                  className="input w-full h-24 resize-none mb-3"
                />
                <button
                  onClick={submitFeedback}
                  disabled={!feedbackMessage.trim() || feedbackSubmitting}
                  className="btn-primary text-sm"
                >
                  {feedbackSubmitting ? 'Sending...' : 'Send Feedback'}
                </button>
              </>
            )}
          </div>
        )}

        {/* Chat History Sidebar */}
        {showHistory && (
          <div className="card mb-4 max-h-80 overflow-hidden flex flex-col">
            {/* Tabs */}
            <div className="flex gap-2 mb-3 border-b border-surface-border pb-2">
              <button
                onClick={() => setHistoryTab('recent')}
                className={`text-sm font-medium px-3 py-1 rounded transition-colors ${
                  historyTab === 'recent'
                    ? 'bg-ice/20 text-ice'
                    : 'text-frost-muted hover:text-frost'
                }`}
              >
                Recent
              </button>
              <button
                onClick={() => setHistoryTab('favorites')}
                className={`text-sm font-medium px-3 py-1 rounded transition-colors ${
                  historyTab === 'favorites'
                    ? 'bg-fire/20 text-fire'
                    : 'text-frost-muted hover:text-frost'
                }`}
              >
                Favorites {favorites.length > 0 && `(${favorites.length})`}
              </button>
            </div>

            {/* Content */}
            <div className="overflow-y-auto flex-1">
              {historyTab === 'recent' ? (
                chatHistory.length === 0 ? (
                  <p className="text-sm text-frost-muted">No chat history yet</p>
                ) : (
                  <div className="space-y-1">
                    {/* Threaded conversations */}
                    {groupedHistory.threads.map((threadGroup) => (
                      <div key={threadGroup.thread_id} className="border-b border-surface-border/30 pb-1 mb-1">
                        {/* Thread header */}
                        <button
                          onClick={() => toggleThreadExpanded(threadGroup.thread_id)}
                          className="w-full flex items-center gap-2 p-2 rounded hover:bg-surface transition-colors text-left"
                        >
                          <span className="text-frost-muted text-xs">
                            {expandedThreads.has(threadGroup.thread_id) ? '\u25BC' : '\u25B6'}
                          </span>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm text-frost truncate font-medium">{threadGroup.title}</p>
                            <p className="text-xs text-frost-muted">
                              {threadGroup.conversations.length} messages &middot;{' '}
                              {new Date(threadGroup.last_date).toLocaleDateString()}
                            </p>
                          </div>
                          <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                            <button
                              onClick={() => loadThreadFromHistory(threadGroup)}
                              className="px-2 py-0.5 text-xs text-ice hover:bg-ice/10 rounded transition-colors"
                              title="Load entire thread"
                            >
                              Load All
                            </button>
                          </div>
                        </button>

                        {/* Expanded thread conversations */}
                        {expandedThreads.has(threadGroup.thread_id) && (
                          <div className="pl-6 space-y-0.5">
                            {threadGroup.conversations.map((chat) => (
                              <div
                                key={chat.SK}
                                className="group flex items-start gap-2 p-1.5 rounded hover:bg-surface transition-colors"
                              >
                                <button
                                  onClick={() => loadChatFromHistory(chat)}
                                  className="flex-1 text-left min-w-0"
                                >
                                  <p className="text-xs text-frost truncate">{chat.question}</p>
                                  <p className="text-xs text-frost-muted">
                                    {chat.routed_to === 'rules' ? '(Rules)' : '(AI)'}
                                  </p>
                                </button>
                                <button
                                  onClick={(e) => toggleFavorite(chat, e)}
                                  className={`p-1 rounded transition-colors text-xs ${
                                    chat.is_favorite
                                      ? 'text-fire'
                                      : 'text-frost-muted opacity-0 group-hover:opacity-100 hover:text-fire'
                                  }`}
                                  title={chat.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
                                >
                                  {chat.is_favorite ? '\u2605' : '\u2606'}
                                </button>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}

                    {/* Standalone conversations */}
                    {groupedHistory.standalone.length > 0 && groupedHistory.threads.length > 0 && (
                      <div className="px-2 py-1">
                        <p className="text-xs text-frost-muted font-medium uppercase tracking-wider">
                          Individual
                        </p>
                      </div>
                    )}
                    {groupedHistory.standalone.map((chat) => (
                      <div
                        key={chat.SK}
                        className="group flex items-start gap-2 p-2 rounded hover:bg-surface transition-colors"
                      >
                        <button
                          onClick={() => loadChatFromHistory(chat)}
                          className="flex-1 text-left"
                        >
                          <p className="text-sm text-frost truncate">{chat.question}</p>
                          <p className="text-xs text-frost-muted">
                            {chat.routed_to === 'rules' ? '(Rules)' : '(AI)'} &middot;{' '}
                            {new Date(chat.created_at).toLocaleDateString()}
                          </p>
                        </button>
                        <div className="flex gap-1">
                          <button
                            onClick={(e) => toggleFavorite(chat, e)}
                            className={`p-1 rounded transition-colors ${
                              chat.is_favorite
                                ? 'text-fire'
                                : 'text-frost-muted opacity-0 group-hover:opacity-100 hover:text-fire'
                            }`}
                            title={chat.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
                          >
                            {chat.is_favorite ? '\u2605' : '\u2606'}
                          </button>
                          {messages.length > 0 && (
                            <button
                              onClick={() => loadChatFromHistory(chat, true)}
                              className="p-1 text-frost-muted opacity-0 group-hover:opacity-100 hover:text-ice transition-colors text-xs"
                              title="Add to current chat"
                            >
                              +
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )
              ) : (
                favorites.length === 0 ? (
                  <div className="text-center py-4">
                    <p className="text-sm text-frost-muted">No favorites yet</p>
                    <p className="text-xs text-frost-muted mt-1">
                      Click the {'\u2606'} on any chat to save it
                    </p>
                  </div>
                ) : (
                  <div className="space-y-1">
                    {favorites.map((chat) => (
                      <div
                        key={chat.SK}
                        className="group flex items-start gap-2 p-2 rounded hover:bg-surface transition-colors"
                      >
                        <button
                          onClick={() => loadChatFromHistory(chat as any)}
                          className="flex-1 text-left"
                        >
                          <p className="text-sm text-frost truncate">{chat.question}</p>
                          <p className="text-xs text-frost-muted">
                            {(chat as any).routed_to === 'rules' ? '(Rules)' : '(AI)'} &middot;{' '}
                            {new Date(chat.created_at).toLocaleDateString()}
                          </p>
                        </button>
                        <button
                          onClick={(e) => toggleFavorite(chat as any, e)}
                          className="p-1 text-fire transition-colors"
                          title="Remove from favorites"
                        >
                          {'\u2605'}
                        </button>
                      </div>
                    ))}
                  </div>
                )
              )}
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto mb-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <div className="flex justify-center mb-4">
                {bearPawLoaded ? (
                  <Image
                    src="/images/bear_paw.png"
                    alt="Bear Paw"
                    width={56}
                    height={56}
                    onError={() => setBearPawLoaded(false)}
                  />
                ) : (
                  <span className="text-5xl">{'\uD83D\uDC3E'}</span>
                )}
              </div>
              <h2 className="text-xl font-bold text-frost mb-2">Ask me anything about WoS!</h2>
              <p className="text-frost-muted mb-6">
                I can help with hero upgrades, lineups, SvS strategy, and more.
              </p>
              <div className="flex flex-wrap justify-center gap-2">
                {suggestedQuestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => setInput(q)}
                    className="px-4 py-2 rounded-full bg-surface text-frost-muted hover:text-frost hover:bg-surface-hover transition-colors text-sm"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {/* Bear paw avatar for assistant messages */}
                {msg.role === 'assistant' && (
                  <div className="flex-shrink-0 mr-2 mt-1">
                    {bearPawLoaded ? (
                      <Image
                        src="/images/bear_paw.png"
                        alt="Bear Paw"
                        width={28}
                        height={28}
                        className="rounded-full"
                        onError={() => setBearPawLoaded(false)}
                      />
                    ) : (
                      <span className="text-lg">{'\uD83D\uDC3E'}</span>
                    )}
                  </div>
                )}
                <div
                  className={`max-w-[80%] p-4 rounded-2xl ${
                    msg.role === 'user'
                      ? 'bg-ice text-background rounded-br-md'
                      : 'bg-surface text-frost rounded-bl-md'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                  {msg.role === 'assistant' && (
                    <>
                      <div className="flex items-center justify-between mt-3 pt-3 border-t border-surface-border/50">
                        <span className="text-xs text-frost-muted">
                          {msg.source === 'rules' ? '(Rules)' : msg.source === 'ai' ? '(AI)' : ''}
                        </span>
                        <div className="flex items-center gap-3">
                          {/* Favorite toggle */}
                          {msg.conversationId && (
                            <button
                              onClick={() => toggleMessageFavorite(msg.id, msg.conversationId!)}
                              className={`text-lg hover:scale-110 transition-all ${
                                msg.isFavorite ? 'text-fire' : 'text-frost-muted hover:text-fire'
                              }`}
                              title={msg.isFavorite ? 'Remove from favorites' : 'Save to favorites'}
                            >
                              {msg.isFavorite ? '\u2605' : '\u2606'}
                            </button>
                          )}
                          {/* Rating buttons */}
                          {msg.rated ? (
                            <span className="text-xs text-frost-muted">
                              {msg.rated === 'up' ? '\uD83D\uDC4D Thanks!' : '\uD83D\uDC4E Thanks for feedback'}
                            </span>
                          ) : inlineFeedbackId === msg.id ? null : (
                            <>
                              <button
                                onClick={() => handleRating(msg.id, msg.conversationId, true)}
                                className="text-lg hover:scale-110 transition-transform"
                                title="Helpful"
                                disabled={!msg.conversationId}
                              >
                                {'\uD83D\uDC4D'}
                              </button>
                              <button
                                onClick={() => handleRating(msg.id, msg.conversationId, false)}
                                className="text-lg hover:scale-110 transition-transform"
                                title="Not helpful"
                                disabled={!msg.conversationId}
                              >
                                {'\uD83D\uDC4E'}
                              </button>
                            </>
                          )}
                        </div>
                      </div>
                      {/* Inline feedback form for thumbs down */}
                      {inlineFeedbackId === msg.id && (
                        <div className="mt-3 pt-3 border-t border-surface-border/50">
                          <p className="text-sm font-medium text-frost mb-2">Chief, what went wrong?</p>
                          <textarea
                            value={inlineFeedbackText}
                            onChange={(e) => setInlineFeedbackText(e.target.value)}
                            placeholder="Please be specific so we can improve! e.g., 'The hero tier was wrong' or 'Didn't account for my FC level'"
                            className="input w-full h-20 resize-none text-sm mb-2"
                            autoFocus
                          />
                          <div className="flex gap-2">
                            <button
                              onClick={() => msg.conversationId && submitInlineFeedback(msg.id, msg.conversationId)}
                              disabled={!inlineFeedbackText.trim()}
                              className="btn-primary text-xs px-3 py-1"
                            >
                              Submit
                            </button>
                            <button
                              onClick={cancelInlineFeedback}
                              className="btn-secondary text-xs px-3 py-1"
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex-shrink-0 mr-2 mt-1">
                {bearPawLoaded ? (
                  <Image
                    src="/images/bear_paw.png"
                    alt="Bear Paw"
                    width={28}
                    height={28}
                    className="rounded-full"
                    onError={() => setBearPawLoaded(false)}
                  />
                ) : (
                  <span className="text-lg">{'\uD83D\uDC3E'}</span>
                )}
              </div>
              <div className="bg-surface text-frost p-4 rounded-2xl rounded-bl-md">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-frost-muted rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 bg-frost-muted rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 bg-frost-muted rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about heroes, lineups, strategy..."
            className="input flex-1"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="btn-primary px-6"
          >
            Send
          </button>
        </form>

        {/* Rate Limit Warning at Bottom */}
        {aiStatus && aiStatus.mode !== 'unlimited' && aiStatus.requests_today > 0 && (
          <div className="mt-1 px-1">
            <p className="text-xs text-frost-muted">
              {aiStatus.requests_remaining} AI request{aiStatus.requests_remaining !== 1 ? 's' : ''} remaining today
            </p>
          </div>
        )}

        {/* Donate Banner */}
        <div className="card mt-4 border-fire/30 bg-gradient-to-r from-fire/10 to-fire/5">
          <div className="flex items-center gap-4">
            <Image src="/images/frost_star.png" alt="Frost Star" width={32} height={32} className="flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm text-frost">
                Finding the AI Advisor helpful? Support Bear&apos;s Den development!
              </p>
            </div>
            <a
              href="https://ko-fi.com/randomchaoslabs"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-fire text-sm whitespace-nowrap"
            >
              Support Us
            </a>
          </div>
        </div>
      </div>
    </PageLayout>
  );
}
