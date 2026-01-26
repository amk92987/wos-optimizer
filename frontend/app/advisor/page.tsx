'use client';

import { useEffect, useState, useRef } from 'react';
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
}

interface ChatHistory {
  id: number;
  question: string;
  answer: string;
  source: string;
  created_at: string;
}

export default function AIAdvisorPage() {
  const { token } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackType, setFeedbackType] = useState<'bug' | 'feature' | 'bad_recommendation'>('bad_recommendation');
  const [feedbackMessage, setFeedbackMessage] = useState('');
  const [feedbackSubmitting, setFeedbackSubmitting] = useState(false);
  const [feedbackSuccess, setFeedbackSuccess] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchChatHistory();
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

  const loadChatFromHistory = (chat: ChatHistory) => {
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
    };
    setMessages([userMsg, assistantMsg]);
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
  };

  const handleRating = async (messageId: string, conversationId: number | undefined, isHelpful: boolean) => {
    if (!conversationId) return;

    // Update local state to show rating
    setMessages((prev) =>
      prev.map((m) =>
        m.id === messageId ? { ...m, rated: isHelpful ? 'up' : 'down' } : m
      )
    );

    try {
      await fetch('http://localhost:8000/api/advisor/rate', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ conversation_id: conversationId, is_helpful: isHelpful }),
      });
    } catch (error) {
      console.error('Failed to submit rating:', error);
    }
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
          <div className="card mb-4 max-h-48 overflow-y-auto">
            <h3 className="text-sm font-medium text-frost-muted mb-2">Recent Conversations</h3>
            {chatHistory.length === 0 ? (
              <p className="text-sm text-frost-muted">No chat history yet</p>
            ) : (
              <div className="space-y-1">
                {chatHistory.map((chat) => (
                  <button
                    key={chat.id}
                    onClick={() => loadChatFromHistory(chat)}
                    className="w-full p-2 text-left rounded hover:bg-surface transition-colors"
                  >
                    <p className="text-sm text-frost truncate">{chat.question}</p>
                    <p className="text-xs text-frost-muted">
                      {chat.source === 'rules' ? '(Rules)' : '(AI)'} ·{' '}
                      {new Date(chat.created_at).toLocaleDateString()}
                    </p>
                  </button>
                ))}
              </div>
            )}
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
                    <div className="flex items-center justify-between mt-3 pt-3 border-t border-surface-border/50">
                      <span className="text-xs text-frost-muted">
                        {msg.source === 'rules' ? '(Rules)' : msg.source === 'ai' ? '(AI)' : ''}
                      </span>
                      <div className="flex gap-2">
                        {msg.rated ? (
                          <span className="text-xs text-frost-muted">
                            {msg.rated === 'up' ? '👍 Thanks!' : '👎 Thanks for feedback'}
                          </span>
                        ) : (
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
            <span className="text-2xl">⭐</span>
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
