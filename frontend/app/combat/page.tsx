'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';
import { api, profileApi } from '@/lib/api';

type TabKey = 'combat-audit' | 'stats-sources' | 'battle-estimator' | 'phase-priorities';

const tabs: { key: TabKey; label: string }[] = [
  { key: 'combat-audit', label: 'Combat Audit' },
  { key: 'stats-sources', label: 'Stats & Sources' },
  { key: 'battle-estimator', label: 'Battle Estimator' },
  { key: 'phase-priorities', label: 'Phase Priorities' },
];

const impactColors: Record<string, string> = {
  'Critical': 'text-red-400 bg-red-500/20',
  'CRITICAL': 'text-red-400 bg-red-500/20',
  'Very High': 'text-red-400 bg-red-500/20',
  'VERY HIGH': 'text-red-400 bg-red-500/20',
  'High': 'text-orange-400 bg-orange-500/20',
  'HIGH': 'text-orange-400 bg-orange-500/20',
  'Medium-High': 'text-yellow-400 bg-yellow-500/20',
  'MEDIUM-HIGH': 'text-yellow-400 bg-yellow-500/20',
  'Medium': 'text-blue-400 bg-blue-500/20',
  'MEDIUM': 'text-blue-400 bg-blue-500/20',
  'Low-Medium': 'text-green-400 bg-green-500/20',
  'LOW-MEDIUM': 'text-green-400 bg-green-500/20',
  'Low': 'text-gray-400 bg-gray-500/20',
  'LOW': 'text-gray-400 bg-gray-500/20',
};

function useGamePhase(): string {
  const { token } = useAuth();
  const [phase, setPhase] = useState('mid_game');

  useEffect(() => {
    if (!token) return;
    profileApi.getCurrent(token)
      .then(({ profile }) => {
        const fl = profile.furnace_level || 1;
        const fc = profile.furnace_fc_level || '';
        if (fl < 19) setPhase('early_game');
        else if (fl < 30) setPhase('mid_game');
        else if (fc && parseInt(fc.replace(/\D/g, '') || '0') >= 5) setPhase('endgame');
        else setPhase('late_game');
      })
      .catch((err) => console.warn('Could not load profile for game phase detection:', err));
  }, [token]);

  return phase;
}

export default function CombatPage() {
  const [activeTab, setActiveTab] = useState<TabKey>('combat-audit');
  const gamePhase = useGamePhase();

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-frost">Combat Optimization Guide</h1>
          <p className="text-frost-muted mt-2">
            Find your hidden weaknesses. Understand why similar-power players crush each other.
          </p>
        </div>

        {/* PvE vs PvP Explainer */}
        <details className="card mb-6">
          <summary className="cursor-pointer text-lg font-semibold text-frost">
            Understanding PvE vs PvP Combat
          </summary>
          <div className="mt-4 space-y-3 text-sm text-frost-muted">
            <div className="bg-surface rounded-lg p-3">
              <h4 className="font-semibold text-frost mb-1">PvE (Player vs Environment)</h4>
              <p>Bear Trap, Labyrinth, Exploration. Uses <strong className="text-ice">Exploration Skills</strong>. You can retry for better RNG.</p>
            </div>
            <div className="bg-surface rounded-lg p-3">
              <h4 className="font-semibold text-frost mb-1">PvP (Player vs Player)</h4>
              <p>Rally Leader/Joiner, Garrison Defense, SvS, Arena, Brothers in Arms. Uses <strong className="text-fire">Expedition Skills</strong>. No retries - optimize first.</p>
            </div>
            <div className="bg-surface rounded-lg p-3">
              <h4 className="font-semibold text-frost mb-1">City Attacks (Brothers in Arms, SvS)</h4>
              <p>Use your Rally Leader lineup with strongest Expedition heroes. <strong className="text-fire">Always attack in a rally - never solo.</strong></p>
            </div>
          </div>
        </details>

        {/* Core Insight */}
        <div className="card mb-6 border-fire/30">
          <h2 className="text-xl font-bold text-frost mb-3">Why You Lost With Similar Troops</h2>
          <p className="text-frost-muted mb-4">
            Two players with identical hero levels and troop counts can have WILDLY different combat results.
            The difference is in the &quot;hidden multipliers&quot; - stats from Research, <Link href="/daybreak" className="text-ice underline hover:text-frost">Daybreak Island</Link>, Chief Gear,
            Charms, Pets, and Alliance Tech that compound in the background.
          </p>
          <div className="bg-surface rounded-lg p-4 font-mono text-sm mb-4">
            <span className="text-fire">Formula:</span>{' '}
            <span className="text-frost">Damage = (sqrt(Troops) x Attack x Lethality x SkillModifier) / (Enemy Defense x Enemy Health)</span>
          </div>
          <p className="text-sm text-frost-muted mb-4">
            <strong className="text-fire">Key insight:</strong> Attack and Lethality MULTIPLY together.
            A 10% boost to each = 21% more damage. These stats come from places most players neglect.
          </p>

          {/* Troop Type Advantage */}
          <div className="bg-surface rounded-lg p-4">
            <h3 className="font-semibold text-frost mb-3">Troop Type Advantage (10% attack bonus)</h3>
            <div className="flex flex-wrap items-center justify-center gap-3 text-center">
              <div className="flex flex-col items-center">
                <span className="text-2xl mb-1">🗡️</span>
                <span className="text-red-400 font-bold">Infantry</span>
              </div>
              <span className="text-success text-xl">→</span>
              <div className="flex flex-col items-center">
                <span className="text-2xl mb-1">🔱</span>
                <span className="text-green-400 font-bold">Lancer</span>
              </div>
              <span className="text-success text-xl">→</span>
              <div className="flex flex-col items-center">
                <span className="text-2xl mb-1">🏹</span>
                <span className="text-blue-400 font-bold">Marksman</span>
              </div>
              <span className="text-success text-xl">→</span>
              <div className="flex flex-col items-center">
                <span className="text-2xl mb-1">🗡️</span>
                <span className="text-red-400 font-bold">Infantry</span>
              </div>
            </div>
            <p className="text-xs text-frost-muted text-center mt-3">
              <strong className="text-frost">Infantry</strong> beats <strong className="text-green-400">Lancer</strong> •
              <strong className="text-green-400"> Lancer</strong> beats <strong className="text-blue-400">Marksman</strong> •
              <strong className="text-blue-400"> Marksman</strong> beats <strong className="text-red-400">Infantry</strong>
            </p>
            <p className="text-xs text-warning text-center mt-1">
              Match your troops to counter the enemy's main type for a significant damage boost!
            </p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex flex-wrap gap-1.5 mb-6 border-b border-surface-border pb-4 lg:flex-nowrap lg:gap-2">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors whitespace-nowrap lg:flex-1 lg:text-center ${
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
        {activeTab === 'combat-audit' && <CombatAuditTab gamePhase={gamePhase} />}
        {activeTab === 'stats-sources' && <StatsSourcesTab />}
        {activeTab === 'battle-estimator' && <BattleEstimatorTab />}
        {activeTab === 'phase-priorities' && <PhasePrioritiesTab gamePhase={gamePhase} />}
      </div>
    </PageLayout>
  );
}

function CombatAuditTab({ gamePhase }: { gamePhase: string }) {
  const milestones = {
    early_game: [
      { question: 'Use Jessie/Jeronimo in leftmost slot when joining rallies', impact: 'High', why: 'Only leftmost hero\'s expedition skill applies. Wrong hero = wasted slot.' },
      { question: 'Alliance actively researching combat tech', impact: 'Medium', why: 'Alliance tech provides permanent stat boosts while you\'re a member.' },
    ],
    mid_game: [
      { question: 'Completed Tool Enhancement VII', impact: 'Critical', why: '35% faster research on everything. Must be done first.' },
      { question: 'Researched Tier 4+ Lethality for your main troop type', impact: 'Very High', why: 'Lethality is a damage MULTIPLIER. This is often the difference in close fights.' },
      { question: 'Mythic Attack decoration for main troop type (Floating Market/Amphitheatre/Observation Deck)', impact: 'Very High', why: '+10% Attack for your troop type. See Daybreak Island guide for details.' },
      { question: 'Mythic Defense decoration for main troop type (Snow Castle/Elegant Villa/Art Gallery)', impact: 'Very High', why: '+10% Defense for your troop type. Combined with Attack = +20% stats.' },
      { question: 'All 6 Chief Gear pieces at same tier, Infantry (Coat/Pants) highest', impact: 'Very High', why: '6-piece set bonus gives Attack to ALL troops. Infantry first because they\'re frontline.' },
      { question: 'All Chief Charms at Level 5+', impact: 'Medium-High', why: 'Each charm level adds combat stats. Even upgrades unlock army-wide bonus.' },
      { question: 'Own a combat pet (Saber-tooth, Mammoth, Frost Gorilla)', impact: 'High', why: '+10% stat buffs for 2 hours. Activate before every major battle.' },
    ],
    late_game: [
      { question: 'Mythic battle decorations upgraded to high levels', impact: 'High', why: 'Mythic decorations scale to +10% at max level. Unleveled ones give much less.' },
      { question: 'Tree of Life Level 10', impact: 'High', why: '+5% Attack, +5% Defense, +5% Health, +5% Lethality - universal bonuses for all troops.' },
      { question: 'Main troop type Charms at Level 8+', impact: 'High', why: 'Focused investment in your primary class pays off in every fight.' },
      { question: 'Combat pet at Level 50+', impact: 'Medium-High', why: 'Higher level = bigger buff. L100 pet gives ~2x the buff of L50.' },
      { question: 'Main combat troops T9 or T10', impact: 'Very High', why: 'Higher tier = higher base stats. All % bonuses multiply off this base.' },
    ],
  };

  const phases = [
    { id: 'early_game', label: 'Early Game (F9-19)', color: 'text-green-400' },
    { id: 'mid_game', label: 'Mid Game (F20-29)', color: 'text-blue-400' },
    { id: 'late_game', label: 'Late Game (F30+)', color: 'text-purple-400' },
  ];

  return (
    <>
      <div className="card mb-6">
        <h2 className="text-xl font-bold text-frost mb-2">Combat Stat Priorities</h2>
        <p className="text-frost-muted text-sm mb-4">Key milestones to check at each game phase. If you answer "No" to these, you've found a weakness.</p>

        <div className="space-y-4">
          {phases.map((phase) => (
            <details key={phase.id} className="bg-surface rounded-lg" open={phase.id === gamePhase || (gamePhase === 'endgame' && phase.id === 'late_game')}>
              <summary className={`cursor-pointer p-3 font-semibold ${phase.color}`}>
                {phase.label}
              </summary>
              <div className="p-3 pt-0 space-y-2">
                {milestones[phase.id as keyof typeof milestones]?.map((m, i) => (
                  <div key={i} className={`bg-background rounded-lg p-3 border-l-4 ${
                    m.impact === 'Critical' || m.impact === 'Very High' ? 'border-l-red-500' :
                    m.impact === 'High' ? 'border-l-orange-500' :
                    m.impact === 'Medium-High' ? 'border-l-yellow-500' :
                    'border-l-blue-500'
                  }`}>
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${impactColors[m.impact]}`}>
                        {m.impact}
                      </span>
                      <span className="font-medium text-frost text-sm">{m.question}</span>
                    </div>
                    <p className="text-xs text-frost-muted">{m.why}</p>
                  </div>
                ))}
              </div>
            </details>
          ))}
        </div>
      </div>

      {/* Stat Stacking Example */}
      <div className="card">
        <h2 className="text-xl font-bold text-frost mb-4">How Stats Compound: A Real Example</h2>
        <p className="text-frost-muted text-sm mb-4 italic">Two players with 100,000 T10 Infantry each</p>

        <div className="grid md:grid-cols-2 gap-4 mb-4">
          {/* Player A - Neglected */}
          <div className="bg-surface rounded-lg p-4 border-2 border-red-500/50">
            <h3 className="text-lg font-bold text-red-400 mb-3">Neglected Hidden Stats</h3>
            <div className="text-xs text-frost-muted space-y-1">
              <p>Battle Research Attack: <span className="text-frost">+15%</span></p>
              <p>Battle Research Lethality: <span className="text-frost">+5%</span></p>
              <p>Daybreak Decorations: <span className="text-frost">No Mythics (0%)</span></p>
              <p>Chief Gear Set: <span className="text-frost">Epic (+10% ALL attack)</span></p>
              <p>Chief Gear Infantry: <span className="text-frost">+10% attack/defense</span></p>
              <p>Charms: <span className="text-frost">L3 average (+3% lethality/health)</span></p>
              <p>Pet Buff: <span className="text-frost">None active</span></p>
            </div>
            <div className="mt-3 pt-3 border-t border-red-500/30">
              <p className="text-sm">Total Attack: <strong className="text-frost">+28%</strong></p>
              <p className="text-sm">Total Lethality: <strong className="text-frost">+13%</strong></p>
              <p className="text-red-400 font-bold mt-2">Damage Multiplier: 1.44x</p>
            </div>
          </div>

          {/* Player B - Optimized */}
          <div className="bg-surface rounded-lg p-4 border-2 border-green-500/50">
            <h3 className="text-lg font-bold text-green-400 mb-3">Optimized Hidden Stats</h3>
            <div className="text-xs text-frost-muted space-y-1">
              <p>Battle Research Attack: <span className="text-frost">+25%</span></p>
              <p>Battle Research Lethality: <span className="text-frost">+20%</span></p>
              <p>Daybreak Decorations: <span className="text-frost">+10% ATK, +10% DEF, +5% ToL</span></p>
              <p>Chief Gear Set: <span className="text-frost">Mythic (+25% ALL attack)</span></p>
              <p>Chief Gear Infantry: <span className="text-frost">+25% attack/defense</span></p>
              <p>Charms: <span className="text-frost">L8 average (+12% lethality/health)</span></p>
              <p>Pet Buff: <span className="text-frost">Saber-tooth (+10% lethality)</span></p>
            </div>
            <div className="mt-3 pt-3 border-t border-green-500/30">
              <p className="text-sm">Total Attack: <strong className="text-frost">+77%</strong></p>
              <p className="text-sm">Total Lethality: <strong className="text-frost">+50%</strong></p>
              <p className="text-green-400 font-bold mt-2">Damage Multiplier: 2.66x</p>
            </div>
          </div>
        </div>

        <div className="bg-fire/20 rounded-lg p-4 text-center">
          <p className="text-fire font-bold">
            Player B deals 88% more damage with identical troops and heroes.
          </p>
          <p className="text-sm text-frost-muted mt-1">That's the difference between winning and getting crushed.</p>
        </div>
      </div>

      {/* Common Blind Spots (merged from former Blind Spots tab) */}
      <div className="card">
        <h2 className="text-xl font-bold text-frost mb-2">Common Blind Spots</h2>
        <p className="text-frost-muted text-sm mb-4">Things most players skip that cost them battles.</p>

        <div className="space-y-4">
          {[
            {
              name: 'Battle Research Lethality',
              severity: 'CRITICAL',
              explanation: 'Most players research Attack before Lethality. But Lethality is a MULTIPLIER on Attack. If you have high Attack but low Lethality, you\'re leaving damage on the table.',
              fix: 'Prioritize Lethality research for your main troop type. It\'s often buried in the Battle tree.',
            },
            {
              name: 'Daybreak Island Battle Decorations',
              severity: 'CRITICAL',
              explanation: 'Daybreak seems like a cosmetic minigame. Most players build random decorations or ignore it. But Mythic battle decorations give +10% Attack or Defense PER DECORATION for your troop type.',
              fix: <>Build Mythic decorations for your MAIN troop type. <Link href="/daybreak" className="text-ice underline hover:text-frost">See Daybreak Island Guide</Link> for details.</>,
            },
            {
              name: 'Chief Charms',
              severity: 'HIGH',
              explanation: 'The Charm UI is confusing and materials are scattered. Most players upgrade randomly or ignore them.',
              fix: 'Upgrade all charms evenly for army-wide bonus, then focus on your main troop type.',
            },
            {
              name: 'Chief Gear Set Bonus',
              severity: 'MEDIUM-HIGH',
              explanation: 'Players max one Chief Gear piece while others lag behind, missing the 6-piece set bonus that gives Attack to ALL troops.',
              fix: 'Keep all 6 pieces at same tier. Priority: Infantry (Coat/Pants) > Marksman (Belt/Weapon) > Lancer (Cap/Watch).',
            },
            {
              name: 'Pet Buff Activation',
              severity: 'MEDIUM',
              explanation: 'Combat pets give +10% buffs but only for 2 hours. Players forget to activate before battles.',
              fix: 'Always activate Saber-tooth Tiger (Lethality) or Mammoth (Defense) before SvS/major fights.',
            },
          ].map((spot, i) => (
            <div key={i} className={`rounded-lg border-l-4 p-4 bg-surface ${
              spot.severity === 'CRITICAL' ? 'border-red-500' :
              spot.severity === 'HIGH' ? 'border-orange-500' :
              'border-yellow-500'
            }`}>
              <div className="flex items-center gap-3 mb-2">
                <span className={`px-2 py-0.5 rounded text-xs font-bold ${impactColors[spot.severity]}`}>
                  {spot.severity}
                </span>
                <h3 className="font-semibold text-frost">{spot.name}</h3>
              </div>
              <p className="text-frost-muted text-sm mb-3">{spot.explanation}</p>
              <div className="bg-green-500/10 rounded-lg p-3">
                <p className="text-sm"><strong className="text-green-400">Fix:</strong> <span className="text-frost-muted">{spot.fix}</span></p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

// ── Stats & Sources Tab (merged from 12 Combat Stats + All Stat Sources) ──

const TROOP_TYPES = ['Infantry', 'Lancer', 'Marksman'] as const;
const STAT_TYPES = ['Attack', 'Defense', 'Lethality', 'Health'] as const;

const statDescriptions: Record<string, string> = {
  Attack: 'Base damage dealt to enemies',
  Defense: 'Reduces incoming damage (damage mitigation)',
  Lethality: 'Armor penetration — multiplies with Attack',
  Health: 'HP pool — how much damage troops can absorb',
};

const troopColor: Record<string, string> = {
  Infantry: 'text-red-400',
  Lancer: 'text-green-400',
  Marksman: 'text-blue-400',
};

const troopBg: Record<string, string> = {
  Infantry: 'bg-red-500/10',
  Lancer: 'bg-green-500/10',
  Marksman: 'bg-blue-500/10',
};

// Stat source matrix: which sources affect which stats
const statSources = [
  {
    source: 'Hero Expedition Skills',
    affects: 'Class-specific',
    detail: 'Buffs specific to hero\'s troop class (Infantry/Lancer/Marksman)',
    infantry: true, lancer: true, marksman: true,
    stats: ['Attack', 'Defense', 'Lethality', 'Health'],
  },
  {
    source: 'Chief Gear',
    affects: 'Class-specific',
    detail: 'Coat/Pants → Infantry, Belt/Weapon → Marksman, Cap/Watch → Lancer',
    infantry: true, lancer: true, marksman: true,
    stats: ['Attack', 'Defense'],
  },
  {
    source: 'Chief Charms',
    affects: 'Class-specific',
    detail: 'Same class mapping as Chief Gear (L25+ unlock)',
    infantry: true, lancer: true, marksman: true,
    stats: ['Lethality', 'Health'],
  },
  {
    source: 'Daybreak Decorations',
    affects: 'Class-specific',
    detail: 'Mythic: +10% ATK or DEF per troop type decoration',
    infantry: true, lancer: true, marksman: true,
    stats: ['Attack', 'Defense'],
  },
  {
    source: 'Research (Battle)',
    affects: 'Class-specific',
    detail: 'Marksman/Lancer: ATK, DEF, Lethality. Infantry: ATK, DEF, Health',
    infantry: true, lancer: true, marksman: true,
    stats: ['Attack', 'Defense', 'Lethality', 'Health'],
  },
  {
    source: 'Pets',
    affects: 'ALL troops',
    detail: 'Saber-tooth (+Lethality), Cave Lion (+ATK), Mammoth (+DEF), Gorilla (+HP)',
    infantry: true, lancer: true, marksman: true,
    stats: ['Attack', 'Defense', 'Lethality', 'Health'],
  },
  {
    source: 'Alliance Tech',
    affects: 'ALL troops',
    detail: 'Universal Attack, Defense, Health bonuses',
    infantry: true, lancer: true, marksman: true,
    stats: ['Attack', 'Defense', 'Health'],
  },
  {
    source: 'Tree of Life',
    affects: 'ALL troops',
    detail: 'L4: +5% DEF, L6: +5% ATK, L9: +5% HP, L10: +5% Lethality',
    infantry: true, lancer: true, marksman: true,
    stats: ['Attack', 'Defense', 'Lethality', 'Health'],
  },
];

// Real battle data from battle_report.research.json
const battleData = {
  our: {
    infantry_attack: 745.8, infantry_defense: 715.8, infantry_lethality: 585.7, infantry_health: 518.3,
    lancer_attack: 703.0, lancer_defense: 682.6, lancer_lethality: 401.2, lancer_health: 376.1,
    marksman_attack: 801.8, marksman_defense: 758.9, marksman_lethality: 757.8, marksman_health: 543.6,
  },
  enemy: {
    infantry_attack: 357.3, infantry_defense: 359.8, infantry_lethality: 261.7, infantry_health: 288.1,
    lancer_attack: 324.7, lancer_defense: 310.9, lancer_lethality: 238.7, lancer_health: 266.6,
    marksman_attack: 333.6, marksman_defense: 324.4, marksman_lethality: 244.3, marksman_health: 281.1,
  },
};

function ratioColor(ratio: number): string {
  if (ratio >= 2) return 'text-green-400 bg-green-500/20';
  if (ratio >= 1.5) return 'text-yellow-400 bg-yellow-500/20';
  return 'text-orange-400 bg-orange-500/20';
}

function StatsSourcesTab() {
  return (
    <div className="space-y-6">
      {/* 12 Stats Grid */}
      <div className="card">
        <h2 className="text-xl font-bold text-frost mb-2">The 12 Combat Stats</h2>
        <p className="text-frost-muted text-sm mb-4">
          Every troop type has 4 stats. These bonuses stack from ALL sources to 300-800%+.
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border">
                <th className="text-left p-2 text-frost-muted">Stat</th>
                {TROOP_TYPES.map((t) => (
                  <th key={t} className={`text-center p-2 ${troopColor[t]} font-bold`}>{t}</th>
                ))}
                <th className="text-left p-2 text-frost-muted pl-4">What It Does</th>
              </tr>
            </thead>
            <tbody>
              {STAT_TYPES.map((stat) => (
                <tr key={stat} className="border-b border-surface-border/30">
                  <td className="p-2 font-semibold text-frost">{stat}</td>
                  {TROOP_TYPES.map((t) => (
                    <td key={t} className={`text-center p-2 ${troopBg[t]} rounded`}>
                      <span className={troopColor[t]}>{t[0]}-{stat[0]}</span>
                    </td>
                  ))}
                  <td className="p-2 text-frost-muted pl-4 text-xs">{statDescriptions[stat]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-4 bg-fire/10 border border-fire/30 rounded-lg p-3">
          <p className="text-sm text-fire font-medium">
            Attack x Lethality MULTIPLY together in the damage formula. A 10% boost to each = 21% more damage.
            Defense x Health MULTIPLY for survivability. Neglecting any one stat leaves a massive gap.
          </p>
        </div>
      </div>

      {/* Stat Source Matrix */}
      <div className="card">
        <h2 className="text-xl font-bold text-frost mb-2">Stat Source Matrix</h2>
        <p className="text-frost-muted text-sm mb-4">
          Which sources feed which stats. Check marks mean the source contributes to that stat.
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-surface-border">
                <th className="text-left p-2 text-frost-muted">Source</th>
                <th className="text-center p-2 text-frost-muted">Scope</th>
                <th className="text-center p-2 text-frost-muted">ATK</th>
                <th className="text-center p-2 text-frost-muted">DEF</th>
                <th className="text-center p-2 text-frost-muted">LETH</th>
                <th className="text-center p-2 text-frost-muted">HP</th>
              </tr>
            </thead>
            <tbody>
              {statSources.map((s) => (
                <tr key={s.source} className="border-b border-surface-border/30">
                  <td className="p-2">
                    <p className="font-medium text-frost">{s.source}</p>
                    <p className="text-frost-muted">{s.detail}</p>
                  </td>
                  <td className={`text-center p-2 ${s.affects === 'ALL troops' ? 'text-ice' : 'text-yellow-400'}`}>
                    {s.affects}
                  </td>
                  {(['Attack', 'Defense', 'Lethality', 'Health'] as const).map((stat) => (
                    <td key={stat} className="text-center p-2">
                      {s.stats.includes(stat) ? (
                        <span className="text-green-400 font-bold">+</span>
                      ) : (
                        <span className="text-surface-border">-</span>
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Real Battle Data */}
      <div className="card">
        <h2 className="text-xl font-bold text-frost mb-2">Real Battle Data</h2>
        <p className="text-frost-muted text-sm mb-4">
          Actual stat bonuses from a battle report. The winner had roughly 2x stats across the board.
        </p>

        {/* Battle Result Summary */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3 text-center">
            <p className="text-green-400 font-bold text-lg">WINNER</p>
            <p className="text-frost text-sm">158,012 troops</p>
            <p className="text-green-400 text-2xl font-bold">1,663</p>
            <p className="text-xs text-frost-muted">casualties (1%)</p>
          </div>
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-center">
            <p className="text-red-400 font-bold text-lg">LOSER</p>
            <p className="text-frost text-sm">182,892 troops</p>
            <p className="text-red-400 text-2xl font-bold">53,514</p>
            <p className="text-xs text-frost-muted">casualties (29%)</p>
          </div>
        </div>

        {/* Side-by-side stat comparison */}
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-surface-border">
                <th className="text-left p-2 text-frost-muted">Stat</th>
                <th className="text-right p-2 text-green-400">Winner</th>
                <th className="text-right p-2 text-red-400">Loser</th>
                <th className="text-center p-2 text-frost-muted">Ratio</th>
              </tr>
            </thead>
            <tbody>
              {TROOP_TYPES.map((troop) => (
                STAT_TYPES.map((stat) => {
                  const key = `${troop.toLowerCase()}_${stat.toLowerCase()}` as keyof typeof battleData.our;
                  const ours = battleData.our[key];
                  const theirs = battleData.enemy[key];
                  const ratio = ours / theirs;
                  return (
                    <tr key={key} className="border-b border-surface-border/20">
                      <td className={`p-2 ${troopColor[troop]}`}>{troop} {stat}</td>
                      <td className="text-right p-2 text-frost font-mono">{ours.toFixed(1)}%</td>
                      <td className="text-right p-2 text-frost-muted font-mono">{theirs.toFixed(1)}%</td>
                      <td className="text-center p-2">
                        <span className={`px-2 py-0.5 rounded text-xs font-bold ${ratioColor(ratio)}`}>
                          {ratio.toFixed(2)}x
                        </span>
                      </td>
                    </tr>
                  );
                })
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-4 bg-fire/20 rounded-lg p-4 text-center">
          <p className="text-fire font-bold">
            Even with fewer troops (158k vs 183k), the ~2x stat advantage resulted in 1,663 vs 53,514 casualties.
          </p>
          <p className="text-sm text-frost-muted mt-1">Stats matter more than troop count.</p>
        </div>
      </div>

      {/* Detailed Source Breakdown (merged from former All Stat Sources tab) */}
      <div className="card">
        <h2 className="text-xl font-bold text-frost mb-2">Source Deep Dive</h2>
        <p className="text-frost-muted text-sm mb-4">Expand each source for detailed breakdowns, priority order, and common mistakes.</p>

        <div className="space-y-3">
          {[
            {
              id: 'daybreak', name: 'Daybreak Island Decorations', impact: 'VERY HIGH', neglected: true,
              content: (
                <div className="space-y-3 text-sm">
                  <p className="text-frost-muted">Permanent | <Link href="/daybreak" className="text-ice underline hover:text-frost">See full Daybreak Island Guide</Link></p>
                  <div className="bg-fire/10 border border-fire/30 rounded-lg p-3 text-fire">
                    Combat stats come from DECORATIONS you place on the island, not just Tree of Life progression.
                  </div>
                  <div>
                    <h4 className="font-semibold text-frost mb-2">Mythic Battle Decorations (+10% at max):</h4>
                    <div className="grid grid-cols-3 gap-3">
                      {[
                        { troop: 'Infantry', color: 'text-red-400', decos: [['Floating Market', 'ATK +10%'], ['Snow Castle', 'DEF +10%']] },
                        { troop: 'Lancer', color: 'text-green-400', decos: [['Amphitheatre', 'ATK +10%'], ['Elegant Villa', 'DEF +10%']] },
                        { troop: 'Marksman', color: 'text-blue-400', decos: [['Observation Deck', 'ATK +10%'], ['Art Gallery', 'DEF +10%']] },
                      ].map((g) => (
                        <div key={g.troop} className="bg-surface rounded-lg p-3">
                          <p className={`font-medium mb-1 ${g.color}`}>{g.troop}</p>
                          {g.decos.map(([name, eff]) => <p key={name} className="text-xs text-frost-muted">{name}: {eff}</p>)}
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
                    <h4 className="font-semibold text-red-400 mb-1">Common Mistake:</h4>
                    <p className="text-frost-muted">Players ignore decorations or build random ones. Someone with maxed Floating Market + Snow Castle has +20% Infantry stats you don&apos;t.</p>
                  </div>
                </div>
              ),
            },
            {
              id: 'research', name: 'Research - Battle Tree', impact: 'HIGH', neglected: true,
              content: (
                <div className="space-y-3 text-sm">
                  <p className="text-frost-muted">Permanent</p>
                  <div>
                    <h4 className="font-semibold text-frost mb-2">Priority Order:</h4>
                    <ol className="text-frost-muted space-y-1 list-decimal list-inside">
                      <li>Lethality (your main troop type) - BIGGEST damage multiplier</li>
                      <li>Attack (your main troop type) - Base damage increase</li>
                      <li>Defense (your main troop type) - Reduces losses</li>
                      <li>Regimental Expansion - More troops = more damage</li>
                    </ol>
                  </div>
                  <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
                    <h4 className="font-semibold text-red-400 mb-1">Common Mistake:</h4>
                    <p className="text-frost-muted">Researching Growth/Economy tree while ignoring Battle tree after Tool Enhancement VII</p>
                  </div>
                </div>
              ),
            },
            {
              id: 'chief_gear', name: 'Chief Gear', impact: 'VERY HIGH', neglected: false,
              content: (
                <div className="space-y-3 text-sm">
                  <p className="text-frost-muted">Permanent</p>
                  <div>
                    <h4 className="font-semibold text-frost mb-2">Stats Provided:</h4>
                    <ul className="text-frost-muted space-y-1">
                      <li>Coat/Pants: Infantry Attack/Defense</li>
                      <li>Belt/Weapon: Marksman Attack/Defense</li>
                      <li>Cap/Watch: Lancer Attack/Defense</li>
                      <li>3-piece set: Defense boost for ALL troops</li>
                      <li>6-piece set: Attack boost for ALL troops</li>
                    </ul>
                  </div>
                  <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
                    <h4 className="font-semibold text-red-400 mb-1">Common Mistake:</h4>
                    <p className="text-frost-muted">Maxing one piece while others lag behind. Set bonuses require same tier.</p>
                  </div>
                </div>
              ),
            },
            {
              id: 'charms', name: 'Chief Charms', impact: 'MEDIUM-HIGH', neglected: true,
              content: (
                <div className="space-y-3 text-sm">
                  <p className="text-frost-muted">Permanent | Unlocks: Furnace Level 25</p>
                  <p className="text-ice text-xs">Evenly upgrading all charms grants an ARMY-WIDE lethality/health boost on top of individual bonuses</p>
                  <div>
                    <h4 className="font-semibold text-frost mb-2">Priority:</h4>
                    <ol className="text-frost-muted space-y-1 list-decimal list-inside">
                      <li>Upgrade evenly for army-wide bonus</li>
                      <li>Focus on your main troop type&apos;s charms</li>
                      <li>Target Level 11 on priority charms before spreading</li>
                    </ol>
                  </div>
                </div>
              ),
            },
            {
              id: 'pets', name: 'Pet Combat Skills', impact: 'HIGH', neglected: true,
              content: (
                <div className="space-y-3 text-sm">
                  <p className="text-frost-muted">Temporary (2h buffs)</p>
                  <div className="grid grid-cols-2 gap-2">
                    {[
                      { name: 'Saber-tooth Tiger', effect: '+10% Lethality', tier: 'S-TIER' },
                      { name: 'Mammoth', effect: '+10% Defense', tier: 'S-TIER' },
                      { name: 'Frost Gorilla', effect: '+10% Health', tier: 'S-TIER' },
                      { name: 'Cave Lion', effect: '+10% Attack', tier: 'A-TIER' },
                    ].map((pet) => (
                      <div key={pet.name} className="bg-surface rounded-lg p-2">
                        <p className="font-medium text-frost text-xs">{pet.name}</p>
                        <p className="text-[10px] text-frost-muted">{pet.effect} for 2h ({pet.tier})</p>
                      </div>
                    ))}
                  </div>
                  <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
                    <h4 className="font-semibold text-red-400 mb-1">Common Mistake:</h4>
                    <p className="text-frost-muted">Not activating combat pets before SvS/battles.</p>
                  </div>
                </div>
              ),
            },
            {
              id: 'hero_skills', name: 'Hero Expedition Skills', impact: 'VERY HIGH', neglected: false,
              content: (
                <div className="space-y-3 text-sm">
                  <p className="text-frost-muted">Permanent</p>
                  <div className="space-y-2">
                    {[
                      ['Rally Joining', 'ONLY the leftmost hero\'s expedition skill (top-right) applies'],
                      ['Rally Leading', 'All your expedition skills apply'],
                      ['Garrison', 'All defending expedition skills apply'],
                    ].map(([key, value]) => (
                      <div key={key} className="bg-surface rounded-lg p-2">
                        <span className="font-medium text-ice">{key}:</span>{' '}
                        <span className="text-frost-muted">{value}</span>
                      </div>
                    ))}
                  </div>
                  <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3">
                    <h4 className="font-semibold text-green-400 mb-1">Best Rally Joiners:</h4>
                    <p className="text-frost-muted">Jessie: +25% DMG dealt (Best), Jeronimo: Infantry ATK multiplier</p>
                  </div>
                </div>
              ),
            },
            {
              id: 'alliance_tech', name: 'Alliance Technology', impact: 'MEDIUM', neglected: true,
              content: (
                <div className="space-y-3 text-sm">
                  <p className="text-frost-muted">Permanent (while in alliance)</p>
                  <ul className="text-frost-muted space-y-1">
                    <li>Troop Attack %, Defense %, Health %</li>
                    <li>March Capacity, Rally Capacity</li>
                  </ul>
                  <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
                    <h4 className="font-semibold text-red-400 mb-1">Common Mistake:</h4>
                    <p className="text-frost-muted">Joining a dead alliance for &apos;peace&apos; and missing out on tech bonuses.</p>
                  </div>
                </div>
              ),
            },
          ].map((source) => (
            <details key={source.id} className="bg-surface rounded-lg">
              <summary className="cursor-pointer p-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="font-semibold text-frost text-sm">{source.name}</span>
                  {source.neglected && (
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-red-500/20 text-red-400">
                      NEGLECTED
                    </span>
                  )}
                </div>
                <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${impactColors[source.impact]}`}>
                  {source.impact}
                </span>
              </summary>
              <div className="px-3 pb-3">{source.content}</div>
            </details>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Battle Estimator Tab ──

const PRESETS: Record<string, Record<string, number>> = {
  'Typical F25 (~300%)': Object.fromEntries(
    TROOP_TYPES.flatMap((t) => STAT_TYPES.map((s) => [`${t.toLowerCase()}_${s.toLowerCase()}`, 300]))
  ),
  'Typical FC3 (~500%)': Object.fromEntries(
    TROOP_TYPES.flatMap((t) => STAT_TYPES.map((s) => [`${t.toLowerCase()}_${s.toLowerCase()}`, 500]))
  ),
  'Typical FC8 (~700%)': Object.fromEntries(
    TROOP_TYPES.flatMap((t) => STAT_TYPES.map((s) => [`${t.toLowerCase()}_${s.toLowerCase()}`, 700]))
  ),
};

function BattleEstimatorTab() {
  const { token } = useAuth();
  const defaultStats = () =>
    Object.fromEntries(
      TROOP_TYPES.flatMap((t) => STAT_TYPES.map((s) => [`${t.toLowerCase()}_${s.toLowerCase()}`, 400]))
    );

  const [myStats, setMyStats] = useState<Record<string, number>>(defaultStats);
  const [enemyStats, setEnemyStats] = useState<Record<string, number>>(defaultStats);
  const [whatIfBonus, setWhatIfBonus] = useState(0);
  const [whatIfStat, setWhatIfStat] = useState('all_attack');
  const [dataLoaded, setDataLoaded] = useState(false);
  const [untrackedSources, setUntrackedSources] = useState<string[]>([]);

  // Pre-populate from user's tracked data
  useEffect(() => {
    if (!token) return;
    api<{ stat_insights: {
      gear_stats?: Record<string, Record<string, number>>;
      charm_stats?: Record<string, number>;
      untracked_sources?: string[];
    } }>('/api/recommendations/stat-insights', { token })
      .then((data) => {
        const insights = data.stat_insights;
        if (!insights) return;

        // Backend shape: gear_stats = {Infantry: {attack: 30, defense: 30}, ...}
        const gearStats = insights.gear_stats || {};
        // Backend shape: charm_stats = {Infantry: 4.5, Marksman: 3.0, ...}
        const charmStats = insights.charm_stats || {};
        const untracked = insights.untracked_sources || [];

        // Only pre-populate if we have meaningful data
        const hasGear = Object.values(gearStats).some(
          (troopStats) => typeof troopStats === 'object' && Object.values(troopStats).some((v) => v > 0)
        );
        const hasCharms = Object.values(charmStats).some((v) => typeof v === 'number' && v > 0);
        if (!hasGear && !hasCharms) return;

        // Build estimated stats from tracked sources (gear + charms only)
        // Start at a base of 100% (T10 base), add gear + charm contributions
        const estimated: Record<string, number> = {};
        for (const t of TROOP_TYPES) {
          const troopName = t; // e.g. "Infantry" — matches backend keys
          for (const s of STAT_TYPES) {
            const key = `${t.toLowerCase()}_${s.toLowerCase()}`;
            let base = 100; // T10 troops base
            // Gear contributes to Attack and Defense
            if (s === 'Attack' || s === 'Defense') {
              const gearTroop = gearStats[troopName];
              if (gearTroop) {
                base += gearTroop[s.toLowerCase()] || 0;
              }
            }
            // Charms contribute to Lethality and Health
            if (s === 'Lethality' || s === 'Health') {
              const charmTotal = charmStats[troopName] || 0;
              base += charmTotal / 2;
            }
            estimated[key] = Math.round(base);
          }
        }

        setMyStats(estimated);
        setUntrackedSources(untracked);
        setDataLoaded(true);
      })
      .catch(() => {
        // Silently fail - user can still manually enter stats
      });
  }, [token]);

  const applyPreset = (target: 'my' | 'enemy', presetKey: string) => {
    const setter = target === 'my' ? setMyStats : setEnemyStats;
    setter({ ...PRESETS[presetKey] });
  };

  const updateStat = (target: 'my' | 'enemy', key: string, value: number) => {
    const setter = target === 'my' ? setMyStats : setEnemyStats;
    setter((prev) => ({ ...prev, [key]: value }));
  };

  // Calculate effective stats with what-if bonus
  const effectiveMyStats = { ...myStats };
  if (whatIfBonus !== 0) {
    const applyToAll = (statSuffix: string) => {
      for (const t of TROOP_TYPES) effectiveMyStats[`${t.toLowerCase()}_${statSuffix}`] += whatIfBonus;
    };
    if (whatIfStat === 'all_attack') applyToAll('attack');
    else if (whatIfStat === 'all_defense') applyToAll('defense');
    else if (whatIfStat === 'all_lethality') applyToAll('lethality');
    else if (whatIfStat === 'all_health') applyToAll('health');
    else {
      // Specific stat key like infantry_attack
      effectiveMyStats[whatIfStat] = (effectiveMyStats[whatIfStat] || 0) + whatIfBonus;
    }
  }

  // Find weakest stat ratio
  let weakestKey = '';
  let weakestRatio = Infinity;

  const ratios: Record<string, number> = {};
  for (const t of TROOP_TYPES) {
    for (const s of STAT_TYPES) {
      const key = `${t.toLowerCase()}_${s.toLowerCase()}`;
      const mine = Math.max(effectiveMyStats[key] || 0, 1);
      const theirs = Math.max(enemyStats[key] || 0, 1);
      const r = mine / theirs;
      ratios[key] = r;
      if (r < weakestRatio) {
        weakestRatio = r;
        weakestKey = key;
      }
    }
  }

  // Overall advantage: geometric mean of all ratios (clamped to positive)
  const allRatios = Object.values(ratios);
  const overallAdvantage = allRatios.length > 0
    ? Math.pow(allRatios.reduce((a, b) => a * b, 1), 1 / allRatios.length)
    : 1;

  function advantageColor(r: number): string {
    if (r >= 2) return 'text-green-400 bg-green-500/20';
    if (r >= 1.5) return 'text-yellow-300 bg-yellow-500/20';
    if (r >= 1) return 'text-orange-400 bg-orange-500/20';
    return 'text-red-400 bg-red-500/20';
  }

  function overallLabel(r: number): string {
    if (r >= 2) return 'Dominant advantage — expect minimal casualties';
    if (r >= 1.5) return 'Strong advantage — should win with moderate casualties';
    if (r >= 1.2) return 'Slight advantage — close fight, outcome uncertain';
    if (r >= 1) return 'Roughly even — could go either way';
    return 'Disadvantage — likely to lose unless hero skills compensate';
  }

  return (
    <div className="space-y-6">
      {/* Stat Input Panels */}
      <div className="grid md:grid-cols-2 gap-4">
        {/* My Stats */}
        <div className="card border-green-500/30">
          <h3 className="text-lg font-bold text-green-400 mb-2">Your Stats (%)</h3>
          {dataLoaded && (
            <div className="bg-ice/10 border border-ice/20 rounded-lg p-2 mb-2">
              <p className="text-[10px] text-ice">Pre-filled from your Chief Gear &amp; Charms data. Adjust values to include other sources.</p>
              {untrackedSources.length > 0 && (
                <p className="text-[10px] text-frost-muted mt-1">Not tracked yet: {untrackedSources.join(', ')}</p>
              )}
            </div>
          )}
          <div className="flex flex-wrap gap-1 mb-3">
            {Object.keys(PRESETS).map((pk) => (
              <button
                key={pk}
                onClick={() => applyPreset('my', pk)}
                className="px-2 py-1 rounded text-xs bg-surface text-frost-muted hover:text-frost hover:bg-surface-hover transition-colors"
              >
                {pk}
              </button>
            ))}
          </div>
          {TROOP_TYPES.map((t) => (
            <div key={t} className="mb-3">
              <p className={`text-xs font-bold ${troopColor[t]} mb-1`}>{t}</p>
              <div className="grid grid-cols-4 gap-1">
                {STAT_TYPES.map((s) => {
                  const key = `${t.toLowerCase()}_${s.toLowerCase()}`;
                  return (
                    <div key={key}>
                      <label className="text-[10px] text-frost-muted block">{s.slice(0, 3)}</label>
                      <input
                        type="number"
                        value={myStats[key] || 0}
                        onChange={(e) => updateStat('my', key, Number(e.target.value))}
                        className="w-full bg-surface border border-surface-border rounded px-1.5 py-1 text-xs text-frost focus:outline-none focus:border-ice/50"
                      />
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Enemy Stats */}
        <div className="card border-red-500/30">
          <h3 className="text-lg font-bold text-red-400 mb-3">Enemy Stats (%)</h3>
          <div className="flex flex-wrap gap-1 mb-3">
            {Object.keys(PRESETS).map((pk) => (
              <button
                key={pk}
                onClick={() => applyPreset('enemy', pk)}
                className="px-2 py-1 rounded text-xs bg-surface text-frost-muted hover:text-frost hover:bg-surface-hover transition-colors"
              >
                {pk}
              </button>
            ))}
          </div>
          {TROOP_TYPES.map((t) => (
            <div key={t} className="mb-3">
              <p className={`text-xs font-bold ${troopColor[t]} mb-1`}>{t}</p>
              <div className="grid grid-cols-4 gap-1">
                {STAT_TYPES.map((s) => {
                  const key = `${t.toLowerCase()}_${s.toLowerCase()}`;
                  return (
                    <div key={key}>
                      <label className="text-[10px] text-frost-muted block">{s.slice(0, 3)}</label>
                      <input
                        type="number"
                        value={enemyStats[key] || 0}
                        onChange={(e) => updateStat('enemy', key, Number(e.target.value))}
                        className="w-full bg-surface border border-surface-border rounded px-1.5 py-1 text-xs text-frost focus:outline-none focus:border-ice/50"
                      />
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Results Panel */}
      <div className="card">
        <h3 className="text-lg font-bold text-frost mb-3">Advantage Analysis</h3>

        {/* Overall */}
        <div className={`rounded-lg p-4 mb-4 text-center ${advantageColor(overallAdvantage)}`}>
          <p className="text-2xl font-bold">{overallAdvantage.toFixed(2)}x Overall</p>
          <p className="text-sm mt-1">{overallLabel(overallAdvantage)}</p>
        </div>

        {/* Per-stat ratios */}
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-surface-border">
                <th className="text-left p-2 text-frost-muted">Stat</th>
                <th className="text-right p-2 text-green-400">You</th>
                <th className="text-right p-2 text-red-400">Enemy</th>
                <th className="text-center p-2 text-frost-muted">Ratio</th>
              </tr>
            </thead>
            <tbody>
              {TROOP_TYPES.map((t) =>
                STAT_TYPES.map((s) => {
                  const key = `${t.toLowerCase()}_${s.toLowerCase()}`;
                  const mine = effectiveMyStats[key] || 0;
                  const theirs = enemyStats[key] || 0;
                  const r = ratios[key];
                  const isWeakest = key === weakestKey;
                  return (
                    <tr key={key} className={`border-b border-surface-border/20 ${isWeakest ? 'bg-red-500/10' : ''}`}>
                      <td className={`p-2 ${troopColor[t]} ${isWeakest ? 'font-bold' : ''}`}>
                        {isWeakest && <span className="text-red-400 mr-1">!</span>}
                        {t} {s}
                      </td>
                      <td className="text-right p-2 text-frost font-mono">{mine.toFixed(0)}%</td>
                      <td className="text-right p-2 text-frost-muted font-mono">{theirs.toFixed(0)}%</td>
                      <td className="text-center p-2">
                        <span className={`px-2 py-0.5 rounded text-xs font-bold ${advantageColor(r)}`}>
                          {r.toFixed(2)}x
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Weakest stat callout */}
        {weakestKey && (
          <div className="mt-4 bg-red-500/10 border border-red-500/30 rounded-lg p-3">
            <p className="text-sm">
              <strong className="text-red-400">Weakest stat:</strong>{' '}
              <span className="text-frost">{weakestKey.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}</span>
              {' '}at {weakestRatio.toFixed(2)}x.
              <span className="text-frost-muted"> Upgrading this stat will have the highest marginal impact.</span>
            </p>
          </div>
        )}

        {/* Real data reference */}
        <div className="mt-3 bg-surface rounded-lg p-3 text-xs text-frost-muted">
          <strong className="text-frost">Reference:</strong> A player with ~2x stat advantage across the board suffered only 1% casualties while the opponent lost 29% — with fewer troops.
        </div>
      </div>

      {/* What If Mode */}
      <div className="card border-ice/30">
        <h3 className="text-lg font-bold text-frost mb-3">"What If" Simulator</h3>
        <p className="text-frost-muted text-sm mb-4">See how upgrading a stat source would change your advantage.</p>

        <div className="flex flex-wrap items-end gap-3 mb-4">
          <div>
            <label className="text-xs text-frost-muted block mb-1">Bonus Source</label>
            <select
              value={whatIfStat}
              onChange={(e) => setWhatIfStat(e.target.value)}
              className="bg-surface border border-surface-border rounded px-2 py-1.5 text-sm text-frost focus:outline-none focus:border-ice/50"
            >
              <option value="all_attack">All Troops Attack</option>
              <option value="all_defense">All Troops Defense</option>
              <option value="all_lethality">All Troops Lethality</option>
              <option value="all_health">All Troops Health</option>
              {TROOP_TYPES.map((t) =>
                STAT_TYPES.map((s) => (
                  <option key={`${t}_${s}`} value={`${t.toLowerCase()}_${s.toLowerCase()}`}>
                    {t} {s}
                  </option>
                ))
              )}
            </select>
          </div>
          <div>
            <label className="text-xs text-frost-muted block mb-1">Bonus Amount (%)</label>
            <input
              type="number"
              value={whatIfBonus}
              onChange={(e) => setWhatIfBonus(Number(e.target.value))}
              className="w-24 bg-surface border border-surface-border rounded px-2 py-1.5 text-sm text-frost focus:outline-none focus:border-ice/50"
            />
          </div>
        </div>

        {/* Quick presets */}
        <div className="flex flex-wrap gap-2">
          {[
            { label: 'Mythic Deco (+10% ATK)', stat: 'infantry_attack', bonus: 10 },
            { label: 'Mythic Deco (+10% DEF)', stat: 'infantry_defense', bonus: 10 },
            { label: 'Pet Buff (+10% Lethality)', stat: 'all_lethality', bonus: 10 },
            { label: 'Tree of Life L10 (+5% all)', stat: 'all_lethality', bonus: 5 },
            { label: 'Clear bonus', stat: 'all_attack', bonus: 0 },
          ].map((preset) => (
            <button
              key={preset.label}
              onClick={() => { setWhatIfStat(preset.stat); setWhatIfBonus(preset.bonus); }}
              className="px-3 py-1.5 rounded text-xs bg-surface text-frost-muted hover:text-frost hover:bg-surface-hover transition-colors"
            >
              {preset.label}
            </button>
          ))}
        </div>
        <p className="text-[10px] text-frost-muted mt-2">
          Presets default to Infantry — change the dropdown for your troop type. Mythic Decorations are class-specific (+10% to ONE type, not all).
        </p>

        {whatIfBonus !== 0 && (
          <div className="mt-3 bg-ice/10 border border-ice/30 rounded-lg p-3">
            <p className="text-sm text-ice">
              With +{whatIfBonus}% to {whatIfStat.replace(/_/g, ' ')}: Overall advantage changes to{' '}
              <strong>{overallAdvantage.toFixed(2)}x</strong>
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function PhasePrioritiesTab({ gamePhase }: { gamePhase: string }) {
  const [activePhase, setActivePhase] = useState(gamePhase);

  const phases = {
    early_game: {
      label: 'Early Game (F9-19)',
      color: 'text-green-400',
      focus: 'Not yet - focus on progression',
      priorities: [
        'Tool Enhancement research (I-III minimum)',
        'Unlock and level your core heroes',
        'Troop tier upgrades (T5-T6)',
        'Join an active alliance for tech',
      ],
      skip: ['Daybreak Island (not unlocked until F19)', 'Deep Battle research'],
    },
    mid_game: {
      label: 'Mid Game (F20-29)',
      color: 'text-blue-400',
      focus: 'Building foundation - these stats compound',
      priorities: [
        'Tool Enhancement VII (CRITICAL)',
        'Daybreak Mythic decorations for main troop type (Attack + Defense)',
        'All 6 Chief Gear pieces to same tier (Gold), Infantry first',
        'Battle Research - your main troop type\'s Lethality',
        'Chief Charms to L5 across the board',
      ],
      skip: ['Economy research', 'Defensive gear'],
    },
    late_game: {
      label: 'Late Game (F30+ / FC Era)',
      color: 'text-purple-400',
      focus: 'Maximizing multipliers - every % matters',
      priorities: [
        'Battle Research - Max Lethality and Attack',
        'Max level Daybreak Mythic decorations (both Attack + Defense)',
        'All 6 Chief Gear pieces to Pink/Red tier, Infantry first',
        'Chief Charms to L11 (main troop type)',
        'Combat pets to L50+',
        'T10 troops',
        'Tree of Life L10',
      ],
      skip: ['Nothing - optimize everything'],
    },
    endgame: {
      label: 'Endgame (FC5+ / Competitive)',
      color: 'text-fire',
      focus: 'Marginal gains - the 1-2% differences decide close fights',
      priorities: [
        'Max all Battle Research',
        'Max all Daybreak decorations + Starry Lighthouse',
        'All Chief Gear to Mythic',
        'All Charms to L11-16',
        'Combat pets to L100',
        'T11 troops',
      ],
      skip: [],
    },
  };

  return (
    <div className="card">
      <h2 className="text-xl font-bold text-frost mb-4">What to Focus on By Phase</h2>

      <div className="flex flex-wrap gap-2 mb-6">
        {Object.entries(phases).map(([key, phase]) => (
          <button
            key={key}
            onClick={() => setActivePhase(key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activePhase === key
                ? `bg-surface-hover ${phase.color}`
                : 'bg-surface text-frost-muted hover:text-frost'
            }`}
          >
            {phase.label}
          </button>
        ))}
      </div>

      {Object.entries(phases).map(([key, phase]) => (
        activePhase === key && (
          <div key={key} className="space-y-4">
            <div className="bg-surface rounded-lg p-4">
              <p className="text-frost-muted">
                <strong className={phase.color}>Combat Focus:</strong> {phase.focus}
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div className="bg-surface rounded-lg p-4">
                <h3 className="font-semibold text-green-400 mb-3">Top Priorities</h3>
                <ol className="text-sm text-frost-muted space-y-2 list-decimal list-inside">
                  {phase.priorities.map((p, i) => (
                    <li key={i}>{p}</li>
                  ))}
                </ol>
              </div>

              {phase.skip.length > 0 && (
                <div className="bg-surface rounded-lg p-4">
                  <h3 className="font-semibold text-frost-muted mb-3">Skip For Now</h3>
                  <ul className="text-sm text-frost-muted space-y-2">
                    {phase.skip.map((s, i) => (
                      <li key={i}>• {s}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )
      ))}
    </div>
  );
}
