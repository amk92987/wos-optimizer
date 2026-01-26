'use client';

import { useState } from 'react';
import { UserHero } from '@/lib/api';
import Expander from './Expander';

interface HeroCardProps {
  hero: UserHero;
  onUpdate?: (heroId: number, data: Partial<UserHero>) => void;
  onRemove?: () => void;
}

export default function HeroCard({ hero, onUpdate, onRemove }: HeroCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [level, setLevel] = useState(hero.level);
  const [stars, setStars] = useState(hero.stars);

  const getTierClass = (tier: string | null) => {
    if (!tier) return 'tier-b';
    const t = tier.toLowerCase();
    if (t.includes('s')) return 'tier-s';
    if (t.includes('a')) return 'tier-a';
    if (t.includes('b')) return 'tier-b';
    if (t.includes('c')) return 'tier-c';
    return 'tier-d';
  };

  const getClassBadge = (heroClass: string) => {
    const c = heroClass.toLowerCase();
    if (c === 'infantry') return 'class-infantry';
    if (c === 'lancer') return 'class-lancer';
    if (c === 'marksman') return 'class-marksman';
    return 'badge-blue';
  };

  const handleSave = () => {
    if (onUpdate) {
      onUpdate(hero.hero_id, { level, stars });
    }
    setIsEditing(false);
  };

  const renderStars = (count: number, max: number = 5) => {
    return (
      <div className="flex gap-0.5">
        {[...Array(max)].map((_, i) => (
          <span
            key={i}
            className={`text-sm ${i < count ? 'text-amber' : 'text-zinc-600'}`}
          >
            ★
          </span>
        ))}
      </div>
    );
  };

  const heroHeader = (
    <div className="flex items-center gap-4 w-full">
      {/* Hero Image */}
      <div className="w-16 h-16 rounded-xl overflow-hidden bg-surface-hover flex-shrink-0 border-2 border-zinc-700">
        {hero.image_base64 ? (
          <img
            src={hero.image_base64}
            alt={hero.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-2xl">
            🦸
          </div>
        )}
      </div>

      {/* Hero Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <h3 className="font-semibold text-zinc-100 truncate">{hero.name}</h3>
          <span className={getTierClass(hero.tier_overall)}>
            {hero.tier_overall || 'B'}
          </span>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <span className={getClassBadge(hero.hero_class)}>
            {hero.hero_class}
          </span>
          <span className="text-zinc-500">Gen {hero.generation}</span>
        </div>
      </div>

      {/* Level & Stars */}
      <div className="text-right flex-shrink-0">
        <p className="text-lg font-bold text-amber">Lv.{hero.level}</p>
        {renderStars(hero.stars)}
      </div>
    </div>
  );

  return (
    <Expander title={heroHeader} className="mb-3">
      <div className="space-y-4">
        {/* Stats Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <label className="text-xs text-zinc-500 block mb-1">Level</label>
            {isEditing ? (
              <input
                type="number"
                value={level}
                onChange={(e) => setLevel(parseInt(e.target.value) || 1)}
                min={1}
                max={80}
                className="input py-1 text-sm"
              />
            ) : (
              <p className="font-medium text-zinc-100">{hero.level}</p>
            )}
          </div>
          <div>
            <label className="text-xs text-zinc-500 block mb-1">Stars</label>
            {isEditing ? (
              <input
                type="number"
                value={stars}
                onChange={(e) => setStars(parseInt(e.target.value) || 0)}
                min={0}
                max={5}
                className="input py-1 text-sm"
              />
            ) : (
              <div>{renderStars(hero.stars)}</div>
            )}
          </div>
          <div>
            <label className="text-xs text-zinc-500 block mb-1">Ascension</label>
            <p className="font-medium text-zinc-100">{hero.ascension}</p>
          </div>
          <div>
            <label className="text-xs text-zinc-500 block mb-1">Class</label>
            <p className="font-medium text-zinc-100 capitalize">{hero.hero_class}</p>
          </div>
        </div>

        {/* Skills */}
        <div className="grid grid-cols-2 gap-4">
          <div className="card bg-background">
            <h4 className="text-sm font-medium text-zinc-300 mb-3">Exploration Skills</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-zinc-400">Skill 1</span>
                <span className="badge-blue">{hero.exploration_skill_1}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-zinc-400">Skill 2</span>
                <span className="badge-blue">{hero.exploration_skill_2}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-zinc-400">Skill 3</span>
                <span className="badge-blue">{hero.exploration_skill_3}</span>
              </div>
            </div>
          </div>

          <div className="card bg-background">
            <h4 className="text-sm font-medium text-zinc-300 mb-3">Expedition Skills</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-zinc-400">Skill 1</span>
                <span className="badge-purple">{hero.expedition_skill_1}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-zinc-400">Skill 2</span>
                <span className="badge-purple">{hero.expedition_skill_2}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-zinc-400">Skill 3</span>
                <span className="badge-purple">{hero.expedition_skill_3}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-between pt-2 border-t border-border">
          <div>
            {onRemove && !isEditing && (
              <button
                onClick={onRemove}
                className="text-sm text-red-400 hover:text-red-300 transition-colors"
              >
                Remove from collection
              </button>
            )}
          </div>
          <div className="flex gap-2">
            {isEditing ? (
              <>
                <button
                  onClick={() => setIsEditing(false)}
                  className="btn-ghost text-sm"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  className="btn-primary text-sm"
                >
                  Save Changes
                </button>
              </>
            ) : (
              <button
                onClick={() => setIsEditing(true)}
                className="btn-secondary text-sm"
              >
                Edit Hero
              </button>
            )}
          </div>
        </div>
      </div>
    </Expander>
  );
}
