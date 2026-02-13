'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';
import { adminApi, AdminThread, AdminThreadMessage, AdminUser, FeedbackItem, Conversation, ConversationStats } from '@/lib/api';

interface ErrorItem {
  id: string;
  error_type: string;
  message: string;
  error_message?: string;
  stack_trace: string | null;
  user_id: string | null;
  page: string | null;
  environment: string | null;
  status: string;
  fix_notes: string | null;
  extra_context: string | null;
  created_at: string;
  resolved: boolean;
  ai_diagnosis?: string | null;
  diagnosed_at?: string | null;
}

type TabType = 'feedback' | 'errors' | 'conversations' | 'messages';

export default function AdminInboxPage() {
  const { token, user } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('feedback');
  const [feedback, setFeedback] = useState<FeedbackItem[]>([]);
  const [errors, setErrors] = useState<ErrorItem[]>([]);
  const [threads, setThreads] = useState<AdminThread[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (token) {
      fetchData();
    }
  }, [token]);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [feedbackData, errorsData, threadsData] = await Promise.all([
        adminApi.listFeedback(token!),
        adminApi.getErrors(token!),
        adminApi.listThreads(token!),
      ]);

      const fbList = feedbackData.feedback || feedbackData;
      setFeedback(Array.isArray(fbList) ? fbList : []);
      const errList = errorsData.errors || errorsData;
      setErrors(Array.isArray(errList) ? errList : []);
      const thList = threadsData.threads || threadsData;
      setThreads(Array.isArray(thList) ? thList : []);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setIsLoading(false);
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

  const pendingFeedback = feedback.filter((f) => f.status === 'new' || f.status === 'pending_fix' || f.status === 'pending_update');
  const unresolvedErrors = errors.filter((e) => !e.resolved && e.status !== 'fixed' && e.status !== 'ignored');
  const unreadThreads = threads.filter((t) => !t.is_read_by_admin);

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
          <p className="text-frost-muted mt-1">User feedback, errors, conversations, and messages</p>
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
            onClick={() => setActiveTab('messages')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'messages'
                ? 'bg-ice/20 text-ice'
                : 'text-frost-muted hover:text-frost hover:bg-surface'
            }`}
          >
            Messages
            {unreadThreads.length > 0 && (
              <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-ice/20 text-ice">
                {unreadThreads.length}
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
            token={token || ''}
            onRefresh={fetchData}
            formatDate={formatDate}
          />
        ) : activeTab === 'errors' ? (
          <ErrorsTab
            errors={errors}
            token={token || ''}
            onRefresh={fetchData}
            formatDate={formatDate}
          />
        ) : activeTab === 'messages' ? (
          <MessagesTab
            threads={threads}
            token={token || ''}
            onRefresh={fetchData}
            formatDate={formatDate}
          />
        ) : (
          <ConversationsTab token={token || ''} />
        )}
      </div>
    </PageLayout>
  );
}

// =============================================================
// FEEDBACK TAB - Enhanced with stats, sub-tabs, smart routing
// =============================================================

type FeedbackSubTab = 'new_bugs' | 'new_features' | 'pending_fix' | 'pending_update' | 'completed' | 'archive';

function FeedbackTab({
  feedback,
  token,
  onRefresh,
  formatDate,
}: {
  feedback: FeedbackItem[];
  token: string;
  onRefresh: () => void;
  formatDate: (date: string) => string;
}) {
  const [activeSubTab, setActiveSubTab] = useState<FeedbackSubTab>('new_bugs');
  const [selectedFeedback, setSelectedFeedback] = useState<FeedbackItem | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);
  const [confirmBulk, setConfirmBulk] = useState<string | null>(null);

  // Compute stats
  const newCount = feedback.filter((f) => f.status === 'new').length;
  const pendingFixCount = feedback.filter((f) => f.status === 'pending_fix').length;
  const pendingUpdateCount = feedback.filter((f) => f.status === 'pending_update').length;
  const completedCount = feedback.filter((f) => f.status === 'completed').length;
  const archiveCount = feedback.filter((f) => f.status === 'archive').length;
  const totalCount = feedback.length;

  // Sub-tab filtered data
  const getFilteredFeedback = (): FeedbackItem[] => {
    switch (activeSubTab) {
      case 'new_bugs':
        return feedback.filter((f) => f.category === 'bug' && f.status === 'new');
      case 'new_features':
        return feedback.filter((f) => f.category === 'feature' && f.status === 'new');
      case 'pending_fix':
        return feedback.filter((f) => f.status === 'pending_fix');
      case 'pending_update':
        return feedback.filter((f) => f.status === 'pending_update');
      case 'completed':
        return feedback.filter((f) => f.status === 'completed');
      case 'archive':
        return feedback.filter((f) => f.status === 'archive');
      default:
        return [];
    }
  };

  const handleUpdateStatus = async (id: string, status: string) => {
    try {
      const feedbackId = id;
      await adminApi.updateFeedback(token, String(feedbackId), { status });
      onRefresh();
      setSelectedFeedback(null);
    } catch (error) {
      console.error('Failed to update feedback:', error);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await adminApi.deleteFeedback(token, String(id));
      setConfirmDelete(null);
      onRefresh();
    } catch (error) {
      console.error('Failed to delete feedback:', error);
    }
  };

  const handleBulkAction = async (action: string) => {
    try {
      await adminApi.bulkFeedbackAction(token, action);
      setConfirmBulk(null);
      onRefresh();
    } catch (error) {
      console.error('Failed to perform bulk action:', error);
    }
  };

  const statusColors: Record<string, string> = {
    new: 'bg-sky-500/20 text-sky-400',
    pending_fix: 'bg-red-500/20 text-red-400',
    pending_update: 'bg-purple-500/20 text-purple-400',
    completed: 'bg-emerald-500/20 text-emerald-400',
    archive: 'bg-gray-500/20 text-gray-400',
  };

  const categoryConfig: Record<string, { color: string; icon: string; label: string }> = {
    bug: { color: 'text-red-400', icon: '!', label: 'Bug' },
    feature: { color: 'text-purple-400', icon: '+', label: 'Feature' },
    data_error: { color: 'text-yellow-400', icon: '~', label: 'Data Error' },
    other: { color: 'text-frost-muted', icon: '?', label: 'Other' },
  };

  const subTabs: { key: FeedbackSubTab; label: string; count: number }[] = [
    { key: 'new_bugs', label: 'New Bugs', count: feedback.filter((f) => f.category === 'bug' && f.status === 'new').length },
    { key: 'new_features', label: 'New Features', count: feedback.filter((f) => f.category === 'feature' && f.status === 'new').length },
    { key: 'pending_fix', label: 'Pending Fix', count: pendingFixCount },
    { key: 'pending_update', label: 'Pending Update', count: pendingUpdateCount },
    { key: 'completed', label: 'Completed', count: completedCount },
    { key: 'archive', label: 'Archive', count: archiveCount },
  ];

  const filtered = getFilteredFeedback();

  return (
    <div className="space-y-6">
      {/* Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="card text-center py-3">
          <div className="text-2xl font-bold text-sky-400">{newCount}</div>
          <div className="text-xs text-frost-muted mt-1">New</div>
        </div>
        <div className="card text-center py-3">
          <div className="text-2xl font-bold text-red-400">{pendingFixCount}</div>
          <div className="text-xs text-frost-muted mt-1">Pending Fix</div>
        </div>
        <div className="card text-center py-3">
          <div className="text-2xl font-bold text-purple-400">{pendingUpdateCount}</div>
          <div className="text-xs text-frost-muted mt-1">Pending Update</div>
        </div>
        <div className="card text-center py-3">
          <div className="text-2xl font-bold text-emerald-400">{completedCount}</div>
          <div className="text-xs text-frost-muted mt-1">Completed</div>
        </div>
        <div className="card text-center py-3">
          <div className="text-2xl font-bold text-frost">{totalCount}</div>
          <div className="text-xs text-frost-muted mt-1">Total</div>
        </div>
      </div>

      {/* Sub-tabs */}
      <div className="flex flex-wrap gap-1 bg-surface/50 rounded-lg p-1">
        {subTabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveSubTab(tab.key)}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
              activeSubTab === tab.key
                ? 'bg-ice/20 text-ice'
                : 'text-frost-muted hover:text-frost hover:bg-surface-hover'
            }`}
          >
            {tab.label}
            <span className="ml-1.5 text-[10px] opacity-70">({tab.count})</span>
          </button>
        ))}
      </div>

      {/* Bulk Actions */}
      {activeSubTab === 'completed' && completedCount > 0 && (
        <div className="flex gap-2">
          {confirmBulk === 'archive_completed' ? (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-warning/10 border border-warning/20">
              <span className="text-sm text-warning">Archive all {completedCount} completed items?</span>
              <button
                onClick={() => handleBulkAction('archive_completed')}
                className="px-3 py-1 rounded text-xs font-medium bg-warning/20 text-warning hover:bg-warning/30 transition-colors"
              >
                Yes, Archive
              </button>
              <button
                onClick={() => setConfirmBulk(null)}
                className="px-3 py-1 rounded text-xs font-medium text-frost-muted hover:text-frost transition-colors"
              >
                Cancel
              </button>
            </div>
          ) : (
            <button
              onClick={() => setConfirmBulk('archive_completed')}
              className="btn-secondary text-xs"
            >
              Archive All Completed
            </button>
          )}
        </div>
      )}
      {activeSubTab === 'archive' && archiveCount > 0 && (
        <div className="flex gap-2">
          {confirmBulk === 'empty_archive' ? (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-error/10 border border-error/20">
              <span className="text-sm text-error">Permanently delete all {archiveCount} archived items?</span>
              <button
                onClick={() => handleBulkAction('empty_archive')}
                className="px-3 py-1 rounded text-xs font-medium bg-error/20 text-error hover:bg-error/30 transition-colors"
              >
                Yes, Delete All
              </button>
              <button
                onClick={() => setConfirmBulk(null)}
                className="px-3 py-1 rounded text-xs font-medium text-frost-muted hover:text-frost transition-colors"
              >
                Cancel
              </button>
            </div>
          ) : (
            <button
              onClick={() => setConfirmBulk('empty_archive')}
              className="btn-danger text-xs"
            >
              Empty Archive
            </button>
          )}
        </div>
      )}

      {/* Feedback Items */}
      {filtered.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-4xl mb-4">
            {activeSubTab === 'archive' ? '📦' : activeSubTab === 'completed' ? '✅' : '📬'}
          </div>
          <p className="text-frost-muted">
            {activeSubTab === 'new_bugs' ? 'No new bugs to review' :
             activeSubTab === 'new_features' ? 'No new feature requests' :
             activeSubTab === 'pending_fix' ? 'No bugs pending fix' :
             activeSubTab === 'pending_update' ? 'No features pending update' :
             activeSubTab === 'completed' ? 'No completed items' :
             'Archive is empty'}
          </p>
        </div>
      ) : (
        <div className="card">
          <div className="space-y-3">
            {filtered.map((item) => {
              const itemId = item.feedback_id || item.id;
              const cat = categoryConfig[item.category] || categoryConfig.other;

              return (
                <div
                  key={itemId}
                  className="p-4 rounded-lg bg-surface hover:bg-surface-hover transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      {/* Header: Category + Page + Status */}
                      <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                        <span className={`text-sm font-semibold ${cat.color}`}>
                          [{cat.label}]
                        </span>
                        {item.page && (
                          <span className="text-xs px-2 py-0.5 rounded bg-surface-hover text-frost-muted">
                            {item.page}
                          </span>
                        )}
                        <span className={`text-xs px-2 py-0.5 rounded-full ${statusColors[item.status] || 'bg-gray-500/20 text-gray-400'}`}>
                          {item.status.replace(/_/g, ' ')}
                        </span>
                      </div>

                      {/* Description */}
                      <p className="text-frost text-sm">{item.description}</p>

                      {/* Footer */}
                      <p className="text-xs text-frost-muted mt-2">
                        User: {item.user_id || 'Anonymous'} &middot; {formatDate(item.created_at)}
                      </p>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center gap-2 mt-3 pt-3 border-t border-surface-border/50">
                    {/* Smart routing buttons for new items */}
                    {item.status === 'new' && item.category === 'bug' && (
                      <button
                        onClick={() => handleUpdateStatus(itemId, 'pending_fix')}
                        className="px-3 py-1 rounded text-xs font-medium bg-red-500/15 text-red-400 hover:bg-red-500/25 transition-colors"
                      >
                        To Fix
                      </button>
                    )}
                    {item.status === 'new' && item.category === 'feature' && (
                      <button
                        onClick={() => handleUpdateStatus(itemId, 'pending_update')}
                        className="px-3 py-1 rounded text-xs font-medium bg-purple-500/15 text-purple-400 hover:bg-purple-500/25 transition-colors"
                      >
                        To Update
                      </button>
                    )}
                    {item.status === 'new' && item.category !== 'bug' && item.category !== 'feature' && (
                      <>
                        <button
                          onClick={() => handleUpdateStatus(itemId, 'pending_fix')}
                          className="px-3 py-1 rounded text-xs font-medium bg-red-500/15 text-red-400 hover:bg-red-500/25 transition-colors"
                        >
                          To Fix
                        </button>
                        <button
                          onClick={() => handleUpdateStatus(itemId, 'pending_update')}
                          className="px-3 py-1 rounded text-xs font-medium bg-purple-500/15 text-purple-400 hover:bg-purple-500/25 transition-colors"
                        >
                          To Update
                        </button>
                      </>
                    )}

                    {/* Archive for non-archived items */}
                    {item.status !== 'archive' && (
                      <button
                        onClick={() => handleUpdateStatus(itemId, 'archive')}
                        className="px-3 py-1 rounded text-xs font-medium bg-surface-hover text-frost-muted hover:text-frost transition-colors"
                      >
                        Archive
                      </button>
                    )}

                    {/* Restore for archived items */}
                    {item.status === 'archive' && (
                      <button
                        onClick={() => handleUpdateStatus(itemId, 'new')}
                        className="px-3 py-1 rounded text-xs font-medium bg-sky-500/15 text-sky-400 hover:bg-sky-500/25 transition-colors"
                      >
                        Restore
                      </button>
                    )}

                    {/* Delete with confirmation */}
                    {confirmDelete === itemId ? (
                      <div className="flex items-center gap-1.5 ml-auto">
                        <span className="text-xs text-warning">Delete?</span>
                        <button
                          onClick={() => handleDelete(itemId)}
                          className="px-2 py-1 rounded text-xs font-medium bg-error/20 text-error hover:bg-error/30 transition-colors"
                        >
                          Yes
                        </button>
                        <button
                          onClick={() => setConfirmDelete(null)}
                          className="px-2 py-1 rounded text-xs font-medium text-frost-muted hover:text-frost transition-colors"
                        >
                          No
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => setConfirmDelete(itemId)}
                        className="px-2 py-1 rounded text-xs text-frost-muted hover:text-error transition-colors ml-auto"
                        title="Delete"
                      >
                        Delete
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Feedback Detail Modal */}
      {selectedFeedback && (
        <FeedbackDetailModal
          feedback={selectedFeedback}
          onClose={() => setSelectedFeedback(null)}
          onUpdateStatus={handleUpdateStatus}
          formatDate={formatDate}
        />
      )}
    </div>
  );
}

// =============================================================
// ERRORS TAB - Enhanced with stats, sub-tabs, workflow buttons
// =============================================================

type ErrorSubTab = 'new' | 'reviewed' | 'fixed' | 'ignored';

function ErrorsTab({
  errors,
  token,
  onRefresh,
  formatDate,
}: {
  errors: ErrorItem[];
  token: string;
  onRefresh: () => void;
  formatDate: (date: string) => string;
}) {
  const [activeSubTab, setActiveSubTab] = useState<ErrorSubTab>('new');
  const [expandedTrace, setExpandedTrace] = useState<string | null>(null);
  const [fixNotesInput, setFixNotesInput] = useState<Record<string, string>>({});
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);
  const [confirmBulk, setConfirmBulk] = useState<string | null>(null);
  const [diagnosing, setDiagnosing] = useState<string | null>(null);
  const [expandedDiagnosis, setExpandedDiagnosis] = useState<string | null>(null);

  // Compute stats
  const now = new Date();
  const twentyFourHoursAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
  const newCount = errors.filter((e) => e.status === 'new' || (!e.status && !e.resolved)).length;
  const reviewedCount = errors.filter((e) => e.status === 'reviewed').length;
  const fixedCount = errors.filter((e) => e.status === 'fixed' || e.status === 'resolved' || (e.resolved && !e.status)).length;
  const ignoredCount = errors.filter((e) => e.status === 'ignored').length;
  const last24hCount = errors.filter((e) => new Date(e.created_at) >= twentyFourHoursAgo).length;

  // Filtered errors by sub-tab
  const getFilteredErrors = (): ErrorItem[] => {
    switch (activeSubTab) {
      case 'new':
        return errors.filter((e) => e.status === 'new' || (!e.status && !e.resolved));
      case 'reviewed':
        return errors.filter((e) => e.status === 'reviewed');
      case 'fixed':
        return errors.filter((e) => e.status === 'fixed' || e.status === 'resolved' || (e.resolved && !e.status));
      case 'ignored':
        return errors.filter((e) => e.status === 'ignored');
      default:
        return [];
    }
  };

  const handleUpdateError = async (id: string, status: string) => {
    try {
      await adminApi.updateError(token, String(id), { status });
      onRefresh();
    } catch (error) {
      console.error('Failed to update error:', error);
    }
  };

  const handleSaveFixNotes = async (id: string) => {
    try {
      await adminApi.updateError(token, String(id), { fix_notes: fixNotesInput[id] || '' });
      setFixNotesInput((prev) => ({ ...prev, [id]: '' }));
      onRefresh();
    } catch (error) {
      console.error('Failed to save fix notes:', error);
    }
  };

  const handleDeleteError = async (id: string) => {
    try {
      await adminApi.deleteError(token, String(id));
      setConfirmDelete(null);
      onRefresh();
    } catch (error) {
      console.error('Failed to delete error:', error);
    }
  };

  const handleDiagnose = async (id: string) => {
    setDiagnosing(id);
    try {
      const result = await adminApi.diagnoseError(token, String(id));
      // Update the error in the local list with the diagnosis
      const idx = errors.findIndex((e) => e.id === id);
      if (idx !== -1) {
        errors[idx] = { ...errors[idx], ai_diagnosis: result.diagnosis, diagnosed_at: result.diagnosed_at };
      }
      setExpandedDiagnosis(id);
    } catch (error) {
      console.error('Failed to diagnose error:', error);
    } finally {
      setDiagnosing(null);
    }
  };

  const handleBulkAction = async (action: string) => {
    try {
      await adminApi.bulkErrorAction(token, action);
      setConfirmBulk(null);
      onRefresh();
    } catch (error) {
      console.error('Failed to perform bulk action:', error);
    }
  };

  const subTabs: { key: ErrorSubTab; label: string; count: number }[] = [
    { key: 'new', label: 'New', count: newCount },
    { key: 'reviewed', label: 'Reviewed', count: reviewedCount },
    { key: 'fixed', label: 'Fixed', count: fixedCount },
    { key: 'ignored', label: 'Ignored', count: ignoredCount },
  ];

  const filtered = getFilteredErrors();

  const envBadgeColor = (env: string | null) => {
    if (!env) return 'bg-gray-500/20 text-gray-400';
    if (env === 'production' || env === 'prod') return 'bg-emerald-500/20 text-emerald-400';
    return 'bg-sky-500/20 text-sky-400';
  };

  // Contextual workflow buttons based on current status
  const renderWorkflowButtons = (item: ErrorItem) => {
    const id = item.id;
    const currentStatus = item.status || (item.resolved ? 'fixed' : 'new');

    const buttons: JSX.Element[] = [];

    if (currentStatus === 'new') {
      buttons.push(
        <button key="reviewed" onClick={() => handleUpdateError(id, 'reviewed')}
          className="px-3 py-1 rounded text-xs font-medium bg-amber-500/15 text-amber-400 hover:bg-amber-500/25 transition-colors">
          Reviewed
        </button>,
        <button key="fixed" onClick={() => handleUpdateError(id, 'fixed')}
          className="px-3 py-1 rounded text-xs font-medium bg-emerald-500/15 text-emerald-400 hover:bg-emerald-500/25 transition-colors">
          Fixed
        </button>,
        <button key="ignore" onClick={() => handleUpdateError(id, 'ignored')}
          className="px-3 py-1 rounded text-xs font-medium bg-gray-500/15 text-gray-400 hover:bg-gray-500/25 transition-colors">
          Ignore
        </button>
      );
    } else if (currentStatus === 'reviewed') {
      buttons.push(
        <button key="fixed" onClick={() => handleUpdateError(id, 'fixed')}
          className="px-3 py-1 rounded text-xs font-medium bg-emerald-500/15 text-emerald-400 hover:bg-emerald-500/25 transition-colors">
          Fixed
        </button>,
        <button key="ignore" onClick={() => handleUpdateError(id, 'ignored')}
          className="px-3 py-1 rounded text-xs font-medium bg-gray-500/15 text-gray-400 hover:bg-gray-500/25 transition-colors">
          Ignore
        </button>,
        <button key="reopen" onClick={() => handleUpdateError(id, 'new')}
          className="px-3 py-1 rounded text-xs font-medium bg-sky-500/15 text-sky-400 hover:bg-sky-500/25 transition-colors">
          Reopen
        </button>
      );
    } else if (currentStatus === 'fixed' || currentStatus === 'resolved') {
      buttons.push(
        <button key="reopen" onClick={() => handleUpdateError(id, 'new')}
          className="px-3 py-1 rounded text-xs font-medium bg-sky-500/15 text-sky-400 hover:bg-sky-500/25 transition-colors">
          Reopen
        </button>
      );
    } else if (currentStatus === 'ignored') {
      buttons.push(
        <button key="reopen" onClick={() => handleUpdateError(id, 'new')}
          className="px-3 py-1 rounded text-xs font-medium bg-sky-500/15 text-sky-400 hover:bg-sky-500/25 transition-colors">
          Reopen
        </button>
      );
    }

    return buttons;
  };

  return (
    <div className="space-y-6">
      {/* Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="card text-center py-3">
          <div className="text-2xl font-bold text-red-400">{newCount}</div>
          <div className="text-xs text-frost-muted mt-1">New</div>
        </div>
        <div className="card text-center py-3">
          <div className="text-2xl font-bold text-amber-400">{reviewedCount}</div>
          <div className="text-xs text-frost-muted mt-1">Reviewed</div>
        </div>
        <div className="card text-center py-3">
          <div className="text-2xl font-bold text-emerald-400">{fixedCount}</div>
          <div className="text-xs text-frost-muted mt-1">Fixed</div>
        </div>
        <div className="card text-center py-3">
          <div className="text-2xl font-bold text-gray-400">{ignoredCount}</div>
          <div className="text-xs text-frost-muted mt-1">Ignored</div>
        </div>
        <div className="card text-center py-3">
          <div className="text-2xl font-bold text-ice">{last24hCount}</div>
          <div className="text-xs text-frost-muted mt-1">Last 24h</div>
        </div>
      </div>

      {/* Sub-tabs */}
      <div className="flex flex-wrap gap-1 bg-surface/50 rounded-lg p-1">
        {subTabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveSubTab(tab.key)}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
              activeSubTab === tab.key
                ? 'bg-ice/20 text-ice'
                : 'text-frost-muted hover:text-frost hover:bg-surface-hover'
            }`}
          >
            {tab.label}
            <span className="ml-1.5 text-[10px] opacity-70">({tab.count})</span>
          </button>
        ))}
      </div>

      {/* Bulk Action: Delete All Ignored */}
      {activeSubTab === 'ignored' && ignoredCount > 0 && (
        <div className="flex gap-2">
          {confirmBulk === 'delete_ignored' ? (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-error/10 border border-error/20">
              <span className="text-sm text-error">Permanently delete all {ignoredCount} ignored errors?</span>
              <button
                onClick={() => handleBulkAction('delete_ignored')}
                className="px-3 py-1 rounded text-xs font-medium bg-error/20 text-error hover:bg-error/30 transition-colors"
              >
                Yes, Delete All
              </button>
              <button
                onClick={() => setConfirmBulk(null)}
                className="px-3 py-1 rounded text-xs font-medium text-frost-muted hover:text-frost transition-colors"
              >
                Cancel
              </button>
            </div>
          ) : (
            <button
              onClick={() => setConfirmBulk('delete_ignored')}
              className="btn-danger text-xs"
            >
              Delete All Ignored
            </button>
          )}
        </div>
      )}

      {/* Error Items */}
      {filtered.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-4xl mb-4">
            {activeSubTab === 'new' ? '✅' : activeSubTab === 'fixed' ? '🔧' : '📋'}
          </div>
          <p className="text-frost-muted">
            {activeSubTab === 'new' ? 'No new errors - the system is running smoothly!' :
             activeSubTab === 'reviewed' ? 'No errors awaiting fix' :
             activeSubTab === 'fixed' ? 'No fixed errors' :
             'No ignored errors'}
          </p>
        </div>
      ) : (
        <div className="card">
          <div className="space-y-3">
            {filtered.map((item) => {
              const errorMsg = item.error_message || item.message || '';
              const isTraceExpanded = expandedTrace === item.id;

              return (
                <div
                  key={item.id}
                  className={`p-4 rounded-lg transition-colors ${
                    (item.status === 'new' || (!item.status && !item.resolved))
                      ? 'bg-error/5 border border-error/20'
                      : 'bg-surface'
                  }`}
                >
                  {/* Header: Error type + Page + Environment + Status */}
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                        <span className="text-sm font-semibold text-error">{item.error_type}</span>
                        {item.page && (
                          <span className="text-xs px-2 py-0.5 rounded bg-surface-hover text-frost-muted">
                            {item.page}
                          </span>
                        )}
                        {item.environment && (
                          <span className={`text-xs px-2 py-0.5 rounded ${envBadgeColor(item.environment)}`}>
                            {item.environment}
                          </span>
                        )}
                      </div>

                      {/* Error Message */}
                      <div className="p-2.5 rounded bg-error/5 border-l-2 border-error/40 mb-2">
                        <p className="text-frost text-sm font-mono">{errorMsg.slice(0, 500)}</p>
                      </div>

                      {/* Stack Trace (expandable) */}
                      {item.stack_trace && (
                        <div className="mb-2">
                          <button
                            onClick={() => setExpandedTrace(isTraceExpanded ? null : item.id)}
                            className="text-xs text-ice hover:text-frost transition-colors"
                          >
                            {isTraceExpanded ? 'Hide Stack Trace' : 'Show Stack Trace'}
                          </button>
                          {isTraceExpanded && (
                            <pre className="mt-2 p-3 rounded-lg bg-background text-xs text-frost-muted overflow-x-auto max-h-64 overflow-y-auto border border-surface-border">
                              {item.stack_trace}
                            </pre>
                          )}
                        </div>
                      )}

                      {/* Fix Notes Display */}
                      {item.fix_notes && (
                        <div className="p-2.5 rounded bg-emerald-500/10 border-l-2 border-emerald-500/40 mb-2">
                          <p className="text-xs text-frost-muted uppercase tracking-wide mb-0.5">Fix Notes</p>
                          <p className="text-sm text-frost">{item.fix_notes}</p>
                        </div>
                      )}

                      {/* AI Diagnosis */}
                      {item.ai_diagnosis && (
                        <div className="mb-2">
                          <button
                            onClick={() => setExpandedDiagnosis(expandedDiagnosis === item.id ? null : item.id)}
                            className="text-xs text-purple-400 hover:text-purple-300 transition-colors"
                          >
                            {expandedDiagnosis === item.id ? 'Hide AI Diagnosis' : 'Show AI Diagnosis'}
                            {item.diagnosed_at && (
                              <span className="text-frost-muted ml-1">({formatDate(item.diagnosed_at)})</span>
                            )}
                          </button>
                          {expandedDiagnosis === item.id && (
                            <div className="mt-2 p-3 rounded-lg bg-purple-500/5 border border-purple-500/20">
                              <p className="text-xs text-purple-400 uppercase tracking-wide mb-1.5">AI Diagnosis</p>
                              <pre className="text-sm text-frost whitespace-pre-wrap font-sans">{item.ai_diagnosis}</pre>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Footer */}
                      <p className="text-xs text-frost-muted mt-2">
                        {item.user_id ? `User: ${item.user_id} \u00b7 ` : ''}{formatDate(item.created_at)}
                      </p>
                    </div>
                  </div>

                  {/* Fix Notes Input */}
                  <div className="mt-2">
                    <div className="flex gap-2">
                      <input
                        type="text"
                        placeholder="Add fix notes..."
                        value={fixNotesInput[item.id] || ''}
                        onChange={(e) => setFixNotesInput((prev) => ({ ...prev, [item.id]: e.target.value }))}
                        className="input text-xs py-1 flex-1"
                      />
                      {fixNotesInput[item.id] && (
                        <button
                          onClick={() => handleSaveFixNotes(item.id)}
                          className="px-3 py-1 rounded text-xs font-medium bg-ice/20 text-ice hover:bg-ice/30 transition-colors"
                        >
                          Save
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Workflow Buttons */}
                  <div className="flex items-center gap-2 mt-3 pt-3 border-t border-surface-border/50">
                    {renderWorkflowButtons(item)}

                    {/* Diagnose with AI */}
                    <button
                      onClick={() => handleDiagnose(item.id)}
                      disabled={diagnosing === item.id}
                      className="px-2.5 py-1 rounded text-xs font-medium bg-purple-500/20 text-purple-400 hover:bg-purple-500/30 transition-colors disabled:opacity-50"
                    >
                      {diagnosing === item.id ? 'Diagnosing...' : item.ai_diagnosis ? 'Re-diagnose' : 'Diagnose with AI'}
                    </button>

                    {/* Delete with confirmation */}
                    {confirmDelete === item.id ? (
                      <div className="flex items-center gap-1.5 ml-auto">
                        <span className="text-xs text-warning">Delete?</span>
                        <button
                          onClick={() => handleDeleteError(item.id)}
                          className="px-2 py-1 rounded text-xs font-medium bg-error/20 text-error hover:bg-error/30 transition-colors"
                        >
                          Yes
                        </button>
                        <button
                          onClick={() => setConfirmDelete(null)}
                          className="px-2 py-1 rounded text-xs font-medium text-frost-muted hover:text-frost transition-colors"
                        >
                          No
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => setConfirmDelete(item.id)}
                        className="px-2 py-1 rounded text-xs text-frost-muted hover:text-error transition-colors ml-auto"
                        title="Delete"
                      >
                        Delete
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================
// MESSAGES TAB - Admin-to-user conversation threads
// =============================================================

function MessagesTab({
  threads,
  token,
  onRefresh,
  formatDate,
}: {
  threads: AdminThread[];
  token: string;
  onRefresh: () => void;
  formatDate: (date: string) => string;
}) {
  const [selectedThread, setSelectedThread] = useState<AdminThread | null>(null);
  const [showNewMessage, setShowNewMessage] = useState(false);

  const openCount = threads.filter((t) => t.status === 'open').length;
  const closedCount = threads.filter((t) => t.status === 'closed').length;
  const unreadCount = threads.filter((t) => !t.is_read_by_admin).length;

  return (
    <div className="space-y-6">
      {/* Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="card text-center py-3">
          <div className="text-2xl font-bold text-ice">{threads.length}</div>
          <div className="text-xs text-frost-muted mt-1">Total</div>
        </div>
        <div className="card text-center py-3">
          <div className="text-2xl font-bold text-sky-400">{openCount}</div>
          <div className="text-xs text-frost-muted mt-1">Open</div>
        </div>
        <div className="card text-center py-3">
          <div className="text-2xl font-bold text-amber-400">{unreadCount}</div>
          <div className="text-xs text-frost-muted mt-1">Unread</div>
        </div>
        <div className="card text-center py-3">
          <div className="text-2xl font-bold text-gray-400">{closedCount}</div>
          <div className="text-xs text-frost-muted mt-1">Closed</div>
        </div>
      </div>

      {/* New Message Button */}
      <div>
        <button
          onClick={() => setShowNewMessage(true)}
          className="btn-primary text-sm"
        >
          New Message
        </button>
      </div>

      {/* Thread List */}
      {threads.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-4xl mb-4">💬</div>
          <p className="text-frost-muted">No message threads yet</p>
          <p className="text-sm text-frost-muted mt-2">
            Click "New Message" to start a conversation with a user
          </p>
        </div>
      ) : (
        <div className="card">
          <div className="space-y-2">
            {threads.map((thread) => (
              <button
                key={thread.thread_id}
                onClick={() => setSelectedThread(thread)}
                className={`w-full p-4 rounded-lg text-left transition-colors ${
                  !thread.is_read_by_admin
                    ? 'bg-surface hover:bg-surface-hover'
                    : 'bg-surface/50 hover:bg-surface'
                }`}
              >
                <div className="flex items-start gap-3">
                  {!thread.is_read_by_admin && (
                    <span className="w-2 h-2 mt-2 rounded-full bg-ice flex-shrink-0" />
                  )}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2 min-w-0">
                        <h3 className={`font-medium truncate ${
                          !thread.is_read_by_admin ? 'text-frost' : 'text-frost-muted'
                        }`}>
                          {thread.subject}
                        </h3>
                        {thread.status === 'closed' && (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-gray-500/20 text-gray-400 flex-shrink-0">
                            Closed
                          </span>
                        )}
                        {!thread.is_read_by_admin && thread.last_sender === 'user' && (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-ice/20 text-ice flex-shrink-0">
                            New Reply
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-frost-muted flex-shrink-0">
                        {formatDate(thread.updated_at || thread.created_at)}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-frost-muted">
                        To: {thread.username}
                      </span>
                      <span className="text-xs text-frost-muted">
                        {thread.message_count} {thread.message_count === 1 ? 'message' : 'messages'}
                      </span>
                    </div>
                    <p className="text-sm text-frost-muted truncate mt-1">{thread.last_message}</p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* New Message Modal */}
      {showNewMessage && (
        <NewMessageModal
          token={token}
          onClose={() => setShowNewMessage(false)}
          onSent={() => {
            setShowNewMessage(false);
            onRefresh();
          }}
        />
      )}

      {/* Thread Detail Modal */}
      {selectedThread && (
        <AdminThreadModal
          thread={selectedThread}
          token={token}
          onClose={() => {
            setSelectedThread(null);
            onRefresh();
          }}
          formatDate={formatDate}
        />
      )}
    </div>
  );
}

function NewMessageModal({
  token,
  onClose,
  onSent,
}: {
  token: string;
  onClose: () => void;
  onSent: () => void;
}) {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [selectedUserId, setSelectedUserId] = useState('');
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [isLoadingUsers, setIsLoadingUsers] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const data = await adminApi.listUsers(token, 200);
      const userList = data.users || [];
      // Sort by username
      userList.sort((a, b) => (a.username || a.email || '').localeCompare(b.username || b.email || ''));
      setUsers(userList);
    } catch (err) {
      console.error('Failed to fetch users:', err);
    } finally {
      setIsLoadingUsers(false);
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!selectedUserId) {
      setError('Please select a user');
      return;
    }
    if (!subject.trim()) {
      setError('Please enter a subject');
      return;
    }
    if (!message.trim()) {
      setError('Please enter a message');
      return;
    }

    setIsSending(true);
    try {
      await adminApi.createThread(token, {
        user_id: selectedUserId,
        subject: subject.trim(),
        message: message.trim(),
      });
      onSent();
    } catch (err: any) {
      setError(err.message || 'Failed to send message');
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-surface rounded-xl border border-surface-border max-w-lg w-full p-6 animate-fadeIn">
        <div className="flex items-start justify-between mb-4">
          <h2 className="text-xl font-bold text-frost">New Message</h2>
          <button onClick={onClose} className="text-frost-muted hover:text-frost text-xl">
            ✕
          </button>
        </div>

        <form onSubmit={handleSend} className="space-y-4">
          {/* User Select */}
          <div>
            <label className="text-xs text-frost-muted uppercase tracking-wide block mb-1">To</label>
            {isLoadingUsers ? (
              <div className="input py-2 text-frost-muted">Loading users...</div>
            ) : (
              <select
                value={selectedUserId}
                onChange={(e) => setSelectedUserId(e.target.value)}
                className="input w-full"
              >
                <option value="">Select a user...</option>
                {users.filter((u) => u.role !== 'admin').map((u) => (
                  <option key={u.user_id} value={u.user_id}>
                    {u.username || u.email}
                    {u.is_test_account ? ' (TEST)' : ''}
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Subject */}
          <div>
            <label className="text-xs text-frost-muted uppercase tracking-wide block mb-1">Subject</label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="Message subject..."
              className="input w-full"
              maxLength={200}
            />
          </div>

          {/* Message */}
          <div>
            <label className="text-xs text-frost-muted uppercase tracking-wide block mb-1">Message</label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message..."
              className="input w-full h-32 resize-none"
            />
          </div>

          {error && (
            <p className="text-sm text-error">{error}</p>
          )}

          <div className="flex justify-end gap-2">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={isSending} className="btn-primary">
              {isSending ? 'Sending...' : 'Send'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function AdminThreadModal({
  thread,
  token,
  onClose,
  formatDate,
}: {
  thread: AdminThread;
  token: string;
  onClose: () => void;
  formatDate: (date: string) => string;
}) {
  const [messages, setMessages] = useState<AdminThreadMessage[]>([]);
  const [reply, setReply] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [threadStatus, setThreadStatus] = useState(thread.status);
  const [isReadByAdmin, setIsReadByAdmin] = useState(thread.is_read_by_admin);

  useEffect(() => {
    fetchMessages();
  }, []);

  const fetchMessages = async () => {
    try {
      const data = await adminApi.getThreadMessages(token, thread.thread_id);
      setMessages(data.messages || []);
      // Thread was marked read by the backend when we fetched messages
      setIsReadByAdmin(true);
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
      await adminApi.replyToThread(token, thread.thread_id, reply.trim());
      setReply('');
      fetchMessages();
    } catch (error) {
      console.error('Failed to send reply:', error);
    } finally {
      setIsSending(false);
    }
  };

  const handleToggleStatus = async () => {
    const newStatus = threadStatus === 'open' ? 'closed' : 'open';
    try {
      await adminApi.updateThread(token, thread.thread_id, { status: newStatus });
      setThreadStatus(newStatus);
    } catch (error) {
      console.error('Failed to update thread status:', error);
    }
  };

  const handleToggleRead = async () => {
    const newRead = !isReadByAdmin;
    try {
      await adminApi.updateThread(token, thread.thread_id, { is_read_by_admin: newRead });
      setIsReadByAdmin(newRead);
    } catch (error) {
      console.error('Failed to toggle read status:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-surface rounded-xl border border-surface-border max-w-2xl w-full max-h-[85vh] flex flex-col animate-fadeIn">
        {/* Header */}
        <div className="p-4 border-b border-surface-border">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="font-bold text-frost text-lg">{thread.subject}</h2>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs text-frost-muted">To: {thread.username}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  threadStatus === 'open'
                    ? 'bg-sky-500/20 text-sky-400'
                    : 'bg-gray-500/20 text-gray-400'
                }`}>
                  {threadStatus === 'open' ? 'Open' : 'Closed'}
                </span>
              </div>
            </div>
            <button onClick={onClose} className="text-frost-muted hover:text-frost text-xl">
              ✕
            </button>
          </div>

          {/* Thread Actions */}
          <div className="flex items-center gap-2 mt-3">
            <button
              onClick={handleToggleRead}
              className="px-3 py-1 rounded text-xs font-medium bg-surface-hover text-frost-muted hover:text-frost transition-colors"
            >
              {isReadByAdmin ? 'Mark Unread' : 'Mark Read'}
            </button>
            <button
              onClick={handleToggleStatus}
              className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                threadStatus === 'open'
                  ? 'bg-gray-500/15 text-gray-400 hover:bg-gray-500/25'
                  : 'bg-sky-500/15 text-sky-400 hover:bg-sky-500/25'
              }`}
            >
              {threadStatus === 'open' ? 'Close Thread' : 'Reopen Thread'}
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {isLoading ? (
            <div className="text-center py-4">
              <p className="text-frost-muted">Loading messages...</p>
            </div>
          ) : messages.length === 0 ? (
            <div className="text-center py-4">
              <p className="text-frost-muted">No messages yet</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.is_from_admin ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] p-3 rounded-lg ${
                    msg.is_from_admin
                      ? 'bg-ice/10 border border-ice/20'
                      : 'bg-emerald-500/10 border border-emerald-500/20'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-xs font-medium ${
                      msg.is_from_admin ? 'text-ice' : 'text-emerald-400'
                    }`}>
                      {msg.is_from_admin ? 'Admin' : thread.username}
                    </span>
                    <span className="text-xs text-frost-muted">
                      {new Date(msg.created_at).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-sm text-frost whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Reply Form (only if thread is open) */}
        {threadStatus === 'open' ? (
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
              <button
                type="submit"
                disabled={!reply.trim() || isSending}
                className="btn-primary"
              >
                {isSending ? '...' : 'Send'}
              </button>
            </div>
          </form>
        ) : (
          <div className="p-4 border-t border-surface-border text-center">
            <p className="text-sm text-frost-muted">This thread is closed. Reopen it to reply.</p>
          </div>
        )}
      </div>
    </div>
  );
}

// =============================================================
// CONVERSATIONS TAB - unchanged from original
// =============================================================

type AIConversation = Conversation;

function ConversationsTab({ token }: { token: string }) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [stats, setStats] = useState<ConversationStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);

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
          <button onClick={onClose} className="text-frost-muted hover:text-frost text-xl">
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
                onClick={() => onCurate((conversation.id || conversation.conversation_id), true, false)}
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
                onClick={() => onCurate((conversation.id || conversation.conversation_id), false, true)}
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
                onClick={() => onCurate((conversation.id || conversation.conversation_id), false, false)}
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
                onClick={() => onSaveNotes((conversation.id || conversation.conversation_id), notes)}
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
  const feedbackId = feedback.feedback_id || feedback.id;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-surface rounded-xl border border-surface-border max-w-lg w-full p-6 animate-fadeIn">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-frost">Feedback Details</h2>
            <p className="text-sm text-frost-muted mt-1">{formatDate(feedback.created_at)}</p>
          </div>
          <button onClick={onClose} className="text-frost-muted hover:text-frost text-xl">
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

          {feedback.page && (
            <div>
              <label className="text-xs text-frost-muted uppercase tracking-wide">Page</label>
              <p className="text-frost">{feedback.page}</p>
            </div>
          )}

          <div>
            <label className="text-xs text-frost-muted uppercase tracking-wide">Description</label>
            <p className="text-frost whitespace-pre-wrap">{feedback.description}</p>
          </div>

          <div>
            <label className="text-xs text-frost-muted uppercase tracking-wide block mb-2">
              Update Status
            </label>
            <div className="flex flex-wrap gap-2">
              {['new', 'pending_fix', 'pending_update', 'completed', 'archive'].map((status) => (
                <button
                  key={status}
                  onClick={() => onUpdateStatus(feedbackId, status)}
                  disabled={feedback.status === status}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    feedback.status === status
                      ? 'bg-ice/20 text-ice cursor-default'
                      : 'bg-surface-hover text-frost-muted hover:text-frost'
                  }`}
                >
                  {status.replace(/_/g, ' ')}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
