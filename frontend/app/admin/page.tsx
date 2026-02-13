'use client';

import { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';
import { adminApi, AdminUser } from '@/lib/api';

// ============================================
// Types
// ============================================

interface AdminStats {
  total_users: number;
  active_users: number;
  test_accounts: number;
  total_profiles: number;
  total_heroes_tracked: number;
  ai_requests_today: number;
  pending_feedback: number;
  active_announcements: number;
  // Extended fields from /admin/stats
  new_today?: number;
  new_this_week?: number;
  new_this_month?: number;
  active_30d?: number;
  inactive_30d?: number;
  retention_rate?: number;
  admin_count?: number;
  unique_states?: number;
  total_inventory_items?: number;
  db_size_mb?: number;
}

interface UsageDataPoint {
  date: string;
  total_users: number;
  active_users: number;
  new_users: number;
}

interface ErrorSummary {
  new: number;
  last_24h: number;
  fixed: number;
}

type TimeRange = '7d' | '30d' | '90d';

// ============================================
// Helper: time ago string
// ============================================

function timeAgo(dateStr: string | null): string {
  if (!dateStr) return 'Never';
  const now = new Date();
  const then = new Date(dateStr);
  const diffMs = now.getTime() - then.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  if (diffSec < 60) return 'Just now';
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHour = Math.floor(diffMin / 60);
  if (diffHour < 24) return `${diffHour}h ago`;
  const diffDay = Math.floor(diffHour / 24);
  if (diffDay < 30) return `${diffDay}d ago`;
  return `${Math.floor(diffDay / 30)}mo ago`;
}

// ============================================
// SVG Bar Chart Component
// ============================================

function BarChart({
  data,
  valueKey,
  color,
  label,
  height = 180,
}: {
  data: UsageDataPoint[];
  valueKey: 'total_users' | 'active_users' | 'new_users';
  color: string;
  label: string;
  height?: number;
}) {
  if (!data || data.length === 0) {
    return (
      <div
        className="flex items-center justify-center rounded-lg border border-dashed border-surface-border"
        style={{ height }}
      >
        <p className="text-text-muted text-sm">No data yet. Check back after a few days.</p>
      </div>
    );
  }

  const values = data.map((d) => d[valueKey]);
  const maxVal = Math.max(...values, 1);
  const chartPadding = 30; // bottom space for labels
  const barAreaHeight = height - chartPadding;
  const barWidth = Math.max(12, Math.min(40, (600 - data.length * 4) / data.length));
  const gap = 4;
  const totalWidth = data.length * (barWidth + gap);

  return (
    <div>
      <p className="text-sm font-medium text-frost mb-2">{label}</p>
      <div className="overflow-x-auto">
        <svg
          width={Math.max(totalWidth + 20, 200)}
          height={height}
          className="block"
          role="img"
          aria-label={label}
        >
          {/* Grid lines */}
          {[0.25, 0.5, 0.75, 1].map((frac) => {
            const y = barAreaHeight - barAreaHeight * frac;
            return (
              <g key={frac}>
                <line
                  x1={0}
                  y1={y}
                  x2={totalWidth + 10}
                  y2={y}
                  stroke="rgba(74, 144, 217, 0.1)"
                  strokeDasharray="4 4"
                />
                <text
                  x={totalWidth + 14}
                  y={y + 4}
                  fill="rgba(143, 157, 180, 0.6)"
                  fontSize="9"
                >
                  {Math.round(maxVal * frac)}
                </text>
              </g>
            );
          })}

          {/* Bars */}
          {data.map((d, i) => {
            const val = d[valueKey];
            const barH = (val / maxVal) * barAreaHeight;
            const x = i * (barWidth + gap) + 5;
            const y = barAreaHeight - barH;
            const dateLabel = d.date.length > 5 ? d.date.slice(5) : d.date; // MM-DD or DD

            return (
              <g key={i}>
                <rect
                  x={x}
                  y={y}
                  width={barWidth}
                  height={Math.max(barH, 1)}
                  rx={3}
                  fill={color}
                  opacity={0.85}
                  className="transition-all duration-200 hover:opacity-100"
                >
                  <title>{`${d.date}: ${val}`}</title>
                </rect>
                {/* Value on top of bar */}
                {barH > 15 && (
                  <text
                    x={x + barWidth / 2}
                    y={y - 4}
                    textAnchor="middle"
                    fill={color}
                    fontSize="10"
                    fontWeight="600"
                  >
                    {val}
                  </text>
                )}
                {/* Date label */}
                {(data.length <= 14 || i % Math.ceil(data.length / 10) === 0) && (
                  <text
                    x={x + barWidth / 2}
                    y={barAreaHeight + 14}
                    textAnchor="middle"
                    fill="rgba(143, 157, 180, 0.7)"
                    fontSize="9"
                  >
                    {dateLabel}
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}

// ============================================
// Main Dashboard
// ============================================

export default function AdminDashboard() {
  const { token, user } = useAuth();
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [timeRange, setTimeRange] = useState<TimeRange>('30d');
  const [usageData, setUsageData] = useState<UsageDataPoint[]>([]);
  const [usageLoading, setUsageLoading] = useState(true);
  const [recentUsers, setRecentUsers] = useState<AdminUser[]>([]);
  const [usersLoading, setUsersLoading] = useState(true);
  const [errors, setErrors] = useState<ErrorSummary>({ new: 0, last_24h: 0, fixed: 0 });
  const [errorsLoading, setErrorsLoading] = useState(true);
  const [impersonating, setImpersonating] = useState<string | null>(null);
  const [seedingAccounts, setSeedingAccounts] = useState(false);
  const [seedResult, setSeedResult] = useState<{ message: string; password?: string; error?: boolean } | null>(null);

  // Fetch stats
  useEffect(() => {
    if (!token) return;
    adminApi.getStats(token)
      .then(setStats)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, [token]);

  // Fetch usage data (charts)
  const fetchUsage = useCallback(async () => {
    if (!token) return;
    setUsageLoading(true);
    try {
      const data = await adminApi.getUsageStats(token, timeRange);
      setUsageData(data.data_points || data.datapoints || data.metrics || []);
    } catch (err) {
      console.error('Failed to fetch usage stats:', err);
      setUsageData([]);
    } finally {
      setUsageLoading(false);
    }
  }, [token, timeRange]);

  useEffect(() => {
    fetchUsage();
  }, [fetchUsage]);

  // Fetch recent users
  useEffect(() => {
    if (!token) return;
    adminApi.listUsers(token, 8)
      .then((res) => {
        // Sort by last_login desc, take 8
        const sorted = (res.users || [])
          .filter((u: AdminUser) => u.role !== 'admin' && !u.is_test_account)
          .sort((a: AdminUser, b: AdminUser) => {
            const aDate = a.last_login ? new Date(a.last_login).getTime() : 0;
            const bDate = b.last_login ? new Date(b.last_login).getTime() : 0;
            return bDate - aDate;
          })
          .slice(0, 8);
        setRecentUsers(sorted);
      })
      .catch(console.error)
      .finally(() => setUsersLoading(false));
  }, [token]);

  // Fetch errors
  useEffect(() => {
    if (!token) return;
    adminApi.getErrors(token)
      .then((res) => {
        const errorList = res.errors || [];
        const now = new Date();
        const dayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        setErrors({
          new: errorList.filter((e: any) => e.status === 'new').length,
          last_24h: errorList.filter((e: any) => new Date(e.created_at) > dayAgo).length,
          fixed: errorList.filter((e: any) => e.status === 'resolved' || e.status === 'fixed').length,
        });
      })
      .catch(console.error)
      .finally(() => setErrorsLoading(false));
  }, [token]);

  // Handle impersonation
  const handleImpersonate = async (userId: string, username: string) => {
    if (!token) return;
    setImpersonating(userId);
    try {
      const result = await adminApi.impersonateUser(token, userId);
      if (result.impersonating) {
        // Store impersonation state and redirect
        window.location.href = '/';
      }
    } catch (err) {
      console.error('Impersonation failed:', err);
      alert('Failed to impersonate user. ' + (err instanceof Error ? err.message : ''));
    } finally {
      setImpersonating(null);
    }
  };

  // Redirect non-admins
  if (user && user.role !== 'admin') {
    return (
      <PageLayout>
        <div className="max-w-2xl mx-auto text-center py-16">
          <div className="text-6xl mb-6">&#x1F512;</div>
          <h1 className="text-2xl font-bold text-frost mb-4">Access Denied</h1>
          <p className="text-frost-muted mb-6">You do not have permission to view this page.</p>
          <Link href="/" className="btn-primary">
            Return Home
          </Link>
        </div>
      </PageLayout>
    );
  }

  // Derived stats
  const newToday = stats?.new_today ?? 0;
  const newThisWeek = stats?.new_this_week ?? 0;
  const newThisMonth = stats?.new_this_month ?? 0;
  const active30d = stats?.active_30d ?? stats?.active_users ?? 0;
  const inactive30d = stats?.inactive_30d ?? 0;
  const retentionRate = stats?.retention_rate ?? (
    stats?.total_users && stats.total_users > 0
      ? Math.round(((stats.total_users - inactive30d) / stats.total_users) * 100)
      : 0
  );

  const statCards = [
    { label: 'Total Users', value: stats?.total_users ?? '-', icon: '\uD83D\uDC65', color: 'text-ice', href: '/admin/users' },
    { label: 'Active Users', value: stats?.active_users ?? '-', icon: '\u2705', color: 'text-success' },
    { label: 'Test Accounts', value: stats?.test_accounts ?? '-', icon: '\uD83E\uDDEA', color: 'text-warning', href: '/admin/users?filter=test' },
    { label: 'Total Profiles', value: stats?.total_profiles ?? '-', icon: '\uD83D\uDCCB', color: 'text-frost' },
    { label: 'Heroes Tracked', value: stats?.total_heroes_tracked ?? '-', icon: '\uD83E\uDDB8', color: 'text-fire', href: '/admin/users' },
    { label: 'AI Requests Today', value: stats?.ai_requests_today ?? '-', icon: '\uD83E\uDD16', color: 'text-purple-400', href: '/admin/ai' },
    { label: 'Pending Feedback', value: stats?.pending_feedback ?? '-', icon: '\uD83D\uDCAC', color: 'text-yellow-400', href: '/admin/inbox' },
    { label: 'Announcements', value: stats?.active_announcements ?? '-', icon: '\uD83D\uDCE2', color: 'text-ice', href: '/admin/announcements' },
  ];


  return (
    <PageLayout>
      <div className="max-w-6xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Admin Dashboard</h1>
          <p className="text-frost-muted mt-2">
            System overview and quick actions &bull; {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
          </p>
        </div>

        {/* ============================================ */}
        {/* Stats Grid */}
        {/* ============================================ */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {statCards.map((stat) => {
            const content = (
              <div className={`card text-center hover:border-ice/30 transition-colors ${stat.href ? 'cursor-pointer' : ''}`}>
                <div className="text-2xl mb-2">{stat.icon}</div>
                <p className={`text-2xl font-bold ${stat.color}`}>
                  {isLoading ? (
                    <span className="inline-block w-8 h-8 bg-surface-hover rounded animate-pulse" />
                  ) : (
                    stat.value
                  )}
                </p>
                <p className="text-sm text-frost-muted mt-1">{stat.label}</p>
              </div>
            );

            return stat.href ? (
              <Link key={stat.label} href={stat.href}>
                {content}
              </Link>
            ) : (
              <div key={stat.label}>{content}</div>
            );
          })}
        </div>

        {/* ============================================ */}
        {/* Charts Section */}
        {/* ============================================ */}
        <div className="card mb-8">
          <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
            <h2 className="section-header mb-0">Trends</h2>
            <div className="flex gap-1 bg-background-light rounded-lg p-1">
              {(['7d', '30d', '90d'] as TimeRange[]).map((range) => {
                const labels: Record<TimeRange, string> = { '7d': '1 Week', '30d': '1 Month', '90d': '3 Months' };
                return (
                  <button
                    key={range}
                    onClick={() => setTimeRange(range)}
                    className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                      timeRange === range
                        ? 'bg-surface text-frost font-medium'
                        : 'text-text-secondary hover:text-frost'
                    }`}
                  >
                    {labels[range]}
                  </button>
                );
              })}
            </div>
          </div>

          {usageLoading ? (
            <div className="grid md:grid-cols-2 gap-6">
              <div className="h-[200px] skeleton rounded-lg" />
              <div className="h-[200px] skeleton rounded-lg" />
            </div>
          ) : (
            <div className="grid md:grid-cols-2 gap-6">
              <BarChart
                data={usageData}
                valueKey="total_users"
                color="#4A90D9"
                label="User Growth"
              />
              <BarChart
                data={usageData}
                valueKey="active_users"
                color="#22C55E"
                label="Daily Active Users"
              />
            </div>
          )}
        </div>

        {/* ============================================ */}
        {/* New Registrations + User Health */}
        {/* ============================================ */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* New Registrations */}
          <div className="card">
            <h2 className="section-header">New Registrations</h2>
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: 'Today', value: newToday, color: 'text-success', bg: 'bg-success/10 border-success/20' },
                { label: 'This Week', value: newThisWeek, color: 'text-ice', bg: 'bg-ice/10 border-ice/20' },
                { label: 'This Month', value: newThisMonth, color: 'text-purple-400', bg: 'bg-purple-400/10 border-purple-400/20' },
              ].map((item) => (
                <div
                  key={item.label}
                  className={`rounded-lg border p-4 text-center ${item.bg}`}
                >
                  <p className={`text-2xl font-bold ${item.color}`}>
                    {isLoading ? <span className="inline-block w-6 h-6 skeleton" /> : item.value}
                  </p>
                  <p className="text-xs text-frost-muted mt-1">{item.label}</p>
                </div>
              ))}
            </div>
          </div>

          {/* User Health */}
          <div className="card">
            <h2 className="section-header">User Health</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 rounded-lg bg-surface/30">
                <span className="text-frost-muted">Active (30d)</span>
                <span className="font-bold text-success">
                  {isLoading ? <span className="inline-block w-6 h-4 skeleton" /> : active30d}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-surface/30">
                <span className="text-frost-muted">Inactive (30d+)</span>
                <span className="font-bold text-error">
                  {isLoading ? <span className="inline-block w-6 h-4 skeleton" /> : inactive30d}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-surface/30">
                <span className="text-frost-muted">Retention Rate</span>
                <span className={`font-bold ${
                  retentionRate >= 70 ? 'text-success' : retentionRate >= 40 ? 'text-warning' : 'text-error'
                }`}>
                  {isLoading ? <span className="inline-block w-8 h-4 skeleton" /> : `${retentionRate}%`}
                </span>
              </div>
              {/* Retention bar */}
              {!isLoading && (
                <div className="xp-bar h-3 mt-2">
                  <div
                    className="xp-bar-fill"
                    style={{
                      width: `${Math.min(retentionRate, 100)}%`,
                      background: retentionRate >= 70
                        ? 'linear-gradient(90deg, #22C55E, #4ADE80)'
                        : retentionRate >= 40
                          ? 'linear-gradient(90deg, #F59E0B, #FBBF24)'
                          : 'linear-gradient(90deg, #EF4444, #F87171)',
                    }}
                  />
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ============================================ */}
        {/* Recent Users + System Health + Errors */}
        {/* ============================================ */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Recent Users */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="section-header mb-0">Recent Users</h2>
              <Link href="/admin/users" className="text-sm text-ice hover:text-ice-light transition-colors">
                View All
              </Link>
            </div>
            <div className="space-y-2">
              {usersLoading ? (
                [...Array(4)].map((_, i) => (
                  <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-surface animate-pulse">
                    <div className="w-8 h-8 rounded-full bg-surface-hover" />
                    <div className="flex-1">
                      <div className="h-4 bg-surface-hover rounded w-32 mb-1" />
                      <div className="h-3 bg-surface-hover rounded w-24" />
                    </div>
                  </div>
                ))
              ) : recentUsers.length === 0 ? (
                <p className="text-frost-muted text-sm text-center py-4">
                  No recent user activity.
                </p>
              ) : (
                recentUsers.map((u) => (
                  <div
                    key={u.user_id}
                    className="flex items-center gap-3 p-3 rounded-lg bg-surface/30 hover:bg-surface/50 transition-colors"
                  >
                    {/* Avatar */}
                    <div className="w-8 h-8 rounded-full bg-ice/20 border border-ice/30 flex items-center justify-center text-xs font-bold text-ice flex-shrink-0">
                      {(u.username || u.email || '?')[0].toUpperCase()}
                    </div>
                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-frost truncate">
                        {u.username || u.email}
                        {u.is_test_account && (
                          <span className="badge-warning text-[10px] ml-2">TEST</span>
                        )}
                      </p>
                      <p className="text-xs text-frost-muted truncate">{u.email}</p>
                    </div>
                    {/* Time ago */}
                    <span className="text-xs text-text-muted whitespace-nowrap">
                      {timeAgo(u.last_login)}
                    </span>
                    {/* Impersonate */}
                    <button
                      onClick={() => handleImpersonate(u.user_id, u.username)}
                      disabled={impersonating === u.user_id}
                      className="btn-ghost text-xs px-2 py-1 rounded-md hover:bg-ice/10 hover:text-ice flex-shrink-0"
                      title={`Impersonate ${u.username}`}
                    >
                      {impersonating === u.user_id ? (
                        <span className="inline-block w-3 h-3 border-2 border-ice border-t-transparent rounded-full animate-spin" />
                      ) : (
                        'Impersonate'
                      )}
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* System Health + Error Tracking */}
          <div className="space-y-6">
            {/* System Status */}
            <div className="card">
              <h2 className="section-header">System Status</h2>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-2">
                  <span className="text-frost-muted">Database</span>
                  <span className={stats ? 'badge-success' : 'badge-warning'}>
                    {stats ? 'Online' : 'Checking...'}
                  </span>
                </div>
                <div className="flex items-center justify-between p-2">
                  <span className="text-frost-muted">AI Service</span>
                  <span className={
                    stats?.ai_requests_today !== undefined ? 'badge-success' : 'badge-warning'
                  }>
                    {stats?.ai_requests_today !== undefined ? 'Active' : 'Checking...'}
                  </span>
                </div>
                <div className="flex items-center justify-between p-2">
                  <span className="text-frost-muted">Email Service</span>
                  <span className="text-xs text-frost-muted">Not Configured</span>
                </div>
                {stats?.db_size_mb !== undefined && (
                  <div className="flex items-center justify-between p-2">
                    <span className="text-frost-muted">Database Size</span>
                    <span className="text-sm font-medium text-frost">{stats.db_size_mb.toFixed(2)} MB</span>
                  </div>
                )}
                {stats?.admin_count !== undefined && (
                  <div className="flex items-center justify-between p-2">
                    <span className="text-frost-muted">Admin Accounts</span>
                    <span className="text-sm font-medium text-frost">{stats.admin_count}</span>
                  </div>
                )}
                {stats?.unique_states !== undefined && (
                  <div className="flex items-center justify-between p-2">
                    <span className="text-frost-muted">States Represented</span>
                    <span className="text-sm font-medium text-ice">{stats.unique_states}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Error Tracking */}
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h2 className="section-header mb-0">Error Tracking</h2>
                <Link
                  href="/admin/inbox"
                  className="text-sm text-ice hover:text-ice-light transition-colors"
                >
                  View Errors
                </Link>
              </div>
              {errorsLoading ? (
                <div className="space-y-3">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="h-10 skeleton rounded-lg" />
                  ))}
                </div>
              ) : (
                <div className="space-y-3">
                  <div className={`flex items-center justify-between p-3 rounded-lg border ${
                    errors.new > 0
                      ? 'bg-error/10 border-error/20'
                      : 'bg-success/10 border-success/20'
                  }`}>
                    <span className="text-frost-muted">New Errors</span>
                    <span className={`font-bold ${errors.new > 0 ? 'text-error' : 'text-success'}`}>
                      {errors.new}
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-lg bg-surface/30">
                    <span className="text-frost-muted">Last 24 Hours</span>
                    <span className="font-bold text-frost">{errors.last_24h}</span>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-lg bg-surface/30">
                    <span className="text-frost-muted">Fixed</span>
                    <span className="font-bold text-success">{errors.fixed}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ============================================ */}
        {/* Admin Tools */}
        {/* ============================================ */}
        <div className="card mb-8">
          <h2 className="section-header">Admin Tools</h2>
          <div className="grid md:grid-cols-3 gap-4">
            {/* Create Test Accounts */}
            <div className="rounded-lg border border-purple-400/20 bg-purple-400/5 p-4">
              <h3 className="font-medium text-frost mb-1">Test Accounts</h3>
              <p className="text-xs text-frost-muted mb-4">Create/reset 3 test users with profiles & heroes</p>
              <button
                onClick={async () => {
                  if (!token) return;
                  setSeedingAccounts(true);
                  setSeedResult(null);
                  try {
                    const res = await adminApi.seedTestAccounts(token);
                    const created = res.results.filter((r: any) => r.status === 'created').length;
                    const reset = res.results.filter((r: any) => r.status === 'reset').length;
                    const failed = res.results.filter((r: any) => r.status === 'error').length;
                    let msg = '';
                    if (created > 0) msg += `${created} created`;
                    if (reset > 0) msg += `${msg ? ', ' : ''}${reset} reset`;
                    if (failed > 0) msg += `${msg ? ', ' : ''}${failed} failed`;
                    setSeedResult({ message: msg || res.message, password: res.password });
                  } catch (err) {
                    setSeedResult({ message: err instanceof Error ? err.message : 'Failed', error: true });
                  } finally {
                    setSeedingAccounts(false);
                  }
                }}
                disabled={seedingAccounts}
                className="btn-secondary text-sm w-full"
              >
                {seedingAccounts ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="inline-block w-4 h-4 border-2 border-frost border-t-transparent rounded-full animate-spin" />
                    Creating...
                  </span>
                ) : 'Seed Test Accounts'}
              </button>
              {seedResult && (
                <p className={`text-xs mt-2 ${seedResult.error ? 'text-error' : 'text-success'}`}>
                  {seedResult.message}
                  {seedResult.password && <span className="text-frost-muted"> (pw: {seedResult.password})</span>}
                </p>
              )}
            </div>

            {/* Run Data Audit */}
            <div className="rounded-lg border border-ice/20 bg-ice/5 p-4">
              <h3 className="font-medium text-frost mb-1">Data Audit</h3>
              <p className="text-xs text-frost-muted mb-4">Validate game data integrity</p>
              <Link
                href="/admin/data-integrity"
                className="btn-secondary text-sm w-full block text-center"
              >
                Run Data Audit
              </Link>
            </div>

            {/* Run QA Check */}
            <div className="rounded-lg border border-success/20 bg-success/5 p-4">
              <h3 className="font-medium text-frost mb-1">QA Check</h3>
              <p className="text-xs text-frost-muted mb-4">Run web app QA validation</p>
              <Link
                href="/admin/data-integrity"
                className="btn-secondary text-sm w-full block text-center"
              >
                Run QA Check
              </Link>
            </div>
          </div>
        </div>
      </div>
    </PageLayout>
  );
}
