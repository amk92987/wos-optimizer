'use client';

import React, { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import Expander from '@/components/Expander';
import { useAuth } from '@/lib/auth';
import { profileApi, Profile } from '@/lib/api';

const GEN_SERVER_DAYS: Record<number, { min: number; max: number | null }> = {
  1:  { min: 0,    max: 40 },
  2:  { min: 40,   max: 120 },
  3:  { min: 120,  max: 200 },
  4:  { min: 200,  max: 280 },
  5:  { min: 280,  max: 360 },
  6:  { min: 360,  max: 440 },
  7:  { min: 440,  max: 520 },
  8:  { min: 520,  max: 600 },
  9:  { min: 600,  max: 680 },
  10: { min: 680,  max: 760 },
  11: { min: 760,  max: 840 },
  12: { min: 840,  max: 920 },
  13: { min: 920,  max: 1000 },
  14: { min: 1000, max: null },
};

function estimateGenFromDays(days: number): number {
  for (let gen = 14; gen >= 1; gen--) {
    if (days >= GEN_SERVER_DAYS[gen].min) return gen;
  }
  return 1;
}

export default function SettingsPage() {
  const { token, user } = useAuth();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [currentGen, setCurrentGen] = useState(1);

  useEffect(() => {
    if (token) {
      profileApi.getCurrent(token)
        .then((data: any) => {
          const p = data.profile || data;
          setProfile(p);
          setCurrentGen(estimateGenFromDays(p.server_age_days));
        })
        .catch(console.error)
        .finally(() => setIsLoading(false));
    }
  }, [token]);

  const handleSave = async (data: Partial<Profile>) => {
    if (!token || !profile?.profile_id) return;
    setIsSaving(true);

    try {
      const result: any = await profileApi.update(token, profile.profile_id, data);
      const updated = result.profile || result;
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
                Gen {currentGen} · {profile?.furnace_fc_level || `Lv.${profile?.furnace_level}`}
              </p>
            </div>
          }
          defaultOpen={true}
          className="mb-4"
        >
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-zinc-400 block mb-2">Current Hero Generation</label>
              <select
                value={currentGen}
                onChange={(e) => {
                  const gen = parseInt(e.target.value);
                  setCurrentGen(gen);
                  const range = GEN_SERVER_DAYS[gen];
                  if (range) {
                    // Save midpoint as server age estimate
                    const midpoint = range.max ? Math.round((range.min + range.max) / 2) : range.min;
                    handleSave({ server_age_days: midpoint });
                  }
                }}
                className="select"
              >
                {Object.entries(GEN_SERVER_DAYS).map(([gen, range]) => (
                  <option key={gen} value={gen}>
                    Gen {gen} ({range.max ? `${range.min}-${range.max}` : `${range.min}+`} days)
                  </option>
                ))}
              </select>
              <p className="text-xs text-frost-muted mt-1">
                Estimated server age: {(() => {
                  const range = GEN_SERVER_DAYS[currentGen];
                  if (!range) return '?';
                  return range.max ? `${range.min}-${range.max} days` : `${range.min}+ days`;
                })()}
              </p>
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
                  if (val.startsWith('FC') || val.startsWith('30-')) {
                    handleSave({ furnace_level: 30, furnace_fc_level: val });
                  } else {
                    handleSave({ furnace_level: parseInt(val), furnace_fc_level: null });
                  }
                }}
                className="select"
              >
                <optgroup label="Pre-FC Levels">
                  {Array.from({ length: 29 }, (_, i) => i + 1).map((lvl) => (
                    <option key={lvl} value={String(lvl)}>Level {lvl}</option>
                  ))}
                </optgroup>
                <optgroup label="Level 30 (Pre-FC)">
                  <option value="30">Level 30</option>
                  <option value="30-1">Level 30-1</option>
                  <option value="30-2">Level 30-2</option>
                  <option value="30-3">Level 30-3</option>
                </optgroup>
                <optgroup label="FC Levels">
                  {Array.from({ length: 10 }, (_, i) => i + 1).map((fc) => (
                    <React.Fragment key={`fc-group-${fc}`}>
                      <option value={`FC${fc}`}>FC{fc}</option>
                      {fc < 10 && (
                        <>
                          <option value={`FC${fc}-1`}>FC{fc}-1</option>
                          <option value={`FC${fc}-2`}>FC{fc}-2</option>
                          <option value={`FC${fc}-3`}>FC{fc}-3</option>
                        </>
                      )}
                    </React.Fragment>
                  ))}
                </optgroup>
              </select>
              <p className="text-xs text-frost-muted mt-1">
                Levels 30 and FC have sub-steps (30-1, 30-2, 30-3, then FC1, FC1-1, etc.)
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
