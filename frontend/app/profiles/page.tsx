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
  alliance_role: string;
  hero_count: number;
  is_farm_account: boolean;
  is_active: boolean;
  linked_main_profile_id: number | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

interface PreviewData {
  id: number;
  name: string | null;
  state_number: number | null;
  server_age_days: number;
  furnace_level: number;
  furnace_fc_level: string | null;
  spending_profile: string;
  alliance_role: string;
  is_farm_account: boolean;
  linked_main_profile_id: number | null;
  heroes: Array<{
    name: string;
    level: number;
    stars: number;
    generation: number;
    hero_class: string;
  }>;
}

export default function ProfilesPage() {
  const { token } = useAuth();
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [deletedProfiles, setDeletedProfiles] = useState<Profile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [duplicatingId, setDuplicatingId] = useState<number | null>(null);
  const [previewId, setPreviewId] = useState<number | null>(null);
  const [previewData, setPreviewData] = useState<PreviewData | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);
  const [confirmPermDeleteId, setConfirmPermDeleteId] = useState<number | null>(null);

  useEffect(() => {
    if (token) {
      fetchProfiles();
      fetchDeletedProfiles();
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

  const fetchDeletedProfiles = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/profiles/deleted', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setDeletedProfiles(Array.isArray(data) ? data : []);
      }
    } catch (error) {
      console.error('Failed to fetch deleted profiles:', error);
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
    try {
      const res = await fetch(`http://localhost:8000/api/profiles/${profileId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setConfirmDeleteId(null);
        fetchProfiles();
        fetchDeletedProfiles();
      }
    } catch (error) {
      console.error('Failed to delete profile:', error);
    }
  };

  const handlePermanentDelete = async (profileId: number) => {
    try {
      const res = await fetch(`http://localhost:8000/api/profiles/${profileId}?hard=true`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setConfirmPermDeleteId(null);
        fetchDeletedProfiles();
      }
    } catch (error) {
      console.error('Failed to permanently delete profile:', error);
    }
  };

  const handleRestoreProfile = async (profileId: number) => {
    try {
      const res = await fetch(`http://localhost:8000/api/profiles/${profileId}/restore`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        fetchProfiles();
        fetchDeletedProfiles();
      }
    } catch (error) {
      console.error('Failed to restore profile:', error);
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

  const handlePreview = async (profileId: number) => {
    if (previewId === profileId) {
      setPreviewId(null);
      setPreviewData(null);
      return;
    }
    try {
      const res = await fetch(`http://localhost:8000/api/profiles/${profileId}/preview`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setPreviewData(data);
        setPreviewId(profileId);
      }
    } catch (error) {
      console.error('Failed to fetch preview:', error);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getDaysRemaining = (deletedAt: string) => {
    const deleteDate = new Date(deletedAt);
    const expiryDate = new Date(deleteDate.getTime() + 30 * 24 * 60 * 60 * 1000);
    const now = new Date();
    const daysLeft = Math.ceil((expiryDate.getTime() - now.getTime()) / (24 * 60 * 60 * 1000));
    return Math.max(0, daysLeft);
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

  const activeProfile = profiles.find((p) => p.is_active);
  const mainProfiles = profiles.filter((p) => !p.is_farm_account);

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
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-frost">Profiles</h1>
            <p className="text-frost-muted mt-1">Manage multiple game profiles</p>
          </div>
          <button onClick={() => setShowCreate(true)} className="btn-primary">
            + New Profile
          </button>
        </div>

        {/* Info Banner */}
        <div className="card mb-6 bg-ice/5 border-ice/20">
          <p className="text-sm text-frost">
            Your profile data is <strong>automatically saved</strong> as you make changes.
            Use this page to manage multiple profiles (main account, farms, etc).
          </p>
        </div>

        {/* Current Profile Summary */}
        {activeProfile && (
          <div className="card mb-6">
            <h2 className="section-header mb-4">Current Profile</h2>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="text-center">
                <p className="text-xs text-frost-muted mb-1">Chief Name</p>
                <p className="font-medium text-frost">{activeProfile.name || 'Chief'}</p>
              </div>
              <div className="text-center">
                <p className="text-xs text-frost-muted mb-1">State #</p>
                <p className="font-medium text-frost">{activeProfile.state_number || 'N/A'}</p>
              </div>
              <div className="text-center">
                <p className="text-xs text-frost-muted mb-1">Server Age</p>
                <p className="font-medium text-frost">Day {activeProfile.server_age_days}</p>
              </div>
              <div className="text-center">
                <p className="text-xs text-frost-muted mb-1">Heroes</p>
                <p className="font-medium text-frost">{activeProfile.hero_count}</p>
              </div>
              <div className="text-center">
                <p className="text-xs text-frost-muted mb-1">Furnace</p>
                <p className="font-medium text-frost">{getFurnaceDisplay(activeProfile)}</p>
              </div>
            </div>
          </div>
        )}

        {/* Profiles List */}
        <div className="mb-6">
          <h2 className="section-header mb-4">Your Profiles</h2>
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
            <div className="space-y-3">
              <p className="text-sm text-frost-muted">
                You have {profiles.length} profile(s).
              </p>
              {profiles.map((profile) => (
                <div key={profile.id}>
                  <div
                    className={`card ${
                      profile.is_active ? 'border-2 border-ice bg-ice/5' : ''
                    }`}
                  >
                    <div className="flex flex-col md:flex-row md:items-center gap-4">
                      {/* Profile Info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          {profile.is_active && <span className="text-ice">✓</span>}
                          <h3 className="font-medium text-frost truncate">
                            {profile.name || `Profile ${profile.id}`}
                          </h3>
                          {profile.is_farm_account && (
                            <span className="badge-warning text-xs">🌾 Farm</span>
                          )}
                        </div>
                        <p className="text-sm text-frost-muted">
                          State {profile.state_number || 'N/A'} | {getFurnaceDisplay(profile)} | {profile.hero_count} heroes
                        </p>
                      </div>

                      {/* Actions */}
                      <div className="flex flex-wrap items-center gap-2">
                        {!profile.is_active && (
                          <button
                            onClick={() => handleLoadProfile(profile.id)}
                            className="btn-primary text-sm"
                          >
                            Switch
                          </button>
                        )}
                        {profile.is_active && (
                          <span className="text-xs text-frost-muted px-2">(current)</span>
                        )}
                        <button
                          onClick={() => handlePreview(profile.id)}
                          className="btn-secondary text-sm"
                        >
                          {previewId === profile.id ? 'Hide' : 'Preview'}
                        </button>
                        <button
                          onClick={() => handleToggleFarm(profile)}
                          className={`px-3 py-1.5 text-sm rounded transition-colors ${
                            profile.is_farm_account
                              ? 'bg-warning/20 text-warning hover:bg-warning/30'
                              : 'bg-surface text-frost-muted hover:text-frost hover:bg-surface-hover'
                          }`}
                        >
                          {profile.is_farm_account ? '🌾 Farm' : 'Mark Farm'}
                        </button>
                        <button
                          onClick={() => {
                            setEditingId(profile.id);
                            setDuplicatingId(null);
                            setConfirmDeleteId(null);
                          }}
                          className="btn-ghost text-sm"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => {
                            setDuplicatingId(profile.id);
                            setEditingId(null);
                            setConfirmDeleteId(null);
                          }}
                          className="btn-ghost text-sm"
                        >
                          Duplicate
                        </button>
                        <button
                          onClick={() => {
                            setConfirmDeleteId(profile.id);
                            setEditingId(null);
                            setDuplicatingId(null);
                          }}
                          className="px-2 py-1.5 text-sm text-error hover:bg-error/10 rounded transition-colors"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>

                    {/* Edit Form */}
                    {editingId === profile.id && (
                      <EditProfileForm
                        profile={profile}
                        token={token || ''}
                        onClose={() => setEditingId(null)}
                        onSaved={() => {
                          setEditingId(null);
                          fetchProfiles();
                        }}
                      />
                    )}

                    {/* Duplicate Form */}
                    {duplicatingId === profile.id && (
                      <DuplicateProfileForm
                        profile={profile}
                        token={token || ''}
                        onClose={() => setDuplicatingId(null)}
                        onDuplicated={() => {
                          setDuplicatingId(null);
                          fetchProfiles();
                        }}
                      />
                    )}

                    {/* Delete Confirmation */}
                    {confirmDeleteId === profile.id && (
                      <div className="mt-4 pt-4 border-t border-surface-border">
                        {profile.is_active ? (
                          <div className="flex items-center justify-between">
                            <p className="text-sm text-warning">
                              Cannot delete your current profile. Switch to another profile first.
                            </p>
                            <button
                              onClick={() => setConfirmDeleteId(null)}
                              className="btn-secondary text-sm"
                            >
                              OK
                            </button>
                          </div>
                        ) : (
                          <div className="flex items-center justify-between">
                            <p className="text-sm text-frost">
                              Delete <strong>{profile.name}</strong>? You can restore it within 30 days.
                            </p>
                            <div className="flex gap-2">
                              <button
                                onClick={() => setConfirmDeleteId(null)}
                                className="btn-secondary text-sm"
                              >
                                Cancel
                              </button>
                              <button
                                onClick={() => handleDeleteProfile(profile.id)}
                                className="btn-danger text-sm"
                              >
                                Delete
                              </button>
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Preview Panel */}
                    {previewId === profile.id && previewData && (
                      <div className="mt-4 pt-4 border-t border-surface-border">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <h4 className="text-sm font-medium text-frost mb-2">Profile Settings</h4>
                            <ul className="text-sm text-frost-muted space-y-1">
                              <li>Name: {previewData.name || 'N/A'}</li>
                              <li>State: {previewData.state_number || 'N/A'}</li>
                              <li>Server Age: Day {previewData.server_age_days}</li>
                              <li>Furnace: {previewData.furnace_fc_level || `Lv.${previewData.furnace_level}`}</li>
                              <li>Farm Account: {previewData.is_farm_account ? 'Yes' : 'No'}</li>
                              <li>Spending: {spendingLabels[previewData.spending_profile] || previewData.spending_profile}</li>
                              <li>Alliance Role: {previewData.alliance_role}</li>
                            </ul>
                          </div>
                          <div>
                            <h4 className="text-sm font-medium text-frost mb-2">Heroes ({previewData.heroes.length})</h4>
                            {previewData.heroes.length === 0 ? (
                              <p className="text-sm text-frost-muted italic">No heroes saved</p>
                            ) : (
                              <ul className="text-sm text-frost-muted space-y-1">
                                {previewData.heroes.slice(0, 5).map((hero, i) => (
                                  <li key={i}>
                                    {hero.name} (Lv.{hero.level}, ★{hero.stars})
                                  </li>
                                ))}
                                {previewData.heroes.length > 5 && (
                                  <li className="italic">...and {previewData.heroes.length - 5} more</li>
                                )}
                              </ul>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Farm Linking Section (only if active profile is a farm) */}
        {activeProfile?.is_farm_account && mainProfiles.length > 0 && (
          <div className="card mb-6">
            <h2 className="section-header mb-4">🔗 Link Farm to Main Account</h2>
            <p className="text-sm text-frost-muted mb-3">
              Link this farm to your main account for coordinated recommendations
            </p>
            <FarmLinkingSelect
              profile={activeProfile}
              mainProfiles={mainProfiles}
              token={token || ''}
              onLinked={fetchProfiles}
            />
          </div>
        )}

        {/* Recently Deleted Section */}
        {deletedProfiles.length > 0 && (
          <div className="card mb-6">
            <h2 className="section-header mb-4">🗑️ Recently Deleted</h2>
            <p className="text-sm text-frost-muted mb-3">
              Deleted profiles can be restored within 30 days.
            </p>
            <div className="space-y-2">
              {deletedProfiles.map((profile) => {
                const daysLeft = getDaysRemaining(profile.deleted_at!);
                return (
                  <div
                    key={profile.id}
                    className="flex items-center justify-between p-3 bg-surface rounded-lg"
                  >
                    <div>
                      <p className="text-frost line-through">{profile.name || `Profile ${profile.id}`}</p>
                      <p className="text-xs text-frost-muted">
                        {daysLeft > 0 ? (
                          <span>⏱️ {daysLeft} days left to restore</span>
                        ) : (
                          <span className="text-warning">⚠️ Will be permanently deleted soon</span>
                        )}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleRestoreProfile(profile.id)}
                        className="btn-secondary text-sm"
                      >
                        Restore
                      </button>
                      <button
                        onClick={() => setConfirmPermDeleteId(profile.id)}
                        className="px-3 py-1.5 text-sm text-error hover:bg-error/10 rounded transition-colors"
                      >
                        Delete Now
                      </button>
                    </div>
                    {confirmPermDeleteId === profile.id && (
                      <div className="absolute inset-0 bg-black/50 flex items-center justify-center rounded-lg">
                        <div className="bg-surface p-4 rounded-lg max-w-xs">
                          <p className="text-sm text-frost mb-3">
                            Permanently delete <strong>{profile.name}</strong>? This cannot be undone.
                          </p>
                          <div className="flex gap-2 justify-end">
                            <button
                              onClick={() => setConfirmPermDeleteId(null)}
                              className="btn-secondary text-sm"
                            >
                              Cancel
                            </button>
                            <button
                              onClick={() => handlePermanentDelete(profile.id)}
                              className="btn-danger text-sm"
                            >
                              Delete Forever
                            </button>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Info Card */}
        <div className="card">
          <h2 className="section-header">About Profiles</h2>
          <ul className="space-y-2 text-sm text-frost-muted">
            <li className="flex items-start gap-2">
              <span className="text-ice">•</span>
              <span>Each profile tracks a separate game account (main or farm)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-ice">•</span>
              <span>Mark farm accounts for specialized recommendations focused on resources</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-ice">•</span>
              <span>Link farm accounts to your main for coordinated recommendations</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-ice">•</span>
              <span>Deleted profiles can be restored within 30 days</span>
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

function EditProfileForm({
  profile,
  token,
  onClose,
  onSaved,
}: {
  profile: Profile;
  token: string;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [name, setName] = useState(profile.name || '');
  const [stateNumber, setStateNumber] = useState(profile.state_number?.toString() || '');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const res = await fetch(`http://localhost:8000/api/profiles/${profile.id}`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: name || null,
          state_number: stateNumber ? parseInt(stateNumber) : null,
        }),
      });

      if (res.ok) {
        onSaved();
      }
    } catch (error) {
      console.error('Failed to update profile:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mt-4 pt-4 border-t border-surface-border">
      <div className="flex flex-wrap items-end gap-3">
        <div className="flex-1 min-w-[150px]">
          <label className="block text-xs text-frost-muted mb-1">Profile Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="input text-sm"
            placeholder="Profile name"
          />
        </div>
        <div className="w-24">
          <label className="block text-xs text-frost-muted mb-1">State #</label>
          <input
            type="number"
            value={stateNumber}
            onChange={(e) => setStateNumber(e.target.value)}
            className="input text-sm"
            placeholder="123"
            min="1"
            max="9999"
          />
        </div>
        <button type="submit" disabled={isLoading} className="btn-primary text-sm">
          {isLoading ? 'Saving...' : 'Save'}
        </button>
        <button type="button" onClick={onClose} className="btn-secondary text-sm">
          Cancel
        </button>
      </div>
    </form>
  );
}

function DuplicateProfileForm({
  profile,
  token,
  onClose,
  onDuplicated,
}: {
  profile: Profile;
  token: string;
  onClose: () => void;
  onDuplicated: () => void;
}) {
  const [name, setName] = useState(`${profile.name || 'Profile'}_copy`);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Please enter a name');
      return;
    }
    setIsLoading(true);
    setError('');

    try {
      const res = await fetch(`http://localhost:8000/api/profiles/${profile.id}/duplicate`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: name.trim() }),
      });

      if (res.ok) {
        onDuplicated();
      } else {
        const data = await res.json();
        setError(data.detail || 'Failed to duplicate');
      }
    } catch (error) {
      console.error('Failed to duplicate profile:', error);
      setError('Failed to duplicate profile');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mt-4 pt-4 border-t border-surface-border">
      {error && (
        <p className="text-sm text-error mb-2">{error}</p>
      )}
      <div className="flex flex-wrap items-end gap-3">
        <div className="flex-1 min-w-[200px]">
          <label className="block text-xs text-frost-muted mb-1">New Profile Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="input text-sm"
            placeholder="Name for the copy"
          />
        </div>
        <button type="submit" disabled={isLoading} className="btn-primary text-sm">
          {isLoading ? 'Duplicating...' : 'Duplicate'}
        </button>
        <button type="button" onClick={onClose} className="btn-secondary text-sm">
          Cancel
        </button>
      </div>
    </form>
  );
}

function FarmLinkingSelect({
  profile,
  mainProfiles,
  token,
  onLinked,
}: {
  profile: Profile;
  mainProfiles: Profile[];
  token: string;
  onLinked: () => void;
}) {
  const [selectedId, setSelectedId] = useState<number | ''>(
    profile.linked_main_profile_id || ''
  );
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = async (newValue: number | '') => {
    setSelectedId(newValue);
    setIsLoading(true);

    try {
      await fetch(`http://localhost:8000/api/profiles/${profile.id}`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          linked_main_profile_id: newValue || null,
        }),
      });
      onLinked();
    } catch (error) {
      console.error('Failed to link profile:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <select
      value={selectedId}
      onChange={(e) => handleChange(e.target.value ? parseInt(e.target.value) : '')}
      disabled={isLoading}
      className="input"
    >
      <option value="">-- Not linked --</option>
      {mainProfiles.map((p) => (
        <option key={p.id} value={p.id}>
          {p.name || `Profile ${p.id}`} (State {p.state_number || '?'})
        </option>
      ))}
    </select>
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
