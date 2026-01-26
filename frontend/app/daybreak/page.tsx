'use client';

import { useState } from 'react';
import PageLayout from '@/components/PageLayout';

type TabKey = 'getting-started' | 'battle-decorations' | 'tree-of-life' | 'strategy';

// Priority colors
const priorityColors: Record<string, { bg: string; border: string; text: string }> = {
  CRITICAL: { bg: 'bg-red-500/20', border: 'border-l-red-500', text: 'text-red-400' },
  HIGH: { bg: 'bg-orange-500/15', border: 'border-l-orange-500', text: 'text-orange-400' },
  MEDIUM: { bg: 'bg-blue-500/10', border: 'border-l-blue-500', text: 'text-blue-400' },
  LOW: { bg: 'bg-surface/50', border: 'border-l-slate-500', text: 'text-slate-400' },
};

// Troop type colors
const troopColors: Record<string, { bg: string; border: string; text: string }> = {
  infantry: { bg: 'bg-red-500/10', border: 'border-red-500', text: 'text-red-400' },
  lancer: { bg: 'bg-green-500/10', border: 'border-green-500', text: 'text-green-400' },
  marksman: { bg: 'bg-blue-500/10', border: 'border-blue-500', text: 'text-blue-400' },
};

// Tree of Life progression data
const treeOfLifeProgression = [
  { level: 1, buff: 'Healing Speed +30%', combatValue: 'LOW', notes: 'Free starting buff' },
  { level: 2, buff: 'Healing Speed +30%', combatValue: 'LOW', notes: '' },
  { level: 3, buff: 'Healing Speed +30%', combatValue: 'LOW', notes: '' },
  { level: 4, buff: 'Troops Defense +5%', combatValue: 'MEDIUM', notes: 'First combat buff' },
  { level: 5, buff: 'Healing Speed +30%', combatValue: 'LOW', notes: '' },
  { level: 6, buff: 'Troops Attack +5%', combatValue: 'HIGH', notes: 'Universal attack buff' },
  { level: 7, buff: 'Healing Speed +30%', combatValue: 'LOW', notes: '' },
  { level: 8, buff: 'Healing Speed +30%', combatValue: 'LOW', notes: '' },
  { level: 9, buff: 'Troops Health +5%', combatValue: 'HIGH', notes: 'Universal health buff' },
  { level: 10, buff: 'Troops Lethality +5%', combatValue: 'CRITICAL', notes: 'Max level - unlocks Starry Lighthouse' },
];

// Mythic decorations by troop type
const mythicDecorations = {
  infantry: [
    { name: 'Floating Market', effect: 'Infantry Attack +10%' },
    { name: 'Snow Castle', effect: 'Infantry Defense +10%' },
  ],
  lancer: [
    { name: 'Amphitheatre', effect: 'Lancer Attack +10%' },
    { name: 'Elegant Villa', effect: 'Lancer Defense +10%' },
  ],
  marksman: [
    { name: 'Observation Deck', effect: 'Marksman Attack +10%' },
    { name: 'Art Gallery', effect: 'Marksman Defense +10%' },
  ],
};

// Epic decorations by troop type
const epicDecorations = {
  infantry: [
    { name: 'Rural Mill', effect: 'Infantry Attack +2.5%' },
    { name: 'Warm Greenhouse', effect: 'Infantry Defense +2.5%' },
  ],
  lancer: [
    { name: 'Crystal Garden', effect: 'Lancer Attack +2.5%' },
    { name: "Sailor's Cottage", effect: 'Lancer Defense +2.5%' },
  ],
  marksman: [
    { name: 'Clock Hut', effect: 'Marksman Attack +2.5%' },
    { name: "Fisherman's Chalet", effect: 'Marksman Defense +2.5%' },
  ],
};

// Limited mythic decorations
const limitedMythics = [
  { name: 'Serpent Sanctuary', effect: '+20% ALL combat stats (Attack, Defense, Health, Lethality)' },
  { name: 'Ferris Wheel', effect: '+10% Troop Attack' },
  { name: 'Carousel', effect: '+10% Troop Defense' },
];

// New player tips
const newPlayerTips = [
  { tip: 'Upgrade Lumber Camps and Tree of Life ASAP', why: 'Higher levels = faster Life Essence production. This compounds over time - every day you delay costs you resources.', priority: 'CRITICAL' as const },
  { tip: 'Collect Life Essence every 12 hours', why: 'Storage fills up and you stop generating. Set reminders or collect during daily reset routine.', priority: 'HIGH' as const },
  { tip: 'Move Lumber Camps to direct workers', why: 'Workers cut trees nearest to the camp. Move camps to control which areas get cleared first.', priority: 'HIGH' as const },
  { tip: 'Unlock second Lumber Camp at Tree L5', why: 'Doubles your clearing speed. Rush to Tree L5 to unlock this.', priority: 'HIGH' as const },
  { tip: 'Use decorations to block worker paths', why: 'Place water or decorations to funnel workers toward areas you want cleared (like where you spotted a chest).', priority: 'MEDIUM' as const },
  { tip: 'Use alliance assists daily', why: 'You can help allies 3 times and receive 3 assists per day = 6 bonus Life Essence boosts.', priority: 'MEDIUM' as const },
];

// Common mistakes
const commonMistakes = [
  { mistake: 'Building decorations without a Prosperity goal', whyBad: 'Decorations beyond Prosperity gates waste Life Essence', fix: 'Only build decorations to meet the next Tree of Life gate' },
  { mistake: 'Rushing Daybreak before Furnace L30', whyBad: 'FC unlock is more valuable than Daybreak buffs', fix: 'Get Tree of Life L6, then focus Furnace to L30' },
  { mistake: 'Using Common/Uncommon decorations', whyBad: 'Lowest efficiency - wastes Life Essence', fix: 'Save for Epic/Mythic decorations' },
  { mistake: 'Ignoring Daybreak entirely', whyBad: 'Free combat stats with no downside', fix: 'At minimum, get Tree of Life L6 for Troops Health +5%' },
  { mistake: 'Not upgrading Lumber Camps early', whyBad: 'Lower production rate = less Life Essence over time. This compounds significantly.', fix: 'Rush Lumber Camp and Tree upgrades first before buying decorations.' },
  { mistake: 'Letting Life Essence storage fill up', whyBad: 'Once storage is full, you stop generating. Wasted production.', fix: 'Collect every 12 hours or set reminders.' },
];

// Spending strategies
const spendingStrategies = {
  f2p: {
    priority: 'Medium',
    focus: 'Combat buffs with minimal wood investment',
    strategy: [
      'Rush Tree of Life L6 for first combat buff',
      'Use Epic decorations for balance of cost and efficiency',
      "Don't over-invest beyond L6 until Furnace L30 is reached",
      'Tree of Life L10 is a late-game goal, not mid-game',
    ],
    avoid: 'Prioritizing Daybreak over Furnace progression',
  },
  minnow: {
    priority: 'Medium-High',
    focus: 'Combat buffs compound with other investments',
    strategy: [
      'Rush Tree of Life L6, then steady progress to L10',
      'Mix of Epic and Mythic decorations',
      'Complete alongside FC progression',
    ],
    avoid: 'Spreading resources too thin',
  },
  dolphin: {
    priority: 'High',
    focus: 'Buffs multiply with hero/troop investments',
    strategy: [
      'Rush Tree of Life L10 relatively quickly',
      'Mythic decorations for efficiency',
      'Complete Starry Lighthouse',
    ],
    avoid: 'Neglecting other combat systems',
  },
  whale: {
    priority: 'High',
    focus: 'Complete everything',
    strategy: [
      'Max everything quickly',
      'All Mythic decorations',
      'Tree of Life L10 + Starry Lighthouse ASAP',
    ],
    avoid: 'Nothing - invest fully',
  },
};

function GettingStartedTab() {
  return (
    <div>
      {/* Priority Warning */}
      <div className="mb-6 p-4 rounded-lg border-2 border-red-500 bg-gradient-to-r from-red-500/20 to-orange-500/20">
        <p className="text-lg font-bold text-red-400 text-center">
          Focus on COMBAT STATS (Attack/Defense decorations), NOT on chasing a high Prosperity score!
        </p>
      </div>

      <h2 className="text-xl font-bold text-frost mb-4">Essential Tips</h2>

      <div className="space-y-3 mb-8">
        {newPlayerTips.map((tip, i) => {
          const colors = priorityColors[tip.priority];
          return (
            <div key={i} className={`${colors.bg} border-l-4 ${colors.border} p-4 rounded-r-lg`}>
              <div className="flex justify-between items-start gap-3">
                <div className="flex-1">
                  <p className="font-semibold text-frost">{tip.tip}</p>
                  <p className="text-sm text-frost-muted mt-1">{tip.why}</p>
                </div>
                <span className={`text-xs px-2 py-1 rounded ${colors.text} bg-surface whitespace-nowrap`}>
                  {tip.priority}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Treasure Chests */}
      <div className="card border-orange-500/30">
        <h3 className="text-lg font-bold text-orange-400 mb-3">Treasure Chests</h3>
        <div className="space-y-3 text-sm">
          <div>
            <span className="font-medium text-frost">Spawn Type:</span>
            <span className="text-frost-muted ml-2">Random - chests appear as trees are cleared</span>
          </div>
          <div>
            <span className="font-medium text-frost">Contents:</span>
            <span className="text-frost-muted ml-2">Life Essence, Hero Shards, Gear, and other rewards</span>
          </div>
          <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/20">
            <span className="font-medium text-green-400">Strategy:</span>
            <span className="text-frost-muted ml-2">
              Move Lumber Camps toward chest locations when you spot them. Use decorations to block paths and direct workers to the chest area.
            </span>
          </div>
        </div>
      </div>

      {/* Quick Overview */}
      <div className="grid md:grid-cols-2 gap-4 mt-6">
        <div className="card bg-blue-500/10 border-blue-500/20">
          <h4 className="font-medium text-blue-400 mb-2">Unlock Requirements</h4>
          <p className="text-frost">Furnace Level 19 + Dock building</p>
        </div>
        <div className="card bg-green-500/10 border-green-500/20">
          <h4 className="font-medium text-green-400 mb-2">Currency</h4>
          <p className="text-frost">Life Essence (720 wood = 1 Life Essence via Dock)</p>
        </div>
      </div>
    </div>
  );
}

function BattleDecorationsTab() {
  return (
    <div>
      <h2 className="text-xl font-bold text-frost mb-2">Battle Enhancer Decorations</h2>
      <p className="text-frost-muted mb-4">The MAIN source of combat stats from Daybreak - more impactful than Tree of Life</p>

      {/* Warning */}
      <div className="p-4 rounded-lg bg-red-500/20 border border-red-500/30 mb-6">
        <p className="font-bold text-red-400">
          These are MORE impactful than Tree of Life for your main troop type!
        </p>
        <p className="text-sm text-frost-muted mt-1">
          Two Mythic decorations = +20% (10% ATK + 10% DEF) for your troop type. Tree of Life L10 = only +5% universal.
        </p>
      </div>

      {/* Priority Order */}
      <div className="card mb-6 border-ice/30">
        <h3 className="font-medium text-frost mb-3">Priority Order</h3>
        <ol className="space-y-2 text-sm text-frost-muted">
          <li className="flex items-start gap-2">
            <span className="w-5 h-5 rounded-full bg-red-500/20 text-red-400 flex items-center justify-center text-xs font-bold shrink-0">1</span>
            Build BOTH Mythic decorations for your main troop type (Attack + Defense)
          </li>
          <li className="flex items-start gap-2">
            <span className="w-5 h-5 rounded-full bg-orange-500/20 text-orange-400 flex items-center justify-center text-xs font-bold shrink-0">2</span>
            Level them to max for full +10% each
          </li>
          <li className="flex items-start gap-2">
            <span className="w-5 h-5 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-xs font-bold shrink-0">3</span>
            Tree of Life to L10 for universal buffs
          </li>
          <li className="flex items-start gap-2">
            <span className="w-5 h-5 rounded-full bg-slate-500/20 text-slate-400 flex items-center justify-center text-xs font-bold shrink-0">4</span>
            Consider other troop types if you use mixed compositions
          </li>
        </ol>
      </div>

      {/* Mythic Decorations */}
      <h3 className="text-lg font-bold text-frost mb-4">Mythic Decorations (+10% at max level)</h3>
      <div className="grid md:grid-cols-3 gap-4 mb-8">
        {Object.entries(mythicDecorations).map(([troopType, decos]) => {
          const colors = troopColors[troopType];
          return (
            <div key={troopType} className="space-y-2">
              <div className={`${colors.bg} border-2 ${colors.border} p-3 rounded-lg text-center`}>
                <span className={`font-bold ${colors.text} uppercase`}>{troopType}</span>
              </div>
              {decos.map((deco, i) => (
                <div key={i} className="bg-surface/50 p-3 rounded-lg">
                  <p className="font-medium text-frost">{deco.name}</p>
                  <p className="text-sm text-frost-muted">{deco.effect}</p>
                </div>
              ))}
            </div>
          );
        })}
      </div>

      {/* Epic Decorations */}
      <details className="mb-6">
        <summary className="cursor-pointer text-frost font-medium p-4 bg-surface/30 rounded-lg hover:bg-surface/50">
          Epic Decorations (+2.5% at max level)
        </summary>
        <div className="grid md:grid-cols-3 gap-4 mt-4 p-4 bg-surface/20 rounded-b-lg">
          {Object.entries(epicDecorations).map(([troopType, decos]) => (
            <div key={troopType}>
              <p className={`font-medium ${troopColors[troopType].text} mb-2 capitalize`}>{troopType}</p>
              {decos.map((deco, i) => (
                <p key={i} className="text-sm text-frost-muted">- {deco.name}: {deco.effect}</p>
              ))}
            </div>
          ))}
        </div>
      </details>

      {/* Limited Mythics */}
      <details>
        <summary className="cursor-pointer text-frost font-medium p-4 bg-surface/30 rounded-lg hover:bg-surface/50">
          Limited-Time Mythic Decorations (Event-Only)
        </summary>
        <div className="mt-4 p-4 bg-surface/20 rounded-b-lg space-y-2">
          {limitedMythics.map((deco, i) => (
            <div key={i} className="bg-purple-500/10 border border-purple-500/20 p-3 rounded-lg">
              <p className="font-medium text-purple-300">{deco.name}</p>
              <p className="text-sm text-frost-muted">{deco.effect}</p>
            </div>
          ))}
        </div>
      </details>
    </div>
  );
}

function TreeOfLifeTab() {
  return (
    <div>
      {/* Overview */}
      <h2 className="text-xl font-bold text-frost mb-2">Tree of Life</h2>
      <p className="text-frost-muted mb-6">
        Provides universal buffs, but DECORATIONS provide the BIG troop-type-specific bonuses
      </p>

      {/* Milestone Priorities */}
      <div className="grid md:grid-cols-2 gap-4 mb-6">
        <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/30">
          <p className="font-medium text-green-400 mb-1">First Priority</p>
          <p className="text-sm text-frost">Mythic Battle Decorations for your main troop type (+10% Attack AND +10% Defense)</p>
        </div>
        <div className="p-4 rounded-lg bg-orange-500/10 border border-orange-500/30">
          <p className="font-medium text-orange-400 mb-1">Second Priority</p>
          <p className="text-sm text-frost">Tree of Life L10 for universal +5% Attack, Defense, Health, Lethality</p>
        </div>
      </div>

      <div className="p-3 rounded-lg bg-ice/10 border border-ice/20 mb-6">
        <p className="text-sm text-ice font-medium">Key Insight</p>
        <p className="text-sm text-frost-muted">
          Decorations give BIGGER bonuses per troop type than Tree of Life gives universally
        </p>
      </div>

      {/* Level Progression */}
      <h3 className="text-lg font-bold text-frost mb-4">Level Progression</h3>
      <div className="space-y-2">
        {treeOfLifeProgression.map((level) => {
          const colors = priorityColors[level.combatValue];
          return (
            <div key={level.level} className={`${colors.bg} border-l-4 ${colors.border} p-3 rounded-r-lg flex items-center justify-between`}>
              <div className="flex items-center gap-3">
                <span className={`${colors.text} bg-surface px-3 py-1 rounded-full text-sm font-bold`}>
                  L{level.level}
                </span>
                <span className="font-medium text-frost">{level.buff}</span>
                {level.notes && (
                  <span className="text-xs text-frost-muted">({level.notes})</span>
                )}
              </div>
              <span className={`text-xs font-bold ${colors.text}`}>
                {level.combatValue}
              </span>
            </div>
          );
        })}
      </div>

      {/* Combat buffs summary */}
      <div className="card mt-6 border-ice/30">
        <h3 className="font-medium text-frost mb-3">Combat Buffs Summary (Tree of Life)</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-center">
          <div className="p-3 rounded-lg bg-surface/50">
            <p className="text-2xl font-bold text-frost">+5%</p>
            <p className="text-xs text-frost-muted">Defense (L4)</p>
          </div>
          <div className="p-3 rounded-lg bg-surface/50">
            <p className="text-2xl font-bold text-frost">+5%</p>
            <p className="text-xs text-frost-muted">Attack (L6)</p>
          </div>
          <div className="p-3 rounded-lg bg-surface/50">
            <p className="text-2xl font-bold text-frost">+5%</p>
            <p className="text-xs text-frost-muted">Health (L9)</p>
          </div>
          <div className="p-3 rounded-lg bg-surface/50">
            <p className="text-2xl font-bold text-frost">+5%</p>
            <p className="text-xs text-frost-muted">Lethality (L10)</p>
          </div>
        </div>
        <p className="text-sm text-frost-muted text-center mt-3">
          Total: +20% universal combat stats at max level
        </p>
      </div>
    </div>
  );
}

function StrategyTab() {
  const [selectedProfile, setSelectedProfile] = useState<string>('f2p');

  return (
    <div>
      <h2 className="text-xl font-bold text-frost mb-4">Upgrade Strategy</h2>

      {/* Spending Profile Selector */}
      <div className="flex flex-wrap gap-2 mb-6">
        {Object.keys(spendingStrategies).map((profile) => (
          <button
            key={profile}
            onClick={() => setSelectedProfile(profile)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors capitalize ${
              selectedProfile === profile
                ? 'bg-ice text-background'
                : 'bg-surface text-frost-muted hover:text-frost hover:bg-surface-hover'
            }`}
          >
            {profile}
          </button>
        ))}
      </div>

      {/* Selected Profile Strategy */}
      {(() => {
        const strategy = spendingStrategies[selectedProfile as keyof typeof spendingStrategies];
        return (
          <div className="card mb-8 border-ice/30">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-frost capitalize">{selectedProfile} Strategy</h3>
              <span className={`px-3 py-1 rounded text-sm font-medium ${
                strategy.priority === 'High' ? 'bg-green-500/20 text-green-400' :
                strategy.priority === 'Medium-High' ? 'bg-blue-500/20 text-blue-400' :
                'bg-slate-500/20 text-slate-400'
              }`}>
                {strategy.priority} Priority
              </span>
            </div>

            <p className="text-frost-muted mb-4">
              <span className="font-medium text-frost">Focus:</span> {strategy.focus}
            </p>

            <div className="mb-4">
              <p className="font-medium text-frost mb-2">Strategy:</p>
              <ul className="space-y-1">
                {strategy.strategy.map((item, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-frost-muted">
                    <span className="text-ice">•</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            <div className="p-3 rounded-lg bg-orange-500/10 border border-orange-500/20">
              <span className="font-medium text-orange-400">Avoid:</span>
              <span className="text-frost-muted ml-2">{strategy.avoid}</span>
            </div>
          </div>
        );
      })()}

      {/* Common Mistakes */}
      <h3 className="text-lg font-bold text-frost mb-4">Common Mistakes</h3>
      <div className="space-y-3">
        {commonMistakes.map((mistake, i) => (
          <div key={i} className="bg-surface/30 border-l-4 border-l-red-500/50 p-4 rounded-r-lg">
            <p className="font-medium text-frost mb-2">{mistake.mistake}</p>
            <p className="text-sm text-frost-muted mb-2">
              <span className="text-red-400">Why bad:</span> {mistake.whyBad}
            </p>
            <p className="text-sm">
              <span className="text-green-400 font-medium">Fix:</span>
              <span className="text-frost-muted ml-1">{mistake.fix}</span>
            </p>
          </div>
        ))}
      </div>

      {/* Decoration Efficiency */}
      <div className="card mt-8">
        <h3 className="text-lg font-bold text-frost mb-4">Decoration Efficiency</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border">
                <th className="text-left p-2 text-frost-muted">Rarity</th>
                <th className="text-right p-2 text-frost-muted">Cost</th>
                <th className="text-right p-2 text-frost-muted">Prosperity</th>
                <th className="text-right p-2 text-frost-muted">Efficiency</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-surface-border/50 bg-gray-500/5">
                <td className="p-2 text-frost">Common</td>
                <td className="p-2 text-frost-muted text-right">1,000</td>
                <td className="p-2 text-frost-muted text-right">50</td>
                <td className="p-2 text-red-400 text-right">0.05 (Avoid)</td>
              </tr>
              <tr className="border-b border-surface-border/50 bg-gray-500/5">
                <td className="p-2 text-frost">Uncommon</td>
                <td className="p-2 text-frost-muted text-right">2,000</td>
                <td className="p-2 text-frost-muted text-right">100</td>
                <td className="p-2 text-red-400 text-right">0.05 (Avoid)</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="p-2 text-frost">Rare</td>
                <td className="p-2 text-frost-muted text-right">3,000</td>
                <td className="p-2 text-frost-muted text-right">200</td>
                <td className="p-2 text-orange-400 text-right">0.067</td>
              </tr>
              <tr className="border-b border-surface-border/50 bg-purple-500/5">
                <td className="p-2 text-purple-400 font-medium">Epic</td>
                <td className="p-2 text-frost-muted text-right">5,000</td>
                <td className="p-2 text-frost-muted text-right">400</td>
                <td className="p-2 text-blue-400 text-right">0.08 (Budget)</td>
              </tr>
              <tr className="bg-yellow-500/10">
                <td className="p-2 text-yellow-400 font-medium">Mythic</td>
                <td className="p-2 text-frost-muted text-right">10,000</td>
                <td className="p-2 text-frost-muted text-right">1,000</td>
                <td className="p-2 text-green-400 text-right font-bold">0.10 (Best)</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p className="text-xs text-frost-muted mt-3">
          Efficiency = Prosperity per Life Essence. Higher is better.
        </p>
      </div>
    </div>
  );
}

export default function DaybreakPage() {
  const [activeTab, setActiveTab] = useState<TabKey>('getting-started');

  const tabs: { key: TabKey; label: string }[] = [
    { key: 'getting-started', label: 'Getting Started' },
    { key: 'battle-decorations', label: 'Battle Decorations' },
    { key: 'tree-of-life', label: 'Tree of Life' },
    { key: 'strategy', label: 'Strategy' },
  ];

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-frost">Daybreak Island Guide</h1>
          <p className="text-frost-muted mt-2">
            Combat buffs from Battle Decorations and Tree of Life. <strong className="text-frost">Decorations &gt; Tree of Life for combat.</strong>
          </p>
        </div>

        {/* Quick Warning */}
        <div className="card mb-6 border-red-500/30 bg-gradient-to-r from-red-500/10 to-orange-500/10">
          <div className="flex items-start gap-4">
            <span className="text-3xl">🏝️</span>
            <div>
              <h2 className="font-bold text-red-400 mb-1">Don't Chase Prosperity Score!</h2>
              <p className="text-sm text-frost-muted">
                Focus on <strong className="text-frost">COMBAT STATS</strong>, not a high island score.
                Mythic Battle Decorations give <strong className="text-frost">+10% Attack AND +10% Defense</strong> for your troop type —
                <strong className="text-frost"> MORE</strong> than Tree of Life Level 10 gives universally.
              </p>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-2 mb-6 border-b border-surface-border pb-4">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? 'bg-ice text-background'
                  : 'bg-surface text-frost-muted hover:text-frost hover:bg-surface-hover'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="mb-8">
          {activeTab === 'getting-started' && <GettingStartedTab />}
          {activeTab === 'battle-decorations' && <BattleDecorationsTab />}
          {activeTab === 'tree-of-life' && <TreeOfLifeTab />}
          {activeTab === 'strategy' && <StrategyTab />}
        </div>
      </div>
    </PageLayout>
  );
}
