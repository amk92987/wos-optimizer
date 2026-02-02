'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';
import { adminApi } from '@/lib/api';

interface AdminStats {
  total_users: number;
  active_users: number;
  test_accounts: number;
  total_profiles: number;
  total_heroes_tracked: number;
  ai_requests_today: number;
  pending_feedback: number;
  active_announcements: number;
}

export default function AdminDashboard() {
  const { token, user } = useAuth();
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (token) {
      adminApi.getStats(token)
        .then(setStats)
        .catch(console.error)
        .finally(() => setIsLoading(false));
    }
  }, [token]);

  // Redirect non-admins
  if (user && user.role !== 'admin') {
    return (
      <PageLayout>
        <div className="max-w-2xl mx-auto text-center py-16">
          <div className="text-6xl mb-6">🔒</div>
          <h1 className="text-2xl font-bold text-frost mb-4">Access Denied</h1>
          <p className="text-frost-muted mb-6">You don't have permission to view this page.</p>
          <Link href="/" className="btn-primary">
            Return Home
          </Link>
        </div>
      </PageLayout>
    );
  }

  const statCards = [
    { label: 'Total Users', value: stats?.total_users ?? '-', icon: '👥', color: 'text-ice', href: '/admin/users' },
    { label: 'Active Users', value: stats?.active_users ?? '-', icon: '✅', color: 'text-success' },
    { label: 'Test Accounts', value: stats?.test_accounts ?? '-', icon: '🧪', color: 'text-warning', href: '/admin/users?filter=test' },
    { label: 'Total Profiles', value: stats?.total_profiles ?? '-', icon: '📋', color: 'text-frost' },
    { label: 'Heroes Tracked', value: stats?.total_heroes_tracked ?? '-', icon: '🦸', color: 'text-fire' },
    { label: 'AI Requests Today', value: stats?.ai_requests_today ?? '-', icon: '🤖', color: 'text-purple-400', href: '/admin/ai' },
    { label: 'Pending Feedback', value: stats?.pending_feedback ?? '-', icon: '💬', color: 'text-yellow-400', href: '/admin/inbox' },
    { label: 'Announcements', value: stats?.active_announcements ?? '-', icon: '📢', color: 'text-ice', href: '/admin/announcements' },
  ];

  const quickActions = [
    { label: 'Manage Users', href: '/admin/users', icon: '👥', description: 'Create, edit, or suspend users' },
    { label: 'View Feedback', href: '/admin/inbox', icon: '📬', description: 'Review user feedback and errors' },
    { label: 'Announcements', href: '/admin/announcements', icon: '📢', description: 'Create system announcements' },
    { label: 'Feature Flags', href: '/admin/feature-flags', icon: '🚩', description: 'Toggle features on/off' },
    { label: 'AI Settings', href: '/admin/ai', icon: '🤖', description: 'Configure AI behavior' },
    { label: 'Usage Reports', href: '/admin/usage-reports', icon: '📈', description: 'View analytics and trends' },
  ];

  return (
    <PageLayout>
      <div className="max-w-6xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Admin Dashboard</h1>
          <p className="text-frost-muted mt-2">System overview and quick actions</p>
        </div>

        {/* Stats Grid */}
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

        {/* Quick Actions */}
        <div className="card mb-8">
          <h2 className="section-header">Quick Actions</h2>
          <div className="grid md:grid-cols-3 gap-4">
            {quickActions.map((action) => (
              <Link
                key={action.label}
                href={action.href}
                className="flex items-start gap-4 p-4 rounded-lg bg-surface hover:bg-surface-hover transition-colors group"
              >
                <div className="text-2xl">{action.icon}</div>
                <div>
                  <p className="font-medium text-frost group-hover:text-ice transition-colors">
                    {action.label}
                  </p>
                  <p className="text-sm text-frost-muted">{action.description}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Recent Users */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="section-header mb-0">Recent Users</h2>
              <Link href="/admin/users" className="text-sm text-ice hover:text-ice-light transition-colors">
                View All
              </Link>
            </div>
            <div className="space-y-3">
              {isLoading ? (
                [...Array(3)].map((_, i) => (
                  <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-surface animate-pulse">
                    <div className="w-8 h-8 rounded-full bg-surface-hover" />
                    <div className="flex-1">
                      <div className="h-4 bg-surface-hover rounded w-32 mb-1" />
                      <div className="h-3 bg-surface-hover rounded w-24" />
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-frost-muted text-sm text-center py-4">
                  Recent users will appear here
                </p>
              )}
            </div>
          </div>

          {/* System Health */}
          <div className="card">
            <h2 className="section-header">System Health</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-frost-muted">Database</span>
                <span className="badge-success">Online</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-frost-muted">AI Service</span>
                <span className="badge-success">Active</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-frost-muted">Email Service</span>
                <span className="badge-warning">Debug Mode</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-frost-muted">OCR Service</span>
                <span className="badge-secondary">Optional</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </PageLayout>
  );
}
