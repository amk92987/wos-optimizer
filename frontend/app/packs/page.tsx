'use client';

import { useState, useMemo } from 'react';
import Image from 'next/image';
import PageLayout from '@/components/PageLayout';

// Tier colors
const TIER_COLORS: Record<string, string> = {
  S: '#FFD700',
  A: '#9B59B6',
  B: '#3498DB',
  C: '#95A5A6',
  D: '#E74C3C',
};

// Price options
const PRICE_OPTIONS = [0.99, 1.99, 2.99, 4.99, 9.99, 14.99, 19.99, 29.99, 49.99, 99.99];

interface PackItem {
  id: string;
  name: string;
  image?: string;
  emoji?: string;
  fsValue: number;
  tier: string;
  desc: string;
  category: 'unique' | 'currency' | 'speedups' | 'resources';
}

// Pack items with Frost Star values (1 FS = $0.01)
const PACK_ITEMS: Record<string, { label: string; items: PackItem[] }> = {
  hero: {
    label: 'Hero Items',
    items: [
      { id: 'mythic_shard', name: 'Mythic Shards', image: 'mythic_hero_shard.png', fsValue: 33, tier: 'A', desc: 'Gold/orange shards for Mythic heroes', category: 'unique' },
      { id: 'epic_shard', name: 'Epic Shards', image: 'epic_hero_shard.png', fsValue: 17, tier: 'B', desc: 'Purple shards for Epic heroes', category: 'unique' },
      { id: 'rare_shard', name: 'Rare Shards', image: 'rare_hero_shard.png', fsValue: 8, tier: 'C', desc: 'Blue shards for Rare heroes', category: 'unique' },
      { id: 'hero_xp_1k', name: 'Hero XP (1k)', image: 'hero_xp.png', fsValue: 1, tier: 'C', desc: '1000 experience points', category: 'unique' },
      { id: 'mythic_exploration_manual', name: 'Mythic Explore Manual', image: 'mythic_exploration_manual.png', fsValue: 3.7, tier: 'B', desc: 'Exploration skills for Mythic heroes', category: 'unique' },
      { id: 'mythic_expedition_manual', name: 'Mythic Expedition Manual', image: 'mythic_expedition_manual.png', fsValue: 3.7, tier: 'B', desc: 'Expedition skills for Mythic heroes', category: 'unique' },
      { id: 'epic_exploration_manual', name: 'Epic Explore Manual', image: 'epic_exploration_manual.png', fsValue: 17, tier: 'B', desc: 'Exploration skills for Epic heroes', category: 'unique' },
      { id: 'epic_expedition_manual', name: 'Epic Expedition Manual', image: 'epic_expedition_manual.png', fsValue: 17, tier: 'B', desc: 'Expedition skills for Epic heroes', category: 'unique' },
    ],
  },
  heroGear: {
    label: 'Hero Gear',
    items: [
      { id: 'essence_stone', name: 'Essence Stones', image: 'essence_stone.png', fsValue: 22, tier: 'A', desc: 'For Mythic gear mastery. $0.22 each', category: 'unique' },
      { id: 'mithril', name: 'Mithril', image: 'mithril.png', fsValue: 141, tier: 'S', desc: 'Rare material for gear empowerment. $1.41 each', category: 'unique' },
      { id: 'xp_component', name: 'Hero Gear XP (per 100)', image: 'xp_component.png', fsValue: 13, tier: 'B', desc: 'Enhancement XP components', category: 'unique' },
      { id: 'hero_gear_chest', name: 'Hero Gear Chest', image: 'hero_gear_chest.png', fsValue: 8, tier: 'C', desc: 'Contains random hero gear pieces', category: 'unique' },
    ],
  },
  chiefGear: {
    label: 'Chief Gear',
    items: [
      { id: 'hardened_alloy', name: 'Hardened Alloy', image: 'hardened_alloy.png', fsValue: 0.067, tier: 'C', desc: 'Primary material for chief gear (cheap)', category: 'unique' },
      { id: 'polishing_solution', name: 'Polishing Solution', image: 'polishing_solution.png', fsValue: 6.7, tier: 'B', desc: '1 Polish = 100 Alloy in value', category: 'unique' },
      { id: 'design_plans', name: 'Design Plans', image: 'design_plans.png', fsValue: 10, tier: 'B', desc: 'Blueprints for Blue+ quality chief gear', category: 'unique' },
      { id: 'charm_design', name: 'Charm Designs', image: 'charm_design.png', fsValue: 22, tier: 'A', desc: 'Primary material for Chief Charm upgrades', category: 'unique' },
      { id: 'charm_guide', name: 'Charm Guides', image: 'charm_guide.png', fsValue: 6.5, tier: 'B', desc: 'Secondary material for Chief Charm upgrades', category: 'unique' },
    ],
  },
  currency: {
    label: 'Gems & VIP',
    items: [
      { id: 'gems', name: 'Gems', image: 'gems.png', fsValue: 0.033, tier: 'A', desc: 'Premium currency (30 gems = 1 FS)', category: 'currency' },
      { id: 'stamina', name: 'Stamina', image: 'stamina.png', fsValue: 1, tier: 'A', desc: 'Energy for beasts and exploration', category: 'currency' },
      { id: 'fire_crystal', name: 'Fire Crystals', image: 'fire_crystal.png', fsValue: 1.7, tier: 'B', desc: 'Currency for Furnace upgrades (FC1-FC5)', category: 'currency' },
      { id: 'vip_xp_100', name: 'VIP XP 100', image: 'vip_points.png', fsValue: 7, tier: 'B', desc: '100 VIP experience points', category: 'currency' },
      { id: 'gold_key', name: 'Gold Keys', image: 'gold_key.png', fsValue: 50, tier: 'A', desc: 'Opens gold chests for good rewards', category: 'currency' },
      { id: 'platinum_key', name: 'Platinum Keys', image: 'platinum_key.png', fsValue: 17, tier: 'B', desc: 'Opens platinum chests for rare rewards', category: 'currency' },
    ],
  },
  warItems: {
    label: 'War & Utility',
    items: [
      { id: 'advanced_teleport', name: 'Advanced Teleport', image: 'advanced_teleporter.png', fsValue: 67, tier: 'A', desc: 'Teleport to any location on the map', category: 'unique' },
      { id: 'random_teleport', name: 'Random Teleport', image: 'random_teleporter.png', fsValue: 33, tier: 'B', desc: 'Teleport to random location', category: 'unique' },
      { id: 'transfer_pass', name: 'Transfer Pass', image: 'transfer_pass.png', fsValue: 100, tier: 'S', desc: 'Transfer to another state', category: 'unique' },
      { id: 'peace_shield_24h', name: 'Peace Shield (24hr)', image: 'shield.png', fsValue: 50, tier: 'A', desc: 'Protect city for 24 hours', category: 'unique' },
      { id: 'counter_recon_8h', name: 'Counter Recon (8hr)', image: 'counter_recon.png', fsValue: 35, tier: 'B', desc: 'Hide troop info for 8 hours', category: 'unique' },
    ],
  },
  pets: {
    label: 'Pets',
    items: [
      { id: 'pet_food', name: 'Pet Food', image: 'pet_food.png', fsValue: 0.024, tier: 'C', desc: 'Nutrient substance for leveling up pets', category: 'unique' },
      { id: 'taming_manual', name: 'Taming Manuals', image: 'taming_manual.png', fsValue: 4, tier: 'B', desc: 'Core material for pet advancement', category: 'unique' },
      { id: 'energizing_potion', name: 'Energizing Potion', image: 'energizing_potion.png', fsValue: 14, tier: 'A', desc: 'Pet advancement (Lv.30+)', category: 'unique' },
      { id: 'strengthening_serum', name: 'Strengthening Serum', image: 'strengthening_serum.png', fsValue: 28, tier: 'A', desc: 'Pet advancement (Lv.50+)', category: 'unique' },
      { id: 'advanced_wild_mark', name: 'Advanced Wild Mark', image: 'advanced_wild_mark.png', fsValue: 71, tier: 'S', desc: 'Advanced pet refinement. $0.71 each', category: 'unique' },
    ],
  },
  speedups: {
    label: 'Speedups',
    items: [
      { id: 'speed_gen_1h', name: 'General 1h', emoji: '⏱️', fsValue: 14, tier: 'B', desc: 'General speedup - 1 hour', category: 'speedups' },
      { id: 'speed_gen_3h', name: 'General 3h', emoji: '⏱️', fsValue: 42, tier: 'A', desc: 'General speedup - 3 hours', category: 'speedups' },
      { id: 'speed_gen_8h', name: 'General 8h', emoji: '⏱️', fsValue: 112, tier: 'A', desc: 'General speedup - 8 hours', category: 'speedups' },
      { id: 'speed_gen_24h', name: 'General 24h', emoji: '⏱️', fsValue: 336, tier: 'S', desc: 'General speedup - 24 hours', category: 'speedups' },
      { id: 'speed_build_1h', name: 'Build 1h', emoji: '🔨', fsValue: 14, tier: 'B', desc: 'Construction speedup - 1 hour', category: 'speedups' },
      { id: 'speed_build_8h', name: 'Build 8h', emoji: '🔨', fsValue: 112, tier: 'A', desc: 'Construction speedup - 8 hours', category: 'speedups' },
      { id: 'speed_research_1h', name: 'Research 1h', emoji: '🔬', fsValue: 14, tier: 'B', desc: 'Research speedup - 1 hour', category: 'speedups' },
      { id: 'speed_research_8h', name: 'Research 8h', emoji: '🔬', fsValue: 112, tier: 'A', desc: 'Research speedup - 8 hours', category: 'speedups' },
      { id: 'speed_heal_1h', name: 'Healing 1h', emoji: '💉', fsValue: 0, tier: 'D', desc: 'Healing speedup - VALUE = $0 (batch healing is free!)', category: 'speedups' },
      { id: 'speed_heal_8h', name: 'Healing 8h', emoji: '💉', fsValue: 0, tier: 'D', desc: 'Healing speedup - VALUE = $0 (batch healing is free!)', category: 'speedups' },
    ],
  },
  lateGame: {
    label: 'FC5+ Items',
    items: [
      { id: 'expert_sigil', name: 'Expert Sigils', image: 'common_expert_sigil.png', fsValue: 20, tier: 'A', desc: 'Material for hero expertise trees', category: 'unique' },
      { id: 'lunar_amber', name: 'Lunar Amber', image: 'lunar_amber.png', fsValue: 35, tier: 'A', desc: 'Material for Red+ quality chief gear', category: 'unique' },
      { id: 'charm_secrets', name: 'Charm Secrets', image: 'charm_secrets.png', fsValue: 50, tier: 'S', desc: 'Rare material for L12+ charm upgrades', category: 'unique' },
      { id: 'refined_fire_crystal', name: 'Refined FC', image: 'refined_fire_crystal.png', fsValue: 30, tier: 'A', desc: 'Purified FC for FC6+ upgrades', category: 'unique' },
    ],
  },
  resources: {
    label: 'Resources',
    items: [
      { id: 'meat_100k', name: 'Meat 100k', image: 'meat.png', fsValue: 0.54, tier: 'D', desc: '100,000 Meat', category: 'resources' },
      { id: 'meat_1m', name: 'Meat 1M', image: 'meat.png', fsValue: 5.4, tier: 'D', desc: '1,000,000 Meat', category: 'resources' },
      { id: 'wood_100k', name: 'Wood 100k', image: 'wood.png', fsValue: 0.54, tier: 'D', desc: '100,000 Wood', category: 'resources' },
      { id: 'wood_1m', name: 'Wood 1M', image: 'wood.png', fsValue: 5.4, tier: 'D', desc: '1,000,000 Wood', category: 'resources' },
      { id: 'coal_100k', name: 'Coal 100k', image: 'coal.png', fsValue: 2.7, tier: 'D', desc: '100,000 Coal', category: 'resources' },
      { id: 'iron_100k', name: 'Iron 100k', image: 'iron.png', fsValue: 10.8, tier: 'D', desc: '100,000 Iron', category: 'resources' },
      { id: 'steel_10k', name: 'Steel 10k', image: 'steel.png', fsValue: 56, tier: 'C', desc: '10,000 Steel', category: 'resources' },
    ],
  },
};

interface BreakdownItem {
  name: string;
  image?: string;
  emoji?: string;
  quantity: number;
  tier: string;
  value: number;
  isFiller: boolean;
  category: string;
}

interface AnalysisResult {
  totalValue: number;
  totalValueDollars: number;
  currencyValue: number;
  uniqueValue: number;
  speedupValue: number;
  resourceValue: number;
  fillerValue: number;
  fillerPct: number;
  efficiency: number;
  breakdown: BreakdownItem[];
  price: number;
}

function calculateAnalysis(
  quantities: Record<string, number>,
  price: number,
  farmerMode: boolean
): AnalysisResult {
  let totalValue = 0;
  let currencyValue = 0;
  let uniqueValue = 0;
  let speedupValue = 0;
  let resourceValue = 0;
  let fillerValue = 0;
  const breakdown: BreakdownItem[] = [];

  for (const catData of Object.values(PACK_ITEMS)) {
    for (const item of catData.items) {
      const qty = quantities[item.id] || 0;
      if (qty > 0) {
        let value = qty * item.fsValue;

        // In farmer mode, resources are worth $0
        if (farmerMode && item.category === 'resources') {
          value = 0;
        }

        totalValue += value;
        const isFiller = item.tier === 'D' || item.category === 'resources';

        if (item.category === 'resources') {
          resourceValue += value;
          fillerValue += value;
        } else if (item.category === 'currency') {
          currencyValue += value;
        } else if (item.category === 'speedups') {
          speedupValue += value;
          if (item.tier === 'D') fillerValue += value;
        } else {
          uniqueValue += value;
        }

        breakdown.push({
          name: item.name,
          image: item.image,
          emoji: item.emoji,
          quantity: qty,
          tier: item.tier,
          value,
          isFiller,
          category: item.category,
        });
      }
    }
  }

  breakdown.sort((a, b) => b.value - a.value);

  const priceFs = price * 100;
  const fillerPct = totalValue > 0 ? (fillerValue / totalValue) * 100 : 0;
  const efficiency = priceFs > 0 ? (totalValue / priceFs) * 100 : 0;

  return {
    totalValue,
    totalValueDollars: totalValue / 100,
    currencyValue,
    uniqueValue,
    speedupValue,
    resourceValue,
    fillerValue,
    fillerPct,
    efficiency,
    breakdown,
    price,
  };
}

export default function PackAnalyzerPage() {
  const [quantities, setQuantities] = useState<Record<string, number>>({});
  const [price, setPrice] = useState(4.99);
  const [farmerMode, setFarmerMode] = useState(false);
  const [activeTab, setActiveTab] = useState('hero');

  const analysis = useMemo(
    () => calculateAnalysis(quantities, price, farmerMode),
    [quantities, price, farmerMode]
  );

  const updateQuantity = (itemId: string, value: number) => {
    setQuantities((prev) => ({
      ...prev,
      [itemId]: Math.max(0, value),
    }));
  };

  const clearAll = () => {
    setQuantities({});
  };

  const getEfficiencyColor = (eff: number) => {
    if (eff >= 100) return 'text-success';
    if (eff >= 70) return 'text-warning';
    return 'text-error';
  };

  const getEfficiencyLabel = (eff: number) => {
    if (eff >= 100) return 'Good Value';
    if (eff >= 70) return 'Fair Value';
    return 'Poor Value';
  };

  const categories = Object.keys(PACK_ITEMS);

  return (
    <PageLayout>
      <div className="max-w-5xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-frost">Pack Value Analyzer</h1>
          <p className="text-frost-muted mt-2">
            Cut through inflated % values. See what you're <em>actually</em> paying for.
          </p>
        </div>

        {/* Farmer Mode Toggle */}
        <div className="card mb-6">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={farmerMode}
              onChange={(e) => setFarmerMode(e.target.checked)}
              className="w-5 h-5 rounded border-surface-border bg-surface text-ice focus:ring-ice"
            />
            <div>
              <span className="font-medium text-frost">I'm a resource farmer</span>
              <span className="text-sm text-frost-muted ml-2">(set resources to $0)</span>
            </div>
          </label>
          {farmerMode && (
            <p className="text-sm text-ice mt-2">
              Farmer Mode ON: Resources (Meat, Wood, Coal, Iron, Steel) valued at $0.
            </p>
          )}
        </div>

        {/* The Fluff Problem */}
        <div className="card mb-6 border-warning/30 bg-warning/5">
          <p className="text-sm text-frost">
            <strong>The Fluff Problem:</strong> Packs bundle items together, making specific items feel more valuable than they are.
          </p>
          <p className="text-sm text-frost-muted mt-2">
            For example, if you only want Essence Stones: A $4.99 pack contains ~$0.22 worth of Essence Stones (10 stones × $0.022 each).
            That's only <strong className="text-error">4.4%</strong> of the pack - you're paying a <strong className="text-error">23x markup</strong> for what you actually want!
          </p>
        </div>

        {/* Price Selector & Analysis */}
        <div className="card mb-6">
          <div className="flex flex-wrap items-center gap-4 mb-6">
            <div>
              <label className="text-sm text-frost-muted block mb-1">Pack Price</label>
              <select
                value={price}
                onChange={(e) => setPrice(parseFloat(e.target.value))}
                className="input w-32"
              >
                {PRICE_OPTIONS.map((p) => (
                  <option key={p} value={p}>${p.toFixed(2)}</option>
                ))}
              </select>
            </div>
            <button onClick={clearAll} className="btn-secondary text-sm">
              Clear All
            </button>
          </div>

          {/* Analysis Results */}
          {analysis.totalValue > 0 ? (
            <>
              {/* Value Summary */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center p-4 rounded-lg bg-success/10">
                  <div className="text-2xl font-bold text-success">${analysis.totalValueDollars.toFixed(2)}</div>
                  <div className="text-xs text-frost-muted">Actual Value</div>
                </div>
                <div className="text-center p-4 rounded-lg bg-surface">
                  <div className="text-2xl font-bold text-frost">${analysis.price.toFixed(2)}</div>
                  <div className="text-xs text-frost-muted">Pack Price</div>
                </div>
                <div className={`text-center p-4 rounded-lg ${analysis.efficiency >= 100 ? 'bg-success/10' : analysis.efficiency >= 70 ? 'bg-warning/10' : 'bg-error/10'}`}>
                  <div className={`text-2xl font-bold ${getEfficiencyColor(analysis.efficiency)}`}>
                    {analysis.efficiency.toFixed(0)}%
                  </div>
                  <div className="text-xs text-frost-muted">{getEfficiencyLabel(analysis.efficiency)}</div>
                </div>
                <div className="text-center p-4 rounded-lg bg-error/10">
                  <div className="text-2xl font-bold text-error">{analysis.fillerPct.toFixed(0)}%</div>
                  <div className="text-xs text-frost-muted">Filler{analysis.fillerPct > 50 ? ' (Heavy!)' : ''}</div>
                </div>
              </div>

              {/* Category Breakdown Bar */}
              <div className="mb-6">
                <p className="text-sm text-frost-muted mb-2">Value Breakdown by Category:</p>
                <div className="flex h-6 rounded-lg overflow-hidden">
                  {analysis.currencyValue > 0 && (
                    <div
                      style={{ width: `${(analysis.currencyValue / analysis.totalValue) * 100}%`, backgroundColor: '#FFD700' }}
                      title={`Currency: ${((analysis.currencyValue / analysis.totalValue) * 100).toFixed(0)}%`}
                    />
                  )}
                  {analysis.uniqueValue > 0 && (
                    <div
                      style={{ width: `${(analysis.uniqueValue / analysis.totalValue) * 100}%`, backgroundColor: '#9B59B6' }}
                      title={`Unique: ${((analysis.uniqueValue / analysis.totalValue) * 100).toFixed(0)}%`}
                    />
                  )}
                  {analysis.speedupValue > 0 && (
                    <div
                      style={{ width: `${(analysis.speedupValue / analysis.totalValue) * 100}%`, backgroundColor: '#3498DB' }}
                      title={`Speedups: ${((analysis.speedupValue / analysis.totalValue) * 100).toFixed(0)}%`}
                    />
                  )}
                  {analysis.resourceValue > 0 && (
                    <div
                      style={{ width: `${(analysis.resourceValue / analysis.totalValue) * 100}%`, backgroundColor: '#E74C3C' }}
                      title={`Resources: ${((analysis.resourceValue / analysis.totalValue) * 100).toFixed(0)}%`}
                    />
                  )}
                </div>
                <div className="flex justify-center gap-4 text-xs text-frost-muted mt-2">
                  <span><span style={{ color: '#FFD700' }}>●</span> Currency</span>
                  <span><span style={{ color: '#9B59B6' }}>●</span> Unique</span>
                  <span><span style={{ color: '#3498DB' }}>●</span> Speedups</span>
                  <span><span style={{ color: '#E74C3C' }}>●</span> Resources</span>
                </div>
              </div>

              {/* Item Breakdown */}
              <div>
                <p className="text-sm font-medium text-frost mb-3">Item Breakdown (Top 10)</p>
                <div className="space-y-2">
                  {analysis.breakdown.slice(0, 10).map((item, i) => {
                    const pct = (item.value / analysis.totalValue) * 100;
                    const tierColor = TIER_COLORS[item.tier] || '#666';
                    return (
                      <div
                        key={i}
                        className="flex items-center justify-between p-2 rounded bg-surface/50"
                        style={{ borderLeft: `3px solid ${tierColor}` }}
                      >
                        <div className="flex items-center gap-2">
                          {item.image ? (
                            <div className="relative w-6 h-6">
                              <Image
                                src={`/images/items/${item.image}`}
                                alt={item.name}
                                fill
                                className="object-contain"
                              />
                            </div>
                          ) : (
                            <span>{item.emoji || '📦'}</span>
                          )}
                          <span className="text-sm text-frost">{item.name}</span>
                        </div>
                        <div className="text-sm">
                          <span className="font-bold text-frost">×{item.quantity.toLocaleString()}</span>
                          <span className="text-frost-muted mx-1">→</span>
                          <span style={{ color: tierColor }}>${(item.value / 100).toFixed(2)}</span>
                          <span className="text-frost-muted ml-1">({pct.toFixed(1)}%)</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-8 text-frost-muted">
              <div className="text-4xl mb-4">📦</div>
              <p>Enter item quantities below to see analysis</p>
            </div>
          )}
        </div>

        {/* Item Entry Tabs */}
        <div className="card">
          <h2 className="section-header">Enter Pack Contents</h2>

          {/* Category Tabs */}
          <div className="flex flex-wrap gap-2 mb-6 border-b border-surface-border pb-3">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveTab(cat)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  activeTab === cat
                    ? 'bg-ice/20 text-ice'
                    : 'text-frost-muted hover:text-frost hover:bg-surface'
                }`}
              >
                {PACK_ITEMS[cat].label}
              </button>
            ))}
          </div>

          {/* Item Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {PACK_ITEMS[activeTab].items.map((item) => (
              <div key={item.id} className="text-center">
                <div className="mb-2">
                  {item.image ? (
                    <div className="relative w-12 h-12 mx-auto">
                      <Image
                        src={`/images/items/${item.image}`}
                        alt={item.name}
                        fill
                        className="object-contain"
                        title={item.desc}
                      />
                    </div>
                  ) : (
                    <div className="text-4xl" title={item.desc}>{item.emoji || '📦'}</div>
                  )}
                </div>
                <p className="text-xs text-frost-muted mb-1 truncate" title={item.name}>
                  {item.name}
                </p>
                <input
                  type="number"
                  min={0}
                  value={quantities[item.id] || ''}
                  onChange={(e) => updateQuantity(item.id, parseInt(e.target.value) || 0)}
                  placeholder="0"
                  className="input text-center text-sm w-20 mx-auto"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Tips */}
        <div className="card mt-6">
          <details className="group">
            <summary className="flex items-center justify-between cursor-pointer text-frost font-medium">
              <span>Understanding Pack Value</span>
              <span className="text-ice group-open:rotate-180 transition-transform">▼</span>
            </summary>
            <div className="mt-4 pt-4 border-t border-surface-border space-y-3 text-sm text-frost-muted">
              <div>
                <strong className="text-frost">Item Tiers:</strong>
                <ul className="mt-1 space-y-1">
                  <li><span style={{ color: TIER_COLORS.S }}>S Tier</span>: Mithril ($1.41), Advanced Wild Marks, 24h Speedups - premium items</li>
                  <li><span style={{ color: TIER_COLORS.A }}>A Tier</span>: Essence Stones ($0.22), Gold Keys, Gems - solid value</li>
                  <li><span style={{ color: TIER_COLORS.B }}>B Tier</span>: Hourly speedups, Manuals, Charm Designs - useful but common</li>
                  <li><span style={{ color: TIER_COLORS.C }}>C Tier</span>: Small speedups, Steel, Hero XP - low value</li>
                  <li><span style={{ color: TIER_COLORS.D }}>D Tier</span>: Resources, Healing speedups - FILLER (free for active players!)</li>
                </ul>
              </div>
              <div>
                <strong className="text-frost">Value Efficiency:</strong>
                <ul className="mt-1 space-y-1">
                  <li><span className="text-success">100%+</span> = Actual value exceeds price (good deal)</li>
                  <li><span className="text-warning">70-99%</span> = Fair value, buy if you need the items</li>
                  <li><span className="text-error">Below 70%</span> = Poor value, consider skipping</li>
                </ul>
              </div>
              <div>
                <strong className="text-frost">Farmer Mode:</strong> Active players gather/mine resources constantly. If you have 800M Meat in storage, the resources in packs have zero practical value to you.
              </div>
            </div>
          </details>
        </div>
      </div>
    </PageLayout>
  );
}
