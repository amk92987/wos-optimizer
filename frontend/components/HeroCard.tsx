'use client';

import { useState } from 'react';
import { UserHero } from '@/lib/api';
import Expander from './Expander';
import HeroRoleBadges from './HeroRoleBadges';

interface HeroCardProps {
  hero: UserHero;
  onUpdate?: (heroId: number, data: Partial<UserHero>) => void;
  onRemove?: () => void;
}

const GEAR_SLOTS = ['Weapon', 'Armor', 'Helmet', 'Boots'];
const GEAR_ICONS = ['⚔️', '🛡️', '⛑️', '👢'];
const QUALITY_OPTIONS = ['None', 'Gray', 'Green', 'Blue', 'Purple', 'Gold', 'Legendary'];
const QUALITY_COLORS: Record<number, string> = {
  0: 'bg-zinc-700 text-zinc-500',
  1: 'bg-zinc-600 text-zinc-300',
  2: 'bg-green-900/50 text-green-400',
  3: 'bg-blue-900/50 text-blue-400',
  4: 'bg-purple-900/50 text-purple-400',
  5: 'bg-amber-900/50 text-amber-400',
  6: 'bg-orange-900/50 text-orange-300',
};

export default function HeroCard({ hero, onUpdate, onRemove }: HeroCardProps) {
  const [isEditing, setIsEditing] = useState(false);

  // Basic stats
  const [level, setLevel] = useState(hero.level);
  const [stars, setStars] = useState(hero.stars);
  const [ascension, setAscension] = useState(hero.ascension);

  // Skills
  const [explorationSkill1, setExplorationSkill1] = useState(hero.exploration_skill_1);
  const [explorationSkill2, setExplorationSkill2] = useState(hero.exploration_skill_2);
  const [explorationSkill3, setExplorationSkill3] = useState(hero.exploration_skill_3);
  const [expeditionSkill1, setExpeditionSkill1] = useState(hero.expedition_skill_1);
  const [expeditionSkill2, setExpeditionSkill2] = useState(hero.expedition_skill_2);
  const [expeditionSkill3, setExpeditionSkill3] = useState(hero.expedition_skill_3);

  // Gear
  const [gear, setGear] = useState({
    slot1: { quality: hero.gear_slot1_quality, level: hero.gear_slot1_level, mastery: hero.gear_slot1_mastery },
    slot2: { quality: hero.gear_slot2_quality, level: hero.gear_slot2_level, mastery: hero.gear_slot2_mastery },
    slot3: { quality: hero.gear_slot3_quality, level: hero.gear_slot3_level, mastery: hero.gear_slot3_mastery },
    slot4: { quality: hero.gear_slot4_quality, level: hero.gear_slot4_level, mastery: hero.gear_slot4_mastery },
  });

  // Mythic gear
  const [mythicUnlocked, setMythicUnlocked] = useState(hero.mythic_gear_unlocked);
  const [mythicQuality, setMythicQuality] = useState(hero.mythic_gear_quality);
  const [mythicLevel, setMythicLevel] = useState(hero.mythic_gear_level);
  const [mythicMastery, setMythicMastery] = useState(hero.mythic_gear_mastery);

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

  const getRarityClass = (tier: string | null) => {
    if (!tier) return 'rarity-common';
    const t = tier.toLowerCase();
    if (t === 's+') return 'rarity-legendary';
    if (t.includes('s')) return 'rarity-epic';
    if (t.includes('a')) return 'rarity-rare';
    return 'rarity-common';
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
      onUpdate(hero.hero_id, {
        level,
        stars,
        ascension,
        exploration_skill_1: explorationSkill1,
        exploration_skill_2: explorationSkill2,
        exploration_skill_3: explorationSkill3,
        expedition_skill_1: expeditionSkill1,
        expedition_skill_2: expeditionSkill2,
        expedition_skill_3: expeditionSkill3,
        gear_slot1_quality: gear.slot1.quality,
        gear_slot1_level: gear.slot1.level,
        gear_slot1_mastery: gear.slot1.mastery,
        gear_slot2_quality: gear.slot2.quality,
        gear_slot2_level: gear.slot2.level,
        gear_slot2_mastery: gear.slot2.mastery,
        gear_slot3_quality: gear.slot3.quality,
        gear_slot3_level: gear.slot3.level,
        gear_slot3_mastery: gear.slot3.mastery,
        gear_slot4_quality: gear.slot4.quality,
        gear_slot4_level: gear.slot4.level,
        gear_slot4_mastery: gear.slot4.mastery,
        mythic_gear_unlocked: mythicUnlocked,
        mythic_gear_quality: mythicQuality,
        mythic_gear_level: mythicLevel,
        mythic_gear_mastery: mythicMastery,
      });
    }
    setIsEditing(false);
  };

  const updateGear = (slot: 'slot1' | 'slot2' | 'slot3' | 'slot4', field: 'quality' | 'level' | 'mastery', value: number) => {
    setGear(prev => ({
      ...prev,
      [slot]: { ...prev[slot], [field]: value }
    }));
  };

  const renderStars = (count: number, max: number = 5) => {
    return (
      <div className="flex gap-0.5">
        {[...Array(max)].map((_, i) => (
          <span
            key={i}
            className={`text-sm ${i < count ? 'star-filled' : 'star-empty'}`}
          >
            ★
          </span>
        ))}
      </div>
    );
  };

  const renderSkillPips = (level: number) => {
    return (
      <span className="text-ice text-sm">
        {'●'.repeat(level)}{'○'.repeat(5 - level)}
      </span>
    );
  };

  const SkillRow = ({
    name,
    desc,
    level,
    onLevelChange,
    color = 'text-ice'
  }: {
    name: string | null;
    desc: string | null;
    level: number;
    onLevelChange: (v: number) => void;
    color?: string;
  }) => (
    <div className="flex items-center justify-between py-1">
      <div className="flex-1 min-w-0 flex items-center gap-1">
        <span
          className={`text-sm text-frost truncate ${desc ? 'cursor-help' : ''}`}
          title={desc || undefined}
        >
          {name || 'Unknown Skill'}
        </span>
        {desc && (
          <span className="text-ice/50 text-xs" title={desc}>
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </span>
        )}
      </div>
      {isEditing ? (
        <select
          value={level}
          onChange={(e) => onLevelChange(parseInt(e.target.value))}
          className="input py-0.5 px-2 text-sm w-16"
        >
          {[1, 2, 3, 4, 5].map(l => (
            <option key={l} value={l}>{l}</option>
          ))}
        </select>
      ) : (
        <span className={color}>{renderSkillPips(level)}</span>
      )}
    </div>
  );

  const GearSlot = ({
    index,
    slotKey
  }: {
    index: number;
    slotKey: 'slot1' | 'slot2' | 'slot3' | 'slot4';
  }) => {
    const slotData = gear[slotKey];

    return (
      <div className="space-y-1">
        <div className="flex items-center gap-1 text-xs text-frost-muted">
          <span>{GEAR_ICONS[index]}</span>
          <span>{GEAR_SLOTS[index]}</span>
        </div>
        {isEditing ? (
          <div className="space-y-1">
            <select
              value={slotData.quality}
              onChange={(e) => updateGear(slotKey, 'quality', parseInt(e.target.value))}
              className="input py-0.5 px-2 text-xs w-full"
            >
              {QUALITY_OPTIONS.map((q, i) => (
                <option key={i} value={i}>{q}</option>
              ))}
            </select>
            {slotData.quality > 0 && (
              <>
                <input
                  type="number"
                  value={slotData.level}
                  onChange={(e) => updateGear(slotKey, 'level', Math.min(100, parseInt(e.target.value) || 0))}
                  min={0}
                  max={100}
                  placeholder="Level"
                  className="input py-0.5 px-2 text-xs w-full"
                />
                {slotData.quality >= 5 && slotData.level >= 20 && (
                  <input
                    type="number"
                    value={slotData.mastery}
                    onChange={(e) => updateGear(slotKey, 'mastery', Math.min(20, parseInt(e.target.value) || 0))}
                    min={0}
                    max={20}
                    placeholder="Mastery"
                    className="input py-0.5 px-2 text-xs w-full"
                  />
                )}
              </>
            )}
          </div>
        ) : (
          <div className={`text-xs px-2 py-1 rounded ${QUALITY_COLORS[slotData.quality]}`}>
            {slotData.quality === 0 ? '-' : (
              <>
                {QUALITY_OPTIONS[slotData.quality]}
                {slotData.level > 0 && ` L${slotData.level}`}
                {slotData.mastery > 0 && ` M${slotData.mastery}`}
              </>
            )}
          </div>
        )}
      </div>
    );
  };

  const heroHeader = (
    <div className="flex items-center gap-4 w-full">
      {/* Hero Image */}
      <div className={`w-16 h-16 rounded-xl overflow-hidden bg-surface-hover flex-shrink-0 border-2 ${getRarityClass(hero.tier_overall)}`}>
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
        <div className="flex items-center gap-3 text-sm mb-1">
          <span className={getClassBadge(hero.hero_class)}>
            {hero.hero_class}
          </span>
          <span className="text-zinc-500">Gen {hero.generation}</span>
        </div>
        <HeroRoleBadges heroName={hero.name} />
      </div>

      {/* Level & Stars */}
      <div className="text-right flex-shrink-0">
        <p className="text-lg font-bold text-amber">Lv.{hero.level}</p>
        <div className="flex items-center gap-1">
          {renderStars(hero.stars)}
          {hero.stars < 5 && hero.ascension > 0 && (
            <div className="flex gap-0.5 ml-1">
              {[...Array(5)].map((_, i) => (
                <span key={i} className={i < hero.ascension ? 'ascension-pip-filled' : 'ascension-pip-empty'} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <Expander title={heroHeader} className="mb-3">
      <div className="space-y-4">
        {/* Stats Row */}
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="text-xs text-zinc-500 block mb-1">Level</label>
            {isEditing ? (
              <input
                type="number"
                value={level}
                onChange={(e) => setLevel(parseInt(e.target.value) || 1)}
                min={1}
                max={80}
                className="input py-1 text-sm w-full"
              />
            ) : (
              <p className="font-medium text-zinc-100">{hero.level}</p>
            )}
          </div>
          <div>
            <label className="text-xs text-zinc-500 block mb-1">Stars</label>
            {isEditing ? (
              <select
                value={stars}
                onChange={(e) => setStars(parseInt(e.target.value))}
                className="input py-1 text-sm w-full"
              >
                {[0, 1, 2, 3, 4, 5].map(s => (
                  <option key={s} value={s}>{s} ★</option>
                ))}
              </select>
            ) : (
              <div>{renderStars(hero.stars)}</div>
            )}
          </div>
          <div>
            <label className="text-xs text-zinc-500 block mb-1">Ascension</label>
            {isEditing ? (
              stars < 5 ? (
                <select
                  value={ascension}
                  onChange={(e) => setAscension(parseInt(e.target.value))}
                  className="input py-1 text-sm w-full"
                >
                  {[0, 1, 2, 3, 4, 5].map(a => (
                    <option key={a} value={a}>{a}/5</option>
                  ))}
                </select>
              ) : (
                <p className="text-success text-sm">MAX</p>
              )
            ) : (
              <p className="font-medium text-zinc-100">
                {hero.stars >= 5 ? <span className="text-success">MAX</span> : `${hero.ascension}/5`}
              </p>
            )}
          </div>
        </div>

        {/* Skills */}
        <div className="grid grid-cols-2 gap-4">
          <div className="card bg-background">
            <h4 className="text-xs font-medium text-ice mb-2 uppercase tracking-wide">Exploration Skills</h4>
            <div className="space-y-1">
              <SkillRow
                name={hero.exploration_skill_1_name}
                desc={hero.exploration_skill_1_desc}
                level={isEditing ? explorationSkill1 : hero.exploration_skill_1}
                onLevelChange={setExplorationSkill1}
              />
              <SkillRow
                name={hero.exploration_skill_2_name}
                desc={hero.exploration_skill_2_desc}
                level={isEditing ? explorationSkill2 : hero.exploration_skill_2}
                onLevelChange={setExplorationSkill2}
              />
              {hero.exploration_skill_3_name && (
                <SkillRow
                  name={hero.exploration_skill_3_name}
                  desc={hero.exploration_skill_3_desc}
                  level={isEditing ? explorationSkill3 : hero.exploration_skill_3}
                  onLevelChange={setExplorationSkill3}
                />
              )}
            </div>
          </div>

          <div className="card bg-background">
            <h4 className="text-xs font-medium text-fire mb-2 uppercase tracking-wide">Expedition Skills</h4>
            <div className="space-y-1">
              <SkillRow
                name={hero.expedition_skill_1_name}
                desc={hero.expedition_skill_1_desc}
                level={isEditing ? expeditionSkill1 : hero.expedition_skill_1}
                onLevelChange={setExpeditionSkill1}
                color="text-fire"
              />
              <SkillRow
                name={hero.expedition_skill_2_name}
                desc={hero.expedition_skill_2_desc}
                level={isEditing ? expeditionSkill2 : hero.expedition_skill_2}
                onLevelChange={setExpeditionSkill2}
                color="text-fire"
              />
              {hero.expedition_skill_3_name && (
                <SkillRow
                  name={hero.expedition_skill_3_name}
                  desc={hero.expedition_skill_3_desc}
                  level={isEditing ? expeditionSkill3 : hero.expedition_skill_3}
                  onLevelChange={setExpeditionSkill3}
                  color="text-fire"
                />
              )}
            </div>
          </div>
        </div>

        {/* Hero Gear */}
        <div className="card bg-background">
          <h4 className="text-xs font-medium text-frost-muted mb-3 uppercase tracking-wide">Hero Gear</h4>
          <div className="grid grid-cols-4 gap-3">
            <GearSlot index={0} slotKey="slot1" />
            <GearSlot index={1} slotKey="slot2" />
            <GearSlot index={2} slotKey="slot3" />
            <GearSlot index={3} slotKey="slot4" />
          </div>
        </div>

        {/* Mythic/Exclusive Gear */}
        {hero.mythic_gear_name && (
          <div className="card bg-background border-pink-500/30">
            <h4 className="text-xs font-medium text-pink-400 mb-3 uppercase tracking-wide">
              Exclusive Gear: {hero.mythic_gear_name}
            </h4>
            {isEditing ? (
              <div className="grid grid-cols-4 gap-3">
                <div>
                  <label className="text-xs text-frost-muted block mb-1">Unlocked</label>
                  <input
                    type="checkbox"
                    checked={mythicUnlocked}
                    onChange={(e) => setMythicUnlocked(e.target.checked)}
                    className="w-5 h-5"
                  />
                </div>
                {mythicUnlocked && (
                  <>
                    <div>
                      <label className="text-xs text-frost-muted block mb-1">Quality</label>
                      <select
                        value={mythicQuality}
                        onChange={(e) => setMythicQuality(parseInt(e.target.value))}
                        className="input py-0.5 px-2 text-xs w-full"
                      >
                        {['Gray', 'Green', 'Blue', 'Purple', 'Gold', 'Legendary'].map((q, i) => (
                          <option key={i} value={i + 1}>{q}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-frost-muted block mb-1">Level</label>
                      <input
                        type="number"
                        value={mythicLevel}
                        onChange={(e) => setMythicLevel(Math.min(100, parseInt(e.target.value) || 0))}
                        min={0}
                        max={100}
                        className="input py-0.5 px-2 text-xs w-full"
                      />
                    </div>
                    {mythicQuality >= 5 && mythicLevel >= 20 && (
                      <div>
                        <label className="text-xs text-frost-muted block mb-1">Mastery</label>
                        <input
                          type="number"
                          value={mythicMastery}
                          onChange={(e) => setMythicMastery(Math.min(20, parseInt(e.target.value) || 0))}
                          min={0}
                          max={20}
                          className="input py-0.5 px-2 text-xs w-full"
                        />
                      </div>
                    )}
                  </>
                )}
              </div>
            ) : (
              <div className="text-sm">
                {hero.mythic_gear_unlocked ? (
                  <span className={`px-2 py-1 rounded ${QUALITY_COLORS[hero.mythic_gear_quality]}`}>
                    {QUALITY_OPTIONS[hero.mythic_gear_quality] || 'Gray'}
                    {hero.mythic_gear_level > 0 && ` L${hero.mythic_gear_level}`}
                    {hero.mythic_gear_mastery > 0 && ` M${hero.mythic_gear_mastery}`}
                  </span>
                ) : (
                  <span className="text-frost-muted">Not unlocked</span>
                )}
              </div>
            )}
          </div>
        )}

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
