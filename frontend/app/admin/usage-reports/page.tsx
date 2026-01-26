'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';

interface UsageStats {
  summary: {
    total_users: number;
    active_users: number;
    new_users: number;
    activity_rate: number;
  };
  activity_breakdown: {
    very_active: number;
    active_weekly: number;
    active_monthly: number;
    inactive: number;
  };
  content: {
    profiles: number;
    heroes: number;
    inventory: number;
  };
  top_heroes: { name: string; count: number }[];
  hero_classes: Record<string, number>;
  spending_distribution: Record<string, number>;
  alliance_roles: Record<string, number>;
  top_states: { state: number; count: number }[];
  states_summary: {
    unique_states: number;
    users_with_state: number;
    users_without_state: number;
  };
  daily_active_users: number[];
  ai_usage: { date: string; requests: number; rules: number }[];
  historical: { date: string; total_users: number; active_users: number; new_users: number; heroes_tracked: number }[];
  user_activity: {
    username: string;
    email: string;
    heroes: number;
    items: number;
    activity_score: number;
    last_login: string | null;
  }[];
}

export default function AdminUsageReportsPage() {
  const { token, user } = useAuth();
  const [stats, setStats] = useState<UsageStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [dateRange, setDateRange] = useState('7d');
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'content' | 'trends'>('overview');
  const [userSort, setUserSort] = useState('last_active');

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
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
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

  const formatLastLogin = (lastLogin: string | null) => {
    if (!lastLogin) return 'Never';
    const date = new Date(lastLogin);
    const now = new Date();
    const days = Math.floor((now.getTime() - date.getTime()) / (24 * 60 * 60 * 1000));
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const sortedUsers = stats?.user_activity?.slice().sort((a, b) => {
    switch (userSort) {
      case 'last_active':
        return (b.last_login || '').localeCompare(a.last_login || '');
      case 'heroes':
        return b.heroes - a.heroes;
      case 'items':
        return b.items - a.items;
      case 'activity':
        return b.activity_score - a.activity_score;
      default:
        return 0;
    }
  }) || [];

  return (
    <PageLayout>
      <div className="max-w-6xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
          <div>
            <h1 className="text-3xl font-bold text-frost">Usage Reports</h1>
            <p className="text-frost-muted mt-1">Detailed analytics and user engagement metrics</p>
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

        {/* Tabs */}
        <div className="flex gap-1 mb-6 bg-surface rounded-lg p-1">
          {[
            { id: 'overview', label: 'Overview', icon: '📊' },
            { id: 'users', label: 'User Activity', icon: '👥' },
            { id: 'content', label: 'Content Usage', icon: '📦' },
            { id: 'trends', label: 'Trends', icon: '📈' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                activeTab === tab.id
                  ? 'bg-ice text-background'
                  : 'text-frost-muted hover:text-frost hover:bg-surface-hover'
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>

        {isLoading ? (
          <div className="grid md:grid-cols-2 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="card animate-pulse">
                <div className="h-6 bg-surface-hover rounded w-32 mb-4" />
                <div className="h-32 bg-surface-hover rounded" />
              </div>
            ))}
          </div>
        ) : stats && (
          <>
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Key Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="card text-center bg-ice/10 border-ice/20">
                    <p className="text-3xl font-bold text-ice">{stats.summary.total_users}</p>
                    <p className="text-sm text-frost-muted">Total Users</p>
                  </div>
                  <div className="card text-center bg-success/10 border-success/20">
                    <p className="text-3xl font-bold text-success">{stats.summary.active_users}</p>
                    <p className="text-sm text-frost-muted">Active Users</p>
                  </div>
                  <div className="card text-center bg-purple-500/10 border-purple-500/20">
                    <p className="text-3xl font-bold text-purple-400">{stats.summary.new_users}</p>
                    <p className="text-sm text-frost-muted">New Users</p>
                  </div>
                  <div className="card text-center bg-warning/10 border-warning/20">
                    <p className={`text-3xl font-bold ${
                      stats.summary.activity_rate >= 50 ? 'text-success' :
                      stats.summary.activity_rate >= 25 ? 'text-warning' : 'text-error'
                    }`}>
                      {stats.summary.activity_rate}%
                    </p>
                    <p className="text-sm text-frost-muted">Activity Rate</p>
                  </div>
                </div>

                {/* Activity Breakdown & Content */}
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="card">
                    <h2 className="section-header mb-4">Activity Breakdown</h2>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center p-3 bg-surface rounded-lg">
                        <span className="flex items-center gap-2">
                          <span className="w-3 h-3 rounded-full bg-success" />
                          Very Active (daily)
                        </span>
                        <strong className="text-success">{stats.activity_breakdown.very_active}</strong>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-surface rounded-lg">
                        <span className="flex items-center gap-2">
                          <span className="w-3 h-3 rounded-full bg-ice" />
                          Active (weekly)
                        </span>
                        <strong className="text-ice">{stats.activity_breakdown.active_weekly}</strong>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-surface rounded-lg">
                        <span className="flex items-center gap-2">
                          <span className="w-3 h-3 rounded-full bg-warning" />
                          Occasional (monthly)
                        </span>
                        <strong className="text-warning">{stats.activity_breakdown.active_monthly}</strong>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-surface rounded-lg">
                        <span className="flex items-center gap-2">
                          <span className="w-3 h-3 rounded-full bg-error" />
                          Inactive (30d+)
                        </span>
                        <strong className="text-error">{stats.activity_breakdown.inactive}</strong>
                      </div>
                    </div>
                  </div>

                  <div className="card">
                    <h2 className="section-header mb-4">Content Created</h2>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center p-3 bg-surface rounded-lg">
                        <span>👤 Profiles Created</span>
                        <strong className="text-frost">{stats.content.profiles}</strong>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-surface rounded-lg">
                        <span>🦸 Heroes Tracked</span>
                        <strong className="text-frost">{stats.content.heroes}</strong>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-surface rounded-lg">
                        <span>🎒 Inventory Items</span>
                        <strong className="text-frost">{stats.content.inventory}</strong>
                      </div>
                    </div>
                  </div>
                </div>

                {/* DAU Chart */}
                <div className="card">
                  <h2 className="section-header mb-4">Daily Active Users</h2>
                  <div className="flex items-end gap-1 h-32">
                    {stats.daily_active_users.map((count, i) => {
                      const max = Math.max(...stats.daily_active_users, 1);
                      return (
                        <div
                          key={i}
                          className="flex-1 bg-ice/30 hover:bg-ice/50 rounded-t transition-colors"
                          style={{ height: `${(count / max) * 100}%`, minHeight: count > 0 ? '4px' : 0 }}
                          title={`${count} users`}
                        />
                      );
                    })}
                  </div>
                  <div className="flex justify-between text-xs text-frost-muted mt-2">
                    <span>{dateRange === '7d' ? '7 days ago' : dateRange === '30d' ? '30 days ago' : '90 days ago'}</span>
                    <span>Today</span>
                  </div>
                </div>
              </div>
            )}

            {/* User Activity Tab */}
            {activeTab === 'users' && (
              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="section-header">User Activity Details</h2>
                  <select
                    value={userSort}
                    onChange={(e) => setUserSort(e.target.value)}
                    className="input w-auto text-sm"
                  >
                    <option value="last_active">Last Active</option>
                    <option value="heroes">Most Heroes</option>
                    <option value="items">Most Items</option>
                    <option value="activity">Activity Score</option>
                  </select>
                </div>

                {/* Table Header */}
                <div className="grid grid-cols-5 gap-4 p-3 bg-surface rounded-lg text-xs font-bold text-frost-muted uppercase mb-2">
                  <div>User</div>
                  <div className="text-center">Heroes</div>
                  <div className="text-center">Items</div>
                  <div className="text-center">Activity</div>
                  <div className="text-right">Last Active</div>
                </div>

                {/* Table Body */}
                <div className="space-y-1 max-h-[500px] overflow-y-auto">
                  {sortedUsers.map((user, i) => (
                    <div
                      key={i}
                      className="grid grid-cols-5 gap-4 p-3 border-b border-surface-border text-sm items-center"
                    >
                      <div className="font-medium text-frost truncate">{user.username}</div>
                      <div className="text-center">{user.heroes}</div>
                      <div className="text-center">{user.items}</div>
                      <div className={`text-center font-medium ${
                        user.activity_score >= 5 ? 'text-success' :
                        user.activity_score >= 2 ? 'text-warning' : 'text-error'
                      }`}>
                        {user.activity_score}/7
                      </div>
                      <div className="text-right text-frost-muted">
                        {formatLastLogin(user.last_login)}
                      </div>
                    </div>
                  ))}
                </div>

                {sortedUsers.length === 50 && (
                  <p className="text-xs text-frost-muted mt-3 text-center">
                    Showing top 50 users
                  </p>
                )}
              </div>
            )}

            {/* Content Usage Tab */}
            {activeTab === 'content' && (
              <div className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Popular Heroes */}
                  <div className="card">
                    <h2 className="section-header mb-4">Most Popular Heroes</h2>
                    {stats.top_heroes.length > 0 ? (
                      <div className="space-y-3">
                        {stats.top_heroes.map((hero) => {
                          const max = stats.top_heroes[0]?.count || 1;
                          return (
                            <div key={hero.name}>
                              <div className="flex justify-between text-sm mb-1">
                                <span className="text-frost">{hero.name}</span>
                                <span className="text-frost-muted">{hero.count}</span>
                              </div>
                              <div className="h-2 bg-surface rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-ice rounded-full"
                                  style={{ width: `${(hero.count / max) * 100}%` }}
                                />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <p className="text-frost-muted text-sm">No hero data yet</p>
                    )}
                  </div>

                  {/* Hero Class Distribution */}
                  <div className="card">
                    <h2 className="section-header mb-4">Hero Class Distribution</h2>
                    {Object.keys(stats.hero_classes).length > 0 ? (
                      <div className="space-y-3">
                        {Object.entries(stats.hero_classes).map(([heroClass, count]) => {
                          const total = Object.values(stats.hero_classes).reduce((a, b) => a + b, 0);
                          const pct = total > 0 ? (count / total) * 100 : 0;
                          const icons: Record<string, string> = { Infantry: '🛡️', Marksman: '🏹', Lancer: '🗡️' };
                          const colors: Record<string, string> = { Infantry: 'text-error', Marksman: 'text-success', Lancer: 'text-ice' };
                          return (
                            <div key={heroClass} className="flex items-center justify-between p-3 bg-surface rounded-lg">
                              <div className="flex items-center gap-2">
                                <span className="text-xl">{icons[heroClass] || '❓'}</span>
                                <span className="font-medium">{heroClass}</span>
                              </div>
                              <div className="text-right">
                                <span className={`text-lg font-bold ${colors[heroClass] || 'text-frost'}`}>
                                  {count}
                                </span>
                                <span className="text-xs text-frost-muted ml-2">({pct.toFixed(1)}%)</span>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <p className="text-frost-muted text-sm">No hero data yet</p>
                    )}
                  </div>
                </div>

                {/* Profile Settings */}
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="card">
                    <h2 className="section-header mb-4">Spending Profile</h2>
                    <div className="space-y-2">
                      {Object.entries(stats.spending_distribution).map(([profile, count]) => (
                        <div key={profile} className="flex justify-between p-2 bg-surface rounded">
                          <span className="capitalize">{profile}</span>
                          <strong>{count}</strong>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="card">
                    <h2 className="section-header mb-4">Alliance Role</h2>
                    <div className="space-y-2">
                      {Object.entries(stats.alliance_roles).map(([role, count]) => (
                        <div key={role} className="flex justify-between p-2 bg-surface rounded">
                          <span className="capitalize">{role}</span>
                          <strong>{count}</strong>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* State Distribution */}
                <div className="card">
                  <h2 className="section-header mb-4">State Distribution</h2>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="text-sm font-medium text-frost mb-3">Users by State</h3>
                      {stats.top_states.length > 0 ? (
                        <div className="space-y-2">
                          {stats.top_states.slice(0, 15).map(({ state, count }) => {
                            const max = stats.top_states[0]?.count || 1;
                            return (
                              <div key={state}>
                                <div className="flex justify-between text-sm mb-1">
                                  <span>State {state}</span>
                                  <strong>{count}</strong>
                                </div>
                                <div className="h-1.5 bg-surface rounded-full overflow-hidden">
                                  <div
                                    className="h-full bg-purple-500 rounded-full"
                                    style={{ width: `${(count / max) * 100}%` }}
                                  />
                                </div>
                              </div>
                            );
                          })}
                          {stats.top_states.length > 15 && (
                            <p className="text-xs text-frost-muted mt-2">
                              Showing top 15 of {stats.top_states.length} states
                            </p>
                          )}
                        </div>
                      ) : (
                        <p className="text-frost-muted text-sm">No state data yet</p>
                      )}
                    </div>

                    <div>
                      <h3 className="text-sm font-medium text-frost mb-3">State Summary</h3>
                      <div className="space-y-3">
                        <div className="flex justify-between p-3 bg-surface rounded-lg">
                          <span>🌍 Unique States</span>
                          <strong className="text-purple-400">{stats.states_summary.unique_states}</strong>
                        </div>
                        <div className="flex justify-between p-3 bg-surface rounded-lg">
                          <span>👥 Users with State</span>
                          <strong className="text-success">{stats.states_summary.users_with_state}</strong>
                        </div>
                        <div className="flex justify-between p-3 bg-surface rounded-lg">
                          <span>❓ No State Set</span>
                          <strong className="text-error">{stats.states_summary.users_without_state}</strong>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Trends Tab */}
            {activeTab === 'trends' && (
              <div className="space-y-6">
                {stats.historical.length > 0 ? (
                  <>
                    {/* User Growth */}
                    <div className="card">
                      <h2 className="section-header mb-4">User Growth</h2>
                      <div className="flex items-end gap-0.5 h-40">
                        {stats.historical.map((day, i) => {
                          const max = Math.max(...stats.historical.map((d) => d.total_users), 1);
                          return (
                            <div
                              key={i}
                              className="flex-1 bg-ice/30 hover:bg-ice/50 rounded-t transition-colors cursor-pointer"
                              style={{ height: `${(day.total_users / max) * 100}%`, minHeight: '2px' }}
                              title={`${day.date}: ${day.total_users} users`}
                            />
                          );
                        })}
                      </div>
                      <div className="flex justify-between text-xs text-frost-muted mt-2">
                        <span>{stats.historical[0]?.date}</span>
                        <span>{stats.historical[stats.historical.length - 1]?.date}</span>
                      </div>
                    </div>

                    {/* Active Users */}
                    <div className="card">
                      <h2 className="section-header mb-4">Active Users</h2>
                      <div className="flex items-end gap-0.5 h-32">
                        {stats.historical.map((day, i) => {
                          const max = Math.max(...stats.historical.map((d) => d.active_users), 1);
                          return (
                            <div
                              key={i}
                              className="flex-1 bg-success/30 hover:bg-success/50 rounded-t transition-colors cursor-pointer"
                              style={{ height: `${(day.active_users / max) * 100}%`, minHeight: day.active_users > 0 ? '2px' : 0 }}
                              title={`${day.date}: ${day.active_users} active`}
                            />
                          );
                        })}
                      </div>
                    </div>

                    {/* New Registrations */}
                    <div className="card">
                      <h2 className="section-header mb-4">New Registrations</h2>
                      <div className="flex items-end gap-0.5 h-32">
                        {stats.historical.map((day, i) => {
                          const max = Math.max(...stats.historical.map((d) => d.new_users), 1);
                          return (
                            <div
                              key={i}
                              className="flex-1 bg-purple-500/30 hover:bg-purple-500/50 rounded-t transition-colors cursor-pointer"
                              style={{ height: `${max > 0 ? (day.new_users / max) * 100 : 0}%`, minHeight: day.new_users > 0 ? '2px' : 0 }}
                              title={`${day.date}: ${day.new_users} new`}
                            />
                          );
                        })}
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="card text-center py-12">
                    <div className="text-4xl mb-4">📊</div>
                    <h3 className="text-lg font-medium text-frost mb-2">No Historical Data Yet</h3>
                    <p className="text-frost-muted">
                      Charts will appear after a few days of data collection.
                    </p>
                  </div>
                )}

                {/* AI Usage */}
                <div className="card">
                  <h2 className="section-header mb-4">AI Usage (Rules vs API)</h2>
                  <div className="flex items-end gap-1 h-32">
                    {stats.ai_usage.map((day, i) => {
                      const maxRequests = Math.max(...stats.ai_usage.map((d) => d.requests), 1);
                      const aiRequests = day.requests - day.rules;
                      return (
                        <div key={i} className="flex-1 flex flex-col gap-0.5">
                          <div
                            className="bg-purple-500/30 hover:bg-purple-500/50 rounded-t transition-colors"
                            style={{
                              height: `${maxRequests > 0 ? (aiRequests / maxRequests) * 100 : 0}%`,
                            }}
                            title={`${aiRequests} AI requests`}
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
                    })}
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
            )}
          </>
        )}
      </div>
    </PageLayout>
  );
}
