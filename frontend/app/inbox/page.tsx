'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';

interface Notification {
  id: number;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

interface MessageThread {
  id: number;
  subject: string;
  last_message: string;
  has_unread: boolean;
  message_count: number;
  updated_at: string;
}

type TabType = 'notifications' | 'messages';

export default function UserInboxPage() {
  const { token } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('notifications');
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [threads, setThreads] = useState<MessageThread[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedNotification, setSelectedNotification] = useState<Notification | null>(null);
  const [selectedThread, setSelectedThread] = useState<MessageThread | null>(null);

  useEffect(() => {
    if (token) {
      fetchData();
    }
  }, [token]);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [notifRes, threadRes] = await Promise.all([
        fetch('http://localhost:8000/api/inbox/notifications', {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch('http://localhost:8000/api/inbox/threads', {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);

      if (notifRes.ok) setNotifications(await notifRes.json());
      if (threadRes.ok) setThreads(await threadRes.json());
    } catch (error) {
      console.error('Failed to fetch inbox data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleMarkRead = async (notificationId: number) => {
    try {
      await fetch(`http://localhost:8000/api/inbox/notifications/${notificationId}/read`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchData();
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else if (diffDays < 7) {
      return date.toLocaleDateString('en-US', { weekday: 'short' });
    }
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const unreadNotifications = notifications.filter((n) => !n.is_read).length;
  const unreadThreads = threads.filter((t) => t.has_unread).length;

  return (
    <PageLayout>
      <div className="max-w-3xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Inbox</h1>
          <p className="text-frost-muted mt-2">Notifications and messages from Bear's Den</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('notifications')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'notifications'
                ? 'bg-ice/20 text-ice'
                : 'text-frost-muted hover:text-frost hover:bg-surface'
            }`}
          >
            Notifications
            {unreadNotifications > 0 && (
              <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-fire text-white">
                {unreadNotifications}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('messages')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'messages'
                ? 'bg-ice/20 text-ice'
                : 'text-frost-muted hover:text-frost hover:bg-surface'
            }`}
          >
            Messages
            {unreadThreads > 0 && (
              <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-fire text-white">
                {unreadThreads}
              </span>
            )}
          </button>
        </div>

        {/* Content */}
        {isLoading ? (
          <div className="card">
            <div className="space-y-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="p-4 rounded-lg bg-surface animate-pulse">
                  <div className="h-4 bg-surface-hover rounded w-48 mb-2" />
                  <div className="h-3 bg-surface-hover rounded w-full" />
                </div>
              ))}
            </div>
          </div>
        ) : activeTab === 'notifications' ? (
          <NotificationsTab
            notifications={notifications}
            onSelect={(n) => {
              setSelectedNotification(n);
              if (!n.is_read) handleMarkRead(n.id);
            }}
            formatDate={formatDate}
          />
        ) : (
          <MessagesTab
            threads={threads}
            onSelect={setSelectedThread}
            formatDate={formatDate}
          />
        )}

        {/* Notification Detail */}
        {selectedNotification && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-surface rounded-xl border border-surface-border max-w-lg w-full p-6 animate-fadeIn">
              <div className="flex items-start justify-between mb-4">
                <h2 className="text-xl font-bold text-frost">{selectedNotification.title}</h2>
                <button
                  onClick={() => setSelectedNotification(null)}
                  className="text-frost-muted hover:text-frost"
                >
                  ✕
                </button>
              </div>
              <p className="text-frost-muted whitespace-pre-wrap mb-4">
                {selectedNotification.message}
              </p>
              <p className="text-xs text-text-muted">
                {new Date(selectedNotification.created_at).toLocaleString()}
              </p>
            </div>
          </div>
        )}

        {/* Thread Detail */}
        {selectedThread && (
          <ThreadModal
            thread={selectedThread}
            token={token || ''}
            onClose={() => {
              setSelectedThread(null);
              fetchData();
            }}
          />
        )}
      </div>
    </PageLayout>
  );
}

function NotificationsTab({
  notifications,
  onSelect,
  formatDate,
}: {
  notifications: Notification[];
  onSelect: (n: Notification) => void;
  formatDate: (date: string) => string;
}) {
  if (notifications.length === 0) {
    return (
      <div className="card text-center py-12">
        <div className="text-4xl mb-4">📭</div>
        <p className="text-frost-muted">No notifications yet</p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="space-y-2">
        {notifications.map((n) => (
          <button
            key={n.id}
            onClick={() => onSelect(n)}
            className={`w-full p-4 rounded-lg text-left transition-colors ${
              n.is_read ? 'bg-surface/50' : 'bg-surface hover:bg-surface-hover'
            }`}
          >
            <div className="flex items-start gap-3">
              {!n.is_read && (
                <span className="w-2 h-2 mt-2 rounded-full bg-ice flex-shrink-0" />
              )}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <h3 className={`font-medium truncate ${n.is_read ? 'text-frost-muted' : 'text-frost'}`}>
                    {n.title}
                  </h3>
                  <span className="text-xs text-frost-muted flex-shrink-0">
                    {formatDate(n.created_at)}
                  </span>
                </div>
                <p className="text-sm text-frost-muted truncate mt-1">{n.message}</p>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

function MessagesTab({
  threads,
  onSelect,
  formatDate,
}: {
  threads: MessageThread[];
  onSelect: (t: MessageThread) => void;
  formatDate: (date: string) => string;
}) {
  if (threads.length === 0) {
    return (
      <div className="card text-center py-12">
        <div className="text-4xl mb-4">💬</div>
        <p className="text-frost-muted">No messages yet</p>
        <p className="text-sm text-frost-muted mt-2">
          Messages from admin will appear here
        </p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="space-y-2">
        {threads.map((t) => (
          <button
            key={t.id}
            onClick={() => onSelect(t)}
            className={`w-full p-4 rounded-lg text-left transition-colors ${
              t.has_unread ? 'bg-surface hover:bg-surface-hover' : 'bg-surface/50'
            }`}
          >
            <div className="flex items-start gap-3">
              {t.has_unread && (
                <span className="w-2 h-2 mt-2 rounded-full bg-ice flex-shrink-0" />
              )}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <h3 className={`font-medium truncate ${t.has_unread ? 'text-frost' : 'text-frost-muted'}`}>
                    {t.subject}
                  </h3>
                  <span className="text-xs text-frost-muted flex-shrink-0">
                    {formatDate(t.updated_at)}
                  </span>
                </div>
                <p className="text-sm text-frost-muted truncate mt-1">{t.last_message}</p>
                <p className="text-xs text-text-muted mt-1">{t.message_count} messages</p>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

function ThreadModal({
  thread,
  token,
  onClose,
}: {
  thread: MessageThread;
  token: string;
  onClose: () => void;
}) {
  const [messages, setMessages] = useState<any[]>([]);
  const [reply, setReply] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    fetchMessages();
  }, []);

  const fetchMessages = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/inbox/threads/${thread.id}/messages`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setMessages(await res.json());
      }
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendReply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reply.trim()) return;

    setIsSending(true);
    try {
      await fetch(`http://localhost:8000/api/inbox/threads/${thread.id}/reply`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: reply }),
      });
      setReply('');
      fetchMessages();
    } catch (error) {
      console.error('Failed to send reply:', error);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-surface rounded-xl border border-surface-border max-w-lg w-full max-h-[80vh] flex flex-col animate-fadeIn">
        {/* Header */}
        <div className="p-4 border-b border-surface-border flex items-center justify-between">
          <h2 className="font-bold text-frost">{thread.subject}</h2>
          <button onClick={onClose} className="text-frost-muted hover:text-frost">
            ✕
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {isLoading ? (
            <div className="text-center py-4">
              <p className="text-frost-muted">Loading...</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`p-3 rounded-lg ${
                  msg.is_from_admin
                    ? 'bg-ice/10 border border-ice/20'
                    : 'bg-surface-hover ml-8'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-medium text-frost-muted">
                    {msg.is_from_admin ? 'Admin' : 'You'}
                  </span>
                  <span className="text-xs text-text-muted">
                    {new Date(msg.created_at).toLocaleString()}
                  </span>
                </div>
                <p className="text-sm text-frost">{msg.content}</p>
              </div>
            ))
          )}
        </div>

        {/* Reply Form */}
        <form onSubmit={handleSendReply} className="p-4 border-t border-surface-border">
          <div className="flex gap-2">
            <input
              type="text"
              value={reply}
              onChange={(e) => setReply(e.target.value)}
              placeholder="Type your reply..."
              className="input flex-1"
              disabled={isSending}
            />
            <button type="submit" disabled={!reply.trim() || isSending} className="btn-primary">
              {isSending ? '...' : 'Send'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
