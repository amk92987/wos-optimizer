'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';

interface GearSlot {
  id: string;
  displayName: string;
  type: string;
  icon: string;
  charmKey: string;
}

// 42-tier gear progression matching game's system
const GEAR_TIERS = [
  { id: 1, name: "Green 0★", color: "#2ECC71", bonus: 9.35 },
  { id: 2, name: "Green 1★", color: "#2ECC71", bonus: 12.75 },
  { id: 3, name: "Blue 0★", color: "#3498DB", bonus: 17.00 },
  { id: 4, name: "Blue 1★", color: "#3498DB", bonus: 20.25 },
  { id: 5, name: "Blue 2★", color: "#3498DB", bonus: 24.50 },
  { id: 6, name: "Blue 3★", color: "#3498DB", bonus: 29.75 },
  { id: 7, name: "Purple 0★", color: "#9B59B6", bonus: 34.00 },
  { id: 8, name: "Purple 1★", color: "#9B59B6", bonus: 38.00 },
  { id: 9, name: "Purple 2★", color: "#9B59B6", bonus: 42.50 },
  { id: 10, name: "Purple 3★", color: "#9B59B6", bonus: 47.00 },
  { id: 11, name: "Purple T1 0★", color: "#9B59B6", bonus: 48.50 },
  { id: 12, name: "Purple T1 1★", color: "#9B59B6", bonus: 50.00 },
  { id: 13, name: "Purple T1 2★", color: "#9B59B6", bonus: 52.00 },
  { id: 14, name: "Purple T1 3★", color: "#9B59B6", bonus: 54.23 },
  { id: 15, name: "Gold 0★", color: "#F1C40F", bonus: 56.78 },
  { id: 16, name: "Gold 1★", color: "#F1C40F", bonus: 59.50 },
  { id: 17, name: "Gold 2★", color: "#F1C40F", bonus: 62.50 },
  { id: 18, name: "Gold 3★", color: "#F1C40F", bonus: 66.00 },
  { id: 19, name: "Gold T1 0★", color: "#F1C40F", bonus: 69.00 },
  { id: 20, name: "Gold T1 1★", color: "#F1C40F", bonus: 72.00 },
  { id: 21, name: "Gold T1 2★", color: "#F1C40F", bonus: 75.50 },
  { id: 22, name: "Gold T1 3★", color: "#F1C40F", bonus: 79.00 },
  { id: 23, name: "Gold T2 0★", color: "#F1C40F", bonus: 80.50 },
  { id: 24, name: "Gold T2 1★", color: "#F1C40F", bonus: 82.00 },
  { id: 25, name: "Gold T2 2★", color: "#F1C40F", bonus: 83.50 },
  { id: 26, name: "Gold T2 3★", color: "#F1C40F", bonus: 85.00 },
  { id: 27, name: "Pink 0★", color: "#E84393", bonus: 89.25 },
  { id: 28, name: "Pink 1★", color: "#E84393", bonus: 94.00 },
  { id: 29, name: "Pink 2★", color: "#E84393", bonus: 99.00 },
  { id: 30, name: "Pink 3★", color: "#E84393", bonus: 104.50 },
  { id: 31, name: "Pink T1 0★", color: "#E84393", bonus: 110.00 },
  { id: 32, name: "Pink T1 1★", color: "#E84393", bonus: 116.00 },
  { id: 33, name: "Pink T1 2★", color: "#E84393", bonus: 122.50 },
  { id: 34, name: "Pink T1 3★", color: "#E84393", bonus: 129.00 },
  { id: 35, name: "Pink T2 0★", color: "#E84393", bonus: 136.00 },
  { id: 36, name: "Pink T2 1★", color: "#E84393", bonus: 143.50 },
  { id: 37, name: "Pink T2 2★", color: "#E84393", bonus: 151.50 },
  { id: 38, name: "Pink T2 3★", color: "#E84393", bonus: 160.00 },
  { id: 39, name: "Pink T3 0★", color: "#E84393", bonus: 165.00 },
  { id: 40, name: "Pink T3 1★", color: "#E84393", bonus: 171.00 },
  { id: 41, name: "Pink T3 2★", color: "#E84393", bonus: 178.00 },
  { id: 42, name: "Pink T3 3★", color: "#E84393", bonus: 187.00 },
];

// Gear slots with API field mapping
const gearSlots = [
  { id: 'helmet', displayName: 'Cap', type: 'Lancer', icon: '🎩', charmKey: 'cap' },
  { id: 'ring', displayName: 'Watch', type: 'Lancer', icon: '⌚', charmKey: 'watch' },
  { id: 'armor', displayName: 'Coat', type: 'Infantry', icon: '🧥', charmKey: 'coat' },
  { id: 'boots', displayName: 'Pants', type: 'Infantry', icon: '👖', charmKey: 'pants' },
  { id: 'gloves', displayName: 'Belt', type: 'Marksman', icon: '🔗', charmKey: 'belt' },
  { id: 'amulet', displayName: 'Weapon', type: 'Marksman', icon: '⚔️', charmKey: 'weapon' },
];

// Color options for tier selector
const TIER_COLORS = ['Green', 'Blue', 'Purple', 'Gold', 'Pink'];

// Build tier structure for cascading selects
function getTierStructure() {
  const structure: Record<string, Record<string, number[]>> = {};

  for (const tier of GEAR_TIERS) {
    const parts = tier.name.split(' ');
    const color = parts[0];
    let subtier = 'Base';
    let stars = 0;

    for (const p of parts) {
      if (p.startsWith('T') && p.length === 2) subtier = p;
      if (p.includes('★')) stars = parseInt(p);
    }

    if (!structure[color]) structure[color] = {};
    if (!structure[color][subtier]) structure[color][subtier] = [];
    if (!structure[color][subtier].includes(stars)) {
      structure[color][subtier].push(stars);
    }
  }

  return structure;
}

function getTierFromSelections(color: string, subtier: string, stars: number): number {
  const name = subtier === 'Base'
    ? `${color} ${stars}★`
    : `${color} ${subtier} ${stars}★`;
  const tier = GEAR_TIERS.find(t => t.name === name);
  return tier?.id || 1;
}

function parseTierToSelections(tierId: number): { color: string; subtier: string; stars: number } {
  const tier = GEAR_TIERS.find(t => t.id === tierId) || GEAR_TIERS[0];
  const parts = tier.name.split(' ');
  const color = parts[0];
  let subtier = 'Base';
  let stars = 0;

  for (const p of parts) {
    if (p.startsWith('T') && p.length === 2) subtier = p;
    if (p.includes('★')) stars = parseInt(p);
  }

  return { color, subtier, stars };
}

// Charm level options with sub-levels
const charmLevels = ['1', '2', '3'];
for (let level = 4; level <= 16; level++) {
  charmLevels.push(`${level}-1`, `${level}-2`, `${level}-3`);
}

// Charm stats by main level
const CHARM_STATS: Record<number, { bonus: number; shape: string }> = {
  1: { bonus: 9.0, shape: "△" },
  2: { bonus: 15.0, shape: "◇" },
  3: { bonus: 22.0, shape: "□" },
  4: { bonus: 29.0, shape: "□" },
  5: { bonus: 36.0, shape: "⬠" },
  6: { bonus: 43.0, shape: "⬠" },
  7: { bonus: 50.0, shape: "⬡" },
  8: { bonus: 57.0, shape: "⬡" },
  9: { bonus: 64.0, shape: "○" },
  10: { bonus: 71.0, shape: "○" },
  11: { bonus: 78.0, shape: "○" },
  12: { bonus: 83.0, shape: "○" },
  13: { bonus: 88.0, shape: "○" },
  14: { bonus: 93.0, shape: "○" },
  15: { bonus: 97.0, shape: "○" },
  16: { bonus: 100.0, shape: "●" },
};

function parseCharmLevel(value: string): number {
  if (value.includes('-')) return parseInt(value.split('-')[0]);
  return parseInt(value) || 1;
}

function getCharmBonus(level: string): number {
  const mainLevel = parseCharmLevel(level);
  return CHARM_STATS[mainLevel]?.bonus || 9.0;
}

function formatCharmDisplay(level: string): string {
  const mainLevel = parseCharmLevel(level);
  const shape = CHARM_STATS[mainLevel]?.shape || '△';
  const bonus = getCharmBonus(level);
  return `${shape} ${level} (+${bonus.toFixed(0)}%)`;
}

interface ChiefGearData {
  helmet_quality: number;
  armor_quality: number;
  gloves_quality: number;
  boots_quality: number;
  ring_quality: number;
  amulet_quality: number;
}

interface ChiefCharmData {
  cap_slot_1: string;
  cap_slot_2: string;
  cap_slot_3: string;
  watch_slot_1: string;
  watch_slot_2: string;
  watch_slot_3: string;
  coat_slot_1: string;
  coat_slot_2: string;
  coat_slot_3: string;
  pants_slot_1: string;
  pants_slot_2: string;
  pants_slot_3: string;
  belt_slot_1: string;
  belt_slot_2: string;
  belt_slot_3: string;
  weapon_slot_1: string;
  weapon_slot_2: string;
  weapon_slot_3: string;
}

type TabType = 'gear' | 'charms' | 'priority';

export default function ChiefTrackerPage() {
  const { token } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('gear');
  const [gear, setGear] = useState<ChiefGearData | null>(null);
  const [charms, setCharms] = useState<ChiefCharmData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (token) {
      fetchData();
    }
  }, [token]);

  const fetchData = async () => {
    try {
      const [gearRes, charmsRes] = await Promise.all([
        fetch('http://localhost:8000/api/chief/gear', {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch('http://localhost:8000/api/chief/charms', {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);
      if (gearRes.ok) setGear(await gearRes.json());
      if (charmsRes.ok) setCharms(await charmsRes.json());
    } catch (error) {
      console.error('Failed to fetch chief data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateGear = async (slotId: string, tierId: number) => {
    if (!gear) return;
    const qualityField = `${slotId}_quality` as keyof ChiefGearData;

    setGear(prev => prev ? { ...prev, [qualityField]: tierId } : null);
    setIsSaving(true);

    try {
      await fetch('http://localhost:8000/api/chief/gear', {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ [qualityField]: tierId }),
      });
    } catch (error) {
      console.error('Failed to save gear:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleUpdateCharm = async (field: string, value: string) => {
    if (!charms) return;

    setCharms(prev => prev ? { ...prev, [field]: value } : null);
    setIsSaving(true);

    try {
      await fetch('http://localhost:8000/api/chief/charms', {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ [field]: value }),
      });
    } catch (error) {
      console.error('Failed to save charms:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const typeColors: Record<string, string> = {
    Infantry: 'border-red-400/30',
    Lancer: 'border-green-400/30',
    Marksman: 'border-blue-400/30',
  };

  const typeTextColors: Record<string, string> = {
    Infantry: 'text-red-400',
    Lancer: 'text-green-400',
    Marksman: 'text-blue-400',
  };

  if (isLoading) {
    return (
      <PageLayout>
        <div className="max-w-4xl mx-auto">
          <div className="h-8 bg-surface rounded w-48 mb-8 animate-pulse" />
          <div className="grid md:grid-cols-2 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="card animate-pulse">
                <div className="h-6 bg-surface-hover rounded w-32 mb-4" />
                <div className="h-20 bg-surface-hover rounded" />
              </div>
            ))}
          </div>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Chief Tracker</h1>
          <p className="text-frost-muted mt-2">Track your chief gear and charms progression</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-surface-border pb-2">
          {[
            { id: 'gear' as const, label: 'Chief Gear' },
            { id: 'charms' as const, label: 'Chief Charms' },
            { id: 'priority' as const, label: 'Upgrade Priority' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-ice/20 text-ice'
                  : 'text-frost-muted hover:text-frost hover:bg-surface'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === 'gear' && gear && (
          <GearTab
            gear={gear}
            gearSlots={gearSlots}
            typeColors={typeColors}
            typeTextColors={typeTextColors}
            handleUpdateGear={handleUpdateGear}
          />
        )}
        {activeTab === 'charms' && charms && (
          <CharmsTab
            charms={charms}
            gearSlots={gearSlots}
            handleUpdateCharm={handleUpdateCharm}
          />
        )}
        {activeTab === 'priority' && <PriorityTab />}

        {/* Saving indicator */}
        {isSaving && (
          <div className="fixed bottom-4 right-4 bg-surface border border-surface-border px-4 py-2 rounded-lg shadow-lg">
            <span className="text-sm text-frost-muted">Saving...</span>
          </div>
        )}
      </div>
    </PageLayout>
  );
}

function GearTab({
  gear,
  gearSlots,
  typeColors,
  typeTextColors,
  handleUpdateGear,
}: {
  gear: ChiefGearData;
  gearSlots: GearSlot[];
  typeColors: Record<string, string>;
  typeTextColors: Record<string, string>;
  handleUpdateGear: (slotId: string, tierId: number) => void;
}) {
  const tierStructure = getTierStructure();

  // Group by troop type
  const troopGroups = [
    { type: 'Lancer', slots: gearSlots.filter((s: GearSlot) => s.type === 'Lancer') },
    { type: 'Infantry', slots: gearSlots.filter((s: GearSlot) => s.type === 'Infantry') },
    { type: 'Marksman', slots: gearSlots.filter((s: GearSlot) => s.type === 'Marksman') },
  ];

  return (
    <>
      {/* Info box */}
      <div className="card mb-6 border-ice/30 bg-ice/5">
        <p className="text-sm text-frost mb-2">
          Chief Gear boosts your troops based on type. Each piece progresses through tiers
          (Green → Blue → Purple → Gold → Pink) with sub-tiers (T1, T2, T3) and stars (0-3★).
        </p>
        <p className="text-xs text-warning">
          <strong>Set Bonus:</strong> 3-piece = Defense boost | 6-piece = Attack boost (same tier)
        </p>
      </div>

      {troopGroups.map((group) => (
        <div key={group.type} className="mb-6">
          <div className={`px-4 py-2 rounded-lg mb-3 bg-opacity-10 border-l-4 ${typeColors[group.type]}`}>
            <span className={`font-medium ${typeTextColors[group.type]}`}>{group.type} Gear</span>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {group.slots.map((slot) => {
              const qualityField = `${slot.id}_quality` as keyof ChiefGearData;
              const tierId = gear[qualityField] || 1;
              const tier = GEAR_TIERS.find(t => t.id === tierId) || GEAR_TIERS[0];
              const { color, subtier, stars } = parseTierToSelections(tierId);

              return (
                <div key={slot.id} className={`card border ${typeColors[slot.type]}`}>
                  <div className="flex items-center gap-3 mb-4">
                    <span className="text-3xl">{slot.icon}</span>
                    <div className="flex-1">
                      <h3 className="font-medium text-frost">{slot.displayName}</h3>
                      <div className="flex items-center gap-2">
                        <span
                          className="text-xs px-2 py-0.5 rounded font-medium"
                          style={{ backgroundColor: tier.color + '33', color: tier.color }}
                        >
                          {tier.name}
                        </span>
                        <span className="text-xs text-frost-muted">+{tier.bonus.toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>

                  {/* Cascading selectors */}
                  <div className="grid grid-cols-3 gap-2">
                    <div>
                      <label className="text-xs text-frost-muted block mb-1">Color</label>
                      <select
                        value={color}
                        onChange={(e) => {
                          const newColor = e.target.value;
                          const subtiers = Object.keys(tierStructure[newColor] || {});
                          const newSubtier = subtiers[0] || 'Base';
                          const newStars = tierStructure[newColor]?.[newSubtier]?.[0] || 0;
                          const newTierId = getTierFromSelections(newColor, newSubtier, newStars);
                          handleUpdateGear(slot.id, newTierId);
                        }}
                        className="input text-sm py-1"
                      >
                        {TIER_COLORS.map((c) => (
                          <option key={c} value={c}>{c}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-frost-muted block mb-1">Tier</label>
                      <select
                        value={subtier}
                        onChange={(e) => {
                          const newSubtier = e.target.value;
                          const newStars = tierStructure[color]?.[newSubtier]?.[0] || 0;
                          const newTierId = getTierFromSelections(color, newSubtier, newStars);
                          handleUpdateGear(slot.id, newTierId);
                        }}
                        className="input text-sm py-1"
                      >
                        {Object.keys(tierStructure[color] || {}).map((s) => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-frost-muted block mb-1">Stars</label>
                      <select
                        value={stars}
                        onChange={(e) => {
                          const newStars = parseInt(e.target.value);
                          const newTierId = getTierFromSelections(color, subtier, newStars);
                          handleUpdateGear(slot.id, newTierId);
                        }}
                        className="input text-sm py-1"
                      >
                        {(tierStructure[color]?.[subtier] || [0]).map((s) => (
                          <option key={s} value={s}>{s}★</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}

      {/* Tips */}
      <div className="card">
        <h2 className="section-header">Chief Gear Tips</h2>
        <ul className="space-y-2 text-sm text-frost-muted">
          <li className="flex items-start gap-2">
            <span className="text-ice">•</span>
            <span>Keep all 6 pieces at the same tier for set bonuses</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-ice">•</span>
            <span>Gold T2 3★ unlocks the Enhancement Material Exchange</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-ice">•</span>
            <span>Pink gear provides the biggest stat boost - prioritize Infantry first</span>
          </li>
        </ul>
      </div>
    </>
  );
}

function CharmsTab({
  charms,
  gearSlots,
  handleUpdateCharm,
}: {
  charms: ChiefCharmData;
  gearSlots: GearSlot[];
  handleUpdateCharm: (field: string, value: string) => void;
}) {
  const charmTypeInfo = {
    Lancer: { name: 'Keenness', icon: '⚡', color: 'text-green-400', bgColor: 'bg-green-500/10', borderColor: 'border-green-500/30' },
    Infantry: { name: 'Protection', icon: '🛡️', color: 'text-red-400', bgColor: 'bg-red-500/10', borderColor: 'border-red-500/30' },
    Marksman: { name: 'Vision', icon: '👁️', color: 'text-blue-400', bgColor: 'bg-blue-500/10', borderColor: 'border-blue-500/30' },
  };

  // Calculate summary totals
  const calculateTotal = (slots: string[]) => {
    return slots.reduce((sum, field) => {
      const value = (charms as any)[field] || '1';
      return sum + parseCharmLevel(value);
    }, 0);
  };

  const lancerSlots = ['cap_slot_1', 'cap_slot_2', 'cap_slot_3', 'watch_slot_1', 'watch_slot_2', 'watch_slot_3'];
  const infantrySlots = ['coat_slot_1', 'coat_slot_2', 'coat_slot_3', 'pants_slot_1', 'pants_slot_2', 'pants_slot_3'];
  const marksmanSlots = ['belt_slot_1', 'belt_slot_2', 'belt_slot_3', 'weapon_slot_1', 'weapon_slot_2', 'weapon_slot_3'];

  const lancerTotal = calculateTotal(lancerSlots);
  const infantryTotal = calculateTotal(infantrySlots);
  const marksmanTotal = calculateTotal(marksmanSlots);

  return (
    <>
      {/* Info box */}
      <div className="card mb-6 border-ice/30 bg-ice/5">
        <p className="text-sm text-frost mb-2">
          Unlocks at <strong>Furnace 25</strong>. Each gear piece has 3 charm slots of the same type.
          Charms progress through sub-levels at 4+ (e.g., 4-1 → 4-2 → 4-3 → 5).
        </p>
        <div className="flex flex-wrap gap-4 text-xs mt-2">
          <span><span className="text-green-400">⚡ Keenness</span> = Cap & Watch (Lancer)</span>
          <span><span className="text-red-400">🛡️ Protection</span> = Coat & Pants (Infantry)</span>
          <span><span className="text-blue-400">👁️ Vision</span> = Belt & Weapon (Marksman)</span>
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="card text-center bg-green-500/10 border-green-500/30">
          <div className="text-green-400 font-medium">⚡ Keenness</div>
          <div className="text-xs text-frost-muted">Lancer Buff</div>
          <div className="text-2xl font-bold text-frost mt-2">{lancerTotal}/96</div>
          <div className="text-xs text-frost-muted">Avg Lv.{(lancerTotal / 6).toFixed(1)}</div>
        </div>
        <div className="card text-center bg-red-500/10 border-red-500/30">
          <div className="text-red-400 font-medium">🛡️ Protection</div>
          <div className="text-xs text-frost-muted">Infantry Buff</div>
          <div className="text-2xl font-bold text-frost mt-2">{infantryTotal}/96</div>
          <div className="text-xs text-frost-muted">Avg Lv.{(infantryTotal / 6).toFixed(1)}</div>
        </div>
        <div className="card text-center bg-blue-500/10 border-blue-500/30">
          <div className="text-blue-400 font-medium">👁️ Vision</div>
          <div className="text-xs text-frost-muted">Marksman Buff</div>
          <div className="text-2xl font-bold text-frost mt-2">{marksmanTotal}/96</div>
          <div className="text-xs text-frost-muted">Avg Lv.{(marksmanTotal / 6).toFixed(1)}</div>
        </div>
      </div>

      {/* Charm Grid by troop type */}
      {['Lancer', 'Infantry', 'Marksman'].map((troopType) => {
        const info = charmTypeInfo[troopType as keyof typeof charmTypeInfo];
        const slots = gearSlots.filter((s: GearSlot) => s.type === troopType);

        return (
          <div key={troopType} className="mb-6">
            <div className={`px-4 py-2 rounded-lg mb-3 ${info.bgColor} border-l-4 ${info.borderColor}`}>
              <span className={`font-medium ${info.color}`}>{info.icon} {troopType} Gear Charms ({info.name})</span>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              {slots.map((slot: GearSlot) => {
                const charmKey = slot.charmKey;
                const slot1 = (charms as any)[`${charmKey}_slot_1`] || '1';
                const slot2 = (charms as any)[`${charmKey}_slot_2`] || '1';
                const slot3 = (charms as any)[`${charmKey}_slot_3`] || '1';

                return (
                  <div key={slot.id} className={`card border ${info.borderColor}`}>
                    <div className="flex items-center gap-3 mb-4">
                      <span className="text-2xl">{slot.icon}</span>
                      <div>
                        <h3 className="font-medium text-frost">{slot.displayName}</h3>
                        <p className={`text-sm ${info.color}`}>3× {info.name} Charms</p>
                      </div>
                    </div>

                    {/* Triangular layout */}
                    <div className="flex flex-col items-center gap-2">
                      <div>
                        <div className="text-xs text-center mb-1">
                          <span className={info.color}>{info.icon}</span>
                          <span className="text-warning ml-1">+{getCharmBonus(slot1).toFixed(0)}%</span>
                        </div>
                        <select
                          value={slot1}
                          onChange={(e) => handleUpdateCharm(`${charmKey}_slot_1`, e.target.value)}
                          className="input text-sm w-28 text-center"
                        >
                          {charmLevels.map((level) => (
                            <option key={level} value={level}>{formatCharmDisplay(level)}</option>
                          ))}
                        </select>
                      </div>
                      <div className="flex gap-4">
                        <div>
                          <div className="text-xs text-center mb-1">
                            <span className={info.color}>{info.icon}</span>
                            <span className="text-warning ml-1">+{getCharmBonus(slot2).toFixed(0)}%</span>
                          </div>
                          <select
                            value={slot2}
                            onChange={(e) => handleUpdateCharm(`${charmKey}_slot_2`, e.target.value)}
                            className="input text-sm w-28 text-center"
                          >
                            {charmLevels.map((level) => (
                              <option key={level} value={level}>{formatCharmDisplay(level)}</option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <div className="text-xs text-center mb-1">
                            <span className={info.color}>{info.icon}</span>
                            <span className="text-warning ml-1">+{getCharmBonus(slot3).toFixed(0)}%</span>
                          </div>
                          <select
                            value={slot3}
                            onChange={(e) => handleUpdateCharm(`${charmKey}_slot_3`, e.target.value)}
                            className="input text-sm w-28 text-center"
                          >
                            {charmLevels.map((level) => (
                              <option key={level} value={level}>{formatCharmDisplay(level)}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}

      {/* Tips */}
      <div className="card">
        <h2 className="section-header">Charm Tips</h2>
        <ul className="space-y-2 text-sm text-frost-muted">
          <li className="flex items-start gap-2">
            <span className="text-ice">•</span>
            <span>Charm level 16 requires Generation 7 materials</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-ice">•</span>
            <span>Charms level 12+ require Jewel Secrets - plan your materials</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-ice">•</span>
            <span>Shape progression: △ → ◇ → □ → ⬠ → ⬡ → ●</span>
          </li>
        </ul>
      </div>
    </>
  );
}

function PriorityTab() {
  return (
    <div className="space-y-6">
      {/* When to focus */}
      <div className="card border-warning/30 bg-warning/5">
        <h2 className="section-header">When to Focus on Chief Gear/Charms</h2>
        <div className="space-y-3">
          <div className="flex items-start gap-3 p-3 rounded-lg bg-surface">
            <span className="text-frost-muted font-bold">F1-22</span>
            <p className="text-sm text-frost-muted">Focus on heroes and furnace. Chief gear unlocks at F22.</p>
          </div>
          <div className="flex items-start gap-3 p-3 rounded-lg bg-ice/10">
            <span className="text-ice font-bold">F22-FC</span>
            <p className="text-sm text-frost">Start upgrading Chief Gear. Keep all pieces at same tier for set bonus.</p>
          </div>
          <div className="flex items-start gap-3 p-3 rounded-lg bg-success/10">
            <span className="text-success font-bold">FC+</span>
            <p className="text-sm text-frost">Chief Gear/Charms become major power source. Balance with hero investment.</p>
          </div>
        </div>
      </div>

      {/* Gear Upgrade Order */}
      <div className="card">
        <h2 className="section-header">Chief Gear Upgrade Priority</h2>
        <ol className="space-y-3">
          <li className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-fire flex items-center justify-center text-white text-sm font-bold shrink-0">1</span>
            <div>
              <p className="font-medium text-frost">Infantry Gear First (Coat & Pants)</p>
              <p className="text-sm text-frost-muted">Frontline absorbs damage - prioritize defense</p>
            </div>
          </li>
          <li className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-fire/80 flex items-center justify-center text-white text-sm font-bold shrink-0">2</span>
            <div>
              <p className="font-medium text-frost">Marksman Gear Second (Belt & Weapon)</p>
              <p className="text-sm text-frost-muted">Key damage dealers need stat boosts</p>
            </div>
          </li>
          <li className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-fire/60 flex items-center justify-center text-white text-sm font-bold shrink-0">3</span>
            <div>
              <p className="font-medium text-frost">Lancer Gear Last (Cap & Watch)</p>
              <p className="text-sm text-frost-muted">Less exposed to direct fire</p>
            </div>
          </li>
        </ol>
      </div>

      {/* Charm Upgrade Order */}
      <div className="card">
        <h2 className="section-header">Chief Charm Upgrade Priority</h2>
        <ol className="space-y-3">
          <li className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-ice flex items-center justify-center text-white text-sm font-bold shrink-0">1</span>
            <div>
              <p className="font-medium text-frost">All Slots to Level 3</p>
              <p className="text-sm text-frost-muted">Quick wins with low material cost</p>
            </div>
          </li>
          <li className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-ice/80 flex items-center justify-center text-white text-sm font-bold shrink-0">2</span>
            <div>
              <p className="font-medium text-frost">Main Troop Type to Level 10</p>
              <p className="text-sm text-frost-muted">Focus on one type (all 6 charms for 2 gear pieces)</p>
            </div>
          </li>
          <li className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-ice/60 flex items-center justify-center text-white text-sm font-bold shrink-0">3</span>
            <div>
              <p className="font-medium text-frost">Push to Level 16 (Max)</p>
              <p className="text-sm text-frost-muted">Requires Gen 7 materials - long-term goal</p>
            </div>
          </li>
        </ol>
      </div>

      {/* Troop Type Selection */}
      <div className="card">
        <h2 className="section-header">Choosing Your Main Troop Type</h2>
        <div className="grid md:grid-cols-3 gap-4">
          <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20">
            <h3 className="font-medium text-red-400 mb-2">Infantry</h3>
            <p className="text-sm text-frost-muted">Best for garrison defense and tanking. Good for Crazy Joe.</p>
            <p className="text-xs text-frost-muted mt-2">Gear: Coat, Pants</p>
          </div>
          <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
            <h3 className="font-medium text-green-400 mb-2">Lancer</h3>
            <p className="text-sm text-frost-muted">Balanced offense/defense. Good for field combat.</p>
            <p className="text-xs text-frost-muted mt-2">Gear: Cap, Watch</p>
          </div>
          <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
            <h3 className="font-medium text-blue-400 mb-2">Marksman</h3>
            <p className="text-sm text-frost-muted">Highest damage output. Best for Bear Trap and rallies.</p>
            <p className="text-xs text-frost-muted mt-2">Gear: Belt, Weapon</p>
          </div>
        </div>
      </div>
    </div>
  );
}
