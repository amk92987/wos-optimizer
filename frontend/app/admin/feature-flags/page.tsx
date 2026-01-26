'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';

interface FeatureFlag {
  id: number;
  name: string;
  description: string;
  is_enabled: boolean;
  updated_at: string | null;
}

interface FlagMetadata {
  display_name: string;
  icon: string;
  category: string;
  details: string[];
}

const FLAG_METADATA: Record<string, FlagMetadata> = {
  hero_recommendations: {
    display_name: 'Hero Recommendations',
    icon: '🤖',
    category: 'AI Features',
    details: [
      'AI Advisor page recommendations',
      'Hero priority scoring',
      'Upgrade path suggestions',
      'Resource optimization tips',
    ],
  },
  inventory_ocr: {
    display_name: 'Inventory OCR',
    icon: '📷',
    category: 'Scanning',
    details: [
      'Backpack screenshot scanning',
      'Auto-detection of item quantities',
      'Batch import from screenshots',
      'OCR error correction UI',
    ],
  },
  alliance_features: {
    display_name: 'Alliance Tools',
    icon: '🏰',
    category: 'Social',
    details: [
      'Alliance member tracking',
      'Rally coordination tools',
      'Shared lineup planning',
      'Alliance event tracking',
    ],
  },
  beta_features: {
    display_name: 'Beta Features',
    icon: '🧪',
    category: 'Experimental',
    details: [
      'Unreleased functionality',
      'Features under development',
      'May contain bugs or change',
      'Early access for testing',
    ],
  },
  maintenance_mode: {
    display_name: 'Maintenance Mode',
    icon: '🔧',
    category: 'System',
    details: [
      'Displays maintenance banner',
      'Blocks new data submissions',
      'Allows read-only access',
      'Admin access unaffected',
    ],
  },
  new_user_onboarding: {
    display_name: 'User Onboarding',
    icon: '👋',
    category: 'UX',
    details: [
      'Welcome tour on first login',
      'Profile setup wizard',
      'Feature highlights',
      'Quick start guide prompts',
    ],
  },
  dark_theme_only: {
    display_name: 'Force Dark Theme',
    icon: '🌙',
    category: 'Display',
    details: [
      'Forces Arctic Night theme',
      'Ignores user settings',
      'Useful for screenshots/demos',
      'Affects all users',
    ],
  },
  analytics_tracking: {
    display_name: 'Analytics Tracking',
    icon: '📊',
    category: 'Data',
    details: [
      'Page view tracking',
      'Feature usage metrics',
      'User engagement data',
      'Admin dashboard charts',
    ],
  },
};

export default function AdminFeatureFlagsPage() {
  const { token, user } = useAuth();
  const [flags, setFlags] = useState<FeatureFlag[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showFilter, setShowFilter] = useState<'all' | 'enabled' | 'disabled'>('all');
  const [expandedFlag, setExpandedFlag] = useState<string | null>(null);
  const [editingFlag, setEditingFlag] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);

  // Form state
  const [newName, setNewName] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newEnabled, setNewEnabled] = useState(false);
  const [editName, setEditName] = useState('');
  const [editDesc, setEditDesc] = useState('');

  useEffect(() => {
    if (token) {
      fetchFlags();
    }
  }, [token]);

  const fetchFlags = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/admin/feature-flags', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setFlags(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to fetch flags:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggle = async (name: string, currentValue: boolean) => {
    try {
      await fetch(`http://localhost:8000/api/admin/feature-flags/${name}`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_enabled: !currentValue }),
      });
      fetchFlags();
    } catch (error) {
      console.error('Failed to toggle flag:', error);
    }
  };

  const handleCreate = async () => {
    if (!newName.trim()) return;
    try {
      const res = await fetch('http://localhost:8000/api/admin/feature-flags', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newName.trim(),
          description: newDesc.trim() || null,
          is_enabled: newEnabled,
        }),
      });
      if (res.ok) {
        setNewName('');
        setNewDesc('');
        setNewEnabled(false);
        setShowCreateForm(false);
        fetchFlags();
      }
    } catch (error) {
      console.error('Failed to create flag:', error);
    }
  };

  const handleUpdate = async (name: string) => {
    try {
      await fetch(`http://localhost:8000/api/admin/feature-flags/${name}`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: editName.trim() || undefined,
          description: editDesc,
        }),
      });
      setEditingFlag(null);
      fetchFlags();
    } catch (error) {
      console.error('Failed to update flag:', error);
    }
  };

  const handleDelete = async (name: string) => {
    try {
      await fetch(`http://localhost:8000/api/admin/feature-flags/${name}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      setDeleteConfirm(null);
      fetchFlags();
    } catch (error) {
      console.error('Failed to delete flag:', error);
    }
  };

  const handleBulkAction = async (action: string) => {
    try {
      await fetch('http://localhost:8000/api/admin/feature-flags/bulk', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action }),
      });
      fetchFlags();
    } catch (error) {
      console.error('Failed to perform bulk action:', error);
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'Never';
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  const getMetadata = (name: string): FlagMetadata => {
    return (
      FLAG_METADATA[name] || {
        display_name: name.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
        icon: '🚩',
        category: 'Custom',
        details: [],
      }
    );
  };

  // Filter flags
  const filteredFlags = flags.filter((flag) => {
    const meta = getMetadata(flag.name);
    const searchLower = search.toLowerCase();
    const matchesSearch =
      !search ||
      flag.name.toLowerCase().includes(searchLower) ||
      meta.display_name.toLowerCase().includes(searchLower) ||
      (flag.description || '').toLowerCase().includes(searchLower);

    const matchesFilter =
      showFilter === 'all' ||
      (showFilter === 'enabled' && flag.is_enabled) ||
      (showFilter === 'disabled' && !flag.is_enabled);

    return matchesSearch && matchesFilter;
  });

  // Stats
  const enabledCount = flags.filter((f) => f.is_enabled).length;
  const categories = new Set(flags.map((f) => getMetadata(f.name).category));

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
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Feature Flags</h1>
          <p className="text-frost-muted mt-1">Toggle features on or off across the application</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="card text-center">
            <div className="text-2xl font-bold text-frost">{flags.length}</div>
            <div className="text-xs text-frost-muted">Total</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-success">{enabledCount}</div>
            <div className="text-xs text-frost-muted">Enabled</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-frost-muted">{flags.length - enabledCount}</div>
            <div className="text-xs text-frost-muted">Disabled</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-ice">{categories.size}</div>
            <div className="text-xs text-frost-muted">Categories</div>
          </div>
        </div>

        {/* Search and Filter */}
        <div className="card mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <input
              type="text"
              placeholder="Search flags..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input flex-1"
            />
            <select
              value={showFilter}
              onChange={(e) => setShowFilter(e.target.value as typeof showFilter)}
              className="input w-full sm:w-40"
            >
              <option value="all">All</option>
              <option value="enabled">Enabled</option>
              <option value="disabled">Disabled</option>
            </select>
            <button onClick={() => setShowCreateForm(true)} className="btn-primary whitespace-nowrap">
              + New Flag
            </button>
          </div>
        </div>

        {/* Create Form Modal */}
        {showCreateForm && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-surface rounded-xl border border-surface-border max-w-md w-full p-6 animate-fadeIn">
              <h2 className="text-xl font-bold text-frost mb-4">Create New Flag</h2>
              <div className="space-y-4">
                <div>
                  <label className="text-xs text-frost-muted uppercase tracking-wide block mb-1">
                    Internal Name
                  </label>
                  <input
                    type="text"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    placeholder="feature_name"
                    className="input w-full"
                  />
                  <p className="text-xs text-frost-muted mt-1">Lowercase with underscores</p>
                </div>
                <div>
                  <label className="text-xs text-frost-muted uppercase tracking-wide block mb-1">
                    Description
                  </label>
                  <input
                    type="text"
                    value={newDesc}
                    onChange={(e) => setNewDesc(e.target.value)}
                    placeholder="What does this flag control?"
                    className="input w-full"
                  />
                </div>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={newEnabled}
                    onChange={(e) => setNewEnabled(e.target.checked)}
                    className="w-4 h-4 rounded"
                  />
                  <span className="text-frost">Enable immediately</span>
                </label>
              </div>
              <div className="flex gap-2 mt-6">
                <button onClick={handleCreate} disabled={!newName.trim()} className="btn-primary flex-1">
                  Create Flag
                </button>
                <button onClick={() => setShowCreateForm(false)} className="btn-secondary flex-1">
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Flags List */}
        <div className="card">
          <p className="text-xs text-frost-muted mb-4">Showing {filteredFlags.length} flags</p>
          {isLoading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="flex items-center justify-between p-4 rounded-lg bg-surface animate-pulse">
                  <div className="flex-1">
                    <div className="h-4 bg-surface-hover rounded w-48 mb-2" />
                    <div className="h-3 bg-surface-hover rounded w-64" />
                  </div>
                  <div className="w-12 h-6 bg-surface-hover rounded-full" />
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-2">
              {filteredFlags.map((flag) => {
                const meta = getMetadata(flag.name);
                const isExpanded = expandedFlag === flag.name;
                const isEditing = editingFlag === flag.name;
                const isDeleting = deleteConfirm === flag.name;

                return (
                  <div key={flag.name}>
                    <div
                      className={`p-4 rounded-lg transition-colors ${
                        flag.is_enabled ? 'bg-success/5 border border-success/20' : 'bg-surface'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-lg">{meta.icon}</span>
                            <span className="font-medium text-frost">{meta.display_name}</span>
                            <span className="text-xs px-2 py-0.5 rounded bg-surface-hover text-frost-muted">
                              {meta.category}
                            </span>
                            {flag.name === 'maintenance_mode' && flag.is_enabled && (
                              <span className="badge badge-error text-xs">ACTIVE</span>
                            )}
                          </div>
                          <p className="text-sm text-frost-muted mt-1">{flag.description || meta.details[0]}</p>
                          <p className="text-xs text-frost-muted mt-2">
                            Last updated: {formatDate(flag.updated_at)}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          {meta.details.length > 0 && (
                            <button
                              onClick={() => setExpandedFlag(isExpanded ? null : flag.name)}
                              className="p-2 rounded hover:bg-surface-hover text-frost-muted hover:text-frost"
                              title="Details"
                            >
                              {isExpanded ? '▼' : '▶'}
                            </button>
                          )}
                          <button
                            onClick={() => {
                              setEditName(flag.name);
                              setEditDesc(flag.description || '');
                              setEditingFlag(flag.name);
                            }}
                            className="p-2 rounded hover:bg-surface-hover text-frost-muted hover:text-frost"
                            title="Edit"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => setDeleteConfirm(flag.name)}
                            className="p-2 rounded hover:bg-error/20 text-frost-muted hover:text-error"
                            title="Delete"
                          >
                            🗑️
                          </button>
                          <button
                            onClick={() => handleToggle(flag.name, flag.is_enabled)}
                            className={`relative w-14 h-7 rounded-full transition-colors ${
                              flag.is_enabled ? 'bg-success' : 'bg-surface-hover'
                            }`}
                            title={flag.is_enabled ? 'Click to disable' : 'Click to enable'}
                          >
                            <span
                              className={`absolute top-1 w-5 h-5 rounded-full bg-white shadow transition-transform ${
                                flag.is_enabled ? 'left-8' : 'left-1'
                              }`}
                            />
                          </button>
                        </div>
                      </div>

                      {/* Expanded details */}
                      {isExpanded && meta.details.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-surface-border">
                          <p className="text-xs text-frost-muted uppercase tracking-wide mb-2">What's included</p>
                          <ul className="space-y-1">
                            {meta.details.map((detail, i) => (
                              <li key={i} className="text-sm text-frost-muted flex items-start gap-2">
                                <span className="text-ice">•</span>
                                {detail}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>

                    {/* Edit form */}
                    {isEditing && (
                      <div className="mt-2 p-4 rounded-lg bg-surface-hover">
                        <h4 className="font-medium text-frost mb-3">Edit: {meta.display_name}</h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          <div>
                            <label className="text-xs text-frost-muted block mb-1">Internal Name</label>
                            <input
                              type="text"
                              value={editName}
                              onChange={(e) => setEditName(e.target.value)}
                              className="input w-full"
                            />
                          </div>
                          <div>
                            <label className="text-xs text-frost-muted block mb-1">Description</label>
                            <input
                              type="text"
                              value={editDesc}
                              onChange={(e) => setEditDesc(e.target.value)}
                              className="input w-full"
                            />
                          </div>
                        </div>
                        <div className="flex gap-2 mt-4">
                          <button onClick={() => handleUpdate(flag.name)} className="btn-primary text-sm">
                            Save
                          </button>
                          <button onClick={() => setEditingFlag(null)} className="btn-secondary text-sm">
                            Cancel
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Delete confirmation */}
                    {isDeleting && (
                      <div className="mt-2 p-4 rounded-lg bg-error/10 border border-error/30">
                        <p className="text-frost mb-3">
                          Delete <strong>{meta.display_name}</strong>? This cannot be undone.
                        </p>
                        <div className="flex gap-2">
                          <button onClick={() => handleDelete(flag.name)} className="btn-error text-sm">
                            Delete
                          </button>
                          <button onClick={() => setDeleteConfirm(null)} className="btn-secondary text-sm">
                            Cancel
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="card mt-6">
          <h3 className="font-medium text-frost mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <button onClick={() => handleBulkAction('enable_all')} className="btn-success">
              Enable All
            </button>
            <button onClick={() => handleBulkAction('disable_all')} className="btn-secondary">
              Disable All
            </button>
            <button onClick={() => handleBulkAction('reset_defaults')} className="btn-secondary">
              Reset Defaults
            </button>
          </div>
        </div>

        {/* Warning */}
        <div className="card mt-6 border-warning/30 bg-warning/5">
          <div className="flex gap-3">
            <span className="text-2xl">⚠️</span>
            <div>
              <h3 className="font-medium text-frost">Caution</h3>
              <p className="text-sm text-frost-muted mt-1">
                Changing feature flags affects all users immediately. Use maintenance_mode to temporarily disable
                access when making significant changes.
              </p>
            </div>
          </div>
        </div>
      </div>
    </PageLayout>
  );
}
