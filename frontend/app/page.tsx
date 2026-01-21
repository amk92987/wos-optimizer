'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';
import { dashboardApi, DashboardStats } from '@/lib/api';

export default function DashboardPage() {
  const { token } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (token) {
      dashboardApi.getStats(token)
        .then(setStats)
        .catch(console.error)
        .finally(() => setIsLoading(false));
    }
  }, [token]);

  const spendingLabels: Record<string, string> = {
    f2p: 'Free to Play',
    minnow: 'Minnow',
    dolphin: 'Dolphin',
    orca: 'Orca',
    whale: 'Whale',
  };

  const focusLabels: Record<string, string> = {
    svs_combat: 'SvS Combat',
    balanced_growth: 'Balanced Growth',
    economy_focus: 'Economy Focus',
  };

  const roleLabels: Record<string, string> = {
    rally_lead: 'Rally Lead',
    filler: 'Rally Filler',
    farmer: 'Farmer',
    casual: 'Casual',
  };

  return (
    <PageLayout>
      <div className="max-w-6xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-zinc-100">Dashboard</h1>
          <p className="text-zinc-400 mt-2">Welcome back, Chief</p>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="card animate-pulse">
                <div className="h-8 bg-surface-hover rounded w-16 mb-2"></div>
                <div className="h-4 bg-surface-hover rounded w-24"></div>
              </div>
            ))}
          </div>
        ) : stats && (
          <>
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <div className="card-hover">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="stat-value">{stats.owned_heroes}</p>
                    <p className="stat-label">Heroes Owned</p>
                  </div>
                  <div className="w-12 h-12 bg-amber/10 rounded-xl flex items-center justify-center">
                    <span className="text-2xl">🦸</span>
                  </div>
                </div>
                <div className="mt-3 text-xs text-zinc-500">
                  of {stats.total_heroes} total heroes
                </div>
              </div>

              <div className="card-hover">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="stat-value">{stats.furnace_display}</p>
                    <p className="stat-label">Furnace Level</p>
                  </div>
                  <div className="w-12 h-12 bg-red-500/10 rounded-xl flex items-center justify-center">
                    <span className="text-2xl">🔥</span>
                  </div>
                </div>
                <div className="mt-3 text-xs text-zinc-500">
                  Day {stats.server_age_days}
                </div>
              </div>

              <div className="card-hover">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="stat-value">Gen {stats.generation}</p>
                    <p className="stat-label">Server Generation</p>
                  </div>
                  <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center">
                    <span className="text-2xl">📅</span>
                  </div>
                </div>
                <div className="mt-3 text-xs text-zinc-500">
                  {stats.state_number ? `State ${stats.state_number}` : 'No state set'}
                </div>
              </div>

              <div className="card-hover">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="stat-value text-lg">{spendingLabels[stats.spending_profile] || stats.spending_profile}</p>
                    <p className="stat-label">Spending Profile</p>
                  </div>
                  <div className="w-12 h-12 bg-green-500/10 rounded-xl flex items-center justify-center">
                    <span className="text-2xl">💰</span>
                  </div>
                </div>
                <div className="mt-3 text-xs text-zinc-500">
                  {roleLabels[stats.alliance_role] || stats.alliance_role}
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-zinc-100 mb-4">Quick Actions</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <a href="/heroes" className="card-hover group">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-amber/10 rounded-lg flex items-center justify-center group-hover:bg-amber/20 transition-colors">
                      <span className="text-xl">🦸</span>
                    </div>
                    <div>
                      <p className="font-medium text-zinc-100">Manage Heroes</p>
                      <p className="text-sm text-zinc-500">Track your hero collection</p>
                    </div>
                  </div>
                </a>

                <a href="/settings" className="card-hover group">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center group-hover:bg-blue-500/20 transition-colors">
                      <span className="text-xl">⚙️</span>
                    </div>
                    <div>
                      <p className="font-medium text-zinc-100">Settings</p>
                      <p className="text-sm text-zinc-500">Configure your profile</p>
                    </div>
                  </div>
                </a>

                <div className="card border-dashed border-zinc-700 opacity-50">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-surface rounded-lg flex items-center justify-center">
                      <span className="text-xl">🤖</span>
                    </div>
                    <div>
                      <p className="font-medium text-zinc-400">AI Advisor</p>
                      <p className="text-sm text-zinc-600">Coming soon</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Profile Summary */}
            <div className="card">
              <h2 className="text-xl font-semibold text-zinc-100 mb-4">Profile Summary</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-zinc-500">Focus</p>
                  <p className="font-medium text-zinc-100">{focusLabels[stats.priority_focus] || stats.priority_focus}</p>
                </div>
                <div>
                  <p className="text-sm text-zinc-500">Role</p>
                  <p className="font-medium text-zinc-100">{roleLabels[stats.alliance_role] || stats.alliance_role}</p>
                </div>
                <div>
                  <p className="text-sm text-zinc-500">Spending</p>
                  <p className="font-medium text-zinc-100">{spendingLabels[stats.spending_profile] || stats.spending_profile}</p>
                </div>
                <div>
                  <p className="text-sm text-zinc-500">State</p>
                  <p className="font-medium text-zinc-100">{stats.state_number || 'Not set'}</p>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </PageLayout>
  );
}
