'use client';

import React, { Suspense, useEffect, useState, useRef } from 'react';
import { useSearchParams } from 'next/navigation';
import PageLayout from '@/components/PageLayout';
import Expander from '@/components/Expander';
import { useAuth } from '@/lib/auth';
import { api, profileApi, heroesApi, Profile } from '@/lib/api';

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

const MILESTONE_UNLOCKS = [
  { furnace: 9, label: 'F9 Research' },
  { furnace: 18, label: 'F18 Pets' },
  { furnace: 19, label: 'F19 Daybreak' },
  { furnace: 25, label: 'F25 Charms' },
  { furnace: 30, label: 'F30 FC' },
];

function estimateGenFromDays(days: number): number {
  for (let gen = 14; gen >= 1; gen--) {
    if (days >= GEN_SERVER_DAYS[gen].min) return gen;
  }
  return 1;
}

function getGamePhase(furnaceLevel: number, fcLevel: string | null): {
  id: string; name: string; focus: string; color: string;
} {
  if (furnaceLevel < 19) {
    return { id: 'early_game', name: 'Early Game', focus: 'Rush to F19 for Daybreak Island', color: 'blue' };
  }
  if (furnaceLevel < 30) {
    return { id: 'mid_game', name: 'Mid Game', focus: 'Rush to F30 for FC', color: 'green' };
  }
  // FC5+ = endgame
  if (fcLevel) {
    const match = fcLevel.match(/^FC(\d+)/);
    if (match && parseInt(match[1]) >= 5) {
      return { id: 'endgame', name: 'Endgame', focus: 'FC10 completion', color: 'purple' };
    }
  }
  return { id: 'late_game', name: 'Late Game', focus: 'FC progression', color: 'orange' };
}

function getEffectiveFurnaceLevel(profile: Profile): number {
  if (profile.furnace_fc_level) {
    return 30;
  }
  return profile.furnace_level;
}

function getDaysUntilNextGen(serverAgeDays: number): { daysLeft: number; nextGen: number } | null {
  const currentGen = estimateGenFromDays(serverAgeDays);
  if (currentGen >= 14) return null;
  const nextGen = currentGen + 1;
  const nextMin = GEN_SERVER_DAYS[nextGen].min;
  return { daysLeft: nextMin - serverAgeDays, nextGen };
}

const PHASE_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  blue:   { bg: 'bg-blue-500/15',   border: 'border-blue-500/40',   text: 'text-blue-400' },
  green:  { bg: 'bg-green-500/15',  border: 'border-green-500/40',  text: 'text-green-400' },
  orange: { bg: 'bg-amber-500/15',  border: 'border-amber-500/40',  text: 'text-amber-400' },
  purple: { bg: 'bg-purple-500/15', border: 'border-purple-500/40', text: 'text-purple-400' },
};

function SettingsContent() {
  const { token, user } = useAuth();
  const searchParams = useSearchParams();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [currentGen, setCurrentGen] = useState(1);
  const [useManualDays, setUseManualDays] = useState(false);
  const [manualDays, setManualDays] = useState<number | null>(null);
  const [confirmClearHeroes, setConfirmClearHeroes] = useState(false);
  const [clearingHeroes, setClearingHeroes] = useState(false);
  const [resetMessage, setResetMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Security section state
  const securityRef = useRef<HTMLDivElement>(null);
  const tabParam = searchParams.get('tab');
  const [securityOpen, setSecurityOpen] = useState(tabParam === 'password' || tabParam === 'email');

  // Password change
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState('');
  const [passwordLoading, setPasswordLoading] = useState(false);

  // Email change
  const [newEmail, setNewEmail] = useState('');
  const [emailPassword, setEmailPassword] = useState('');
  const [emailError, setEmailError] = useState('');
  const [emailSuccess, setEmailSuccess] = useState('');
  const [emailLoading, setEmailLoading] = useState(false);

  // Auto-scroll to security section when tab param present
  useEffect(() => {
    if ((tabParam === 'password' || tabParam === 'email') && securityRef.current) {
      setSecurityOpen(true);
      setTimeout(() => {
        securityRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    }
  }, [tabParam]);

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError('');
    setPasswordSuccess('');

    if (newPassword.length < 8) {
      setPasswordError('New password must be at least 8 characters.');
      return;
    }

    if (newPassword !== confirmNewPassword) {
      setPasswordError('New passwords do not match.');
      return;
    }

    setPasswordLoading(true);
    try {
      await api('/api/auth/change-password', {
        method: 'PUT',
        body: { current_password: currentPassword, new_password: newPassword },
        token: token || undefined,
      });
      setPasswordSuccess('Password changed successfully.');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmNewPassword('');
    } catch (err: any) {
      setPasswordError(err.message || 'Failed to change password.');
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleEmailChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setEmailError('');
    setEmailSuccess('');

    if (!newEmail) {
      setEmailError('Please enter a new email address.');
      return;
    }

    setEmailLoading(true);
    try {
      await api('/api/auth/change-email', {
        method: 'POST',
        body: { new_email: newEmail, password: emailPassword },
        token: token || undefined,
      });
      setEmailSuccess('Verification email sent to your new address. Please check your inbox to confirm the change.');
      setNewEmail('');
      setEmailPassword('');
    } catch (err: any) {
      setEmailError(err.message || 'Failed to initiate email change.');
    } finally {
      setEmailLoading(false);
    }
  };

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

  const effectiveFurnace = profile ? getEffectiveFurnaceLevel(profile) : 1;
  const phase = profile ? getGamePhase(profile.furnace_level, profile.furnace_fc_level) : null;
  const phaseStyle = phase ? PHASE_COLORS[phase.color] : null;
  const serverDays = useManualDays && manualDays !== null ? manualDays : profile?.server_age_days || 0;
  const nextGenInfo = getDaysUntilNextGen(serverDays);
  const furnaceDisplay = profile?.furnace_fc_level || `Lv.${profile?.furnace_level || 1}`;
  const stateDisplay = profile?.state_number ? `State ${profile.state_number}` : 'State N/A';
  const chiefName = profile?.name || 'Chief';

  return (
    <PageLayout>
      <div className="max-w-3xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-zinc-100">Settings</h1>
          <p className="text-zinc-400 mt-2">Configure your profile and priorities</p>
        </div>

        {/* Feature 6: Profile Summary Banner */}
        {profile && (
          <div className="mb-6 p-3 rounded-lg bg-frost/10 border border-frost/20 flex items-center gap-3 text-sm">
            <span className="text-frost font-semibold">{chiefName}</span>
            <span className="text-zinc-500">|</span>
            <span className="text-zinc-300">{stateDisplay}</span>
            <span className="text-zinc-500">|</span>
            <span className="text-zinc-300">{furnaceDisplay}</span>
            <span className="text-zinc-500">|</span>
            <span className="text-zinc-300">Day {serverDays}</span>
          </div>
        )}

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
                  if (!useManualDays) {
                    const range = GEN_SERVER_DAYS[gen];
                    if (range) {
                      const midpoint = range.max ? Math.round((range.min + range.max) / 2) : range.min;
                      handleSave({ server_age_days: midpoint });
                    }
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

              {/* Feature 4: Manual Day Count Override */}
              <label className="flex items-center gap-2 mt-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={useManualDays}
                  onChange={(e) => {
                    setUseManualDays(e.target.checked);
                    if (!e.target.checked && profile) {
                      // Revert to generation midpoint estimate
                      const range = GEN_SERVER_DAYS[currentGen];
                      if (range) {
                        const midpoint = range.max ? Math.round((range.min + range.max) / 2) : range.min;
                        setManualDays(null);
                        handleSave({ server_age_days: midpoint });
                      }
                    } else if (e.target.checked && profile) {
                      setManualDays(profile.server_age_days);
                    }
                  }}
                  className="rounded border-zinc-600 bg-surface text-frost focus:ring-frost/50"
                />
                <span className="text-xs text-zinc-400">Enter exact day count</span>
              </label>
              {useManualDays && (
                <div className="mt-2">
                  <input
                    type="number"
                    min={0}
                    max={2000}
                    value={manualDays ?? profile?.server_age_days ?? 0}
                    onChange={(e) => {
                      const days = parseInt(e.target.value) || 0;
                      setManualDays(days);
                      setCurrentGen(estimateGenFromDays(days));
                      handleSave({ server_age_days: days });
                    }}
                    className="input"
                    placeholder="Days since server started"
                  />
                  <p className="text-xs text-frost-muted mt-1">Precise server age in days</p>
                </div>
              )}

              {/* Feature 3: Days Until Next Generation */}
              {nextGenInfo ? (
                <p className="text-xs text-amber mt-2">
                  {nextGenInfo.daysLeft} days until Gen {nextGenInfo.nextGen}
                </p>
              ) : (
                <p className="text-xs text-purple-400 mt-2">
                  Latest generation reached
                </p>
              )}
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

              {/* Feature 1: Game Phase Indicator */}
              {phase && phaseStyle && (
                <div className={`mt-3 px-3 py-2 rounded-lg border-l-4 ${phaseStyle.bg} ${phaseStyle.border}`}>
                  <span className={`font-semibold text-sm ${phaseStyle.text}`}>{phase.name}</span>
                  <span className="text-xs text-zinc-400 ml-2">{phase.focus}</span>
                </div>
              )}

              {/* Feature 2: Key Milestone Unlocks */}
              <div className="mt-2 flex flex-wrap gap-1.5">
                {MILESTONE_UNLOCKS.map((m) => {
                  const unlocked = effectiveFurnace >= m.furnace;
                  return (
                    <span
                      key={m.furnace}
                      className={`text-xs px-2 py-0.5 rounded-full border ${
                        unlocked
                          ? 'bg-green-500/15 border-green-500/30 text-green-400'
                          : 'bg-zinc-800/50 border-zinc-700/50 text-zinc-500'
                      }`}
                    >
                      {unlocked ? '\u2713' : '\u2022'} {m.label}
                    </span>
                  );
                })}
              </div>
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
          defaultOpen={true}
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

        {/* Security */}
        <div ref={securityRef}>
          <Expander
            title={
              <div>
                <h2 className="text-lg font-semibold text-zinc-100">Security</h2>
                <p className="text-sm text-zinc-500">Change password or email</p>
              </div>
            }
            defaultOpen={securityOpen}
            className="mb-4"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Password Change */}
              <div>
                <h3 className="text-base font-medium text-zinc-200 mb-4">Change Password</h3>

                {passwordSuccess && (
                  <div className="mb-4 p-3 rounded-lg bg-green-500/20 border border-green-500/30 text-green-400 text-sm">
                    {passwordSuccess}
                  </div>
                )}
                {passwordError && (
                  <div className="mb-4 p-3 rounded-lg bg-error/20 border border-error/30 text-error text-sm">
                    {passwordError}
                  </div>
                )}

                <form onSubmit={handlePasswordChange} className="space-y-3">
                  <div>
                    <label className="text-sm text-zinc-400 block mb-1">Current Password</label>
                    <input
                      type="password"
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                      className="input"
                      placeholder="Enter current password"
                      required
                      autoComplete="current-password"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-zinc-400 block mb-1">New Password</label>
                    <input
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      className="input"
                      placeholder="At least 8 characters"
                      required
                      minLength={8}
                      autoComplete="new-password"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-zinc-400 block mb-1">Confirm New Password</label>
                    <input
                      type="password"
                      value={confirmNewPassword}
                      onChange={(e) => setConfirmNewPassword(e.target.value)}
                      className="input"
                      placeholder="Re-enter new password"
                      required
                      minLength={8}
                      autoComplete="new-password"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={passwordLoading}
                    className="btn-primary py-2 px-4"
                  >
                    {passwordLoading ? 'Changing...' : 'Change Password'}
                  </button>
                </form>
              </div>

              {/* Email Change */}
              <div>
                <h3 className="text-base font-medium text-zinc-200 mb-4">Change Email</h3>

                {emailSuccess && (
                  <div className="mb-4 p-3 rounded-lg bg-green-500/20 border border-green-500/30 text-green-400 text-sm">
                    {emailSuccess}
                  </div>
                )}
                {emailError && (
                  <div className="mb-4 p-3 rounded-lg bg-error/20 border border-error/30 text-error text-sm">
                    {emailError}
                  </div>
                )}

                <form onSubmit={handleEmailChange} className="space-y-3">
                  <div>
                    <label className="text-sm text-zinc-400 block mb-1">New Email Address</label>
                    <input
                      type="email"
                      value={newEmail}
                      onChange={(e) => setNewEmail(e.target.value)}
                      className="input"
                      placeholder="new@email.com"
                      required
                      autoComplete="email"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-zinc-400 block mb-1">Current Password</label>
                    <input
                      type="password"
                      value={emailPassword}
                      onChange={(e) => setEmailPassword(e.target.value)}
                      className="input"
                      placeholder="Confirm with your password"
                      required
                      autoComplete="current-password"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={emailLoading}
                    className="btn-primary py-2 px-4"
                  >
                    {emailLoading ? 'Sending...' : 'Change Email'}
                  </button>
                  <p className="text-xs text-zinc-500 mt-1">
                    A verification email will be sent to your new address. The change takes effect after you confirm.
                  </p>
                </form>
              </div>
            </div>
          </Expander>
        </div>

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

export default function SettingsPage() {
  return (
    <Suspense>
      <SettingsContent />
    </Suspense>
  );
}
