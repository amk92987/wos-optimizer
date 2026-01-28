'use client';

import { useEffect, useState, useRef } from 'react';
import Image from 'next/image';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  source?: 'rules' | 'ai';
  conversationId?: number;
  timestamp: Date;
  rated?: 'up' | 'down' | null;
  showFeedbackForm?: boolean;
  isFavorite?: boolean;
}

interface ChatHistory {
  id: number;
  question: string;
  answer: string;
  source: string;
  created_at: string;
  is_favorite: boolean;
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
  }, [token]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchChatHistory = async () => {
    if (!token) return;
    try {
      const res = await fetch('http://localhost:8000/api/advisor/history?limit=10', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setChatHistory(Array.isArray(data) ? data : []);
      }
    } catch (error) {
      console.error('Failed to fetch chat history:', error);
    }
  };

  const fetchFavorites = async () => {
    if (!token) return;
    try {
      const res = await fetch('http://localhost:8000/api/advisor/favorites?limit=20', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setFavorites(Array.isArray(data) ? data : []);
      }
    } catch (error) {
      console.error('Failed to fetch favorites:', error);
    }
  };

  const toggleFavorite = async (chat: ChatHistory, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent loading the chat when clicking favorite
    if (!token) return;

    try {
      const res = await fetch(`http://localhost:8000/api/advisor/favorite/${chat.id}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        // Update local state
        setChatHistory((prev) =>
          prev.map((c) =>
            c.id === chat.id ? { ...c, is_favorite: data.is_favorite } : c
          )
        );
        // Refresh favorites list
        fetchFavorites();
      }
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  const toggleMessageFavorite = async (messageId: string, conversationId: number) => {
    if (!token) return;

    try {
      const res = await fetch(`http://localhost:8000/api/advisor/favorite/${conversationId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        // Update message state
        setMessages((prev) =>
          prev.map((m) =>
            m.id === messageId ? { ...m, isFavorite: data.is_favorite } : m
          )
        );
        // Refresh history and favorites
        fetchChatHistory();
        fetchFavorites();
      }
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  const loadChatFromHistory = (chat: ChatHistory, continueChat: boolean = false) => {
    // Load a past conversation into the chat
    const userMsg: Message = {
      id: `hist-user-${chat.id}`,
      role: 'user',
      content: chat.question,
      timestamp: new Date(chat.created_at),
    };
    const assistantMsg: Message = {
      id: `hist-asst-${chat.id}`,
      role: 'assistant',
      content: chat.answer,
      source: chat.source as 'rules' | 'ai',
      conversationId: chat.id,
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
    }
    setShowHistory(false);
  };

  const submitFeedback = async () => {
    if (!feedbackMessage.trim()) return;
    setFeedbackSubmitting(true);
    try {
      const res = await fetch('http://localhost:8000/api/feedback', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: feedbackType,
          message: feedbackMessage,
        }),
      });
      if (res.ok) {
        setFeedbackSuccess(true);
        setFeedbackMessage('');
        setTimeout(() => {
          setShowFeedback(false);
          setFeedbackSuccess(false);
        }, 2000);
      }
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
      const res = await fetch('http://localhost:8000/api/advisor/ask', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: userMessage.content }),
      });

      const data = await res.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer || 'Sorry, I could not process your request.',
        source: data.source,
        conversationId: data.conversation_id,
        timestamp: new Date(),
        rated: null,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      fetchChatHistory();
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
    localStorage.removeItem(CHAT_STORAGE_KEY);
  };

  const handleRating = async (messageId: string, conversationId: number | undefined, isHelpful: boolean) => {
    if (!conversationId) return;

    if (isHelpful) {
      // Thumbs up - submit immediately
      setMessages((prev) =>
        prev.map((m) =>
          m.id === messageId ? { ...m, rated: 'up' } : m
        )
      );

      try {
        await fetch('http://localhost:8000/api/advisor/rate', {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ conversation_id: conversationId, is_helpful: true }),
        });
      } catch (error) {
        console.error('Failed to submit rating:', error);
      }
    } else {
      // Thumbs down - show inline feedback form
      setInlineFeedbackId(messageId);
      setInlineFeedbackText('');
    }
  };

  const submitInlineFeedback = async (messageId: string, conversationId: number) => {
    if (!inlineFeedbackText.trim()) return;

    // Update local state to show rating
    setMessages((prev) =>
      prev.map((m) =>
        m.id === messageId ? { ...m, rated: 'down' } : m
      )
    );

    try {
      await fetch('http://localhost:8000/api/advisor/rate', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversation_id: conversationId,
          is_helpful: false,
          user_feedback: inlineFeedbackText,
        }),
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

  const suggestedQuestions = [
    'What hero should I upgrade next?',
    'Best lineup for Bear Trap?',
    'How do I prepare for SvS?',
    'What chief gear should I focus on?',
  ];

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto h-[calc(100vh-8rem)] flex flex-col animate-fadeIn">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-frost">AI Advisor</h1>
            <p className="text-sm text-frost-muted">Get personalized recommendations</p>
          </div>
          <div className="flex gap-2">
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
                <span className="text-2xl">✓</span>
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
          <div className="card mb-4 max-h-64 overflow-hidden flex flex-col">
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
                    {chatHistory.map((chat) => (
                      <div
                        key={chat.id}
                        className="group flex items-start gap-2 p-2 rounded hover:bg-surface transition-colors"
                      >
                        <button
                          onClick={() => loadChatFromHistory(chat)}
                          className="flex-1 text-left"
                        >
                          <p className="text-sm text-frost truncate">{chat.question}</p>
                          <p className="text-xs text-frost-muted">
                            {chat.source === 'rules' ? '(Rules)' : '(AI)'} ·{' '}
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
                            {chat.is_favorite ? '★' : '☆'}
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
                      Click the ☆ on any chat to save it
                    </p>
                  </div>
                ) : (
                  <div className="space-y-1">
                    {favorites.map((chat) => (
                      <div
                        key={chat.id}
                        className="group flex items-start gap-2 p-2 rounded hover:bg-surface transition-colors"
                      >
                        <button
                          onClick={() => loadChatFromHistory(chat)}
                          className="flex-1 text-left"
                        >
                          <p className="text-sm text-frost truncate">{chat.question}</p>
                          <p className="text-xs text-frost-muted">
                            {chat.source === 'rules' ? '(Rules)' : '(AI)'} ·{' '}
                            {new Date(chat.created_at).toLocaleDateString()}
                          </p>
                        </button>
                        <button
                          onClick={(e) => toggleFavorite(chat, e)}
                          className="p-1 text-fire transition-colors"
                          title="Remove from favorites"
                        >
                          ★
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
              <div className="text-5xl mb-4">🤖</div>
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
                              {msg.isFavorite ? '★' : '☆'}
                            </button>
                          )}
                          {/* Rating buttons */}
                          {msg.rated ? (
                            <span className="text-xs text-frost-muted">
                              {msg.rated === 'up' ? '👍 Thanks!' : '👎 Thanks for feedback'}
                            </span>
                          ) : inlineFeedbackId === msg.id ? null : (
                            <>
                              <button
                                onClick={() => handleRating(msg.id, msg.conversationId, true)}
                                className="text-lg hover:scale-110 transition-transform"
                                title="Helpful"
                                disabled={!msg.conversationId}
                              >
                                👍
                              </button>
                              <button
                                onClick={() => handleRating(msg.id, msg.conversationId, false)}
                                className="text-lg hover:scale-110 transition-transform"
                                title="Not helpful"
                                disabled={!msg.conversationId}
                              >
                                👎
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

        {/* Donate Banner */}
        <div className="card mt-4 border-fire/30 bg-gradient-to-r from-fire/10 to-fire/5">
          <div className="flex items-center gap-4">
            <Image src="/images/frost_star.png" alt="Frost Star" width={32} height={32} className="flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm text-frost">
                Finding the AI Advisor helpful? Support Bear's Den development!
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
