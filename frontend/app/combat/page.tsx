'use client';

import { useState } from 'react';
import PageLayout from '@/components/PageLayout';

type TabKey = 'quick-audit' | 'stat-sources' | 'blind-spots' | 'phase-priorities';

const tabs: { key: TabKey; label: string }[] = [
  { key: 'quick-audit', label: 'Quick Audit' },
  { key: 'stat-sources', label: 'All Stat Sources' },
  { key: 'blind-spots', label: 'Blind Spots' },
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

export default function CombatPage() {
  const [activeTab, setActiveTab] = useState<TabKey>('quick-audit');

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
            The difference is in the "hidden multipliers" - stats from Research, Daybreak Island, Chief Gear,
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
            <h3 className="font-semibold text-frost mb-3">Troop Type Advantage (~30% bonus damage)</h3>
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
        <div className="flex flex-wrap gap-2 mb-6 border-b border-frost/10 pb-4">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? 'bg-ice/20 text-ice'
                  : 'bg-surface text-frost-muted hover:text-frost hover:bg-surface-hover'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === 'quick-audit' && <QuickAuditTab />}
        {activeTab === 'stat-sources' && <StatSourcesTab />}
        {activeTab === 'blind-spots' && <BlindSpotsTab />}
        {activeTab === 'phase-priorities' && <PhasePrioritiesTab />}
      </div>
    </PageLayout>
  );
}

function QuickAuditTab() {
  const milestones = {
    early_game: [
      { question: 'Use Jessie/Jeronimo in leftmost slot when joining rallies', impact: 'High', why: 'Only leftmost hero\'s expedition skill applies. Wrong hero = wasted slot.' },
      { question: 'Alliance actively researching combat tech', impact: 'Medium', why: 'Alliance tech provides permanent stat boosts while you\'re a member.' },
    ],
    mid_game: [
      { question: 'Completed Tool Enhancement VII', impact: 'Critical', why: '35% faster research on everything. Must be done first.' },
      { question: 'Researched Tier 4+ Lethality for your main troop type', impact: 'Very High', why: 'Lethality is a damage MULTIPLIER. This is often the difference in close fights.' },
      { question: 'Mythic Attack decoration for main troop type (Floating Market/Amphitheatre/Observation Deck)', impact: 'Very High', why: '+10% Attack for your troop type. Massive damage boost most players skip.' },
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
            <details key={phase.id} className="bg-surface rounded-lg" open={phase.id === 'mid_game'}>
              <summary className={`cursor-pointer p-3 font-semibold ${phase.color}`}>
                {phase.label}
              </summary>
              <div className="p-3 pt-0 space-y-2">
                {milestones[phase.id as keyof typeof milestones]?.map((m, i) => (
                  <div key={i} className="bg-background rounded-lg p-3 border-l-3" style={{ borderLeftColor: impactColors[m.impact]?.split(' ')[0].replace('text-', '') }}>
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
              <p>Charms: <span className="text-frost">L3 average (+3% attack)</span></p>
              <p>Pet Buff: <span className="text-frost">None active</span></p>
            </div>
            <div className="mt-3 pt-3 border-t border-red-500/30">
              <p className="text-sm">Total Attack: <strong className="text-frost">+28%</strong></p>
              <p className="text-sm">Total Lethality: <strong className="text-frost">+10%</strong></p>
              <p className="text-red-400 font-bold mt-2">Damage Multiplier: 1.41x</p>
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
              <p>Charms: <span className="text-frost">L8 average (+12% attack)</span></p>
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
    </>
  );
}

function StatSourcesTab() {
  const sources = [
    {
      id: 'daybreak',
      name: 'Daybreak Island - Battle Enhancer Decorations',
      impact: 'VERY HIGH',
      neglected: true,
      category: 'Permanent',
      overview: 'Combat stats come from DECORATIONS you place on the island, not just Tree of Life progression.',
      mythicDecos: {
        infantry: { 'Floating Market': 'Infantry Attack +10%', 'Snow Castle': 'Infantry Defense +10%' },
        lancer: { 'Amphitheatre': 'Lancer Attack +10%', 'Elegant Villa': 'Lancer Defense +10%' },
        marksman: { 'Observation Deck': 'Marksman Attack +10%', 'Art Gallery': 'Marksman Defense +10%' },
      },
      treeOfLife: ['L4: Troops Defense +5%', 'L6: Troops Attack +5%', 'L9: Troops Health +5%', 'L10: Troops Lethality +5%'],
      maxPotential: '+10% Attack, +10% Defense from Mythic decorations alone | With Tree of Life: +15% Attack, +15% Defense, +5% Health, +5% Lethality total',
      priority: ['Build Mythic decorations for your MAIN troop type first', 'Get both Attack AND Defense Mythic for main type (+20% combined)', 'Tree of Life to L10 for universal buffs'],
      mistake: 'Players ignore Daybreak decorations or build random ones for aesthetics. Someone with maxed Floating Market + Snow Castle has +20% Infantry stats you don\'t.',
    },
    {
      id: 'research',
      name: 'Research - Battle Tree',
      impact: 'HIGH',
      neglected: true,
      category: 'Permanent',
      stats: ['Infantry/Lancer/Marksman Attack', 'Infantry/Lancer/Marksman Defense', 'Marksman/Lancer Lethality (CRITICAL)', 'Regimental Expansion (more troops per march)'],
      priority: ['Lethality (your main troop type) - BIGGEST damage multiplier', 'Attack (your main troop type) - Base damage increase', 'Defense (your main troop type) - Reduces losses', 'Regimental Expansion - More troops = more damage'],
      mistake: 'Researching Growth/Economy tree while ignoring Battle tree after Tool Enhancement VII',
    },
    {
      id: 'chief_gear',
      name: 'Chief Gear',
      impact: 'VERY HIGH',
      neglected: false,
      category: 'Permanent',
      stats: ['Coat/Pants: Infantry Attack/Defense', 'Belt/Weapon: Marksman Attack/Defense', 'Cap/Watch: Lancer Attack/Defense', '3-piece set: Defense boost for ALL troops', '6-piece set: Attack boost for ALL troops'],
      priority: ['Keep all 6 pieces at SAME TIER for set bonuses', 'Infantry (Coat/Pants) - Frontline, engage first', 'Marksman (Belt/Weapon) - Key damage dealers', 'Lancer (Cap/Watch) - Mid-line support'],
      mistake: 'Maxing one piece while others lag behind. Set bonuses require same tier - 6-piece Attack bonus helps ALL troops.',
    },
    {
      id: 'charms',
      name: 'Chief Charms',
      impact: 'MEDIUM-HIGH',
      neglected: true,
      category: 'Permanent',
      unlock: 'Furnace Level 25',
      stats: ['Cap/Watch: Lancer Attack/Defense', 'Coat/Pants: Infantry Attack/Defense', 'Belt/Weapon: Marksman Attack/Defense'],
      bonus: 'Evenly upgrading all charms grants an ARMY-WIDE attack/defense boost on top of individual bonuses',
      priority: ['Upgrade evenly for army-wide bonus', 'Focus on your main troop type\'s charms', 'Target Level 11 on priority charms before spreading'],
      mistake: 'Ignoring charms because the UI is confusing and materials seem scarce. Each charm level adds combat stats.',
    },
    {
      id: 'pets',
      name: 'Pet Combat Skills',
      impact: 'HIGH',
      neglected: true,
      category: 'Temporary (2h buffs)',
      combatPets: [
        { name: 'Saber-tooth Tiger', skill: 'Lethality Boost', effect: '+10% troop lethality for 2h', tier: 'S-TIER for attack' },
        { name: 'Mammoth', skill: 'Defense Boost', effect: '+10% troop defense for 2h', tier: 'S-TIER for defense' },
        { name: 'Frost Gorilla', skill: 'Health Boost', effect: '+10% troop health for 2h', tier: 'S-TIER for survivability' },
        { name: 'Cave Lion', skill: 'Attack Boost', effect: '+10% troop attack for 2h', tier: 'A-TIER for attack' },
      ],
      mistake: 'Not activating combat pets before SvS/battles. Also not leveling combat pets - a L50 pet gives much smaller buff than L100.',
    },
    {
      id: 'hero_skills',
      name: 'Hero Expedition Skills',
      impact: 'VERY HIGH',
      neglected: false,
      category: 'Permanent',
      critical: {
        'Rally Joining': 'ONLY the leftmost hero\'s expedition skill (top-right skill) applies',
        'Rally Leading': 'All your expedition skills apply',
        'Garrison': 'All defending expedition skills apply',
      },
      bestJoiners: ['Jessie: +25% DMG dealt to all troops (Best rally joiner)', 'Jeronimo: Infantry ATK multiplier'],
      bestGarrison: ['Sergey: -20% DMG taken (Best defensive skill)'],
      mistake: 'Using wrong hero in leftmost slot when joining rallies. Their expedition skill is wasted.',
    },
    {
      id: 'alliance_tech',
      name: 'Alliance Technology',
      impact: 'MEDIUM',
      neglected: true,
      category: 'Permanent (while in alliance)',
      stats: ['Troop Attack %', 'Troop Defense %', 'Troop Health %', 'March Capacity', 'Rally Capacity'],
      note: 'This is alliance-wide. Strong alliances have better tech.',
      actions: ['Donate to alliance tech daily', 'Join an active alliance that prioritizes combat tech', 'Check alliance tech levels before joining'],
      mistake: 'Joining a dead alliance for \'peace\' and missing out on tech bonuses.',
    },
  ];

  return (
    <div className="space-y-4">
      <div className="card">
        <h2 className="text-xl font-bold text-frost mb-2">All Combat Stat Sources</h2>
        <p className="text-frost-muted text-sm">Every place your combat stats come from. Expand each to see details.</p>
      </div>

      {sources.map((source) => (
        <details key={source.id} className="card">
          <summary className="cursor-pointer flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="font-semibold text-frost">{source.name}</span>
              {source.neglected && (
                <span className="px-2 py-0.5 rounded text-xs font-medium bg-red-500/20 text-red-400">
                  OFTEN NEGLECTED
                </span>
              )}
            </div>
            <span className={`px-2 py-0.5 rounded text-xs font-medium ${impactColors[source.impact]}`}>
              {source.impact} IMPACT
            </span>
          </summary>

          <div className="mt-4 space-y-4 text-sm">
            <p className="text-frost-muted">{source.category}{source.unlock ? ` | Unlocks: ${source.unlock}` : ''}</p>

            {source.overview && (
              <div className="bg-fire/10 border border-fire/30 rounded-lg p-3 text-fire">
                {source.overview}
              </div>
            )}

            {source.stats && (
              <div>
                <h4 className="font-semibold text-frost mb-2">Stats Provided:</h4>
                <ul className="text-frost-muted space-y-1">
                  {source.stats.map((stat, i) => (
                    <li key={i}>• {stat}</li>
                  ))}
                </ul>
              </div>
            )}

            {source.mythicDecos && (
              <div>
                <h4 className="font-semibold text-frost mb-2">Mythic Battle Decorations (+10% at max):</h4>
                <div className="grid grid-cols-3 gap-3">
                  {Object.entries(source.mythicDecos).map(([troop, decos]) => (
                    <div key={troop} className="bg-surface rounded-lg p-3">
                      <p className={`font-medium mb-1 ${troop === 'infantry' ? 'text-red-400' : troop === 'lancer' ? 'text-green-400' : 'text-blue-400'}`}>
                        {troop.charAt(0).toUpperCase() + troop.slice(1)}
                      </p>
                      {Object.entries(decos).map(([name, effect]) => (
                        <p key={name} className="text-xs text-frost-muted">{name}: {effect}</p>
                      ))}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {source.treeOfLife && (
              <div>
                <h4 className="font-semibold text-frost mb-2">Tree of Life (Universal Buffs):</h4>
                <ul className="text-frost-muted space-y-1">
                  {source.treeOfLife.map((level, i) => (
                    <li key={i}>• {level}</li>
                  ))}
                </ul>
              </div>
            )}

            {source.combatPets && (
              <div>
                <h4 className="font-semibold text-frost mb-2">Combat Pets:</h4>
                <div className="grid md:grid-cols-2 gap-2">
                  {source.combatPets.map((pet) => (
                    <div key={pet.name} className="bg-surface rounded-lg p-3">
                      <p className="font-medium text-frost">{pet.name}</p>
                      <p className="text-xs text-frost-muted">{pet.skill}: {pet.effect}</p>
                      <p className="text-xs text-ice">{pet.tier}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {source.critical && (
              <div>
                <h4 className="font-semibold text-frost mb-2">Critical Understanding:</h4>
                <div className="space-y-2">
                  {Object.entries(source.critical).map(([key, value]) => (
                    <div key={key} className="bg-surface rounded-lg p-2">
                      <span className="font-medium text-ice">{key}:</span>{' '}
                      <span className="text-frost-muted">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {source.bestJoiners && (
              <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3">
                <h4 className="font-semibold text-green-400 mb-1">Best Rally Joiners:</h4>
                <ul className="text-frost-muted space-y-1">
                  {source.bestJoiners.map((j, i) => <li key={i}>• {j}</li>)}
                </ul>
              </div>
            )}

            {source.priority && (
              <div>
                <h4 className="font-semibold text-frost mb-2">Priority Order:</h4>
                <ol className="text-frost-muted space-y-1 list-decimal list-inside">
                  {source.priority.map((p, i) => (
                    <li key={i}>{p}</li>
                  ))}
                </ol>
              </div>
            )}

            {source.mistake && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
                <h4 className="font-semibold text-red-400 mb-1">Common Mistake:</h4>
                <p className="text-frost-muted">{source.mistake}</p>
              </div>
            )}
          </div>
        </details>
      ))}
    </div>
  );
}

function BlindSpotsTab() {
  const blindSpots = [
    {
      name: 'Battle Research Lethality',
      severity: 'CRITICAL',
      explanation: 'Most players research Attack before Lethality. But Lethality is a MULTIPLIER on Attack. If you have high Attack but low Lethality, you\'re leaving damage on the table.',
      fix: 'Prioritize Lethality research for your main troop type. It\'s often buried in the Battle tree.',
    },
    {
      name: 'Daybreak Island Battle Decorations',
      severity: 'CRITICAL',
      explanation: 'Daybreak seems like a cosmetic minigame. Most players build random decorations or ignore it. But Mythic battle decorations give +10% Attack or Defense PER DECORATION for your troop type. An opponent with both Attack + Defense Mythics has +20% stats you don\'t have.',
      fix: 'Build Mythic decorations for your MAIN troop type: Infantry (Floating Market + Snow Castle), Lancer (Amphitheatre + Elegant Villa), Marksman (Observation Deck + Art Gallery). Level them up for full +10% each.',
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
    {
      name: 'Alliance Tech',
      severity: 'MEDIUM',
      explanation: 'Players join weak/dead alliances for \'peace\' and miss out on tech bonuses that strong alliances have.',
      fix: 'Check alliance tech levels before joining. An active alliance\'s tech gives permanent stat boosts.',
    },
    {
      name: 'Rally Joiner Hero Slot',
      severity: 'MEDIUM',
      explanation: 'When joining rallies, ONLY the leftmost hero\'s expedition skill applies. Using the wrong hero wastes a skill slot.',
      fix: 'Always put Jessie (best) or Jeronimo in leftmost slot when joining rallies.',
    },
  ];

  return (
    <div className="card">
      <h2 className="text-xl font-bold text-frost mb-2">Common Blind Spots</h2>
      <p className="text-frost-muted text-sm mb-4">Things most players skip that cost them battles.</p>

      <div className="space-y-4">
        {blindSpots.map((spot, i) => (
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
  );
}

function PhasePrioritiesTab() {
  const [activePhase, setActivePhase] = useState('mid_game');

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
