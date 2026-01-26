'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';

interface FeatureFlag {
  id: number;
  name: string;
  description: string;
  is_enabled: boolean;
  updated_at: string;
}

export default function AdminFeatureFlagsPage() {
  const { token, user } = useAuth();
  const [flags, setFlags] = useState<FeatureFlag[]>([]);
  const [isLoading, setIsLoading] = useState(true);

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

  // Default flags to show if API doesn't return them
  const defaultFlags: Omit<FeatureFlag, 'id' | 'updated_at'>[] = [
    { name: 'hero_recommendations', description: 'Enable AI-powered hero upgrade recommendations', is_enabled: true },
    { name: 'new_user_onboarding', description: 'Show onboarding flow for new users', is_enabled: true },
    { name: 'analytics_tracking', description: 'Enable usage analytics tracking', is_enabled: true },
    { name: 'inventory_ocr', description: 'Enable OCR for inventory screenshots', is_enabled: false },
    { name: 'alliance_features', description: 'Enable alliance coordination features', is_enabled: false },
    { name: 'beta_features', description: 'Enable beta features for testing', is_enabled: false },
    { name: 'maintenance_mode', description: 'Put site in maintenance mode', is_enabled: false },
    { name: 'dark_theme_only', description: 'Force dark theme for all users', is_enabled: false },
  ];

  const displayFlags = flags.length > 0 ? flags : defaultFlags.map((f, i) => ({
    ...f,
    id: i,
    updated_at: new Date().toISOString(),
  }));

  return (
    <PageLayout>
      <div className="max-w-3xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Feature Flags</h1>
          <p className="text-frost-muted mt-1">Toggle features on or off across the application</p>
        </div>

        {/* Flags List */}
        <div className="card">
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
              {displayFlags.map((flag) => (
                <div
                  key={flag.name}
                  className={`flex items-center justify-between p-4 rounded-lg transition-colors ${
                    flag.is_enabled ? 'bg-success/5 border border-success/20' : 'bg-surface'
                  }`}
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-frost">{flag.name}</span>
                      {flag.name === 'maintenance_mode' && flag.is_enabled && (
                        <span className="badge badge-error text-xs">ACTIVE</span>
                      )}
                    </div>
                    <p className="text-sm text-frost-muted mt-1">{flag.description}</p>
                    {flags.length > 0 && (
                      <p className="text-xs text-text-muted mt-2">
                        Last updated: {formatDate(flag.updated_at)}
                      </p>
                    )}
                  </div>
                  <button
                    onClick={() => handleToggle(flag.name, flag.is_enabled)}
                    className={`relative w-14 h-7 rounded-full transition-colors ${
                      flag.is_enabled ? 'bg-success' : 'bg-surface-hover'
                    }`}
                    title={flag.is_enabled ? 'Click to disable' : 'Click to enable'}
                  >
                    <span
                      className={`absolute left-0 top-1 w-5 h-5 rounded-full bg-white shadow transition-transform ${
                        flag.is_enabled ? 'translate-x-8' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Warning */}
        <div className="card mt-6 border-warning/30 bg-warning/5">
          <div className="flex gap-3">
            <span className="text-2xl">⚠️</span>
            <div>
              <h3 className="font-medium text-frost">Caution</h3>
              <p className="text-sm text-frost-muted mt-1">
                Changing feature flags affects all users immediately. Use maintenance_mode to
                temporarily disable access when making significant changes.
              </p>
            </div>
          </div>
        </div>
      </div>
    </PageLayout>
  );
}
