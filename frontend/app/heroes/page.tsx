'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import HeroCard from '@/components/HeroCard';
import { useAuth } from '@/lib/auth';
import { heroesApi, UserHero } from '@/lib/api';

type FilterClass = 'all' | 'infantry' | 'lancer' | 'marksman';
type SortBy = 'name' | 'level' | 'generation' | 'tier';

export default function HeroesPage() {
  const { token } = useAuth();
  const [heroes, setHeroes] = useState<UserHero[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filterClass, setFilterClass] = useState<FilterClass>('all');
  const [sortBy, setSortBy] = useState<SortBy>('level');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (token) {
      heroesApi.getOwned(token)
        .then(setHeroes)
        .catch(console.error)
        .finally(() => setIsLoading(false));
    }
  }, [token]);

  const handleUpdateHero = async (heroId: number, data: Partial<UserHero>) => {
    if (!token) return;

    try {
      await heroesApi.updateHero(token, heroId, data);
      // Refresh heroes
      const updated = await heroesApi.getOwned(token);
      setHeroes(updated);
    } catch (error) {
      console.error('Failed to update hero:', error);
    }
  };

  // Filter and sort heroes
  const filteredHeroes = heroes
    .filter(h => {
      if (filterClass !== 'all' && h.hero_class.toLowerCase() !== filterClass) {
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

  const classFilters: { value: FilterClass; label: string; color: string }[] = [
    { value: 'all', label: 'All Classes', color: 'bg-zinc-700' },
    { value: 'infantry', label: 'Infantry', color: 'bg-red-500/20 text-red-400' },
    { value: 'lancer', label: 'Lancer', color: 'bg-green-500/20 text-green-400' },
    { value: 'marksman', label: 'Marksman', color: 'bg-blue-500/20 text-blue-400' },
  ];

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-zinc-100">Hero Tracker</h1>
          <p className="text-zinc-400 mt-2">
            {heroes.length} heroes in your collection
          </p>
        </div>

        {/* Filters */}
        <div className="card mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search heroes..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input"
              />
            </div>

            {/* Class Filter */}
            <div className="flex gap-2">
              {classFilters.map((filter) => (
                <button
                  key={filter.value}
                  onClick={() => setFilterClass(filter.value)}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
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

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortBy)}
              className="input w-auto"
            >
              <option value="level">Sort by Level</option>
              <option value="name">Sort by Name</option>
              <option value="generation">Sort by Generation</option>
              <option value="tier">Sort by Tier</option>
            </select>
          </div>
        </div>

        {/* Hero List */}
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
        ) : filteredHeroes.length === 0 ? (
          <div className="card text-center py-12">
            <div className="text-4xl mb-4">🦸</div>
            <h3 className="text-lg font-medium text-zinc-100 mb-2">
              {heroes.length === 0 ? 'No heroes yet' : 'No heroes match your filters'}
            </h3>
            <p className="text-zinc-500">
              {heroes.length === 0
                ? 'Start tracking your hero collection'
                : 'Try adjusting your search or filters'}
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredHeroes.map((hero) => (
              <HeroCard
                key={hero.hero_id}
                hero={hero}
                onUpdate={handleUpdateHero}
              />
            ))}
          </div>
        )}

        {/* Summary */}
        {heroes.length > 0 && (
          <div className="card mt-6">
            <h3 className="text-sm font-medium text-zinc-400 mb-3">Collection Summary</h3>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold text-red-400">
                  {heroes.filter(h => h.hero_class.toLowerCase() === 'infantry').length}
                </p>
                <p className="text-xs text-zinc-500">Infantry</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-green-400">
                  {heroes.filter(h => h.hero_class.toLowerCase() === 'lancer').length}
                </p>
                <p className="text-xs text-zinc-500">Lancer</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-blue-400">
                  {heroes.filter(h => h.hero_class.toLowerCase() === 'marksman').length}
                </p>
                <p className="text-xs text-zinc-500">Marksman</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </PageLayout>
  );
}
