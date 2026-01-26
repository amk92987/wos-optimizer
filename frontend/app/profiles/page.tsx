'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';

interface Profile {
  id: number;
  name: string | null;
  state_number: number | null;
  server_age_days: number;
  furnace_level: number;
  furnace_fc_level: string | null;
  spending_profile: string;
  hero_count: number;
  is_farm_account: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export default function ProfilesPage() {
  const { token } = useAuth();
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);

  useEffect(() => {
    if (token) {
      fetchProfiles();
    }
  }, [token]);

  const fetchProfiles = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/profiles/all', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setProfiles(Array.isArray(data) ? data : []);
      }
    } catch (error) {
      console.error('Failed to fetch profiles:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoadProfile = async (profileId: number) => {
    try {
      await fetch(`http://localhost:8000/api/profiles/${profileId}/activate`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchProfiles();
    } catch (error) {
      console.error('Failed to load profile:', error);
    }
  };

  const handleDeleteProfile = async (profileId: number) => {
    if (!confirm('Are you sure you want to delete this profile? This cannot be undone.')) return;

    try {
      await fetch(`http://localhost:8000/api/profiles/${profileId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchProfiles();
    } catch (error) {
      console.error('Failed to delete profile:', error);
    }
  };

  const handleToggleFarm = async (profile: Profile) => {
    try {
      await fetch(`http://localhost:8000/api/profiles/${profile.id}`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_farm_account: !profile.is_farm_account }),
      });
      fetchProfiles();
    } catch (error) {
      console.error('Failed to update profile:', error);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getFurnaceDisplay = (profile: Profile) => {
    if (profile.furnace_fc_level) {
      return profile.furnace_fc_level;
    }
    return `F${profile.furnace_level}`;
  };

  const spendingLabels: Record<string, string> = {
    f2p: 'F2P',
    minnow: 'Minnow',
    dolphin: 'Dolphin',
    orca: 'Orca',
    whale: 'Whale',
  };

  if (isLoading) {
    return (
      <PageLayout>
        <div className="max-w-3xl mx-auto">
          <div className="h-8 bg-surface rounded w-48 mb-8 animate-pulse" />
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="card animate-pulse">
                <div className="h-20 bg-surface-hover rounded" />
              </div>
            ))}
          </div>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="max-w-3xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-frost">Save / Load</h1>
            <p className="text-frost-muted mt-2">Manage multiple game profiles</p>
          </div>
          <button onClick={() => setShowCreate(true)} className="btn-primary">
            + New Profile
          </button>
        </div>

        {/* Profiles List */}
        {profiles.length === 0 ? (
          <div className="card text-center py-12">
            <div className="text-4xl mb-4">📋</div>
            <h3 className="text-lg font-medium text-frost mb-2">No profiles yet</h3>
            <p className="text-frost-muted mb-4">Create a profile to track your game progress</p>
            <button onClick={() => setShowCreate(true)} className="btn-primary">
              Create First Profile
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {profiles.map((profile) => (
              <div
                key={profile.id}
                className={`card ${
                  profile.is_active
                    ? 'border-2 border-ice bg-ice/5'
                    : ''
                }`}
              >
                <div className="flex items-center gap-4">
                  {/* Profile Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-medium text-frost truncate">
                        {profile.name || `Profile ${profile.id}`}
                      </h3>
                      {profile.is_active && (
                        <span className="badge-success text-xs">Active</span>
                      )}
                      {profile.is_farm_account && (
                        <span className="badge-warning text-xs">Farm</span>
                      )}
                    </div>
                    <div className="flex flex-wrap gap-3 text-sm text-frost-muted">
                      {profile.state_number && (
                        <span>State #{profile.state_number}</span>
                      )}
                      <span>{getFurnaceDisplay(profile)}</span>
                      <span>Day {profile.server_age_days}</span>
                      <span>{profile.hero_count} heroes</span>
                      <span>{spendingLabels[profile.spending_profile] || profile.spending_profile}</span>
                    </div>
                    <p className="text-xs text-text-muted mt-1">
                      Updated: {formatDate(profile.updated_at)}
                    </p>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    {!profile.is_active && (
                      <button
                        onClick={() => handleLoadProfile(profile.id)}
                        className="btn-primary text-sm"
                      >
                        Load
                      </button>
                    )}
                    <button
                      onClick={() => handleToggleFarm(profile)}
                      className={`px-3 py-1.5 text-sm rounded transition-colors ${
                        profile.is_farm_account
                          ? 'bg-warning/20 text-warning hover:bg-warning/30'
                          : 'bg-surface text-frost-muted hover:text-frost hover:bg-surface-hover'
                      }`}
                    >
                      {profile.is_farm_account ? 'Farm' : 'Mark Farm'}
                    </button>
                    <button
                      onClick={() => handleDeleteProfile(profile.id)}
                      className="px-3 py-1.5 text-sm text-error hover:bg-error/10 rounded transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Info Card */}
        <div className="card mt-6">
          <h2 className="section-header">About Profiles</h2>
          <ul className="space-y-2 text-sm text-frost-muted">
            <li className="flex items-start gap-2">
              <span className="text-ice">•</span>
              <span>Each profile tracks a separate game account (main or farm)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-ice">•</span>
              <span>Mark farm accounts for specialized recommendations</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-ice">•</span>
              <span>Link farm accounts to your main by setting the same State #</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-ice">•</span>
              <span>Only one profile can be active at a time</span>
            </li>
          </ul>
        </div>

        {/* Create Profile Modal */}
        {showCreate && (
          <CreateProfileModal
            token={token || ''}
            onClose={() => setShowCreate(false)}
            onCreated={() => {
              setShowCreate(false);
              fetchProfiles();
            }}
          />
        )}
      </div>
    </PageLayout>
  );
}

function CreateProfileModal({
  token,
  onClose,
  onCreated,
}: {
  token: string;
  onClose: () => void;
  onCreated: () => void;
}) {
  const [name, setName] = useState('');
  const [stateNumber, setStateNumber] = useState('');
  const [isFarm, setIsFarm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const res = await fetch('http://localhost:8000/api/profiles', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: name || null,
          state_number: stateNumber ? parseInt(stateNumber) : null,
          is_farm_account: isFarm,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Failed to create profile');
      }

      onCreated();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-surface rounded-xl border border-surface-border max-w-md w-full p-6 animate-fadeIn">
        <h2 className="text-xl font-bold text-frost mb-4">Create Profile</h2>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-error/20 border border-error/30 text-error text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-frost-muted mb-1">
              Profile Name (optional)
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="input"
              placeholder="My Main Account"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-frost-muted mb-1">
              State Number (optional)
            </label>
            <input
              type="number"
              value={stateNumber}
              onChange={(e) => setStateNumber(e.target.value)}
              className="input"
              placeholder="456"
            />
          </div>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={isFarm}
              onChange={(e) => setIsFarm(e.target.checked)}
              className="w-4 h-4 rounded border-surface-border"
            />
            <span className="text-sm text-frost-muted">This is a farm account</span>
          </label>

          <div className="flex gap-3 pt-4">
            <button type="button" onClick={onClose} className="btn-secondary flex-1">
              Cancel
            </button>
            <button type="submit" disabled={isLoading} className="btn-primary flex-1">
              {isLoading ? 'Creating...' : 'Create Profile'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
