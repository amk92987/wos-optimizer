'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import Expander from '@/components/Expander';
import { useAuth } from '@/lib/auth';
import { profileApi, Profile } from '@/lib/api';

export default function SettingsPage() {
  const { token, user } = useAuth();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (token) {
      profileApi.getCurrent(token)
        .then(setProfile)
        .catch(console.error)
        .finally(() => setIsLoading(false));
    }
  }, [token]);

  const handleSave = async (data: Partial<Profile>) => {
    if (!token) return;
    setIsSaving(true);

    try {
      const updated = await profileApi.update(token, data);
      setProfile(updated);
    } catch (error) {
      console.error('Failed to save:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const spendingOptions = [
    { value: 'f2p', label: 'Free to Play', description: '$0/month' },
    { value: 'minnow', label: 'Minnow', description: '$5-30/month' },
    { value: 'dolphin', label: 'Dolphin', description: '$30-100/month' },
    { value: 'orca', label: 'Orca', description: '$100-500/month' },
    { value: 'whale', label: 'Whale', description: '$500+/month' },
  ];

  const focusOptions = [
    { value: 'svs_combat', label: 'SvS Combat', description: 'Maximize combat power' },
    { value: 'balanced_growth', label: 'Balanced Growth', description: 'Steady progression' },
    { value: 'economy_focus', label: 'Economy Focus', description: 'Resource generation' },
  ];

  const roleOptions = [
    { value: 'rally_lead', label: 'Rally Lead', description: 'Lead attacks' },
    { value: 'filler', label: 'Rally Filler', description: 'Join rallies' },
    { value: 'farmer', label: 'Farmer', description: 'Resource gathering' },
    { value: 'casual', label: 'Casual', description: 'Relaxed play' },
  ];

  if (isLoading) {
    return (
      <PageLayout>
        <div className="max-w-3xl mx-auto">
          <div className="h-8 bg-surface rounded w-48 mb-8 animate-pulse"></div>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="card animate-pulse">
                <div className="h-6 bg-surface-hover rounded w-32 mb-4"></div>
                <div className="h-10 bg-surface-hover rounded"></div>
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
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-zinc-100">Settings</h1>
          <p className="text-zinc-400 mt-2">Configure your profile and priorities</p>
        </div>

        {/* Account Info */}
        <div className="card mb-6">
          <h2 className="text-lg font-semibold text-zinc-100 mb-4">Account</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-zinc-500">Email</label>
              <p className="font-medium text-zinc-100">{user?.email}</p>
            </div>
            <div>
              <label className="text-sm text-zinc-500">Role</label>
              <p className="font-medium text-zinc-100 capitalize">{user?.role}</p>
            </div>
          </div>
        </div>

        {/* Server & Progression */}
        <Expander
          title={
            <div>
              <h2 className="text-lg font-semibold text-zinc-100">Server & Progression</h2>
              <p className="text-sm text-zinc-500">
                Day {profile?.server_age_days} · {profile?.furnace_fc_level || `Lv.${profile?.furnace_level}`}
              </p>
            </div>
          }
          defaultOpen={true}
          className="mb-4"
        >
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-zinc-400 block mb-2">Server Age (Days)</label>
              <input
                type="number"
                value={profile?.server_age_days || 0}
                onChange={(e) => handleSave({ server_age_days: parseInt(e.target.value) || 0 })}
                className="input"
                min={0}
                max={2000}
              />
            </div>
            <div>
              <label className="text-sm text-zinc-400 block mb-2">State Number</label>
              <input
                type="number"
                value={profile?.state_number || ''}
                onChange={(e) => handleSave({ state_number: parseInt(e.target.value) || null })}
                className="input"
                placeholder="e.g. 456"
              />
            </div>
            <div className="md:col-span-2">
              <label className="text-sm text-zinc-400 block mb-2">Furnace Level</label>
              <select
                value={profile?.furnace_fc_level || (profile?.furnace_level ? `${profile.furnace_level}` : '1')}
                onChange={(e) => {
                  const val = e.target.value;
                  if (val.startsWith('FC')) {
                    handleSave({ furnace_level: 30, furnace_fc_level: val });
                  } else {
                    handleSave({ furnace_level: parseInt(val), furnace_fc_level: null });
                  }
                }}
                className="select"
              >
                <optgroup label="Pre-FC Levels">
                  {Array.from({ length: 29 }, (_, i) => i + 1).map((lvl) => (
                    <option key={lvl} value={lvl}>Level {lvl}</option>
                  ))}
                </optgroup>
                <optgroup label="FC Levels">
                  <option value="30">Level 30 (Pre-FC)</option>
                  {Array.from({ length: 10 }, (_, i) => i + 1).map((fc) => (
                    <>
                      <option key={`FC${fc}`} value={`FC${fc}`}>FC{fc}</option>
                      {fc < 10 && (
                        <>
                          <option key={`FC${fc}-1`} value={`FC${fc}-1`}>FC{fc}-1</option>
                          <option key={`FC${fc}-2`} value={`FC${fc}-2`}>FC{fc}-2</option>
                          <option key={`FC${fc}-3`} value={`FC${fc}-3`}>FC{fc}-3</option>
                        </>
                      )}
                    </>
                  ))}
                </optgroup>
              </select>
              <p className="text-xs text-frost-muted mt-1">
                FC levels have sub-steps (FC1-1, FC1-2, FC1-3) before reaching the next level
              </p>
            </div>
          </div>
        </Expander>

        {/* Playstyle */}
        <Expander
          title={
            <div>
              <h2 className="text-lg font-semibold text-zinc-100">Playstyle</h2>
              <p className="text-sm text-zinc-500">
                {spendingOptions.find(o => o.value === profile?.spending_profile)?.label} · {roleOptions.find(o => o.value === profile?.alliance_role)?.label}
              </p>
            </div>
          }
          defaultOpen={true}
          className="mb-4"
        >
          <div className="space-y-6">
            {/* Spending Profile */}
            <div>
              <label className="text-sm text-zinc-400 block mb-3">Spending Profile</label>
              <div className="grid grid-cols-5 gap-2">
                {spendingOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => handleSave({ spending_profile: option.value })}
                    className={`p-3 rounded-lg text-center transition-all ${
                      profile?.spending_profile === option.value
                        ? 'bg-amber/20 border-2 border-amber text-amber'
                        : 'bg-surface border border-border text-zinc-400 hover:text-zinc-100 hover:border-zinc-600'
                    }`}
                  >
                    <p className="font-medium text-sm">{option.label}</p>
                    <p className="text-xs opacity-70 mt-1">{option.description}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Focus */}
            <div>
              <label className="text-sm text-zinc-400 block mb-3">Priority Focus</label>
              <div className="grid grid-cols-3 gap-2">
                {focusOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => handleSave({ priority_focus: option.value })}
                    className={`p-3 rounded-lg text-center transition-all ${
                      profile?.priority_focus === option.value
                        ? 'bg-blue-500/20 border-2 border-blue-500 text-blue-400'
                        : 'bg-surface border border-border text-zinc-400 hover:text-zinc-100 hover:border-zinc-600'
                    }`}
                  >
                    <p className="font-medium text-sm">{option.label}</p>
                    <p className="text-xs opacity-70 mt-1">{option.description}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Alliance Role */}
            <div>
              <label className="text-sm text-zinc-400 block mb-3">Alliance Role</label>
              <div className="grid grid-cols-4 gap-2">
                {roleOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => handleSave({ alliance_role: option.value })}
                    className={`p-3 rounded-lg text-center transition-all ${
                      profile?.alliance_role === option.value
                        ? 'bg-green-500/20 border-2 border-green-500 text-green-400'
                        : 'bg-surface border border-border text-zinc-400 hover:text-zinc-100 hover:border-zinc-600'
                    }`}
                  >
                    <p className="font-medium text-sm">{option.label}</p>
                    <p className="text-xs opacity-70 mt-1">{option.description}</p>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </Expander>

        {/* Combat Priorities */}
        <Expander
          title={
            <div>
              <h2 className="text-lg font-semibold text-zinc-100">Combat Priorities</h2>
              <p className="text-sm text-zinc-500">Higher values = more weight in recommendations</p>
            </div>
          }
          className="mb-4"
        >
          <div className="space-y-4">
            {[
              { key: 'priority_svs', label: 'SvS / State vs State' },
              { key: 'priority_rally', label: 'Rally Attacks' },
              { key: 'priority_castle_battle', label: 'Castle Battles' },
              { key: 'priority_exploration', label: 'Exploration / PvE' },
              { key: 'priority_gathering', label: 'Resource Gathering' },
            ].map((item) => (
              <div key={item.key} className="flex items-center gap-4">
                <label className="text-sm text-zinc-300 w-48">{item.label}</label>
                <input
                  type="range"
                  min={1}
                  max={5}
                  value={(profile as any)?.[item.key] || 3}
                  onChange={(e) => handleSave({ [item.key]: parseInt(e.target.value) })}
                  className="flex-1 accent-amber"
                />
                <span className="text-amber font-bold w-8 text-center">
                  {(profile as any)?.[item.key] || 3}
                </span>
              </div>
            ))}
          </div>
        </Expander>

        {/* Saving indicator */}
        {isSaving && (
          <div className="fixed bottom-4 right-4 bg-surface border border-border px-4 py-2 rounded-lg shadow-lg">
            <span className="text-sm text-zinc-400">Saving...</span>
          </div>
        )}
      </div>
    </PageLayout>
  );
}
