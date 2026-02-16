'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import PageLayout from '@/components/PageLayout';
import HeroCard from '@/components/HeroCard';
import HeroRoleBadges from '@/components/HeroRoleBadges';
import HeroDetailModal from '@/components/HeroDetailModal';
import { useAuth } from '@/lib/auth';
import { heroesApi, profileApi, UserHero, Hero, bumpHeroDataVersion } from '@/lib/api';

type Tab = 'owned' | 'all';
type FilterClass = 'all' | 'infantry' | 'lancer' | 'marksman';
type FilterTier = 'all' | 'S+' | 'S' | 'A' | 'B' | 'C' | 'D';
type FilterGeneration = 'all' | number;
type SortBy = 'name' | 'level' | 'generation' | 'tier';

export default function HeroesPage() {
  const { token } = useAuth();
  const [activeTab, setActiveTab] = useState<Tab>('owned');
  const [ownedHeroes, setOwnedHeroes] = useState<UserHero[]>([]);
  const [allHeroes, setAllHeroes] = useState<Hero[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [allHeroesLoading, setAllHeroesLoading] = useState(false);
  const [allHeroesError, setAllHeroesError] = useState<string | null>(null);
  const [filterClass, setFilterClass] = useState<FilterClass>('all');
  const [filterTier, setFilterTier] = useState<FilterTier>('all');
  const [filterGeneration, setFilterGeneration] = useState<FilterGeneration>('all');
  const [sortBy, setSortBy] = useState<SortBy>('generation');
  const [searchQuery, setSearchQuery] = useState('');
  const [addError, setAddError] = useState<string | null>(null);
  const [justAdded, setJustAdded] = useState<string | null>(null);
  const [selectedHero, setSelectedHero] = useState<Hero | null>(null);

  // Bulk update mode
  const [isBulkMode, setIsBulkMode] = useState(false);
  const [selectedForBulk, setSelectedForBulk] = useState<Set<string>>(new Set());
  const [bulkLevel, setBulkLevel] = useState<number | null>(null);
  const [bulkStars, setBulkStars] = useState<number | null>(null);
  const [bulkAscension, setBulkAscension] = useState<number | null>(null);
  const [bulkExplorationSkills, setBulkExplorationSkills] = useState<number | null>(null);
  const [bulkExpeditionSkills, setBulkExpeditionSkills] = useState<number | null>(null);
  const [isBulkApplying, setIsBulkApplying] = useState(false);
  const [bulkMessage, setBulkMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Load owned heroes
  useEffect(() => {
    if (token) {
      heroesApi.getOwned(token)
        .then(data => setOwnedHeroes(data.heroes || []))
        .catch(console.error)
        .finally(() => setIsLoading(false));
    }
  }, [token]);

  // Load all heroes when tab switches
  useEffect(() => {
    if (token && activeTab === 'all' && allHeroes.length === 0 && !allHeroesLoading) {
      setAllHeroesLoading(true);
      setAllHeroesError(null);
      heroesApi.getAll(token, false)
        .then(data => setAllHeroes(data.heroes || []))
        .catch(err => {
          console.error('Failed to load all heroes:', err);
          setAllHeroesError('Failed to load heroes. Please try again.');
        })
        .finally(() => setAllHeroesLoading(false));
    }
  }, [token, activeTab, allHeroes.length]);

  const ownedHeroNames = new Set(ownedHeroes.map(h => h.hero_name));

  // Generation day ranges: [start, end] for each gen 1-14
  const GEN_DAY_RANGES: Record<number, [number, number]> = {
    1: [0, 39], 2: [40, 119], 3: [120, 199], 4: [200, 279],
    5: [280, 359], 6: [360, 439], 7: [440, 519], 8: [520, 599],
    9: [600, 679], 10: [680, 759], 11: [760, 839], 12: [840, 919],
    13: [920, 999], 14: [1000, 1080],
  };

  const getGenMidpointDays = (gen: number): number => {
    const range = GEN_DAY_RANGES[gen];
    if (!range) return 0;
    return Math.floor((range[0] + range[1]) / 2);
  };

  const getCurrentGenFromDays = (days: number): number => {
    const thresholds = [40, 120, 200, 280, 360, 440, 520, 600, 680, 760, 840, 920, 1000];
    for (let i = 0; i < thresholds.length; i++) {
      if (days < thresholds[i]) return i + 1;
    }
    return 14;
  };

  const refreshOwnedHeroes = async () => {
    if (!token) return;
    try {
      const data = await heroesApi.getOwned(token);
      setOwnedHeroes(data.heroes || []);
      bumpHeroDataVersion();
    } catch (error) {
      console.error('Failed to refresh heroes:', error);
    }
  };

  // Build a UserHero from reference data with defaults for optimistic UI
  const buildOptimisticUserHero = (hero: Hero): UserHero => ({
    hero_name: hero.name,
    name: hero.name,
    generation: hero.generation,
    hero_class: hero.hero_class,
    rarity: hero.rarity,
    tier_overall: hero.tier_overall,
    level: 1,
    stars: 0,
    ascension: 0,
    exploration_skill_1: 1, exploration_skill_2: 1, exploration_skill_3: 1,
    expedition_skill_1: 1, expedition_skill_2: 1, expedition_skill_3: 1,
    exploration_skill_1_name: hero.exploration_skill_1,
    exploration_skill_2_name: hero.exploration_skill_2,
    exploration_skill_3_name: hero.exploration_skill_3,
    expedition_skill_1_name: hero.expedition_skill_1,
    expedition_skill_2_name: hero.expedition_skill_2,
    expedition_skill_3_name: hero.expedition_skill_3,
    exploration_skill_1_desc: hero.exploration_skill_1_desc,
    exploration_skill_2_desc: hero.exploration_skill_2_desc,
    exploration_skill_3_desc: hero.exploration_skill_3_desc,
    expedition_skill_1_desc: hero.expedition_skill_1_desc,
    expedition_skill_2_desc: hero.expedition_skill_2_desc,
    expedition_skill_3_desc: hero.expedition_skill_3_desc,
    gear_slot1_quality: 0, gear_slot1_level: 0, gear_slot1_mastery: 0,
    gear_slot2_quality: 0, gear_slot2_level: 0, gear_slot2_mastery: 0,
    gear_slot3_quality: 0, gear_slot3_level: 0, gear_slot3_mastery: 0,
    gear_slot4_quality: 0, gear_slot4_level: 0, gear_slot4_mastery: 0,
    mythic_gear_name: hero.mythic_gear,
    mythic_gear_unlocked: false, mythic_gear_quality: 0, mythic_gear_level: 0, mythic_gear_mastery: 0,
    exclusive_gear_skill_level: 0,
    image_filename: hero.image_filename,
    image_base64: hero.image_base64,
  });

  const handleAddHero = async (heroName: string) => {
    if (!token) return;

    const heroRef = allHeroes.find(h => h.name === heroName);
    if (!heroRef) return;

    setAddError(null);

    // Optimistic: instantly add to owned list
    const optimisticHero = buildOptimisticUserHero(heroRef);
    setOwnedHeroes(prev => [...prev, optimisticHero]);

    // Brief "just added" highlight on the Owned badge
    setJustAdded(heroName);
    setTimeout(() => setJustAdded(null), 1500);

    // Fire backend call in background
    heroesApi.addHero(token, heroName).then(() => {
      bumpHeroDataVersion();

      // Auto-update profile generation in background (non-blocking)
      profileApi.getCurrent(token).then(profileData => {
        const profile = profileData.profile;
        const currentGen = getCurrentGenFromDays(profile.server_age_days);
        if (heroRef.generation > currentGen) {
          const newDays = getGenMidpointDays(heroRef.generation);
          profileApi.update(token, profile.profile_id, { server_age_days: newDays }).catch(() => {});
        }
      }).catch(() => {});
    }).catch((error: any) => {
      // Revert optimistic add
      setOwnedHeroes(prev => prev.filter(h => h.hero_name !== heroName));

      const message = error?.message || 'Failed to add hero. Please try again.';
      if (message.includes('No profile found')) {
        setAddError('Please set up your profile in Settings first.');
      } else {
        setAddError(message);
      }
      setTimeout(() => setAddError(null), 5000);
    });
  };

  const handleRemoveHero = async (heroName: string) => {
    if (!token) return;

    // Optimistic: instantly remove from owned list
    const previousHeroes = ownedHeroes;
    setOwnedHeroes(prev => prev.filter(h => h.hero_name !== heroName));

    try {
      await heroesApi.removeHero(token, heroName);
      bumpHeroDataVersion();
    } catch (error) {
      // Revert on failure
      setOwnedHeroes(previousHeroes);
      console.error('Failed to remove hero:', error);
    }
  };

  const tierOrder: Record<string, number> = { 'S+': 0, 'S': 1, 'A': 2, 'B': 3, 'C': 4, 'D': 5 };
  const rarityOrder: Record<string, number> = { 'rare': 0, 'epic': 1, 'legendary': 2 };

  // Bulk mode helpers
  const toggleBulkSelect = (heroName: string) => {
    setSelectedForBulk(prev => {
      const next = new Set(prev);
      if (next.has(heroName)) next.delete(heroName);
      else next.add(heroName);
      return next;
    });
  };

  const selectAllFiltered = () => {
    setSelectedForBulk(new Set(filteredOwnedHeroes.map(h => h.hero_name)));
  };

  const deselectAll = () => {
    setSelectedForBulk(new Set());
  };

  const exitBulkMode = () => {
    setIsBulkMode(false);
    setSelectedForBulk(new Set());
    setBulkLevel(null);
    setBulkStars(null);
    setBulkAscension(null);
    setBulkExplorationSkills(null);
    setBulkExpeditionSkills(null);
    setBulkMessage(null);
  };

  const handleBulkApply = async () => {
    if (!token || selectedForBulk.size === 0) return;

    // Build update payload - only include non-null values
    const updates: Record<string, any> = {};
    if (bulkLevel !== null) updates.level = bulkLevel;
    if (bulkStars !== null) updates.stars = bulkStars;
    if (bulkAscension !== null) updates.ascension = bulkAscension;
    if (bulkExplorationSkills !== null) {
      updates.exploration_skill_1 = bulkExplorationSkills;
      updates.exploration_skill_2 = bulkExplorationSkills;
      updates.exploration_skill_3 = bulkExplorationSkills;
    }
    if (bulkExpeditionSkills !== null) {
      updates.expedition_skill_1 = bulkExpeditionSkills;
      updates.expedition_skill_2 = bulkExpeditionSkills;
      updates.expedition_skill_3 = bulkExpeditionSkills;
    }

    if (Object.keys(updates).length === 0) {
      setBulkMessage({ type: 'error', text: 'Set at least one value to apply.' });
      return;
    }

    setIsBulkApplying(true);
    setBulkMessage(null);

    const heroesPayload = Array.from(selectedForBulk).map(heroName => ({
      name: heroName,
      ...updates,
    }));

    try {
      await heroesApi.batchUpdate(token, heroesPayload);
      setBulkMessage({ type: 'success', text: `Updated ${heroesPayload.length} heroes.` });
      // Refresh hero list
      await refreshOwnedHeroes();
    } catch (error: any) {
      setBulkMessage({ type: 'error', text: error?.message || 'Bulk update failed.' });
    } finally {
      setIsBulkApplying(false);
    }
  };

  // Filter and sort owned heroes
  const filteredOwnedHeroes = ownedHeroes
    .filter(h => {
      if (filterClass !== 'all' && h.hero_class.toLowerCase() !== filterClass) {
        return false;
      }
      if (filterTier !== 'all' && h.tier_overall !== filterTier) {
        return false;
      }
      if (filterGeneration !== 'all' && h.generation !== filterGeneration) {
        return false;
      }
      if (searchQuery && !h.name.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false;
      }
      return true;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'level':
          return b.level - a.level;
        case 'generation': {
          // Sort by generation first, then rarity (blue→purple→gold), then name
          if (a.generation !== b.generation) return a.generation - b.generation;
          const aRarity = rarityOrder[(a.rarity || 'rare').toLowerCase()] ?? 0;
          const bRarity = rarityOrder[(b.rarity || 'rare').toLowerCase()] ?? 0;
          if (aRarity !== bRarity) return aRarity - bRarity;
          return a.name.localeCompare(b.name);
        }
        case 'tier': {
          const aTier = tierOrder[a.tier_overall || 'D'] ?? 5;
          const bTier = tierOrder[b.tier_overall || 'D'] ?? 5;
          return aTier - bTier;
        }
        default:
          return 0;
      }
    });

  // Filter and sort all heroes
  const filteredAllHeroes = allHeroes
    .filter(h => {
      if (filterClass !== 'all' && h.hero_class.toLowerCase() !== filterClass) {
        return false;
      }
      if (filterTier !== 'all' && h.tier_overall !== filterTier) {
        return false;
      }
      if (filterGeneration !== 'all' && h.generation !== filterGeneration) {
        return false;
      }
      if (searchQuery && !h.name.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false;
      }
      return true;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'generation': {
          // Sort by generation first, then rarity (blue→purple→gold), then name
          if (a.generation !== b.generation) return a.generation - b.generation;
          const aRarity = rarityOrder[(a.rarity || 'rare').toLowerCase()] ?? 0;
          const bRarity = rarityOrder[(b.rarity || 'rare').toLowerCase()] ?? 0;
          if (aRarity !== bRarity) return aRarity - bRarity;
          return a.name.localeCompare(b.name);
        }
        case 'tier': {
          const aTier = tierOrder[a.tier_overall || 'D'] ?? 5;
          const bTier = tierOrder[b.tier_overall || 'D'] ?? 5;
          return aTier - bTier;
        }
        default: {
          if (a.generation !== b.generation) return a.generation - b.generation;
          const aR = rarityOrder[(a.rarity || 'rare').toLowerCase()] ?? 0;
          const bR = rarityOrder[(b.rarity || 'rare').toLowerCase()] ?? 0;
          if (aR !== bR) return aR - bR;
          return a.name.localeCompare(b.name);
        }
      }
    });

  const classFilters: { value: FilterClass; label: string; color: string }[] = [
    { value: 'all', label: 'All', color: 'bg-zinc-700' },
    { value: 'infantry', label: 'Infantry', color: 'bg-red-500/20 text-red-400' },
    { value: 'lancer', label: 'Lancer', color: 'bg-green-500/20 text-green-400' },
    { value: 'marksman', label: 'Marksman', color: 'bg-blue-500/20 text-blue-400' },
  ];

  const getClassColor = (heroClass: string) => {
    switch (heroClass.toLowerCase()) {
      case 'infantry': return 'text-red-400 border-red-500/30';
      case 'lancer': return 'text-green-400 border-green-500/30';
      case 'marksman': return 'text-blue-400 border-blue-500/30';
      default: return 'text-zinc-400 border-zinc-500/30';
    }
  };

  const getRarityBorderClass = (rarity: string | null) => {
    switch (rarity?.toLowerCase()) {
      case 'legendary': return 'rarity-legendary';
      case 'epic': return 'rarity-epic';
      case 'rare': return 'rarity-rare';
      default: return 'rarity-common';
    }
  };

  const getTierColor = (tier: string | null) => {
    switch (tier) {
      case 'S+': return 'bg-amber-500/20 text-amber-400';
      case 'S': return 'bg-purple-500/20 text-purple-400';
      case 'A': return 'bg-blue-500/20 text-blue-400';
      case 'B': return 'bg-green-500/20 text-green-400';
      case 'C': return 'bg-zinc-500/20 text-zinc-400';
      default: return 'bg-zinc-700 text-zinc-500';
    }
  };

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-zinc-100">Hero Tracker</h1>
          <p className="text-zinc-400 mt-2">
            {ownedHeroes.length} of {allHeroes.length || '?'} heroes in your collection
          </p>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-2 mb-6">
          <button
            onClick={() => setActiveTab('owned')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'owned'
                ? 'bg-ice text-zinc-900'
                : 'bg-surface text-zinc-400 hover:text-zinc-100'
            }`}
          >
            My Heroes ({ownedHeroes.length})
          </button>
          <button
            onClick={() => setActiveTab('all')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'all'
                ? 'bg-ice text-zinc-900'
                : 'bg-surface text-zinc-400 hover:text-zinc-100'
            }`}
          >
            All Heroes
          </button>
          {activeTab === 'owned' && ownedHeroes.length > 0 && !isBulkMode && (
            <button
              onClick={() => setIsBulkMode(true)}
              className="ml-auto px-3 py-2 rounded-lg text-sm font-medium bg-surface text-frost-muted hover:text-frost hover:bg-surface-hover transition-colors"
            >
              Bulk Update
            </button>
          )}
          {isBulkMode && (
            <button
              onClick={exitBulkMode}
              className="ml-auto px-3 py-2 rounded-lg text-sm font-medium bg-error/20 text-error hover:bg-error/30 transition-colors"
            >
              Exit Bulk Mode
            </button>
          )}
        </div>

        {/* Error Message */}
        {addError && (
          <div className="mb-4 p-3 rounded-lg bg-error/20 border border-error/30 text-error text-sm flex items-center gap-2 animate-fadeIn">
            <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {addError}
          </div>
        )}

        {/* Filters */}
        <div className="card mb-6">
          <div className="flex flex-col gap-4">
            {/* Row 1: Search + Sort */}
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="Search heroes..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="input"
                />
              </div>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SortBy)}
                className="input w-auto"
              >
                <option value="generation">Sort by Generation</option>
                <option value="name">Sort by Name</option>
                {activeTab === 'owned' && <option value="level">Sort by Level</option>}
                <option value="tier">Sort by Tier</option>
              </select>
            </div>

            {/* Row 2: Filters */}
            <div className="flex flex-wrap gap-3 items-center">
              {/* Generation Filter */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-frost-muted">Gen:</span>
                <select
                  value={filterGeneration}
                  onChange={(e) => setFilterGeneration(e.target.value === 'all' ? 'all' : parseInt(e.target.value))}
                  className="input py-1 px-2 text-sm w-auto"
                >
                  <option value="all">All</option>
                  {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14].map(g => (
                    <option key={g} value={g}>Gen {g}</option>
                  ))}
                </select>
              </div>

              {/* Tier Filter */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-frost-muted">Tier:</span>
                <select
                  value={filterTier}
                  onChange={(e) => setFilterTier(e.target.value as FilterTier)}
                  className="input py-1 px-2 text-sm w-auto"
                >
                  <option value="all">All</option>
                  <option value="S+">S+</option>
                  <option value="S">S</option>
                  <option value="A">A</option>
                  <option value="B">B</option>
                  <option value="C">C</option>
                  <option value="D">D</option>
                </select>
              </div>

              {/* Class Filter */}
              <div className="flex gap-1">
                {classFilters.map((filter) => (
                  <button
                    key={filter.value}
                    onClick={() => setFilterClass(filter.value)}
                    className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                      filterClass === filter.value
                        ? filter.value === 'all'
                          ? 'bg-amber text-zinc-900'
                          : filter.color + ' ring-1 ring-current'
                        : 'bg-surface text-zinc-400 hover:text-zinc-100'
                    }`}
                  >
                    {filter.label}
                  </button>
                ))}
              </div>

              {/* Clear Filters */}
              {(filterClass !== 'all' || filterTier !== 'all' || filterGeneration !== 'all' || searchQuery) && (
                <button
                  onClick={() => {
                    setFilterClass('all');
                    setFilterTier('all');
                    setFilterGeneration('all');
                    setSearchQuery('');
                  }}
                  className="text-xs text-ice hover:text-ice/80 underline"
                >
                  Clear filters
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Bulk Update Bar */}
        {isBulkMode && activeTab === 'owned' && (
          <div className="card mb-6 border-ice/30 bg-ice/5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <h3 className="text-sm font-medium text-ice">Bulk Update</h3>
                <span className="text-xs text-frost-muted">
                  {selectedForBulk.size} of {filteredOwnedHeroes.length} selected
                </span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={selectedForBulk.size === filteredOwnedHeroes.length ? deselectAll : selectAllFiltered}
                  className="px-3 py-1 rounded text-xs font-medium bg-surface text-frost-muted hover:text-frost transition-colors"
                >
                  {selectedForBulk.size === filteredOwnedHeroes.length ? 'Deselect All' : 'Select All'}
                </button>
              </div>
            </div>

            {/* Bulk value inputs */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3 mb-4">
              <div>
                <label className="text-xs text-frost-muted block mb-1">Level</label>
                <input
                  type="number"
                  min={1}
                  max={80}
                  placeholder="--"
                  value={bulkLevel ?? ''}
                  onChange={(e) => setBulkLevel(e.target.value ? Number(e.target.value) : null)}
                  className="input text-sm py-1.5 w-full"
                />
              </div>
              <div>
                <label className="text-xs text-frost-muted block mb-1">Stars</label>
                <select
                  value={bulkStars ?? ''}
                  onChange={(e) => setBulkStars(e.target.value ? Number(e.target.value) : null)}
                  className="input text-sm py-1.5 w-full"
                >
                  <option value="">--</option>
                  {[0, 1, 2, 3, 4, 5].map(v => (
                    <option key={v} value={v}>{v} {v === 1 ? 'star' : 'stars'}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs text-frost-muted block mb-1">Ascension</label>
                <select
                  value={bulkAscension ?? ''}
                  onChange={(e) => setBulkAscension(e.target.value ? Number(e.target.value) : null)}
                  className="input text-sm py-1.5 w-full"
                >
                  <option value="">--</option>
                  {[0, 1, 2, 3, 4, 5].map(v => (
                    <option key={v} value={v}>{v}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs text-frost-muted block mb-1">Exploration Skills</label>
                <select
                  value={bulkExplorationSkills ?? ''}
                  onChange={(e) => setBulkExplorationSkills(e.target.value ? Number(e.target.value) : null)}
                  className="input text-sm py-1.5 w-full"
                >
                  <option value="">--</option>
                  {[1, 2, 3, 4, 5].map(v => (
                    <option key={v} value={v}>All to {v}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs text-frost-muted block mb-1">Expedition Skills</label>
                <select
                  value={bulkExpeditionSkills ?? ''}
                  onChange={(e) => setBulkExpeditionSkills(e.target.value ? Number(e.target.value) : null)}
                  className="input text-sm py-1.5 w-full"
                >
                  <option value="">--</option>
                  {[1, 2, 3, 4, 5].map(v => (
                    <option key={v} value={v}>All to {v}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Bulk message */}
            {bulkMessage && (
              <div className={`mb-3 p-2 rounded text-xs ${
                bulkMessage.type === 'success' ? 'bg-success/20 text-success' : 'bg-error/20 text-error'
              }`}>
                {bulkMessage.text}
              </div>
            )}

            {/* Apply button */}
            <button
              onClick={handleBulkApply}
              disabled={selectedForBulk.size === 0 || isBulkApplying}
              className="btn-primary text-sm disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {isBulkApplying
                ? 'Applying...'
                : `Apply to ${selectedForBulk.size} Selected`}
            </button>
          </div>
        )}

        {/* Content */}
        {activeTab === 'owned' ? (
          // Owned Heroes Tab
          <>
            {isLoading ? (
              <div className="space-y-3">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="card animate-pulse">
                    <div className="flex items-center gap-4">
                      <div className="w-16 h-16 bg-surface-hover rounded-xl"></div>
                      <div className="flex-1">
                        <div className="h-5 bg-surface-hover rounded w-32 mb-2"></div>
                        <div className="h-4 bg-surface-hover rounded w-24"></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : filteredOwnedHeroes.length === 0 ? (
              <div className="card text-center py-12">
                <div className="text-4xl mb-4">🦸</div>
                <h3 className="text-lg font-medium text-zinc-100 mb-2">
                  {ownedHeroes.length === 0 ? 'No heroes yet' : 'No heroes match your filters'}
                </h3>
                <p className="text-zinc-500 mb-4">
                  {ownedHeroes.length === 0
                    ? 'Start by adding heroes from the "All Heroes" tab'
                    : 'Try adjusting your search or filters'}
                </p>
                {ownedHeroes.length === 0 && (
                  <button
                    onClick={() => setActiveTab('all')}
                    className="btn-primary"
                  >
                    Browse All Heroes
                  </button>
                )}
              </div>
            ) : (
              <div className="space-y-3">
                {sortBy === 'generation' ? (
                  // Group by generation with section headers
                  (() => {
                    const generationGroups: Record<number, UserHero[]> = {};
                    filteredOwnedHeroes.forEach(hero => {
                      const gen = hero.generation;
                      if (!generationGroups[gen]) generationGroups[gen] = [];
                      generationGroups[gen].push(hero);
                    });
                    return Object.keys(generationGroups)
                      .map(Number)
                      .sort((a, b) => a - b)
                      .map(gen => (
                        <div key={`gen-${gen}`}>
                          <div className="flex items-center gap-3 mt-4 mb-2 first:mt-0">
                            <h3 className="text-sm font-semibold text-frost-muted uppercase tracking-wider whitespace-nowrap">
                              Generation {gen}
                            </h3>
                            <div className="flex-1 border-t border-surface-border" />
                            <span className="text-xs text-zinc-500">
                              {generationGroups[gen].length} {generationGroups[gen].length === 1 ? 'hero' : 'heroes'}
                            </span>
                          </div>
                          {generationGroups[gen].map(hero => (
                            <div key={hero.hero_name} className="flex items-start gap-2">
                              {isBulkMode && (
                                <label className="flex items-center mt-5 cursor-pointer flex-shrink-0">
                                  <input
                                    type="checkbox"
                                    checked={selectedForBulk.has(hero.hero_name)}
                                    onChange={() => toggleBulkSelect(hero.hero_name)}
                                    className="w-5 h-5 rounded border-zinc-600 bg-surface text-ice focus:ring-ice/50 cursor-pointer"
                                  />
                                </label>
                              )}
                              <div className="flex-1 min-w-0">
                                <HeroCard
                                  hero={hero}
                                  token={token}
                                  onSaved={refreshOwnedHeroes}
                                  onRemove={() => handleRemoveHero(hero.hero_name)}
                                />
                              </div>
                            </div>
                          ))}
                        </div>
                      ));
                  })()
                ) : (
                  // Flat list for other sort modes
                  filteredOwnedHeroes.map((hero) => (
                    <div key={hero.hero_name} className="flex items-start gap-2">
                      {isBulkMode && (
                        <label className="flex items-center mt-5 cursor-pointer flex-shrink-0">
                          <input
                            type="checkbox"
                            checked={selectedForBulk.has(hero.hero_name)}
                            onChange={() => toggleBulkSelect(hero.hero_name)}
                            className="w-5 h-5 rounded border-zinc-600 bg-surface text-ice focus:ring-ice/50 cursor-pointer"
                          />
                        </label>
                      )}
                      <div className="flex-1 min-w-0">
                        <HeroCard
                          hero={hero}
                          token={token}
                          onSaved={refreshOwnedHeroes}
                          onRemove={() => handleRemoveHero(hero.hero_name)}
                        />
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {/* Summary */}
            {ownedHeroes.length > 0 && (
              <div className="card mt-6">
                <h3 className="text-sm font-medium text-zinc-400 mb-3">Collection Summary</h3>
                <div className="grid grid-cols-5 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-red-400">
                      {ownedHeroes.filter(h => h.hero_class.toLowerCase() === 'infantry').length}
                    </p>
                    <p className="text-xs text-zinc-500">Infantry</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-green-400">
                      {ownedHeroes.filter(h => h.hero_class.toLowerCase() === 'lancer').length}
                    </p>
                    <p className="text-xs text-zinc-500">Lancer</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-blue-400">
                      {ownedHeroes.filter(h => h.hero_class.toLowerCase() === 'marksman').length}
                    </p>
                    <p className="text-xs text-zinc-500">Marksman</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-amber-400">
                      {(ownedHeroes.reduce((sum, h) => sum + Number(h.level || 0), 0) / ownedHeroes.length).toFixed(1)}
                    </p>
                    <p className="text-xs text-zinc-500">Avg Level</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-yellow-400">
                      {ownedHeroes.reduce((sum, h) => sum + Number(h.stars || 0), 0)}
                    </p>
                    <p className="text-xs text-zinc-500">Total Stars</p>
                  </div>
                </div>
              </div>
            )}
          </>
        ) : (
          // All Heroes Tab
          <>
            {allHeroesError ? (
              <div className="card text-center py-12">
                <div className="text-4xl mb-4">⚠️</div>
                <h3 className="text-lg font-medium text-zinc-100 mb-2">
                  {allHeroesError}
                </h3>
                <button
                  onClick={() => { setAllHeroesError(null); setAllHeroes([]); }}
                  className="mt-4 px-4 py-2 bg-ice/20 text-ice rounded-lg hover:bg-ice/30 transition-colors"
                >
                  Retry
                </button>
              </div>
            ) : allHeroesLoading || allHeroes.length === 0 ? (
              <div className="space-y-3">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="card animate-pulse">
                    <div className="flex items-center gap-4">
                      <div className="w-16 h-16 bg-surface-hover rounded-xl"></div>
                      <div className="flex-1">
                        <div className="h-5 bg-surface-hover rounded w-32 mb-2"></div>
                        <div className="h-4 bg-surface-hover rounded w-24"></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : filteredAllHeroes.length === 0 ? (
              <div className="card text-center py-12">
                <div className="text-4xl mb-4">🔍</div>
                <h3 className="text-lg font-medium text-zinc-100 mb-2">
                  No heroes match your filters
                </h3>
                <p className="text-zinc-500">
                  Try adjusting your search or filters
                </p>
              </div>
            ) : (
              <div className="grid gap-3 md:grid-cols-2">
                {filteredAllHeroes.map((hero) => {
                  const isOwned = ownedHeroNames.has(hero.name);

                  return (
                    <div
                      key={hero.name}
                      className={`card flex items-center gap-4 transition-all cursor-pointer hover:border-ice/30 ${
                        isOwned ? 'border-ice/30 bg-ice/5' : ''
                      }`}
                      onClick={() => setSelectedHero(hero)}
                    >
                      {/* Hero Image */}
                      <div className={`w-16 h-16 rounded-xl overflow-hidden flex-shrink-0 border-2 ${getRarityBorderClass(hero.rarity)}`}>
                        {hero.image_base64 || hero.image_filename ? (
                          <img
                            src={hero.image_base64 || `/images/heroes/${hero.image_filename}`}
                            alt={hero.name}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full bg-surface flex items-center justify-center text-2xl">
                            ?
                          </div>
                        )}
                      </div>

                      {/* Hero Info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-medium text-zinc-100 truncate">{hero.name}</h3>
                          <span className={`px-1.5 py-0.5 rounded text-xs font-medium ${getTierColor(hero.tier_overall)}`}>
                            {hero.tier_overall || '?'}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-zinc-500 mb-1">
                          <span>Gen {hero.generation}</span>
                          <span>•</span>
                          <span className={getClassColor(hero.hero_class).split(' ')[0]}>
                            {hero.hero_class}
                          </span>
                        </div>
                        <HeroRoleBadges heroName={hero.name} compact />
                      </div>

                      {/* Add/Owned Button */}
                      {isOwned ? (
                        <span className={`px-3 py-1.5 rounded-lg text-sm font-medium flex items-center gap-1 transition-colors duration-500 ${
                          justAdded === hero.name ? 'bg-success/30 text-success' : 'bg-ice/20 text-ice'
                        }`}>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          {justAdded === hero.name ? 'Added!' : 'Owned'}
                        </span>
                      ) : (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleAddHero(hero.name);
                          }}
                          className="px-3 py-1.5 bg-success/20 text-success hover:bg-success/30
                                     rounded-lg text-sm font-medium transition-colors flex-shrink-0"
                        >
                          <span className="flex items-center gap-1">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                            </svg>
                            Add
                          </span>
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {/* Stats */}
            <div className="card mt-6">
              <h3 className="text-sm font-medium text-zinc-400 mb-3">Hero Database</h3>
              <div className="grid grid-cols-4 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-ice">{allHeroes.length}</p>
                  <p className="text-xs text-zinc-500">Total Heroes</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-red-400">
                    {allHeroes.filter(h => h.hero_class.toLowerCase() === 'infantry').length}
                  </p>
                  <p className="text-xs text-zinc-500">Infantry</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-green-400">
                    {allHeroes.filter(h => h.hero_class.toLowerCase() === 'lancer').length}
                  </p>
                  <p className="text-xs text-zinc-500">Lancer</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-blue-400">
                    {allHeroes.filter(h => h.hero_class.toLowerCase() === 'marksman').length}
                  </p>
                  <p className="text-xs text-zinc-500">Marksman</p>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Hero Detail Modal */}
        {selectedHero && (
          <HeroDetailModal
            hero={selectedHero}
            isOwned={ownedHeroNames.has(selectedHero.name)}
            onClose={() => setSelectedHero(null)}
            onAdd={() => {
              handleAddHero(selectedHero.name);
              setSelectedHero(null);
            }}
          />
        )}
      </div>
    </PageLayout>
  );
}
