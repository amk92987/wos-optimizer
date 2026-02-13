'use client';

import { Hero } from '@/lib/api';
import HeroRoleBadges from './HeroRoleBadges';
import { useEffect, useRef } from 'react';

interface HeroDetailModalProps {
  hero: Hero;
  isOwned: boolean;
  onClose: () => void;
  onAdd?: () => void;
}

const getTierColor = (tier: string | null) => {
  switch (tier) {
    case 'S+': return 'bg-amber-500/20 text-amber-400 border-amber-500/50';
    case 'S': return 'bg-purple-500/20 text-purple-400 border-purple-500/50';
    case 'A': return 'bg-blue-500/20 text-blue-400 border-blue-500/50';
    case 'B': return 'bg-green-500/20 text-green-400 border-green-500/50';
    case 'C': return 'bg-zinc-500/20 text-zinc-400 border-zinc-500/50';
    default: return 'bg-zinc-700 text-zinc-500 border-zinc-600';
  }
};

const getClassColor = (heroClass: string) => {
  switch (heroClass.toLowerCase()) {
    case 'infantry': return 'text-red-400 border-red-500/50 bg-red-500/10';
    case 'lancer': return 'text-green-400 border-green-500/50 bg-green-500/10';
    case 'marksman': return 'text-blue-400 border-blue-500/50 bg-blue-500/10';
    default: return 'text-zinc-400 border-zinc-500/50 bg-zinc-500/10';
  }
};

const getRarityColor = (rarity: string | null) => {
  switch (rarity?.toLowerCase()) {
    case 'legendary': return 'text-amber-400';
    case 'epic': return 'text-purple-400';
    case 'rare': return 'text-blue-400';
    default: return 'text-zinc-400';
  }
};

export default function HeroDetailModal({ hero, isOwned, onClose, onAdd }: HeroDetailModalProps) {
  const hasExplorationSkills = hero.exploration_skill_1 || hero.exploration_skill_2 || hero.exploration_skill_3;
  const hasExpeditionSkills = hero.expedition_skill_1 || hero.expedition_skill_2 || hero.expedition_skill_3;
  const modalRef = useRef<HTMLDivElement>(null);

  // Handle Escape key to close modal
  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        onClose();
      }
    }
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  // Auto-focus the modal content on mount
  useEffect(() => {
    if (modalRef.current) {
      modalRef.current.focus();
    }
  }, []);

  return (
    <div
      className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="hero-modal-title"
    >
      <div
        ref={modalRef}
        className="bg-surface rounded-xl border border-surface-border max-w-2xl w-full max-h-[90vh] overflow-y-auto animate-fade-in"
        onClick={e => e.stopPropagation()}
        tabIndex={-1}
      >
        {/* Header */}
        <div className="sticky top-0 bg-surface border-b border-surface-border p-4 flex items-start gap-4">
          {/* Hero Image */}
          <div className={`w-20 h-20 rounded-xl overflow-hidden flex-shrink-0 border-2 ${getClassColor(hero.hero_class)}`}>
            {hero.image_base64 || hero.image_filename ? (
              <img
                src={hero.image_base64 || `/images/heroes/${hero.image_filename}`}
                alt={hero.name}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full bg-surface-hover flex items-center justify-center text-3xl">
                ?
              </div>
            )}
          </div>

          {/* Hero Basic Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <h2 id="hero-modal-title" className="text-xl font-bold text-frost">{hero.name}</h2>
              <span className={`px-2 py-0.5 rounded text-sm font-medium border ${getTierColor(hero.tier_overall)}`}>
                {hero.tier_overall || '?'}
              </span>
              {isOwned && (
                <span className="px-2 py-0.5 bg-ice/20 text-ice rounded text-xs font-medium">
                  Owned
                </span>
              )}
            </div>
            <div className="flex items-center gap-3 text-sm text-frost-muted mb-2">
              <span className={getRarityColor(hero.rarity)}>{hero.rarity}</span>
              <span>•</span>
              <span>Gen {hero.generation}</span>
              <span>•</span>
              <span className={getClassColor(hero.hero_class).split(' ')[0]}>{hero.hero_class}</span>
            </div>
            <HeroRoleBadges heroName={hero.name} />
          </div>

          {/* Close Button */}
          <button
            onClick={onClose}
            className="p-2 hover:bg-surface-hover rounded-lg transition-colors text-frost-muted hover:text-frost"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {/* Tier Breakdown */}
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-surface-hover rounded-lg p-3 text-center">
              <div className="text-xs text-frost-muted mb-1">Overall</div>
              <div className={`text-lg font-bold ${getTierColor(hero.tier_overall).split(' ').slice(1).join(' ')}`}>
                {hero.tier_overall || '?'}
              </div>
            </div>
            <div className="bg-surface-hover rounded-lg p-3 text-center">
              <div className="text-xs text-frost-muted mb-1">Expedition (PvP)</div>
              <div className={`text-lg font-bold ${getTierColor(hero.tier_expedition).split(' ').slice(1).join(' ')}`}>
                {hero.tier_expedition || '?'}
              </div>
            </div>
            <div className="bg-surface-hover rounded-lg p-3 text-center">
              <div className="text-xs text-frost-muted mb-1">Exploration (PvE)</div>
              <div className={`text-lg font-bold ${getTierColor(hero.tier_exploration).split(' ').slice(1).join(' ')}`}>
                {hero.tier_exploration || '?'}
              </div>
            </div>
          </div>

          {/* How to Obtain */}
          {hero.how_to_obtain && (
            <div className="bg-surface-hover rounded-lg p-3">
              <div className="text-xs text-frost-muted mb-1">How to Obtain</div>
              <div className="text-frost">{hero.how_to_obtain}</div>
            </div>
          )}

          {/* Best Use */}
          {hero.best_use && (
            <div className="bg-ice/10 border border-ice/30 rounded-lg p-3">
              <div className="text-xs text-ice mb-1">Best Use</div>
              <div className="text-frost">{hero.best_use}</div>
            </div>
          )}

          {/* Notes */}
          {hero.notes && (
            <div className="bg-surface-hover rounded-lg p-3">
              <div className="text-xs text-frost-muted mb-1">Notes</div>
              <div className="text-frost-muted text-sm">{hero.notes}</div>
            </div>
          )}

          {/* Skills Section */}
          <div className="grid md:grid-cols-2 gap-4">
            {/* Exploration Skills (PvE) */}
            {hasExplorationSkills && (
              <div className="bg-surface-hover rounded-lg p-4">
                <h3 className="text-sm font-medium text-green-400 mb-3 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-green-500"></span>
                  Exploration Skills (PvE)
                </h3>
                <div className="space-y-3">
                  {hero.exploration_skill_1 && (
                    <div>
                      <div className="font-medium text-frost text-sm">{hero.exploration_skill_1}</div>
                      {hero.exploration_skill_1_desc && (
                        <div className="text-xs text-frost-muted mt-1">{hero.exploration_skill_1_desc}</div>
                      )}
                    </div>
                  )}
                  {hero.exploration_skill_2 && (
                    <div>
                      <div className="font-medium text-frost text-sm">{hero.exploration_skill_2}</div>
                      {hero.exploration_skill_2_desc && (
                        <div className="text-xs text-frost-muted mt-1">{hero.exploration_skill_2_desc}</div>
                      )}
                    </div>
                  )}
                  {hero.exploration_skill_3 && (
                    <div>
                      <div className="font-medium text-frost text-sm">{hero.exploration_skill_3}</div>
                      {hero.exploration_skill_3_desc && (
                        <div className="text-xs text-frost-muted mt-1">{hero.exploration_skill_3_desc}</div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Expedition Skills (PvP) */}
            {hasExpeditionSkills && (
              <div className="bg-surface-hover rounded-lg p-4">
                <h3 className="text-sm font-medium text-blue-400 mb-3 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                  Expedition Skills (PvP)
                </h3>
                <div className="space-y-3">
                  {hero.expedition_skill_1 && (
                    <div>
                      <div className="font-medium text-frost text-sm">{hero.expedition_skill_1}</div>
                      {hero.expedition_skill_1_desc && (
                        <div className="text-xs text-frost-muted mt-1">{hero.expedition_skill_1_desc}</div>
                      )}
                    </div>
                  )}
                  {hero.expedition_skill_2 && (
                    <div>
                      <div className="font-medium text-frost text-sm">{hero.expedition_skill_2}</div>
                      {hero.expedition_skill_2_desc && (
                        <div className="text-xs text-frost-muted mt-1">{hero.expedition_skill_2_desc}</div>
                      )}
                    </div>
                  )}
                  {hero.expedition_skill_3 && (
                    <div>
                      <div className="font-medium text-frost text-sm">{hero.expedition_skill_3}</div>
                      {hero.expedition_skill_3_desc && (
                        <div className="text-xs text-frost-muted mt-1">{hero.expedition_skill_3_desc}</div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Mythic Gear */}
          {hero.mythic_gear && (
            <div className="bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/30 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs px-2 py-0.5 rounded bg-gradient-to-r from-amber-500 to-orange-500 text-black font-bold">
                  MYTHIC GEAR
                </span>
              </div>
              <div className="text-frost font-medium">{hero.mythic_gear}</div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="sticky bottom-0 bg-surface border-t border-surface-border p-4 flex justify-end gap-3">
          {!isOwned && onAdd && (
            <button
              onClick={onAdd}
              className="px-4 py-2 bg-success/20 text-success hover:bg-success/30 rounded-lg font-medium transition-colors flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Add to Collection
            </button>
          )}
          <button
            onClick={onClose}
            className="px-4 py-2 bg-surface-hover text-frost hover:bg-surface-border rounded-lg font-medium transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
