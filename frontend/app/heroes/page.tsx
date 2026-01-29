'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import PageLayout from '@/components/PageLayout';
import HeroCard from '@/components/HeroCard';
import HeroRoleBadges from '@/components/HeroRoleBadges';
import HeroDetailModal from '@/components/HeroDetailModal';
import { useAuth } from '@/lib/auth';
import { heroesApi, UserHero, Hero } from '@/lib/api';

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
  const [filterClass, setFilterClass] = useState<FilterClass>('all');
  const [filterTier, setFilterTier] = useState<FilterTier>('all');
  const [filterGeneration, setFilterGeneration] = useState<FilterGeneration>('all');
  const [sortBy, setSortBy] = useState<SortBy>('generation');
  const [searchQuery, setSearchQuery] = useState('');
  const [addingHeroId, setAddingHeroId] = useState<number | null>(null);
  const [addError, setAddError] = useState<string | null>(null);
  const [addSuccess, setAddSuccess] = useState<string | null>(null);
  const [selectedHero, setSelectedHero] = useState<Hero | null>(null);

  // Load owned heroes
  useEffect(() => {
    if (token) {
      heroesApi.getOwned(token)
        .then(setOwnedHeroes)
        .catch(console.error)
        .finally(() => setIsLoading(false));
    }
  }, [token]);

  // Load all heroes when tab switches
  useEffect(() => {
    if (token && activeTab === 'all' && allHeroes.length === 0) {
      heroesApi.getAll(token, true)
        .then(setAllHeroes)
        .catch(console.error);
    }
  }, [token, activeTab, allHeroes.length]);

  const ownedHeroIds = new Set(ownedHeroes.map(h => h.hero_id));

  const refreshOwnedHeroes = async () => {
    if (!token) return;
    try {
      const updated = await heroesApi.getOwned(token);
      setOwnedHeroes(updated);
    } catch (error) {
      console.error('Failed to refresh heroes:', error);
    }
  };

  const handleAddHero = async (heroId: number, heroName?: string) => {
    if (!token) return;

    setAddingHeroId(heroId);
    setAddError(null);
    setAddSuccess(null);

    try {
      await heroesApi.addHero(token, heroId);
      const updated = await heroesApi.getOwned(token);
      setOwnedHeroes(updated);

      // Show success message
      setAddSuccess(`${heroName || 'Hero'} added to your collection!`);
      setTimeout(() => setAddSuccess(null), 3000);
    } catch (error: any) {
      console.error('Failed to add hero:', error);
      // Show user-friendly error message
      const message = error?.message || 'Failed to add hero. Please try again.';
      if (message.includes('No profile found')) {
        setAddError('Please set up your profile in Settings first.');
      } else {
        setAddError(message);
      }
      setTimeout(() => setAddError(null), 5000);
    } finally {
      setAddingHeroId(null);
    }
  };

  const handleRemoveHero = async (heroId: number) => {
    if (!token) return;

    try {
      await heroesApi.removeHero(token, heroId);
      const updated = await heroesApi.getOwned(token);
      setOwnedHeroes(updated);
    } catch (error) {
      console.error('Failed to remove hero:', error);
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
        case 'generation':
          return a.generation - b.generation;
        case 'tier':
          const tierOrder: Record<string, number> = { 'S+': 0, 'S': 1, 'A': 2, 'B': 3, 'C': 4, 'D': 5 };
          const aTier = tierOrder[a.tier_overall || 'D'] ?? 5;
          const bTier = tierOrder[b.tier_overall || 'D'] ?? 5;
          return aTier - bTier;
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
        case 'generation':
          return a.generation - b.generation;
        case 'tier':
          const tierOrder: Record<string, number> = { 'S+': 0, 'S': 1, 'A': 2, 'B': 3, 'C': 4, 'D': 5 };
          const aTier = tierOrder[a.tier_overall || 'D'] ?? 5;
          const bTier = tierOrder[b.tier_overall || 'D'] ?? 5;
          return aTier - bTier;
        default:
          return a.generation - b.generation;
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
        <div className="flex gap-2 mb-6">
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
        </div>

        {/* Success/Error Messages */}
        {addSuccess && (
          <div className="mb-4 p-3 rounded-lg bg-success/20 border border-success/30 text-success text-sm flex items-center gap-2 animate-fadeIn">
            <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            {addSuccess}
          </div>
        )}
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
                {filteredOwnedHeroes.map((hero) => (
                  <HeroCard
                    key={hero.hero_id}
                    hero={hero}
                    token={token}
                    onSaved={refreshOwnedHeroes}
                    onRemove={() => handleRemoveHero(hero.hero_id)}
                  />
                ))}
              </div>
            )}

            {/* Summary */}
            {ownedHeroes.length > 0 && (
              <div className="card mt-6">
                <h3 className="text-sm font-medium text-zinc-400 mb-3">Collection Summary</h3>
                <div className="grid grid-cols-3 gap-4 text-center">
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
                </div>
              </div>
            )}
          </>
        ) : (
          // All Heroes Tab
          <>
            {allHeroes.length === 0 ? (
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
                  const isOwned = ownedHeroIds.has(hero.id);
                  const isAdding = addingHeroId === hero.id;

                  return (
                    <div
                      key={hero.id}
                      className={`card flex items-center gap-4 transition-all cursor-pointer hover:border-ice/30 ${
                        isOwned ? 'border-ice/30 bg-ice/5' : ''
                      }`}
                      onClick={() => setSelectedHero(hero)}
                    >
                      {/* Hero Image */}
                      <div className={`w-16 h-16 rounded-xl overflow-hidden flex-shrink-0 border-2 ${getClassColor(hero.hero_class)}`}>
                        {hero.image_base64 ? (
                          <img
                            src={hero.image_base64}
                            alt={hero.name}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full bg-surface flex items-center justify-center text-2xl">
                            🦸
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
                        <span className="px-3 py-1.5 bg-ice/20 text-ice rounded-lg text-sm font-medium flex items-center gap-1">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          Owned
                        </span>
                      ) : (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleAddHero(hero.id, hero.name);
                          }}
                          disabled={isAdding}
                          className="px-3 py-1.5 bg-success/20 text-success hover:bg-success/30
                                     rounded-lg text-sm font-medium transition-colors disabled:opacity-50 flex-shrink-0"
                        >
                          {isAdding ? (
                            <span className="flex items-center gap-1">
                              <svg className="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                              </svg>
                              Adding...
                            </span>
                          ) : (
                            <span className="flex items-center gap-1">
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                              </svg>
                              Add
                            </span>
                          )}
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
            isOwned={ownedHeroIds.has(selectedHero.id)}
            onClose={() => setSelectedHero(null)}
            onAdd={() => {
              handleAddHero(selectedHero.id, selectedHero.name);
              setSelectedHero(null);
            }}
          />
        )}
      </div>
    </PageLayout>
  );
}
