'use client';

import { useState, useCallback } from 'react';
import { UserHero } from '@/lib/api';
import { useAutoSave } from '@/hooks/useAutoSave';
import Expander from './Expander';
import HeroRoleBadges from './HeroRoleBadges';
import SaveIndicator from './hero/SaveIndicator';
import StarRating from './hero/StarRating';
import SkillPips from './hero/SkillPips';
import NumberStepper from './hero/NumberStepper';
import GearSlotEditor from './hero/GearSlotEditor';
import MythicGearEditor from './hero/MythicGearEditor';

interface HeroCardProps {
  hero: UserHero;
  token: string | null;
  onSaved?: () => void;
  onRemove?: () => void;
}

const GEAR_SLOTS = ['Weapon', 'Armor', 'Helmet', 'Boots'];
const GEAR_ICONS = ['\u2694\uFE0F', '\uD83D\uDEE1\uFE0F', '\u26D1\uFE0F', '\uD83D\uDC62'];

export default function HeroCard({ hero, token, onSaved, onRemove }: HeroCardProps) {
  // Local state mirrors hero props, updated optimistically on interaction
  const [state, setState] = useState(() => ({
    level: hero.level,
    stars: hero.stars,
    ascension: hero.ascension,
    exploration_skill_1: hero.exploration_skill_1,
    exploration_skill_2: hero.exploration_skill_2,
    exploration_skill_3: hero.exploration_skill_3,
    expedition_skill_1: hero.expedition_skill_1,
    expedition_skill_2: hero.expedition_skill_2,
    expedition_skill_3: hero.expedition_skill_3,
    gear_slot1_quality: hero.gear_slot1_quality,
    gear_slot1_level: hero.gear_slot1_level,
    gear_slot1_mastery: hero.gear_slot1_mastery,
    gear_slot2_quality: hero.gear_slot2_quality,
    gear_slot2_level: hero.gear_slot2_level,
    gear_slot2_mastery: hero.gear_slot2_mastery,
    gear_slot3_quality: hero.gear_slot3_quality,
    gear_slot3_level: hero.gear_slot3_level,
    gear_slot3_mastery: hero.gear_slot3_mastery,
    gear_slot4_quality: hero.gear_slot4_quality,
    gear_slot4_level: hero.gear_slot4_level,
    gear_slot4_mastery: hero.gear_slot4_mastery,
    mythic_gear_unlocked: hero.mythic_gear_unlocked,
    mythic_gear_quality: hero.mythic_gear_quality,
    mythic_gear_level: hero.mythic_gear_level,
    mythic_gear_mastery: hero.mythic_gear_mastery,
    exclusive_gear_skill_level: hero.exclusive_gear_skill_level,
  }));

  const { saveField, saveFields, saveStatus } = useAutoSave({
    heroName: hero.hero_name,
    token,
    onSaved,
  });

  const update = useCallback((field: string, value: any) => {
    setState(prev => ({ ...prev, [field]: value }));
    saveField(field, value);
  }, [saveField]);

  const updateMultiple = useCallback((fields: Record<string, any>) => {
    setState(prev => ({ ...prev, ...fields }));
    saveFields(fields);
  }, [saveFields]);

  const getTierClass = (tier: string | null) => {
    if (!tier) return 'tier-b';
    const t = tier.toLowerCase();
    if (t === 's+') return 'tier-splus';
    if (t.includes('s')) return 'tier-s';
    if (t.includes('a')) return 'tier-a';
    if (t.includes('b')) return 'tier-b';
    if (t.includes('c')) return 'tier-c';
    return 'tier-d';
  };

  const getRarityClass = (rarity: string | null) => {
    if (!rarity) return 'rarity-common';
    const r = rarity.toLowerCase();
    if (r === 'legendary') return 'rarity-legendary';
    if (r === 'epic') return 'rarity-epic';
    if (r === 'rare') return 'rarity-rare';
    return 'rarity-common';
  };

  const getClassBadge = (heroClass: string) => {
    const c = heroClass.toLowerCase();
    if (c === 'infantry') return 'class-infantry';
    if (c === 'lancer') return 'class-lancer';
    if (c === 'marksman') return 'class-marksman';
    return 'badge-blue';
  };

  const renderStars = (count: number, max: number = 5) => (
    <div className="flex gap-0.5">
      {[...Array(max)].map((_, i) => (
        <svg key={i} width="16" height="16" viewBox="0 0 24 24">
          <path
            d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
            fill={i < count ? '#F59E0B' : 'transparent'}
            stroke={i < count ? '#F59E0B' : '#52525b'}
            strokeWidth="1.5"
          />
        </svg>
      ))}
    </div>
  );

  const renderShards = (count: number, max: number = 5) => (
    <div className="flex gap-0.5">
      {[...Array(max)].map((_, i) => (
        <svg key={i} width="10" height="10" viewBox="0 0 14 14">
          <path
            d="M7 1 L12 7 L7 13 L2 7 Z"
            fill={i < count ? '#A855F7' : 'transparent'}
            stroke={i < count ? '#A855F7' : '#52525b'}
            strokeWidth="1.2"
          />
        </svg>
      ))}
    </div>
  );

  const heroHeader = (
    <div className="flex items-center gap-4 w-full">
      {/* Hero Image */}
      <div className={`w-16 h-16 rounded-xl overflow-hidden bg-surface-hover flex-shrink-0 border-2 ${getRarityClass(hero.rarity)}`}>
        {hero.image_base64 ? (
          <img src={hero.image_base64} alt={hero.name} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-2xl">🦸</div>
        )}
      </div>

      {/* Hero Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <h3 className="font-semibold text-zinc-100 truncate">{hero.name}</h3>
          <span className={getTierClass(hero.tier_overall)}>
            {hero.tier_overall || 'B'}
          </span>
          <SaveIndicator status={saveStatus} />
        </div>
        <div className="flex items-center gap-3 text-sm mb-1">
          <span className={getClassBadge(hero.hero_class)}>{hero.hero_class}</span>
          <span className="text-zinc-500">Gen {hero.generation}</span>
        </div>
        <HeroRoleBadges heroName={hero.name} />
      </div>

      {/* Level & Stars */}
      <div className="text-right flex-shrink-0">
        <p className="text-lg font-bold text-amber">Lv.{state.level}</p>
        <div className="flex flex-col items-end gap-0.5">
          {renderStars(state.stars)}
          {state.stars < 5 && state.ascension > 0 && renderShards(state.ascension)}
        </div>
      </div>
    </div>
  );

  const gearSlots = [
    { key: 'slot1' as const, quality: state.gear_slot1_quality, level: state.gear_slot1_level, mastery: state.gear_slot1_mastery },
    { key: 'slot2' as const, quality: state.gear_slot2_quality, level: state.gear_slot2_level, mastery: state.gear_slot2_mastery },
    { key: 'slot3' as const, quality: state.gear_slot3_quality, level: state.gear_slot3_level, mastery: state.gear_slot3_mastery },
    { key: 'slot4' as const, quality: state.gear_slot4_quality, level: state.gear_slot4_level, mastery: state.gear_slot4_mastery },
  ];

  return (
    <Expander title={heroHeader} className="mb-3">
      <div className="space-y-4">
        {/* Level + Stars/Ascension row */}
        <div className="flex items-start justify-between gap-4">
          <div>
            <label className="text-xs text-zinc-500 block mb-1">Level</label>
            <NumberStepper
              value={state.level}
              min={1}
              max={80}
              onChange={(v) => update('level', v)}
              size="md"
            />
          </div>
          <div>
            <label className="text-xs text-zinc-500 block mb-1">Stars & Ascension</label>
            <StarRating
              stars={state.stars}
              ascension={state.ascension}
              onStarsChange={(v) => update('stars', v)}
              onAscensionChange={(v) => update('ascension', v)}
            />
          </div>
        </div>

        {/* Skills */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="card bg-background">
            <h4 className="text-xs font-medium text-ice mb-2 uppercase tracking-wide">Exploration Skills</h4>
            <div className="space-y-1">
              <SkillPips
                skillName={hero.exploration_skill_1_name}
                skillDesc={hero.exploration_skill_1_desc}
                level={state.exploration_skill_1}
                onChange={(v) => update('exploration_skill_1', v)}
                color="green"
              />
              <SkillPips
                skillName={hero.exploration_skill_2_name}
                skillDesc={hero.exploration_skill_2_desc}
                level={state.exploration_skill_2}
                onChange={(v) => update('exploration_skill_2', v)}
                color="green"
              />
              {hero.exploration_skill_3_name && (
                <SkillPips
                  skillName={hero.exploration_skill_3_name}
                  skillDesc={hero.exploration_skill_3_desc}
                  level={state.exploration_skill_3}
                  onChange={(v) => update('exploration_skill_3', v)}
                  color="green"
                />
              )}
            </div>
          </div>

          <div className="card bg-background">
            <h4 className="text-xs font-medium text-fire mb-2 uppercase tracking-wide">Expedition Skills</h4>
            <div className="space-y-1">
              <SkillPips
                skillName={hero.expedition_skill_1_name}
                skillDesc={hero.expedition_skill_1_desc}
                level={state.expedition_skill_1}
                onChange={(v) => update('expedition_skill_1', v)}
                color="orange"
              />
              <SkillPips
                skillName={hero.expedition_skill_2_name}
                skillDesc={hero.expedition_skill_2_desc}
                level={state.expedition_skill_2}
                onChange={(v) => update('expedition_skill_2', v)}
                color="orange"
              />
              {hero.expedition_skill_3_name && (
                <SkillPips
                  skillName={hero.expedition_skill_3_name}
                  skillDesc={hero.expedition_skill_3_desc}
                  level={state.expedition_skill_3}
                  onChange={(v) => update('expedition_skill_3', v)}
                  color="orange"
                />
              )}
            </div>
          </div>
        </div>

        {/* Hero Gear */}
        <div className="card bg-background">
          <h4 className="text-xs font-medium text-frost-muted mb-3 uppercase tracking-wide">Hero Gear</h4>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {gearSlots.map((slot, index) => (
              <GearSlotEditor
                key={slot.key}
                label={GEAR_SLOTS[index]}
                icon={GEAR_ICONS[index]}
                quality={slot.quality}
                level={slot.level}
                mastery={slot.mastery}
                onQualityChange={(v) => update(`gear_${slot.key}_quality`, v)}
                onLevelChange={(v) => update(`gear_${slot.key}_level`, v)}
                onMasteryChange={(v) => update(`gear_${slot.key}_mastery`, v)}
              />
            ))}
          </div>
        </div>

        {/* Mythic/Exclusive Gear */}
        {hero.mythic_gear_name && (
          <div className="card bg-background border-pink-500/30">
            <h4 className="text-xs font-medium text-pink-400 mb-3 uppercase tracking-wide">
              Exclusive Gear
            </h4>
            <MythicGearEditor
              gearName={hero.mythic_gear_name}
              unlocked={state.mythic_gear_unlocked}
              level={state.mythic_gear_level}
              skillLevel={state.exclusive_gear_skill_level}
              onUnlockedChange={(v) => update('mythic_gear_unlocked', v)}
              onLevelChange={(v) => update('mythic_gear_level', v)}
              onSkillLevelChange={(v) => update('exclusive_gear_skill_level', v)}
            />
          </div>
        )}

        {/* Remove action */}
        {onRemove && (
          <div className="pt-2 border-t border-border">
            <button
              onClick={onRemove}
              className="text-sm text-red-400 hover:text-red-300 transition-colors"
            >
              Remove from collection
            </button>
          </div>
        )}
      </div>
    </Expander>
  );
}
