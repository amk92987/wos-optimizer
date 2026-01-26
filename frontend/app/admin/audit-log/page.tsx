'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';

interface AuditLogEntry {
  id: number;
  user_id: number | null;
  user_email: string | null;
  action: string;
  details: string | null;
  ip_address: string | null;
  created_at: string;
}

export default function AdminAuditLogPage() {
  const { token, user } = useAuth();
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filterAction, setFilterAction] = useState('');
  const [filterUser, setFilterUser] = useState('');

  useEffect(() => {
    if (token) {
      fetchLogs();
    }
  }, [token]);

  const fetchLogs = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/admin/audit-log?limit=100', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setLogs(Array.isArray(data) ? data : []);
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

  // Extract unique actions for filter
  const uniqueActions = Array.from(new Set(logs.map((l) => l.action))).sort();

  // Filter logs
  const filteredLogs = logs.filter((log) => {
    if (filterAction && log.action !== filterAction) return false;
    if (filterUser && !log.user_email?.toLowerCase().includes(filterUser.toLowerCase())) return false;
    return true;
  });

  const actionColors: Record<string, string> = {
    login: 'text-success',
    logout: 'text-frost-muted',
    register: 'text-ice',
    'profile.update': 'text-warning',
    'hero.add': 'text-success',
    'hero.update': 'text-warning',
    'hero.remove': 'text-error',
    'admin.impersonate': 'text-fire',
    'admin.user.suspend': 'text-error',
    'admin.user.activate': 'text-success',
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
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Audit Log</h1>
          <p className="text-frost-muted mt-1">Track user actions and system events</p>
        </div>

        {/* Filters */}
        <div className="card mb-6">
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[200px]">
              <input
                type="text"
                placeholder="Filter by email..."
                value={filterUser}
                onChange={(e) => setFilterUser(e.target.value)}
                className="input"
              />
            </div>
            <select
              value={filterAction}
              onChange={(e) => setFilterAction(e.target.value)}
              className="input w-auto"
            >
              <option value="">All Actions</option>
              {uniqueActions.map((action) => (
                <option key={action} value={action}>
                  {action}
                </option>
              ))}
            </select>
            <button onClick={fetchLogs} className="btn-secondary">
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
                  <div className="w-32 h-4 bg-surface-hover rounded" />
                  <div className="w-24 h-4 bg-surface-hover rounded" />
                  <div className="flex-1 h-4 bg-surface-hover rounded" />
                </div>
              ))}
            </div>
          ) : filteredLogs.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-4xl mb-4">📋</div>
              <p className="text-frost-muted">No log entries found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-surface-border">
                    <th className="text-left p-3 text-frost-muted font-medium">Time</th>
                    <th className="text-left p-3 text-frost-muted font-medium">Action</th>
                    <th className="text-left p-3 text-frost-muted font-medium">User</th>
                    <th className="text-left p-3 text-frost-muted font-medium">Details</th>
                    <th className="text-left p-3 text-frost-muted font-medium">IP</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredLogs.map((log) => (
                    <tr key={log.id} className="border-b border-surface-border/50 hover:bg-surface/50">
                      <td className="p-3 text-frost-muted whitespace-nowrap">
                        {formatDate(log.created_at)}
                      </td>
                      <td className="p-3">
                        <span className={`font-medium ${actionColors[log.action] || 'text-frost'}`}>
                          {log.action}
                        </span>
                      </td>
                      <td className="p-3 text-frost">{log.user_email || 'System'}</td>
                      <td className="p-3 text-frost-muted max-w-md truncate">{log.details || '—'}</td>
                      <td className="p-3 text-frost-muted font-mono text-xs">{log.ip_address || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
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
