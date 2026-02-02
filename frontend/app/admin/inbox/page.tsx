'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';
import { adminApi } from '@/lib/api';

interface FeedbackItem {
  id: string;
  user_id: string | null;
  category: string;
  description: string;
  status: string;
  created_at: string;
}

interface ErrorItem {
  id: string;
  error_type: string;
  message: string;
  stack_trace: string | null;
  user_id: string | null;
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
      const [feedbackData, errorsData] = await Promise.all([
        adminApi.listFeedback(token!),
        adminApi.getErrors(token!),
      ]);

      const fbList = feedbackData.feedback || feedbackData;
      setFeedback(Array.isArray(fbList) ? fbList : []);
      const errList = errorsData.errors || errorsData;
      setErrors(Array.isArray(errList) ? errList : []);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateFeedbackStatus = async (id: string, status: string) => {
    try {
      await adminApi.updateFeedback(token!, String(id), { status });
      fetchData();
      setSelectedFeedback(null);
    } catch (error) {
      console.error('Failed to update feedback:', error);
    }
  };

  const handleResolveError = async (id: string) => {
    try {
      await adminApi.resolveError(token!, String(id));
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
                <p className="text-frost truncate">{item.description}</p>
                <p className="text-xs text-frost-muted mt-1">
                  User: {item.user_id || 'Anonymous'} · {formatDate(item.created_at)}
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
                  {item.user_id && ` · User: ${item.user_id}`}
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

interface AIConversation {
  id: string;
  user_id: string;
  user_email: string;
  question: string;
  answer: string;
  provider: string;
  model: string;
  routed_to: string | null;
  is_helpful: boolean | null;
  rating: number | null;
  user_feedback: string | null;
  is_good_example: boolean;
  is_bad_example: boolean;
  admin_notes: string | null;
  created_at: string;
}

interface ConversationStats {
  total: number;
  ai_routed: number;
  rules_routed: number;
  ai_percentage: number;
  good_examples: number;
  bad_examples: number;
  helpful: number;
  unhelpful: number;
}

function ConversationsTab({ token }: { token: string }) {
  const [conversations, setConversations] = useState<AIConversation[]>([]);
  const [stats, setStats] = useState<ConversationStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedConversation, setSelectedConversation] = useState<AIConversation | null>(null);

  // Filters
  const [ratingFilter, setRatingFilter] = useState('all');
  const [curationFilter, setCurationFilter] = useState('all');
  const [sourceFilter, setSourceFilter] = useState('all');

  useEffect(() => {
    fetchConversations();
    fetchStats();
  }, [ratingFilter, curationFilter, sourceFilter]);

  const fetchConversations = async () => {
    setIsLoading(true);
    try {
      const params: Record<string, string> = {};
      if (ratingFilter !== 'all') params.rating_filter = ratingFilter;
      if (curationFilter !== 'all') params.curation_filter = curationFilter;
      if (sourceFilter !== 'all') params.source_filter = sourceFilter;

      const data = await adminApi.getConversations(token, params);
      const convList = data.conversations || data;
      setConversations(Array.isArray(convList) ? convList : []);
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const data = await adminApi.getConversationStats(token);
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const handleCurate = async (id: string, isGood: boolean | null, isBad: boolean | null) => {
    try {
      await adminApi.curateConversation(token, String(id), {
        is_good_example: isGood ?? undefined,
        is_bad_example: isBad ?? undefined,
      });
      fetchConversations();
      fetchStats();
    } catch (error) {
      console.error('Failed to curate:', error);
    }
  };

  const handleSaveNotes = async (id: string, notes: string) => {
    try {
      await adminApi.curateConversation(token, String(id), { admin_notes: notes });
      fetchConversations();
    } catch (error) {
      console.error('Failed to save notes:', error);
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

  return (
    <div className="space-y-6">
      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="card text-center">
            <div className="text-2xl font-bold text-frost">{stats.total}</div>
            <div className="text-xs text-frost-muted">Total</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-ice">{stats.ai_percentage}%</div>
            <div className="text-xs text-frost-muted">AI Routed</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-success">{stats.good_examples}</div>
            <div className="text-xs text-frost-muted">Good Examples</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-warning">{stats.helpful}</div>
            <div className="text-xs text-frost-muted">Helpful</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="card">
        <div className="flex flex-wrap gap-4">
          <div>
            <label className="text-xs text-frost-muted uppercase tracking-wide block mb-1">Rating</label>
            <select
              value={ratingFilter}
              onChange={(e) => setRatingFilter(e.target.value)}
              className="input text-sm py-1"
            >
              <option value="all">All</option>
              <option value="rated">Rated</option>
              <option value="unrated">Unrated</option>
              <option value="helpful">Helpful</option>
              <option value="unhelpful">Not Helpful</option>
            </select>
          </div>
          <div>
            <label className="text-xs text-frost-muted uppercase tracking-wide block mb-1">Curation</label>
            <select
              value={curationFilter}
              onChange={(e) => setCurationFilter(e.target.value)}
              className="input text-sm py-1"
            >
              <option value="all">All</option>
              <option value="good">Good Examples</option>
              <option value="bad">Bad Examples</option>
              <option value="not_curated">Not Curated</option>
            </select>
          </div>
          <div>
            <label className="text-xs text-frost-muted uppercase tracking-wide block mb-1">Source</label>
            <select
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
              className="input text-sm py-1"
            >
              <option value="all">All</option>
              <option value="ai">AI</option>
              <option value="rules">Rules Engine</option>
            </select>
          </div>
        </div>
      </div>

      {/* Conversations List */}
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
      ) : conversations.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-4xl mb-4">💬</div>
          <p className="text-frost-muted">No conversations found with these filters</p>
        </div>
      ) : (
        <div className="card">
          <p className="text-xs text-frost-muted mb-4">Showing {conversations.length} conversations</p>
          <div className="space-y-3">
            {conversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => setSelectedConversation(conv)}
                className={`w-full p-4 rounded-lg transition-colors text-left ${
                  conv.is_good_example
                    ? 'bg-success/10 border border-success/30'
                    : conv.is_bad_example
                    ? 'bg-error/10 border border-error/30'
                    : 'bg-surface hover:bg-surface-hover'
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        conv.routed_to === 'ai'
                          ? 'bg-ice/20 text-ice'
                          : 'bg-surface-hover text-frost-muted'
                      }`}>
                        {conv.routed_to === 'ai' ? 'AI' : 'Rules'}
                      </span>
                      {conv.is_helpful === true && (
                        <span className="text-xs text-success">Helpful</span>
                      )}
                      {conv.is_helpful === false && (
                        <span className="text-xs text-error">Not Helpful</span>
                      )}
                      {conv.is_good_example && (
                        <span className="badge badge-success text-xs">Good</span>
                      )}
                      {conv.is_bad_example && (
                        <span className="badge badge-error text-xs">Bad</span>
                      )}
                    </div>
                    <p className="text-frost truncate">{conv.question}</p>
                    <p className="text-xs text-frost-muted mt-1">
                      {conv.user_email} · {formatDate(conv.created_at)}
                    </p>
                  </div>
                  <span className="text-frost-muted">→</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Conversation Detail Modal */}
      {selectedConversation && (
        <ConversationDetailModal
          conversation={selectedConversation}
          onClose={() => setSelectedConversation(null)}
          onCurate={handleCurate}
          onSaveNotes={handleSaveNotes}
          formatDate={formatDate}
        />
      )}
    </div>
  );
}

function ConversationDetailModal({
  conversation,
  onClose,
  onCurate,
  onSaveNotes,
  formatDate,
}: {
  conversation: AIConversation;
  onClose: () => void;
  onCurate: (id: string, isGood: boolean | null, isBad: boolean | null) => void;
  onSaveNotes: (id: string, notes: string) => void;
  formatDate: (date: string) => string;
}) {
  const [notes, setNotes] = useState(conversation.admin_notes || '');

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-surface rounded-xl border border-surface-border max-w-2xl w-full p-6 animate-fadeIn max-h-[85vh] overflow-y-auto">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-frost">Conversation Details</h2>
            <div className="flex items-center gap-2 mt-1">
              <span className={`text-xs px-2 py-0.5 rounded ${
                conversation.routed_to === 'ai'
                  ? 'bg-ice/20 text-ice'
                  : 'bg-surface-hover text-frost-muted'
              }`}>
                {conversation.routed_to === 'ai' ? 'AI' : 'Rules'}
              </span>
              <span className="text-sm text-frost-muted">{formatDate(conversation.created_at)}</span>
            </div>
          </div>
          <button onClick={onClose} className="text-frost-muted hover:text-frost">
            ✕
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="text-xs text-frost-muted uppercase tracking-wide">From</label>
            <p className="text-frost">{conversation.user_email}</p>
          </div>

          <div>
            <label className="text-xs text-frost-muted uppercase tracking-wide">Question</label>
            <div className="p-3 rounded-lg bg-background mt-1">
              <p className="text-frost whitespace-pre-wrap">{conversation.question}</p>
            </div>
          </div>

          <div>
            <label className="text-xs text-frost-muted uppercase tracking-wide">Answer</label>
            <div className="p-3 rounded-lg bg-background mt-1 max-h-64 overflow-y-auto">
              <p className="text-frost whitespace-pre-wrap">{conversation.answer}</p>
            </div>
          </div>

          {/* Metadata row */}
          <div className="flex flex-wrap gap-4 text-sm">
            <div>
              <span className="text-frost-muted">Provider:</span>{' '}
              <span className="text-frost">{conversation.provider}</span>
            </div>
            <div>
              <span className="text-frost-muted">Model:</span>{' '}
              <span className="text-frost">{conversation.model}</span>
            </div>
            {conversation.is_helpful !== null && (
              <div>
                <span className="text-frost-muted">Helpful:</span>{' '}
                <span className={conversation.is_helpful ? 'text-success' : 'text-error'}>
                  {conversation.is_helpful ? 'Yes' : 'No'}
                </span>
              </div>
            )}
            {conversation.rating && (
              <div>
                <span className="text-frost-muted">Rating:</span>{' '}
                <span className="text-warning">{'★'.repeat(conversation.rating)}</span>
              </div>
            )}
          </div>

          {conversation.user_feedback && (
            <div>
              <label className="text-xs text-frost-muted uppercase tracking-wide">User Feedback</label>
              <p className="text-frost mt-1">{conversation.user_feedback}</p>
            </div>
          )}

          {/* Curation */}
          <div>
            <label className="text-xs text-frost-muted uppercase tracking-wide block mb-2">
              Curate for Training
            </label>
            <div className="flex gap-2">
              <button
                onClick={() => onCurate(conversation.id, true, false)}
                disabled={conversation.is_good_example}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  conversation.is_good_example
                    ? 'bg-success/20 text-success cursor-default'
                    : 'bg-surface-hover text-frost-muted hover:text-frost'
                }`}
              >
                Good Example
              </button>
              <button
                onClick={() => onCurate(conversation.id, false, true)}
                disabled={conversation.is_bad_example}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  conversation.is_bad_example
                    ? 'bg-error/20 text-error cursor-default'
                    : 'bg-surface-hover text-frost-muted hover:text-frost'
                }`}
              >
                Bad Example
              </button>
              <button
                onClick={() => onCurate(conversation.id, false, false)}
                disabled={!conversation.is_good_example && !conversation.is_bad_example}
                className="px-4 py-2 rounded-lg text-sm font-medium bg-surface-hover text-frost-muted hover:text-frost transition-colors"
              >
                Reset
              </button>
            </div>
          </div>

          {/* Admin Notes */}
          <div>
            <label className="text-xs text-frost-muted uppercase tracking-wide block mb-2">
              Admin Notes
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add notes about this conversation..."
              className="input w-full h-20 resize-none"
            />
            {notes !== (conversation.admin_notes || '') && (
              <button
                onClick={() => onSaveNotes(conversation.id, notes)}
                className="btn-primary text-sm mt-2"
              >
                Save Notes
              </button>
            )}
          </div>
        </div>
      </div>
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
  onUpdateStatus: (id: string, status: string) => void;
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
            <label className="text-xs text-frost-muted uppercase tracking-wide">User</label>
            <p className="text-frost">{feedback.user_id || 'Anonymous'}</p>
          </div>

          <div>
            <label className="text-xs text-frost-muted uppercase tracking-wide">Category</label>
            <p className="text-frost capitalize">{feedback.category || 'Other'}</p>
          </div>

          <div>
            <label className="text-xs text-frost-muted uppercase tracking-wide">Description</label>
            <p className="text-frost whitespace-pre-wrap">{feedback.description}</p>
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

          {error.user_id && (
            <div>
              <label className="text-xs text-frost-muted uppercase tracking-wide">User</label>
              <p className="text-frost">{error.user_id}</p>
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
