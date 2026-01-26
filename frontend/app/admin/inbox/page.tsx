'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';

interface FeedbackItem {
  id: number;
  user_id: number;
  user_email: string;
  category: string;
  message: string;
  status: string;
  created_at: string;
  updated_at: string;
}

interface ErrorItem {
  id: number;
  error_type: string;
  message: string;
  stack_trace: string | null;
  user_id: number | null;
  user_email: string | null;
  page: string | null;
  created_at: string;
  resolved: boolean;
}

type TabType = 'feedback' | 'errors' | 'conversations';

export default function AdminInboxPage() {
  const { token, user } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('feedback');
  const [feedback, setFeedback] = useState<FeedbackItem[]>([]);
  const [errors, setErrors] = useState<ErrorItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedFeedback, setSelectedFeedback] = useState<FeedbackItem | null>(null);
  const [selectedError, setSelectedError] = useState<ErrorItem | null>(null);

  useEffect(() => {
    if (token) {
      fetchData();
    }
  }, [token]);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [feedbackRes, errorsRes] = await Promise.all([
        fetch('http://localhost:8000/api/admin/feedback', {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch('http://localhost:8000/api/admin/errors', {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);

      if (feedbackRes.ok) {
        const feedbackData = await feedbackRes.json();
        setFeedback(Array.isArray(feedbackData) ? feedbackData : []);
      }
      if (errorsRes.ok) {
        const errorsData = await errorsRes.json();
        setErrors(Array.isArray(errorsData) ? errorsData : []);
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateFeedbackStatus = async (id: number, status: string) => {
    try {
      await fetch(`http://localhost:8000/api/admin/feedback/${id}`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status }),
      });
      fetchData();
      setSelectedFeedback(null);
    } catch (error) {
      console.error('Failed to update feedback:', error);
    }
  };

  const handleResolveError = async (id: number) => {
    try {
      await fetch(`http://localhost:8000/api/admin/errors/${id}/resolve`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchData();
      setSelectedError(null);
    } catch (error) {
      console.error('Failed to resolve error:', error);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  const pendingFeedback = feedback.filter((f) => f.status === 'new' || f.status === 'pending');
  const unresolvedErrors = errors.filter((e) => !e.resolved);

  // Redirect non-admins
  if (user && user.role !== 'admin') {
    return (
      <PageLayout>
        <div className="max-w-2xl mx-auto text-center py-16">
          <div className="text-6xl mb-6">🔒</div>
          <h1 className="text-2xl font-bold text-frost mb-4">Access Denied</h1>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="max-w-5xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Inbox</h1>
          <p className="text-frost-muted mt-1">User feedback, errors, and conversations</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-surface-border pb-2">
          <button
            onClick={() => setActiveTab('feedback')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'feedback'
                ? 'bg-ice/20 text-ice'
                : 'text-frost-muted hover:text-frost hover:bg-surface'
            }`}
          >
            Feedback
            {pendingFeedback.length > 0 && (
              <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-warning/20 text-warning">
                {pendingFeedback.length}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('errors')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'errors'
                ? 'bg-ice/20 text-ice'
                : 'text-frost-muted hover:text-frost hover:bg-surface'
            }`}
          >
            Errors
            {unresolvedErrors.length > 0 && (
              <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-error/20 text-error">
                {unresolvedErrors.length}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('conversations')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'conversations'
                ? 'bg-ice/20 text-ice'
                : 'text-frost-muted hover:text-frost hover:bg-surface'
            }`}
          >
            Conversations
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
        ) : activeTab === 'feedback' ? (
          <FeedbackTab
            feedback={feedback}
            onSelect={setSelectedFeedback}
            formatDate={formatDate}
          />
        ) : activeTab === 'errors' ? (
          <ErrorsTab
            errors={errors}
            onSelect={setSelectedError}
            formatDate={formatDate}
          />
        ) : (
          <ConversationsTab token={token || ''} />
        )}

        {/* Feedback Detail Modal */}
        {selectedFeedback && (
          <FeedbackDetailModal
            feedback={selectedFeedback}
            onClose={() => setSelectedFeedback(null)}
            onUpdateStatus={handleUpdateFeedbackStatus}
            formatDate={formatDate}
          />
        )}

        {/* Error Detail Modal */}
        {selectedError && (
          <ErrorDetailModal
            error={selectedError}
            onClose={() => setSelectedError(null)}
            onResolve={() => handleResolveError(selectedError.id)}
            formatDate={formatDate}
          />
        )}
      </div>
    </PageLayout>
  );
}

function FeedbackTab({
  feedback,
  onSelect,
  formatDate,
}: {
  feedback: FeedbackItem[];
  onSelect: (item: FeedbackItem) => void;
  formatDate: (date: string) => string;
}) {
  const statusColors: Record<string, string> = {
    new: 'badge-warning',
    pending: 'badge-info',
    completed: 'badge-success',
    archived: 'badge-secondary',
  };

  const categoryColors: Record<string, string> = {
    bug: 'text-error',
    feature: 'text-ice',
    question: 'text-warning',
    other: 'text-frost-muted',
  };

  if (feedback.length === 0) {
    return (
      <div className="card text-center py-12">
        <div className="text-4xl mb-4">📬</div>
        <p className="text-frost-muted">No feedback yet</p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="space-y-3">
        {feedback.map((item) => (
          <button
            key={item.id}
            onClick={() => onSelect(item)}
            className="w-full p-4 rounded-lg bg-surface hover:bg-surface-hover transition-colors text-left"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`text-sm font-medium ${categoryColors[item.category] || categoryColors.other}`}>
                    [{item.category}]
                  </span>
                  <span className={`badge text-xs ${statusColors[item.status] || statusColors.new}`}>
                    {item.status}
                  </span>
                </div>
                <p className="text-frost truncate">{item.message}</p>
                <p className="text-xs text-frost-muted mt-1">
                  {item.user_email} · {formatDate(item.created_at)}
                </p>
              </div>
              <span className="text-frost-muted">→</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

function ErrorsTab({
  errors,
  onSelect,
  formatDate,
}: {
  errors: ErrorItem[];
  onSelect: (item: ErrorItem) => void;
  formatDate: (date: string) => string;
}) {
  if (errors.length === 0) {
    return (
      <div className="card text-center py-12">
        <div className="text-4xl mb-4">✅</div>
        <p className="text-frost-muted">No errors logged</p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="space-y-3">
        {errors.map((item) => (
          <button
            key={item.id}
            onClick={() => onSelect(item)}
            className={`w-full p-4 rounded-lg transition-colors text-left ${
              item.resolved
                ? 'bg-surface/50 opacity-60'
                : 'bg-error/5 border border-error/20 hover:bg-error/10'
            }`}
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium text-error">{item.error_type}</span>
                  {item.resolved && <span className="badge badge-success text-xs">Resolved</span>}
                </div>
                <p className="text-frost truncate">{item.message}</p>
                <p className="text-xs text-frost-muted mt-1">
                  {item.page || 'Unknown page'} · {formatDate(item.created_at)}
                  {item.user_email && ` · ${item.user_email}`}
                </p>
              </div>
              <span className="text-frost-muted">→</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

function ConversationsTab({ token }: { token: string }) {
  return (
    <div className="card text-center py-12">
      <div className="text-4xl mb-4">💬</div>
      <p className="text-frost-muted mb-4">Admin-to-user messaging</p>
      <button className="btn-primary">Start New Conversation</button>
    </div>
  );
}

function FeedbackDetailModal({
  feedback,
  onClose,
  onUpdateStatus,
  formatDate,
}: {
  feedback: FeedbackItem;
  onClose: () => void;
  onUpdateStatus: (id: number, status: string) => void;
  formatDate: (date: string) => string;
}) {
  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-surface rounded-xl border border-surface-border max-w-lg w-full p-6 animate-fadeIn">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-frost">Feedback Details</h2>
            <p className="text-sm text-frost-muted mt-1">{formatDate(feedback.created_at)}</p>
          </div>
          <button onClick={onClose} className="text-frost-muted hover:text-frost">
            ✕
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="text-xs text-frost-muted uppercase tracking-wide">From</label>
            <p className="text-frost">{feedback.user_email}</p>
          </div>

          <div>
            <label className="text-xs text-frost-muted uppercase tracking-wide">Category</label>
            <p className="text-frost capitalize">{feedback.category}</p>
          </div>

          <div>
            <label className="text-xs text-frost-muted uppercase tracking-wide">Message</label>
            <p className="text-frost whitespace-pre-wrap">{feedback.message}</p>
          </div>

          <div>
            <label className="text-xs text-frost-muted uppercase tracking-wide block mb-2">
              Update Status
            </label>
            <div className="flex gap-2">
              {['pending', 'completed', 'archived'].map((status) => (
                <button
                  key={status}
                  onClick={() => onUpdateStatus(feedback.id, status)}
                  disabled={feedback.status === status}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    feedback.status === status
                      ? 'bg-ice/20 text-ice cursor-default'
                      : 'bg-surface-hover text-frost-muted hover:text-frost'
                  }`}
                >
                  {status}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ErrorDetailModal({
  error,
  onClose,
  onResolve,
  formatDate,
}: {
  error: ErrorItem;
  onClose: () => void;
  onResolve: () => void;
  formatDate: (date: string) => string;
}) {
  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-surface rounded-xl border border-surface-border max-w-2xl w-full p-6 animate-fadeIn max-h-[80vh] overflow-y-auto">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-error">{error.error_type}</h2>
            <p className="text-sm text-frost-muted mt-1">{formatDate(error.created_at)}</p>
          </div>
          <button onClick={onClose} className="text-frost-muted hover:text-frost">
            ✕
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="text-xs text-frost-muted uppercase tracking-wide">Message</label>
            <p className="text-frost">{error.message}</p>
          </div>

          {error.page && (
            <div>
              <label className="text-xs text-frost-muted uppercase tracking-wide">Page</label>
              <p className="text-frost">{error.page}</p>
            </div>
          )}

          {error.user_email && (
            <div>
              <label className="text-xs text-frost-muted uppercase tracking-wide">User</label>
              <p className="text-frost">{error.user_email}</p>
            </div>
          )}

          {error.stack_trace && (
            <div>
              <label className="text-xs text-frost-muted uppercase tracking-wide">Stack Trace</label>
              <pre className="mt-2 p-4 rounded-lg bg-background text-xs text-frost-muted overflow-x-auto">
                {error.stack_trace}
              </pre>
            </div>
          )}

          {!error.resolved && (
            <button onClick={onResolve} className="btn-success w-full">
              Mark as Resolved
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
