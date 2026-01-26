'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';

interface Announcement {
  id: number;
  title: string;
  message: string;
  display_type: string;
  type: string; // info, warning, success, error
  is_active: boolean;
  priority: number;
  created_at: string;
  show_from: string | null;
  show_until: string | null;
  inbox_content: string | null;
}

const TYPE_STYLES: Record<string, { color: string; icon: string; bgClass: string }> = {
  info: { color: 'text-ice', icon: 'ℹ️', bgClass: 'border-ice/30 bg-ice/10' },
  warning: { color: 'text-warning', icon: '⚠️', bgClass: 'border-warning/30 bg-warning/10' },
  success: { color: 'text-success', icon: '✓', bgClass: 'border-success/30 bg-success/10' },
  error: { color: 'text-error', icon: '⚠', bgClass: 'border-error/30 bg-error/10' },
};

export default function AdminAnnouncementsPage() {
  const { token, user } = useAuth();
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [editingAnnouncement, setEditingAnnouncement] = useState<Announcement | null>(null);

  useEffect(() => {
    if (token) {
      fetchAnnouncements();
    }
  }, [token]);

  const fetchAnnouncements = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/admin/announcements', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setAnnouncements(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to fetch announcements:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleActive = async (id: number, isActive: boolean) => {
    try {
      await fetch(`http://localhost:8000/api/admin/announcements/${id}`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_active: !isActive }),
      });
      fetchAnnouncements();
    } catch (error) {
      console.error('Failed to toggle announcement:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this announcement?')) return;

    try {
      await fetch(`http://localhost:8000/api/admin/announcements/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchAnnouncements();
    } catch (error) {
      console.error('Failed to delete announcement:', error);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };

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
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-frost">Announcements</h1>
            <p className="text-frost-muted mt-1">System-wide notifications for users</p>
          </div>
          <button onClick={() => setShowCreate(true)} className="btn-primary">
            + New Announcement
          </button>
        </div>

        {/* Current Banner Status */}
        {announcements.filter((a) => a.is_active && (a.display_type === 'banner' || a.display_type === 'both')).length > 0 && (
          <div className="card mb-6 border-ice/30">
            <h2 className="section-header">Current Banner Preview</h2>
            {announcements
              .filter((a) => a.is_active && (a.display_type === 'banner' || a.display_type === 'both'))
              .sort((a, b) => b.priority - a.priority)
              .slice(0, 1)
              .map((a) => {
                const typeStyle = TYPE_STYLES[a.type] || TYPE_STYLES.info;
                return (
                  <div key={a.id} className={`p-4 rounded-lg border ${typeStyle.bgClass}`}>
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{typeStyle.icon}</span>
                      <span className={`font-medium ${typeStyle.color}`}>{a.title}</span>
                      <span className="text-frost-muted">—</span>
                      <span className="text-frost">{a.message}</span>
                    </div>
                  </div>
                );
              })}
          </div>
        )}

        {/* Active Announcements */}
        <div className="card mb-6">
          <h2 className="section-header">Active Announcements</h2>
          {isLoading ? (
            <div className="space-y-4">
              {[...Array(2)].map((_, i) => (
                <div key={i} className="p-4 rounded-lg bg-surface animate-pulse">
                  <div className="h-5 bg-surface-hover rounded w-48 mb-2" />
                  <div className="h-4 bg-surface-hover rounded w-full" />
                </div>
              ))}
            </div>
          ) : announcements.filter((a) => a.is_active).length === 0 ? (
            <p className="text-frost-muted text-center py-8">No active announcements</p>
          ) : (
            <div className="space-y-4">
              {announcements
                .filter((a) => a.is_active)
                .sort((a, b) => b.priority - a.priority)
                .map((announcement) => (
                  <AnnouncementCard
                    key={announcement.id}
                    announcement={announcement}
                    onEdit={() => setEditingAnnouncement(announcement)}
                    onToggle={() => handleToggleActive(announcement.id, announcement.is_active)}
                    onDelete={() => handleDelete(announcement.id)}
                    formatDate={formatDate}
                  />
                ))}
            </div>
          )}
        </div>

        {/* Inactive Announcements */}
        <div className="card">
          <h2 className="section-header">Inactive Announcements</h2>
          {announcements.filter((a) => !a.is_active).length === 0 ? (
            <p className="text-frost-muted text-center py-8">No inactive announcements</p>
          ) : (
            <div className="space-y-4">
              {announcements
                .filter((a) => !a.is_active)
                .map((announcement) => (
                  <AnnouncementCard
                    key={announcement.id}
                    announcement={announcement}
                    onEdit={() => setEditingAnnouncement(announcement)}
                    onToggle={() => handleToggleActive(announcement.id, announcement.is_active)}
                    onDelete={() => handleDelete(announcement.id)}
                    formatDate={formatDate}
                  />
                ))}
            </div>
          )}
        </div>

        {/* Create/Edit Modal */}
        {(showCreate || editingAnnouncement) && (
          <AnnouncementModal
            token={token || ''}
            announcement={editingAnnouncement}
            onClose={() => {
              setShowCreate(false);
              setEditingAnnouncement(null);
            }}
            onSaved={() => {
              setShowCreate(false);
              setEditingAnnouncement(null);
              fetchAnnouncements();
            }}
          />
        )}
      </div>
    </PageLayout>
  );
}

function AnnouncementCard({
  announcement,
  onEdit,
  onToggle,
  onDelete,
  formatDate,
}: {
  announcement: Announcement;
  onEdit: () => void;
  onToggle: () => void;
  onDelete: () => void;
  formatDate: (date: string) => string;
}) {
  const displayTypeLabels: Record<string, { label: string; color: string }> = {
    banner: { label: 'Banner', color: 'badge-warning' },
    inbox: { label: 'Inbox', color: 'badge-info' },
    both: { label: 'Both', color: 'badge-success' },
  };

  const displayInfo = displayTypeLabels[announcement.display_type] || displayTypeLabels.banner;
  const typeStyle = TYPE_STYLES[announcement.type] || TYPE_STYLES.info;

  // Calculate days remaining
  const getDaysRemaining = () => {
    if (!announcement.show_until) return null;
    const now = new Date();
    const until = new Date(announcement.show_until);
    const diff = Math.ceil((until.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    if (diff < 0) return 'Expired';
    if (diff === 0) return 'Expires today';
    if (diff === 1) return '1 day left';
    return `${diff} days left`;
  };

  const daysRemaining = getDaysRemaining();

  return (
    <div className={`p-4 rounded-lg border ${announcement.is_active ? typeStyle.bgClass : 'bg-surface/50 border-surface-border opacity-60'}`}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg">{typeStyle.icon}</span>
            <h3 className={`font-medium ${typeStyle.color}`}>{announcement.title}</h3>
            <span className={`badge text-xs ${displayInfo.color}`}>{displayInfo.label}</span>
            <span className="badge badge-secondary text-xs">P{announcement.priority}</span>
            {daysRemaining && (
              <span className={`text-xs px-2 py-0.5 rounded ${daysRemaining === 'Expired' ? 'bg-error/20 text-error' : 'bg-surface text-frost-muted'}`}>
                {daysRemaining}
              </span>
            )}
          </div>
          <p className="text-sm text-frost-muted mb-2">{announcement.message}</p>
          {announcement.inbox_content && (
            <p className="text-xs text-frost-muted italic mb-2">
              Inbox: {announcement.inbox_content.substring(0, 100)}...
            </p>
          )}
          <p className="text-xs text-text-muted">
            Created: {formatDate(announcement.created_at)}
            {announcement.show_until && ` · Until: ${formatDate(announcement.show_until)}`}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={onEdit}
            className="px-3 py-1.5 text-sm text-frost-muted hover:text-frost hover:bg-surface-hover rounded transition-colors"
          >
            Edit
          </button>
          <button
            onClick={onToggle}
            className={`px-3 py-1.5 text-sm rounded transition-colors ${
              announcement.is_active
                ? 'text-warning hover:bg-warning/10'
                : 'text-success hover:bg-success/10'
            }`}
          >
            {announcement.is_active ? 'Deactivate' : 'Activate'}
          </button>
          <button
            onClick={onDelete}
            className="px-3 py-1.5 text-sm text-error hover:bg-error/10 rounded transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}

function AnnouncementModal({
  token,
  announcement,
  onClose,
  onSaved,
}: {
  token: string;
  announcement: Announcement | null;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [title, setTitle] = useState(announcement?.title || '');
  const [message, setMessage] = useState(announcement?.message || '');
  const [displayType, setDisplayType] = useState(announcement?.display_type || 'banner');
  const [type, setType] = useState(announcement?.type || 'info');
  const [priority, setPriority] = useState(announcement?.priority || 1);
  const [inboxContent, setInboxContent] = useState(announcement?.inbox_content || '');
  const [expiresInDays, setExpiresInDays] = useState<number | ''>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const url = announcement
        ? `http://localhost:8000/api/admin/announcements/${announcement.id}`
        : 'http://localhost:8000/api/admin/announcements';

      // Calculate show_until date if expiry is set
      let show_until = null;
      if (expiresInDays && typeof expiresInDays === 'number') {
        const date = new Date();
        date.setDate(date.getDate() + expiresInDays);
        show_until = date.toISOString();
      }

      const res = await fetch(url, {
        method: announcement ? 'PUT' : 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title,
          message,
          display_type: displayType,
          type,
          priority,
          inbox_content: inboxContent || null,
          show_until,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Failed to save announcement');
      }

      onSaved();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-surface rounded-xl border border-surface-border max-w-lg w-full p-6 animate-fadeIn max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold text-frost mb-4">
          {announcement ? 'Edit Announcement' : 'New Announcement'}
        </h2>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-error/20 border border-error/30 text-error text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-frost-muted mb-1">Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="input"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-frost-muted mb-1">Banner Message</label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="input min-h-[80px]"
              placeholder="Short message for the banner..."
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-frost-muted mb-1">Type</label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value)}
                className="input"
              >
                <option value="info">ℹ️ Info</option>
                <option value="warning">⚠️ Warning</option>
                <option value="success">✓ Success</option>
                <option value="error">⚠ Error</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-frost-muted mb-1">Display Type</label>
              <select
                value={displayType}
                onChange={(e) => setDisplayType(e.target.value)}
                className="input"
              >
                <option value="banner">Banner Only</option>
                <option value="inbox">Inbox Only</option>
                <option value="both">Both</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-frost-muted mb-1">Priority</label>
              <input
                type="number"
                value={priority}
                onChange={(e) => setPriority(parseInt(e.target.value) || 1)}
                className="input"
                min={1}
                max={10}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-frost-muted mb-1">Expires in (days)</label>
              <input
                type="number"
                value={expiresInDays}
                onChange={(e) => setExpiresInDays(e.target.value ? parseInt(e.target.value) : '')}
                className="input"
                placeholder="Optional"
                min={1}
              />
            </div>
          </div>

          {(displayType === 'inbox' || displayType === 'both') && (
            <div>
              <label className="block text-sm font-medium text-frost-muted mb-1">
                Inbox Content <span className="text-frost-muted font-normal">(full message for inbox)</span>
              </label>
              <textarea
                value={inboxContent}
                onChange={(e) => setInboxContent(e.target.value)}
                className="input min-h-[100px]"
                placeholder="Detailed message that appears in user's inbox..."
              />
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <button type="button" onClick={onClose} className="btn-secondary flex-1">
              Cancel
            </button>
            <button type="submit" disabled={isLoading} className="btn-primary flex-1">
              {isLoading ? 'Saving...' : announcement ? 'Save Changes' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
