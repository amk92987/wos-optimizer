'use client';

import { useEffect, useState, useMemo } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';
import { adminApi } from '@/lib/api';

interface AuditLogEntry {
  id: string;
  user_id: string | null;
  user_email: string | null;
  admin_username: string | null;
  action: string;
  target_name: string | null;
  details: string | null;
  ip_address: string | null;
  created_at: string;
}

type TimeRange = '24h' | '7d' | '30d' | 'all';

// Action type styling map
const actionConfig: Record<string, { icon: string; color: string; bgColor: string }> = {
  login: { icon: '→', color: 'text-emerald-400', bgColor: 'bg-emerald-500/15' },
  logout: { icon: '←', color: 'text-gray-400', bgColor: 'bg-gray-500/15' },
  register: { icon: '+', color: 'text-ice', bgColor: 'bg-ice/15' },
  user_created: { icon: '+', color: 'text-emerald-400', bgColor: 'bg-emerald-500/15' },
  user_deleted: { icon: 'x', color: 'text-red-400', bgColor: 'bg-red-500/15' },
  password_reset: { icon: '*', color: 'text-yellow-400', bgColor: 'bg-yellow-500/15' },
  role_changed: { icon: '#', color: 'text-purple-400', bgColor: 'bg-purple-500/15' },
  impersonation_started: { icon: '~', color: 'text-sky-400', bgColor: 'bg-sky-500/15' },
  user_suspended: { icon: '!', color: 'text-red-400', bgColor: 'bg-red-500/15' },
  user_activated: { icon: '>', color: 'text-emerald-400', bgColor: 'bg-emerald-500/15' },
  update_feedback: { icon: 'f', color: 'text-amber-400', bgColor: 'bg-amber-500/15' },
  delete_feedback: { icon: 'x', color: 'text-red-400', bgColor: 'bg-red-500/15' },
  resolve_error: { icon: '!', color: 'text-emerald-400', bgColor: 'bg-emerald-500/15' },
  update_error: { icon: '!', color: 'text-amber-400', bgColor: 'bg-amber-500/15' },
  delete_error: { icon: 'x', color: 'text-red-400', bgColor: 'bg-red-500/15' },
  'profile.update': { icon: 'p', color: 'text-amber-400', bgColor: 'bg-amber-500/15' },
  'hero.add': { icon: '+', color: 'text-emerald-400', bgColor: 'bg-emerald-500/15' },
  'hero.update': { icon: 'h', color: 'text-amber-400', bgColor: 'bg-amber-500/15' },
  'hero.remove': { icon: 'x', color: 'text-red-400', bgColor: 'bg-red-500/15' },
  'admin.impersonate': { icon: '~', color: 'text-sky-400', bgColor: 'bg-sky-500/15' },
  'admin.user.suspend': { icon: '!', color: 'text-red-400', bgColor: 'bg-red-500/15' },
  'admin.user.activate': { icon: '>', color: 'text-emerald-400', bgColor: 'bg-emerald-500/15' },
};

const defaultActionConfig = { icon: '-', color: 'text-frost-muted', bgColor: 'bg-surface-hover' };

export default function AdminAuditLogPage() {
  const { token, user } = useAuth();
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filterAction, setFilterAction] = useState('');
  const [filterUser, setFilterUser] = useState('');
  const [timeRange, setTimeRange] = useState<TimeRange>('7d');
  const [isExporting, setIsExporting] = useState(false);

  useEffect(() => {
    if (token) {
      fetchLogs();
    }
  }, [token]);

  const fetchLogs = async () => {
    try {
      const data = await adminApi.getAuditLog(token!, undefined, 500);
      setLogs(Array.isArray(data.logs) ? data.logs : Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to fetch audit logs:', error);
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
      second: '2-digit',
    });
  };

  const formatRelativeTime = (dateStr: string) => {
    const now = new Date();
    const then = new Date(dateStr);
    const diffMs = now.getTime() - then.getTime();
    const diffMin = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMin < 1) return 'Just now';
    if (diffMin < 60) return `${diffMin}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return formatDate(dateStr);
  };

  // Time range filter
  const getTimeRangeDate = (range: TimeRange): Date | null => {
    const now = new Date();
    switch (range) {
      case '24h': return new Date(now.getTime() - 24 * 60 * 60 * 1000);
      case '7d': return new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      case '30d': return new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      case 'all': return null;
    }
  };

  // Extract unique values for filters
  const uniqueActions = useMemo(
    () => Array.from(new Set(logs.map((l) => l.action))).sort(),
    [logs]
  );
  const uniqueAdmins = useMemo(
    () => Array.from(new Set(logs.map((l) => l.admin_username || l.user_email || 'System').filter(Boolean))).sort(),
    [logs]
  );

  // Filter logs
  const filteredLogs = useMemo(() => {
    const rangeDate = getTimeRangeDate(timeRange);
    return logs.filter((log) => {
      if (filterAction && log.action !== filterAction) return false;
      const userField = log.admin_username || log.user_email || '';
      if (filterUser && filterUser !== '' && userField !== filterUser) return false;
      if (rangeDate && new Date(log.created_at) < rangeDate) return false;
      return true;
    });
  }, [logs, filterAction, filterUser, timeRange]);

  // Compute stats
  const stats = useMemo(() => {
    const now = new Date();
    const todayCutoff = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    const weekCutoff = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

    return {
      today: logs.filter((l) => new Date(l.created_at) >= todayCutoff).length,
      thisWeek: logs.filter((l) => new Date(l.created_at) >= weekCutoff).length,
      userActions: logs.filter((l) => l.action.includes('user') || l.action === 'login' || l.action === 'register').length,
      total: logs.length,
    };
  }, [logs]);

  // CSV export
  const handleExportCSV = () => {
    setIsExporting(true);
    try {
      const headers = ['Timestamp', 'Action', 'Admin', 'Target', 'Details', 'IP'];
      const rows = filteredLogs.map((log) => [
        new Date(log.created_at).toISOString(),
        log.action,
        log.admin_username || log.user_email || 'System',
        log.target_name || '',
        (log.details || '').replace(/"/g, '""'),
        log.ip_address || '',
      ]);

      const csvContent = [
        headers.join(','),
        ...rows.map((row) => row.map((cell) => `"${cell}"`).join(',')),
      ].join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit_log_${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } finally {
      setIsExporting(false);
    }
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
      <div className="max-w-5xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-frost">Audit Log</h1>
            <p className="text-frost-muted mt-1">Track user actions and system events</p>
          </div>
          <button
            onClick={handleExportCSV}
            disabled={isExporting || filteredLogs.length === 0}
            className="btn-secondary text-sm"
          >
            {isExporting ? 'Exporting...' : 'Export CSV'}
          </button>
        </div>

        {/* Stat Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          <div className="card text-center py-3">
            <div className="text-2xl font-bold text-ice">{stats.today}</div>
            <div className="text-xs text-frost-muted mt-1">Today</div>
          </div>
          <div className="card text-center py-3">
            <div className="text-2xl font-bold text-sky-400">{stats.thisWeek}</div>
            <div className="text-xs text-frost-muted mt-1">This Week</div>
          </div>
          <div className="card text-center py-3">
            <div className="text-2xl font-bold text-amber-400">{stats.userActions}</div>
            <div className="text-xs text-frost-muted mt-1">User Actions</div>
          </div>
          <div className="card text-center py-3">
            <div className="text-2xl font-bold text-frost">{stats.total}</div>
            <div className="text-xs text-frost-muted mt-1">Total Entries</div>
          </div>
        </div>

        {/* Filters */}
        <div className="card mb-6">
          <div className="flex flex-wrap gap-4 items-end">
            {/* Time Range */}
            <div>
              <label className="text-xs text-frost-muted uppercase tracking-wide block mb-1">Time Range</label>
              <div className="flex gap-1 bg-surface/50 rounded-lg p-0.5">
                {([
                  { key: '24h', label: '24h' },
                  { key: '7d', label: '7d' },
                  { key: '30d', label: '30d' },
                  { key: 'all', label: 'All' },
                ] as { key: TimeRange; label: string }[]).map(({ key, label }) => (
                  <button
                    key={key}
                    onClick={() => setTimeRange(key)}
                    className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                      timeRange === key
                        ? 'bg-ice/20 text-ice'
                        : 'text-frost-muted hover:text-frost hover:bg-surface-hover'
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {/* Admin/User filter */}
            <div>
              <label className="text-xs text-frost-muted uppercase tracking-wide block mb-1">Admin</label>
              <select
                value={filterUser}
                onChange={(e) => setFilterUser(e.target.value)}
                className="input text-sm py-1.5"
              >
                <option value="">All Admins</option>
                {uniqueAdmins.map((admin) => (
                  <option key={admin} value={admin}>{admin}</option>
                ))}
              </select>
            </div>

            {/* Action filter */}
            <div>
              <label className="text-xs text-frost-muted uppercase tracking-wide block mb-1">Action</label>
              <select
                value={filterAction}
                onChange={(e) => setFilterAction(e.target.value)}
                className="input text-sm py-1.5"
              >
                <option value="">All Actions</option>
                {uniqueActions.map((action) => (
                  <option key={action} value={action}>{action}</option>
                ))}
              </select>
            </div>

            <button onClick={fetchLogs} className="btn-secondary text-sm py-1.5">
              Refresh
            </button>
          </div>
        </div>

        {/* Logs Table */}
        <div className="card overflow-hidden">
          {isLoading ? (
            <div className="space-y-4 p-4">
              {[...Array(10)].map((_, i) => (
                <div key={i} className="flex gap-4 animate-pulse">
                  <div className="w-8 h-8 bg-surface-hover rounded-full" />
                  <div className="flex-1">
                    <div className="w-32 h-4 bg-surface-hover rounded mb-1" />
                    <div className="w-48 h-3 bg-surface-hover rounded" />
                  </div>
                </div>
              ))}
            </div>
          ) : filteredLogs.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-4xl mb-4">📋</div>
              <p className="text-frost-muted">No log entries found</p>
            </div>
          ) : (
            <div className="divide-y divide-surface-border/50">
              {filteredLogs.map((log) => {
                const config = actionConfig[log.action] || defaultActionConfig;
                const adminName = log.admin_username || log.user_email || 'System';

                return (
                  <div key={log.id} className="flex items-start gap-3 p-3 hover:bg-surface/50 transition-colors">
                    {/* Action Icon */}
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${config.bgColor}`}>
                      <span className={`text-xs font-bold ${config.color}`}>{config.icon}</span>
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className={`text-sm font-medium ${config.color}`}>
                          {log.action.replace(/_/g, ' ').replace(/\./g, ' ')}
                        </span>
                        {log.target_name && (
                          <span className="text-sm text-frost-muted">
                            → {log.target_name}
                          </span>
                        )}
                      </div>
                      {log.details && (
                        <p className="text-xs text-frost-muted mt-0.5 truncate max-w-lg">{log.details}</p>
                      )}
                      <p className="text-xs text-frost-muted/60 mt-0.5">
                        by {adminName}
                        {log.ip_address && <span className="ml-2 font-mono">{log.ip_address}</span>}
                      </p>
                    </div>

                    {/* Time */}
                    <div className="text-right flex-shrink-0">
                      <span className="text-xs text-frost-muted whitespace-nowrap">{formatRelativeTime(log.created_at)}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Summary */}
        <div className="text-center text-sm text-frost-muted mt-4">
          Showing {filteredLogs.length} of {logs.length} entries
        </div>
      </div>
    </PageLayout>
  );
}
