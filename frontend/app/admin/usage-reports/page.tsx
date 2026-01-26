'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';

interface UsageStats {
  daily_active_users: number[];
  weekly_active_users: number;
  monthly_active_users: number;
  page_views: Record<string, number>;
  top_heroes: { name: string; count: number }[];
  ai_usage: { date: string; requests: number; rules: number }[];
  retention: { day: number; percent: number }[];
}

export default function AdminUsageReportsPage() {
  const { token, user } = useAuth();
  const [stats, setStats] = useState<UsageStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [dateRange, setDateRange] = useState('7d');

  useEffect(() => {
    if (token) {
      fetchStats();
    }
  }, [token, dateRange]);

  const fetchStats = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/admin/usage/stats?range=${dateRange}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
      // Demo data
      setStats({
        daily_active_users: [12, 15, 18, 14, 22, 25, 20],
        weekly_active_users: 45,
        monthly_active_users: 120,
        page_views: {
          'Hero Tracker': 450,
          'AI Advisor': 320,
          'Settings': 180,
          'Lineups': 150,
          'Chief Tracker': 120,
        },
        top_heroes: [
          { name: 'Jessie', count: 85 },
          { name: 'Sergey', count: 78 },
          { name: 'Jeronimo', count: 72 },
          { name: 'Molly', count: 65 },
          { name: 'Wu Ming', count: 58 },
        ],
        ai_usage: [
          { date: '2026-01-19', requests: 45, rules: 42 },
          { date: '2026-01-20', requests: 52, rules: 48 },
          { date: '2026-01-21', requests: 38, rules: 35 },
          { date: '2026-01-22', requests: 67, rules: 62 },
          { date: '2026-01-23', requests: 55, rules: 51 },
          { date: '2026-01-24', requests: 72, rules: 66 },
          { date: '2026-01-25', requests: 48, rules: 44 },
        ],
        retention: [
          { day: 1, percent: 85 },
          { day: 7, percent: 62 },
          { day: 14, percent: 48 },
          { day: 30, percent: 35 },
        ],
      });
    } finally {
      setIsLoading(false);
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

  const maxPageViews = stats?.page_views ? Math.max(...Object.values(stats.page_views)) : 0;
  const maxHeroCount = stats?.top_heroes?.length ? Math.max(...stats.top_heroes.map((h) => h.count)) : 0;

  return (
    <PageLayout>
      <div className="max-w-6xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-frost">Usage Reports</h1>
            <p className="text-frost-muted mt-1">Analytics and user engagement metrics</p>
          </div>
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="input w-auto"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
        </div>

        {isLoading ? (
          <div className="grid md:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="card animate-pulse">
                <div className="h-6 bg-surface-hover rounded w-32 mb-4" />
                <div className="h-32 bg-surface-hover rounded" />
              </div>
            ))}
          </div>
        ) : stats && (
          <>
            {/* Key Metrics */}
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="card text-center">
                <p className="text-3xl font-bold text-ice">
                  {stats.daily_active_users?.length ? stats.daily_active_users[stats.daily_active_users.length - 1] : 0}
                </p>
                <p className="text-sm text-frost-muted">Daily Active Users</p>
              </div>
              <div className="card text-center">
                <p className="text-3xl font-bold text-frost">{stats.weekly_active_users}</p>
                <p className="text-sm text-frost-muted">Weekly Active Users</p>
              </div>
              <div className="card text-center">
                <p className="text-3xl font-bold text-success">{stats.monthly_active_users}</p>
                <p className="text-sm text-frost-muted">Monthly Active Users</p>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {/* DAU Chart */}
              <div className="card">
                <h2 className="section-header">Daily Active Users</h2>
                <div className="flex items-end gap-2 h-32">
                  {stats.daily_active_users?.length ? stats.daily_active_users.map((count, i) => (
                    <div
                      key={i}
                      className="flex-1 bg-ice/30 hover:bg-ice/50 rounded-t transition-colors"
                      style={{ height: `${(count / Math.max(...stats.daily_active_users)) * 100}%` }}
                      title={`${count} users`}
                    />
                  )) : <p className="text-frost-muted text-sm">No data available</p>}
                </div>
                <div className="flex justify-between text-xs text-frost-muted mt-2">
                  <span>7 days ago</span>
                  <span>Today</span>
                </div>
              </div>

              {/* Page Views */}
              <div className="card">
                <h2 className="section-header">Top Pages</h2>
                <div className="space-y-3">
                  {stats.page_views ? Object.entries(stats.page_views)
                    .sort(([, a], [, b]) => b - a)
                    .slice(0, 5)
                    .map(([page, count]) => (
                      <div key={page}>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-frost">{page}</span>
                          <span className="text-frost-muted">{count}</span>
                        </div>
                        <div className="h-2 bg-surface rounded-full overflow-hidden">
                          <div
                            className="h-full bg-ice rounded-full"
                            style={{ width: `${(count / maxPageViews) * 100}%` }}
                          />
                        </div>
                      </div>
                    )) : (
                    <p className="text-frost-muted text-sm">No page view data available</p>
                  )}
                </div>
              </div>

              {/* Top Heroes */}
              <div className="card">
                <h2 className="section-header">Most Tracked Heroes</h2>
                <div className="space-y-3">
                  {stats.top_heroes?.length ? stats.top_heroes.map((hero) => (
                    <div key={hero.name}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-frost">{hero.name}</span>
                        <span className="text-frost-muted">{hero.count} users</span>
                      </div>
                      <div className="h-2 bg-surface rounded-full overflow-hidden">
                        <div
                          className="h-full bg-fire rounded-full"
                          style={{ width: `${(hero.count / maxHeroCount) * 100}%` }}
                        />
                      </div>
                    </div>
                  )) : <p className="text-frost-muted text-sm">No hero data available</p>}
                </div>
              </div>

              {/* Retention */}
              <div className="card">
                <h2 className="section-header">User Retention</h2>
                <div className="grid grid-cols-4 gap-4">
                  {stats.retention?.length ? stats.retention.map((r) => (
                    <div key={r.day} className="text-center">
                      <div className="relative w-16 h-16 mx-auto mb-2">
                        <svg className="w-full h-full transform -rotate-90">
                          <circle
                            cx="32"
                            cy="32"
                            r="28"
                            fill="none"
                            stroke="currentColor"
                            className="text-surface"
                            strokeWidth="6"
                          />
                          <circle
                            cx="32"
                            cy="32"
                            r="28"
                            fill="none"
                            stroke="currentColor"
                            className="text-success"
                            strokeWidth="6"
                            strokeDasharray={`${(r.percent / 100) * 176} 176`}
                          />
                        </svg>
                        <span className="absolute inset-0 flex items-center justify-center text-sm font-bold text-frost">
                          {r.percent}%
                        </span>
                      </div>
                      <p className="text-xs text-frost-muted">Day {r.day}</p>
                    </div>
                  )) : <p className="text-frost-muted text-sm col-span-4">No retention data available</p>}
                </div>
              </div>

              {/* AI Usage */}
              <div className="card md:col-span-2">
                <h2 className="section-header">AI Usage (Rules vs API)</h2>
                <div className="flex items-end gap-1 h-32">
                  {stats.ai_usage?.length ? stats.ai_usage.map((day, i) => {
                    const maxRequests = Math.max(...stats.ai_usage.map((d) => d.requests));
                    return (
                      <div key={i} className="flex-1 flex flex-col gap-0.5">
                        <div
                          className="bg-purple-500/30 hover:bg-purple-500/50 rounded-t transition-colors"
                          style={{
                            height: `${maxRequests > 0 ? ((day.requests - day.rules) / maxRequests) * 100 : 0}%`,
                          }}
                          title={`${day.requests - day.rules} AI requests`}
                        />
                        <div
                          className="bg-success/30 hover:bg-success/50 transition-colors"
                          style={{
                            height: `${maxRequests > 0 ? (day.rules / maxRequests) * 100 : 0}%`,
                          }}
                          title={`${day.rules} rules handled`}
                        />
                      </div>
                    );
                  }) : <p className="text-frost-muted text-sm">No AI usage data available</p>}
                </div>
                <div className="flex justify-between items-center mt-4">
                  <div className="flex gap-4 text-xs">
                    <span className="flex items-center gap-1">
                      <span className="w-3 h-3 bg-success/50 rounded" />
                      Rules Engine
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="w-3 h-3 bg-purple-500/50 rounded" />
                      AI Provider
                    </span>
                  </div>
                  <span className="text-xs text-frost-muted">Last 7 days</span>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </PageLayout>
  );
}
