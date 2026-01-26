'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';

interface ChiefGear {
  slot: string;
  name: string;
  quality: number;
  level: number;
  mastery: number;
  troopType: string;
}

interface ChiefCharm {
  slot: string;
  type: string;
  level: string; // String to support sub-levels like "4-1", "4-2"
}

const gearSlots = [
  { id: 'cap', name: 'Cap', type: 'Lancer', icon: '🎩', charmType: 'Keenness' },
  { id: 'coat', name: 'Coat', type: 'Infantry', icon: '🧥', charmType: 'Protection' },
  { id: 'pants', name: 'Pants', type: 'Infantry', icon: '👖', charmType: 'Protection' },
  { id: 'belt', name: 'Belt', type: 'Marksman', icon: '🔗', charmType: 'Vision' },
  { id: 'watch', name: 'Watch', type: 'Lancer', icon: '⌚', charmType: 'Keenness' },
  { id: 'shortstaff', name: 'Shortstaff', type: 'Marksman', icon: '🪄', charmType: 'Vision' },
];

const qualityLevels = [
  { value: 0, label: 'None', color: 'bg-zinc-600' },
  { value: 1, label: 'White', color: 'bg-zinc-400' },
  { value: 2, label: 'Green', color: 'bg-green-500' },
  { value: 3, label: 'Blue', color: 'bg-blue-500' },
  { value: 4, label: 'Purple', color: 'bg-purple-500' },
  { value: 5, label: 'Orange', color: 'bg-orange-500' },
  { value: 6, label: 'Gold', color: 'bg-yellow-400' },
  { value: 7, label: 'Mythic', color: 'bg-red-500' },
];

const charmLevels = [
  'None', '1', '2', '3',
  '4-1', '4-2', '4-3', '5-1', '5-2', '5-3',
  '6-1', '6-2', '6-3', '7-1', '7-2', '7-3',
  '8-1', '8-2', '8-3', '9-1', '9-2', '9-3',
  '10-1', '10-2', '10-3', '11-1', '11-2', '11-3',
  '12-1', '12-2', '12-3', '13-1', '13-2', '13-3',
  '14-1', '14-2', '14-3', '15-1', '15-2', '15-3',
  '16',
];

type TabType = 'gear' | 'charms' | 'priority';

export default function ChiefTrackerPage() {
  const { token } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('gear');
  const [gear, setGear] = useState<Record<string, ChiefGear>>({});
  const [charms, setCharms] = useState<Record<string, ChiefCharm[]>>({});
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

  const handleUpdateGear = async (slotId: string, updates: Partial<ChiefGear>) => {
    const currentGear = gear[slotId] || { slot: slotId, quality: 0, level: 0, mastery: 0 };
    const updated = { ...currentGear, ...updates };

    setGear((prev) => ({ ...prev, [slotId]: updated }));
    setIsSaving(true);

    try {
      await fetch('http://localhost:8000/api/chief/gear', {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ [slotId]: updated }),
      });
    } catch (error) {
      console.error('Failed to save gear:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleUpdateCharm = async (slotId: string, charmIndex: number, level: string) => {
    const slotCharms = charms[slotId] || [
      { slot: slotId, type: 'slot1', level: 'None' },
      { slot: slotId, type: 'slot2', level: 'None' },
      { slot: slotId, type: 'slot3', level: 'None' },
    ];
    const updated = [...slotCharms];
    updated[charmIndex] = { ...updated[charmIndex], level };

    setCharms((prev) => ({ ...prev, [slotId]: updated }));
    setIsSaving(true);

    try {
      await fetch('http://localhost:8000/api/chief/charms', {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ [slotId]: updated }),
      });
    } catch (error) {
      console.error('Failed to save charms:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const getGearForSlot = (slotId: string) => {
    return gear[slotId] || { slot: slotId, quality: 0, level: 0, mastery: 0 };
  };

  const getCharmsForSlot = (slotId: string) => {
    return charms[slotId] || [
      { slot: slotId, type: 'slot1', level: 'None' },
      { slot: slotId, type: 'slot2', level: 'None' },
      { slot: slotId, type: 'slot3', level: 'None' },
    ];
  };

  const typeColors: Record<string, string> = {
    Infantry: 'text-red-400 border-red-400/30',
    Lancer: 'text-green-400 border-green-400/30',
    Marksman: 'text-blue-400 border-blue-400/30',
  };

  const charmTypeColors: Record<string, string> = {
    Keenness: 'bg-green-500/10 border-green-500/30 text-green-400',
    Protection: 'bg-red-500/10 border-red-500/30 text-red-400',
    Vision: 'bg-blue-500/10 border-blue-500/30 text-blue-400',
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
          <p className="text-frost-muted mt-2">Track your chief gear, charms, and upgrade priorities</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-surface-border pb-2">
          <button
            onClick={() => setActiveTab('gear')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'gear'
                ? 'bg-ice/20 text-ice'
                : 'text-frost-muted hover:text-frost hover:bg-surface'
            }`}
          >
            Chief Gear
          </button>
          <button
            onClick={() => setActiveTab('charms')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'charms'
                ? 'bg-ice/20 text-ice'
                : 'text-frost-muted hover:text-frost hover:bg-surface'
            }`}
          >
            Chief Charms
          </button>
          <button
            onClick={() => setActiveTab('priority')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'priority'
                ? 'bg-ice/20 text-ice'
                : 'text-frost-muted hover:text-frost hover:bg-surface'
            }`}
          >
            Upgrade Priority
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'gear' && (
          <GearTab
            gearSlots={gearSlots}
            qualityLevels={qualityLevels}
            getGearForSlot={getGearForSlot}
            handleUpdateGear={handleUpdateGear}
            typeColors={typeColors}
          />
        )}
        {activeTab === 'charms' && (
          <CharmsTab
            gearSlots={gearSlots}
            charmLevels={charmLevels}
            getCharmsForSlot={getCharmsForSlot}
            handleUpdateCharm={handleUpdateCharm}
            charmTypeColors={charmTypeColors}
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
  gearSlots,
  qualityLevels,
  getGearForSlot,
  handleUpdateGear,
  typeColors,
}: {
  gearSlots: typeof gearSlots;
  qualityLevels: typeof qualityLevels;
  getGearForSlot: (id: string) => ChiefGear;
  handleUpdateGear: (id: string, updates: Partial<ChiefGear>) => void;
  typeColors: Record<string, string>;
}) {
  return (
    <>
      <div className="grid md:grid-cols-2 gap-4 mb-8">
        {gearSlots.map((slot) => {
          const slotGear = getGearForSlot(slot.id);
          const quality = qualityLevels.find((q) => q.value === slotGear.quality) || qualityLevels[0];

          return (
            <div key={slot.id} className={`card border ${typeColors[slot.type]}`}>
              <div className="flex items-center gap-3 mb-4">
                <span className="text-3xl">{slot.icon}</span>
                <div>
                  <h3 className="font-medium text-frost">{slot.name}</h3>
                  <p className={`text-sm ${typeColors[slot.type].split(' ')[0]}`}>
                    {slot.type} Gear
                  </p>
                </div>
              </div>

              {/* Quality */}
              <div className="mb-4">
                <label className="text-xs text-frost-muted block mb-2">Quality</label>
                <div className="flex flex-wrap gap-1">
                  {qualityLevels.map((q) => (
                    <button
                      key={q.value}
                      onClick={() => handleUpdateGear(slot.id, { quality: q.value })}
                      className={`px-2 py-1 rounded text-xs font-medium transition-all ${
                        slotGear.quality === q.value
                          ? `${q.color} text-white ring-2 ring-white/30`
                          : 'bg-surface text-frost-muted hover:bg-surface-hover'
                      }`}
                    >
                      {q.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Level & Mastery */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-frost-muted block mb-1">Level</label>
                  <input
                    type="number"
                    value={slotGear.level || ''}
                    onChange={(e) => handleUpdateGear(slot.id, { level: parseInt(e.target.value) || 0 })}
                    className="input text-sm"
                    min={0}
                    max={100}
                    placeholder="0-100"
                  />
                </div>
                {slotGear.quality >= 6 && (
                  <div>
                    <label className="text-xs text-frost-muted block mb-1">Mastery</label>
                    <input
                      type="number"
                      value={slotGear.mastery || ''}
                      onChange={(e) => handleUpdateGear(slot.id, { mastery: parseInt(e.target.value) || 0 })}
                      className="input text-sm"
                      min={0}
                      max={20}
                      placeholder="0-20"
                    />
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Tips */}
      <div className="card">
        <h2 className="section-header">Chief Gear Tips</h2>
        <ul className="space-y-2 text-sm text-frost-muted">
          <li className="flex items-start gap-2">
            <span className="text-ice">•</span>
            <span>Focus on one troop type's gear first for maximum impact</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-ice">•</span>
            <span>Gold quality (6) unlocks mastery for additional stats</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-ice">•</span>
            <span>Mythic gear provides the biggest stat boost - prioritize one set</span>
          </li>
        </ul>
      </div>
    </>
  );
}

function CharmsTab({
  gearSlots,
  charmLevels,
  getCharmsForSlot,
  handleUpdateCharm,
  charmTypeColors,
}: {
  gearSlots: typeof gearSlots;
  charmLevels: string[];
  getCharmsForSlot: (id: string) => ChiefCharm[];
  handleUpdateCharm: (slotId: string, charmIndex: number, level: string) => void;
  charmTypeColors: Record<string, string>;
}) {
  return (
    <>
      <div className="card mb-6">
        <p className="text-sm text-frost-muted mb-4">
          Unlocks at <strong className="text-frost">Furnace 25</strong>. Each gear piece has 3 charm slots of the same type.
        </p>

        <div className="grid grid-cols-3 gap-4 text-sm mb-6">
          <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/20">
            <p className="font-medium text-green-400">Keenness</p>
            <p className="text-frost-muted text-xs">Cap, Watch</p>
            <p className="text-frost-muted text-xs">Lancer buffs</p>
          </div>
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20">
            <p className="font-medium text-red-400">Protection</p>
            <p className="text-frost-muted text-xs">Coat, Pants</p>
            <p className="text-frost-muted text-xs">Infantry buffs</p>
          </div>
          <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
            <p className="font-medium text-blue-400">Vision</p>
            <p className="text-frost-muted text-xs">Belt, Shortstaff</p>
            <p className="text-frost-muted text-xs">Marksman buffs</p>
          </div>
        </div>
      </div>

      {/* Charm Grid */}
      <div className="grid md:grid-cols-2 gap-4 mb-6">
        {gearSlots.map((slot) => {
          const slotCharms = getCharmsForSlot(slot.id);

          return (
            <div key={slot.id} className={`card border ${charmTypeColors[slot.charmType]}`}>
              <div className="flex items-center gap-3 mb-4">
                <span className="text-2xl">{slot.icon}</span>
                <div>
                  <h3 className="font-medium text-frost">{slot.name}</h3>
                  <p className={`text-sm ${charmTypeColors[slot.charmType].split(' ')[2]}`}>
                    {slot.charmType} Charms
                  </p>
                </div>
              </div>

              {/* Triangular Charm Layout */}
              <div className="flex flex-col items-center gap-2">
                {/* Top charm */}
                <select
                  value={slotCharms[0]?.level || 'None'}
                  onChange={(e) => handleUpdateCharm(slot.id, 0, e.target.value)}
                  className="input text-sm w-24 text-center"
                >
                  {charmLevels.map((level) => (
                    <option key={level} value={level}>
                      {level}
                    </option>
                  ))}
                </select>
                {/* Bottom two charms */}
                <div className="flex gap-4">
                  <select
                    value={slotCharms[1]?.level || 'None'}
                    onChange={(e) => handleUpdateCharm(slot.id, 1, e.target.value)}
                    className="input text-sm w-24 text-center"
                  >
                    {charmLevels.map((level) => (
                      <option key={level} value={level}>
                        {level}
                      </option>
                    ))}
                  </select>
                  <select
                    value={slotCharms[2]?.level || 'None'}
                    onChange={(e) => handleUpdateCharm(slot.id, 2, e.target.value)}
                    className="input text-sm w-24 text-center"
                  >
                    {charmLevels.map((level) => (
                      <option key={level} value={level}>
                        {level}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          );
        })}
      </div>

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
            <span>Levels 4-15 have sub-levels (e.g., 4-1 → 4-2 → 4-3 → 5)</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-ice">•</span>
            <span>Focus on your main troop type's charms first</span>
          </li>
        </ul>
      </div>
    </>
  );
}

function PriorityTab() {
  return (
    <div className="space-y-6">
      {/* Upgrade Priority Order */}
      <div className="card">
        <h2 className="section-header">Chief Gear Upgrade Priority</h2>
        <ol className="space-y-3">
          <li className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-fire flex items-center justify-center text-white text-sm font-bold shrink-0">1</span>
            <div>
              <p className="font-medium text-frost">Main Troop Type Gear to Gold</p>
              <p className="text-sm text-frost-muted">Get all 2 pieces (e.g., Cap + Watch for Lancer) to Gold quality first</p>
            </div>
          </li>
          <li className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-fire/80 flex items-center justify-center text-white text-sm font-bold shrink-0">2</span>
            <div>
              <p className="font-medium text-frost">Level to 60+</p>
              <p className="text-sm text-frost-muted">Each level provides meaningful stat increases</p>
            </div>
          </li>
          <li className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-fire/60 flex items-center justify-center text-white text-sm font-bold shrink-0">3</span>
            <div>
              <p className="font-medium text-frost">Max Mastery (20)</p>
              <p className="text-sm text-frost-muted">Unlocks at Gold - provides additional stats</p>
            </div>
          </li>
          <li className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-fire/40 flex items-center justify-center text-white text-sm font-bold shrink-0">4</span>
            <div>
              <p className="font-medium text-frost">Push to Mythic</p>
              <p className="text-sm text-frost-muted">Biggest stat jump but expensive - prioritize one set</p>
            </div>
          </li>
          <li className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-fire/20 flex items-center justify-center text-white text-sm font-bold shrink-0">5</span>
            <div>
              <p className="font-medium text-frost">Secondary Troop Type</p>
              <p className="text-sm text-frost-muted">Then work on your secondary army</p>
            </div>
          </li>
        </ol>
      </div>

      {/* Charm Priority */}
      <div className="card">
        <h2 className="section-header">Chief Charm Upgrade Priority</h2>
        <ol className="space-y-3">
          <li className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-ice flex items-center justify-center text-white text-sm font-bold shrink-0">1</span>
            <div>
              <p className="font-medium text-frost">All slots to Level 3</p>
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
      <div className="card border-warning/30 bg-warning/5">
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
            <p className="text-xs text-frost-muted mt-2">Gear: Belt, Shortstaff</p>
          </div>
        </div>
      </div>
    </div>
  );
}
