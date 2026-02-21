'use client';

import { useState } from 'react';
import PageLayout from '@/components/PageLayout';

type TabKey = 'getting-started' | 'progression' | 'first-30-days' | 'resources' | 'game-systems' | 'tips';

const tabs: { key: TabKey; label: string }[] = [
  { key: 'getting-started', label: 'Getting Started' },
  { key: 'progression', label: 'Progression' },
  { key: 'first-30-days', label: 'First 30 Days' },
  { key: 'resources', label: 'Resources' },
  { key: 'game-systems', label: 'Game Systems' },
  { key: 'tips', label: 'Tips & Checklist' },
];

export default function BeginnerGuidePage() {
  const [activeTab, setActiveTab] = useState<TabKey>('getting-started');

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-frost">Beginner's Guide</h1>
          <p className="text-frost-muted mt-2">
            Everything you need to know for your first 30+ days in Whiteout Survival.
          </p>
          <p className="text-frost-muted text-sm italic">Welcome, Chief. Stay warm out there.</p>
        </div>

        {/* Key Advice Banner */}
        <div className="card mb-6 border-fire/30 bg-gradient-to-r from-fire/10 to-fire/5">
          <div className="flex items-start gap-4">
            <span className="text-3xl">💡</span>
            <div>
              <h2 className="text-lg font-bold text-frost mb-2">The Most Important Advice</h2>
              <p className="text-sm text-frost-muted">
                This game rewards <strong className="text-frost">patience and planning</strong>. The players who get ahead aren't the ones who spend
                the most - they're the ones who spend <strong className="text-frost">smart</strong>. Save your resources for events, focus on heroes
                over troops, and stay active in your alliance. Almost everything you do can earn extra rewards
                if you do it during the right event.
              </p>
            </div>
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
        <div className="space-y-6">
          {activeTab === 'getting-started' && <GettingStartedTab />}
          {activeTab === 'progression' && <ProgressionTab />}
          {activeTab === 'first-30-days' && <First30DaysTab />}
          {activeTab === 'resources' && <ResourcesTab />}
          {activeTab === 'game-systems' && <GameSystemsTab />}
          {activeTab === 'tips' && <TipsTab />}
        </div>

        {/* CTA */}
        <div className="card mt-8 text-center">
          <h3 className="text-lg font-bold text-frost mb-2">Ready to track your progress?</h3>
          <p className="text-frost-muted mb-4">
            Use Bear's Den to track your heroes, get AI recommendations, and optimize your gameplay.
          </p>
          <a href="/heroes" className="btn-primary">
            Start Tracking Heroes
          </a>
        </div>
      </div>
    </PageLayout>
  );
}

function GettingStartedTab() {
  return (
    <>
      {/* Golden Rule */}
      <div className="card">
        <h2 className="text-xl font-bold text-frost mb-3">The Golden Rule</h2>
        <p className="text-frost-muted">
          <strong className="text-fire">Save your resources for events.</strong> Don't spend gems, speedups, or upgrade materials the moment
          you get them just to clear red notification dots. Almost everything you do in this game can earn
          you extra rewards if you do it during the right event. This one habit will put you weeks ahead
          of other players.
        </p>
      </div>

      {/* What Matters Most */}
      <div className="card">
        <h2 className="text-xl font-bold text-frost mb-4">What Matters Most</h2>

        <div className="space-y-6">
          {/* Hero Power */}
          <div>
            <h3 className="text-lg font-semibold text-ice mb-2">1. Hero Power (Your #1 Priority)</h3>
            <p className="text-frost-muted mb-3">
              Heroes are the foundation of everything in this game. A strong hero lineup beats a large army every time.
            </p>

            <div className="bg-surface rounded-lg p-4 mb-3">
              <h4 className="font-medium text-frost mb-2">Why heroes matter:</h4>
              <ul className="text-sm text-frost-muted space-y-1">
                <li>• Heroes multiply troop effectiveness - A max-skilled hero can make your troops 2-3x more effective</li>
                <li>• Heroes are permanent - Troops die, heroes don't</li>
                <li>• Heroes unlock content - Exploration stages, expedition battles, and events all require hero power</li>
                <li>• SvS is won by heroes - Hero skills and gear matter more than raw troop count</li>
              </ul>
            </div>

            <div className="bg-surface rounded-lg p-4">
              <h4 className="font-medium text-frost mb-2">Early hero priorities:</h4>
              <ul className="text-sm text-frost-muted space-y-1">
                <li>• Focus on 3-5 heroes maximum (F2P: stick to 3 core heroes)</li>
                <li>• Level them evenly rather than maxing one</li>
                <li>• Prioritize expedition skills over exploration skills for combat</li>
                <li>• Legendary heroes {'>'} Epic heroes for long-term investment</li>
              </ul>
            </div>
          </div>

          {/* Furnace Level */}
          <div>
            <h3 className="text-lg font-semibold text-ice mb-2">2. Furnace Level (Your Progress Gate)</h3>
            <p className="text-frost-muted">
              Your Furnace level gates everything else. Each level unlocks new features, higher troop tiers,
              and better rewards. Rush your Furnace as your secondary priority after daily hero investments.
            </p>
          </div>

          {/* Troops */}
          <div>
            <h3 className="text-lg font-semibold text-ice mb-2">3. Troops (Important but Replaceable)</h3>
            <p className="text-frost-muted">
              You need troops to fight, gather, and fill rallies. But troops die and need to be rebuilt.
              Don't over-invest in troops early - build what you need, focus the rest on heroes and Furnace.
            </p>
          </div>
        </div>
      </div>
    </>
  );
}

function ProgressionTab() {
  const milestones = [
    { range: '1-8', name: 'Tutorial Phase', desc: 'Basic buildings, T1-T3 troops, initial heroes. Just follow the guide.' },
    { range: '9', name: 'Research Center', desc: 'Research unlocks! Always keep something researching. Prioritize Tool Enhancement at each tier for research speed.' },
    { range: '10-14', name: 'Early Game', desc: 'More building slots, T4 troops unlock, Alliance features. Join an active alliance ASAP.' },
    { range: '15', name: 'Hero Gear Unlocks', desc: 'You can now equip gear on heroes. Start collecting gear materials.' },
    { range: '16-18', name: 'Pets Unlock', desc: 'T5 troops. Pets unlock at F18 (requires 55+ server days). Start leveling combat pets.' },
    { range: '19', name: 'Daybreak Island', desc: 'Unlocks combat buff decorations. Build Mythic decorations (+10% stats) for your main troop type.' },
    { range: '20-24', name: 'Tier 6 Era', desc: 'T6 troops unlock. You\'re now a real contributor in alliance battles.' },
    { range: '25', name: 'Chief Charms & Labyrinth', desc: 'Chief Charms unlock — huge stat bonuses for your main troop type. Labyrinth provides mythic shards.' },
    { range: '26-29', name: 'Late Game Prep', desc: 'T7-T8 troops. Focus heavily on hero gear and skills now.' },
    { range: '30', name: 'FC Unlocks!', desc: 'Fire Crystal system, War Academy, and Hero Gear Mastery begin. T9 troops available.' },
    { range: 'FC1-FC10', name: 'Fire Crystal Era', desc: 'New upgrade currency (Fire Crystals). Much slower progression but huge power gains.' },
    { range: 'RFC1+', name: 'Refined FC Era', desc: 'Requires Refined Fire Crystals. You\'re now a veteran player.' },
  ];

  return (
    <>
      <div className="card">
        <h2 className="text-xl font-bold text-frost mb-4">Furnace Level Milestones</h2>
        <div className="space-y-3">
          {milestones.map((m, i) => (
            <div key={i} className="flex gap-4 p-3 bg-surface rounded-lg">
              <div className="w-20 shrink-0">
                <span className={`text-sm font-bold ${
                  m.range.includes('FC') || m.range.includes('RFC') ? 'text-fire' : 'text-ice'
                }`}>
                  F{m.range}
                </span>
              </div>
              <div>
                <p className="font-medium text-frost">{m.name}</p>
                <p className="text-sm text-frost-muted">{m.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-bold text-frost mb-3">How FC Building Upgrades Work</h2>
        <p className="text-frost-muted mb-4">
          Once you reach Furnace 30 (FC), building upgrades change from single upgrades to a <strong className="text-frost">5-phase incremental system</strong>:
        </p>
        <ul className="text-sm text-frost-muted space-y-2">
          <li>• Each FC level (FC1, FC2, etc.) has <strong className="text-frost">5 upgrade phases</strong> per building</li>
          <li>• You must complete all 5 phases to fully upgrade a building at that FC level</li>
          <li>• Each phase costs Fire Crystals instead of regular resources</li>
          <li>• Your Furnace must reach the next FC level before buildings can advance to their next FC tier</li>
          <li>• Example: To fully upgrade a building at FC3, you complete phases FC3-1, FC3-2, FC3-3, FC3-4, FC3-5</li>
        </ul>
      </div>
    </>
  );
}

function First30DaysTab() {
  const periods = [
    {
      days: 'Days 1-7',
      title: 'Foundation',
      items: [
        'Complete the tutorial and initial quests',
        'Join the best alliance that will accept you - Top alliances kill stronger beasts, win more events, and their members will teach you',
        'Focus on Furnace upgrades above all else',
        'Collect your free heroes from events and exploration',
        'Don\'t spend gems yet - save them',
      ],
    },
    {
      days: 'Days 8-14',
      title: 'Building Momentum',
      items: [
        'Keep pushing Furnace level (aim for F15+ by day 14)',
        'Start leveling your best 3-5 heroes evenly',
        'Participate in every event, even if you can\'t complete them',
        'Learn which events are worth spending resources on',
        'Build troops to meet alliance rally requirements',
      ],
    },
    {
      days: 'Days 15-21',
      title: 'Event Cycling',
      items: [
        'You\'ll start seeing event patterns repeat',
        'Save speedups for construction/research events',
        'Save hero materials for hero upgrade events',
        'Join alliance rallies to earn rewards and learn mechanics',
        'Start working on hero gear (unlocked at F15)',
      ],
    },
    {
      days: 'Days 22-30',
      title: 'Optimization',
      items: [
        'You should be approaching F20 if you\'ve been efficient',
        'Focus shifts more toward hero skills and gear',
        'Learn SvS basics and prepare for your first one',
        'Identify your main troop type (Infantry, Lancer, or Marksman)',
        'Specialize your hero lineup around that troop type',
      ],
    },
  ];

  return (
    <div className="card">
      <h2 className="text-xl font-bold text-frost mb-4">Your First 30 Days</h2>
      <div className="space-y-6">
        {periods.map((period, i) => (
          <div key={i} className="border-l-2 border-ice/30 pl-4">
            <h3 className="text-lg font-semibold text-ice mb-2">
              {period.days}: {period.title}
            </h3>
            <ul className="text-sm text-frost-muted space-y-2">
              {period.items.map((item, j) => (
                <li key={j}>• {item}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}

function ResourcesTab() {
  return (
    <>
      <div className="card">
        <h2 className="text-xl font-bold text-frost mb-4">Resource Management</h2>

        <div className="grid md:grid-cols-2 gap-4 mb-6">
          <div className="bg-surface rounded-lg p-4">
            <h3 className="font-semibold text-fire mb-2">What to Save (Don't Spend Randomly)</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">Gems</strong> - Save for Lucky Wheel during hero events, VIP shop refreshes</li>
              <li>• <strong className="text-frost">Speedups</strong> - Save for construction/research events (2x+ rewards)</li>
              <li>• <strong className="text-frost">Hero Shards</strong> - Save for hero upgrade events</li>
              <li>• <strong className="text-frost">Hero XP items</strong> - Save for hero leveling events</li>
              <li>• <strong className="text-frost">Skill Books</strong> - Save for skill upgrade events</li>
              <li>• <strong className="text-frost">Fire Crystals</strong> - Save for SvS Prep Day 1 (2,000 pts each)</li>
              <li>• <strong className="text-frost">Mithril</strong> - Save for SvS Prep Day 4 (40,000 pts each!)</li>
              <li>• <strong className="text-frost">Wild Marks</strong> - Save for SvS Day 3 (Advanced = 15,000 pts each)</li>
            </ul>
          </div>

          <div className="bg-surface rounded-lg p-4">
            <h3 className="font-semibold text-success mb-2">What to Spend Freely</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">Basic resources</strong> (meat, wood, coal, iron) - These accumulate fast</li>
              <li>• <strong className="text-frost">Stamina</strong> - Use it daily or it's wasted (caps at a maximum)</li>
              <li>• <strong className="text-frost">Alliance tokens</strong> - Spend daily, they reset</li>
            </ul>
          </div>
        </div>

        <div className="bg-surface rounded-lg p-4">
          <h3 className="font-semibold text-ice mb-2">Event Timing</h3>
          <p className="text-sm text-frost-muted mb-2">Most events run on predictable cycles:</p>
          <ul className="text-sm text-frost-muted space-y-1">
            <li>• <strong className="text-frost">Hero events</strong> - Usually every 1-2 weeks</li>
            <li>• <strong className="text-frost">Construction events</strong> - Very frequent, save your building speedups</li>
            <li>• <strong className="text-frost">Power events</strong> - Reward overall power gains, good time to do everything</li>
            <li>• <strong className="text-frost">Spend events</strong> - Sometimes spending gems/speedups gives bonus rewards</li>
          </ul>
          <p className="text-sm text-frost-muted mt-2 italic">
            When in doubt, wait. If an event is coming in 1-2 days, save your resources.
          </p>
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-bold text-frost mb-4">What to Prioritize Acquiring</h2>

        <div className="space-y-4">
          <div className="bg-surface rounded-lg p-4 border-l-4 border-fire">
            <h3 className="font-semibold text-fire mb-2">High Priority</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">Legendary Hero Shards</strong> - Any source. These are gold.</li>
              <li>• <strong className="text-frost">Expedition Skill Books</strong> (Mythic/Epic) - Combat power</li>
              <li>• <strong className="text-frost">Hero Gear Materials</strong> - For your main heroes</li>
              <li>• <strong className="text-frost">VIP Points</strong> - Permanent bonuses, very valuable long-term</li>
            </ul>
          </div>

          <div className="bg-surface rounded-lg p-4 border-l-4 border-ice">
            <h3 className="font-semibold text-ice mb-2">Medium Priority</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">Speedups</strong> - Always useful, especially construction</li>
              <li>• <strong className="text-frost">Fire Crystal Shards</strong> - You'll need mountains of these later</li>
              <li>• <strong className="text-frost">Chief Gear Materials</strong> - Steady improvement over time</li>
              <li>• <strong className="text-frost">Pet Materials</strong> - Pets add up over time</li>
            </ul>
          </div>

          <div className="bg-surface rounded-lg p-4 border-l-4 border-frost-muted">
            <h3 className="font-semibold text-frost-muted mb-2">Lower Priority</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Basic Resources - You'll get plenty from gathering</li>
              <li>• Exploration Skill Books - Nice but not critical</li>
              <li>• Random hero shards - Focus on specific heroes instead</li>
              <li>• Cosmetics - Zero gameplay value</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-bold text-frost mb-3">Where to Get Good Stuff</h2>
        <div className="grid md:grid-cols-2 gap-3">
          <div className="bg-surface rounded-lg p-3">
            <p className="font-medium text-frost">Lucky Wheel</p>
            <p className="text-sm text-frost-muted">Best source of legendary shards (save gems for hero events)</p>
          </div>
          <div className="bg-surface rounded-lg p-3">
            <p className="font-medium text-frost">Alliance Shop</p>
            <p className="text-sm text-frost-muted">Teleports, some materials</p>
          </div>
          <div className="bg-surface rounded-lg p-3">
            <p className="font-medium text-frost">VIP Shop</p>
            <p className="text-sm text-frost-muted">Skill books, shards (refresh with gems during events)</p>
          </div>
          <div className="bg-surface rounded-lg p-3">
            <p className="font-medium text-frost">Arena Shop</p>
            <p className="text-sm text-frost-muted">Chief gear materials, stamina</p>
          </div>
          <div className="bg-surface rounded-lg p-3 md:col-span-2">
            <p className="font-medium text-frost">Events</p>
            <p className="text-sm text-frost-muted">Best value for most items</p>
          </div>
        </div>
      </div>
    </>
  );
}

function GameSystemsTab() {
  return (
    <>
      <div className="card">
        <h2 className="text-xl font-bold text-frost mb-4">Game Systems Explained</h2>

        <div className="space-y-6">
          {/* Heroes */}
          <div>
            <h3 className="text-lg font-semibold text-ice mb-2">Heroes</h3>
            <p className="text-frost-muted mb-3">Your most important asset. Heroes have:</p>
            <ul className="text-sm text-frost-muted space-y-1 mb-3">
              <li>• <strong className="text-frost">Level</strong> (1-80) - Increases base stats</li>
              <li>• <strong className="text-frost">Stars</strong> (0-5) - Major power jumps, requires shards</li>
              <li>• <strong className="text-frost">Skills</strong> - Exploration (PvE) and Expedition (PvP/combat)</li>
              <li>• <strong className="text-frost">Gear</strong> - 4 slots per hero, huge stat boosts</li>
              <li>• <strong className="text-frost">Exclusive Gear</strong> - Special mythic gear for top-tier heroes</li>
            </ul>
            <p className="text-sm text-frost-muted bg-surface rounded p-2">
              Focus on <strong className="text-frost">Expedition skills</strong> for combat content (SvS, rallies). Exploration skills help with PvE stages.
            </p>
          </div>

          {/* Troops */}
          <div>
            <h3 className="text-lg font-semibold text-ice mb-2">Troops</h3>
            <p className="text-frost-muted mb-3">Three types with a rock-paper-scissors relationship:</p>
            <div className="grid grid-cols-3 gap-3 mb-3">
              <div className="bg-surface rounded-lg p-3 text-center">
                <p className="text-red-400 font-bold">Infantry</p>
                <p className="text-xs text-frost-muted">Beats Lancer</p>
                <p className="text-xs text-frost-muted">Loses to Marksman</p>
              </div>
              <div className="bg-surface rounded-lg p-3 text-center">
                <p className="text-green-400 font-bold">Lancer</p>
                <p className="text-xs text-frost-muted">Beats Marksman</p>
                <p className="text-xs text-frost-muted">Loses to Infantry</p>
              </div>
              <div className="bg-surface rounded-lg p-3 text-center">
                <p className="text-blue-400 font-bold">Marksman</p>
                <p className="text-xs text-frost-muted">Beats Infantry</p>
                <p className="text-xs text-frost-muted">Loses to Lancer</p>
              </div>
            </div>
            <p className="text-sm text-frost-muted">
              Pick <strong className="text-frost">ONE main type</strong> and specialize. Most players choose based on their best heroes.
              The class counter bonus is only ~10% — hero skills and stat investments matter far more than getting the matchup right.
            </p>
          </div>

          {/* Chief Gear & Charms */}
          <div>
            <h3 className="text-lg font-semibold text-ice mb-2">Chief Gear & Charms</h3>
            <p className="text-frost-muted mb-2">Equipment for your chief (separate from hero gear):</p>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">Chief Gear</strong> - 6 pieces (2 per troop type). Keep all at SAME TIER for 6-piece Attack set bonus. Infantry first when pushing to next tier.</li>
              <li>• <strong className="text-frost">Chief Charms</strong> - 6 charms, boost specific troop types. Focus on your main type.</li>
            </ul>
          </div>

          {/* Pets */}
          <div>
            <h3 className="text-lg font-semibold text-ice mb-2">Pets (F18 + 55 days)</h3>
            <p className="text-frost-muted mb-2">15 pets across 7 generations with combat buffs and daily utility:</p>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">Combat pets</strong> — buff troop stats for 2 hours (Attack, Defense, Lethality, Health). Always activate before battles!</li>
              <li>• <strong className="text-frost">Utility pets</strong> — daily use abilities (+Stamina, +Pet Food, complete resource tiles, unearth items)</li>
              <li>• <strong className="text-frost">Passive bonuses</strong> — every pet level adds permanent ATK/DEF %. SSR pets at L100 give +33.5% each</li>
              <li>• <strong className="text-frost">Refinement</strong> — uses Wild Marks to randomly boost pet stats further. Save marks for SvS Day 3</li>
              <li>• You can activate multiple pets at once — no limit</li>
            </ul>
          </div>

          {/* Daybreak Island */}
          <div>
            <h3 className="text-lg font-semibold text-ice mb-2">Daybreak Island (F19+)</h3>
            <p className="text-frost-muted mb-2">An island that provides combat buffs:</p>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">Tree of Life</strong> - Universal buffs for all troops</li>
              <li>• <strong className="text-frost">Battle Decorations</strong> - Troop-specific buffs (more impactful!)</li>
              <li>• Don't rush this over Furnace progression</li>
            </ul>
          </div>

          {/* Research */}
          <div>
            <h3 className="text-lg font-semibold text-ice mb-2">Research (F9+)</h3>
            <p className="text-frost-muted mb-2">Three trees: Battle, Growth, Economy.</p>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">Tool Enhancement FIRST</strong> at each tier (I-VII) — gives ~35% total research speed. Do this before anything else.</li>
              <li>• <strong className="text-frost">Lethality is a multiplier</strong> — Attack and Lethality multiply together. +10% each = +21% damage. Prioritize Lethality.</li>
              <li>• Priority order: Battle tree {'>'} Growth tree {'>'} Economy tree</li>
              <li>• Research your main troop type stats first before touching others</li>
              <li>• <strong className="text-frost">Always research something</strong> — dead time is wasted time</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Farm Accounts */}
      <div className="card border-ice/30">
        <h2 className="text-xl font-bold text-frost mb-3">Farm Accounts (Advanced Strategy)</h2>
        <p className="text-frost-muted mb-4">
          Once your main account is established, consider creating farm accounts to accelerate resource income.
        </p>

        <div className="space-y-4">
          <div className="bg-surface rounded-lg p-4">
            <h3 className="font-semibold text-frost mb-2">What are farm accounts?</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Separate accounts dedicated to gathering resources</li>
              <li>• Resources are transferred to your main account via alliance</li>
              <li>• Essential for F2P and dolphin players to keep pace</li>
            </ul>
          </div>

          <div className="bg-surface rounded-lg p-4">
            <h3 className="font-semibold text-fire mb-2">Farm account rules:</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">Must be in the SAME STATE</strong> as your main (resources can't cross states)</li>
              <li>• Only level Furnace and resource buildings (F18-F20 sweet spot)</li>
              <li>• No investment in heroes, research, or combat</li>
              <li>• Keep shielded 24/7 (farms are easy targets)</li>
              <li>• Use basic gathering heroes: Smith, Eugene, Charlie, Cloris</li>
            </ul>
          </div>

          <div className="bg-ice/10 rounded-lg p-4">
            <h3 className="font-semibold text-ice mb-2">Setting up in Bear's Den:</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Go to Profiles page and create a separate profile</li>
              <li>• Check "This is a farm account" to get specialized recommendations</li>
              <li>• Link it to your main account for coordinated advice</li>
            </ul>
          </div>
        </div>
      </div>
    </>
  );
}

function TipsTab() {
  const mistakes = [
    { title: 'Spreading heroes too thin', desc: 'Focus on 3-5 heroes, not 15. A few strong heroes beat many weak ones.' },
    { title: 'Ignoring events', desc: 'Events multiply your progress. Always check what\'s running before spending resources.' },
    { title: 'Rushing troops over heroes', desc: 'Troops die. Heroes don\'t. Prioritize hero investment.' },
    { title: 'Spending gems randomly', desc: 'Gems are premium currency. Save for Lucky Wheel and VIP shop refreshes.' },
    { title: 'Neglecting alliance activities', desc: 'Alliance help, rallies, and donations give huge rewards. Participate daily.' },
    { title: 'Upgrading the wrong skills', desc: 'Expedition skills matter for combat. Don\'t dump all books into exploration skills.' },
    { title: 'Not joining rallies', desc: 'Even if you\'re weak, join rallies. You get rewards and learn mechanics.' },
    { title: 'Clearing red dots immediately', desc: 'Those notification dots trick you into wasting resources outside events.' },
    { title: 'Ignoring research', desc: 'Always have something researching. The time adds up significantly.' },
    { title: 'Staying in a weak alliance out of loyalty', desc: 'Your alliance determines your growth speed. If your alliance is inactive, thank them and move up.' },
    { title: 'Leaving Cookhouse on default Healthy Gruel', desc: 'Switch to Fancy Meal immediately. Small meat increase, huge happiness/health boost. Tap Cookhouse > Stove > menu icon > Fancy Meal.' },
  ];

  const checklist = [
    { task: 'Collect free rewards', desc: 'Daily login, mail, event freebies' },
    { task: 'Use stamina', desc: 'Beast hunts or exploration (don\'t let it cap)' },
    { task: 'Alliance help', desc: 'Request and give help for free speedups' },
    { task: 'Donate to alliance tech', desc: 'Earns alliance tokens' },
    { task: 'Complete daily missions', desc: 'Easy rewards' },
    { task: 'Check events', desc: 'See what\'s running, plan your spending' },
    { task: 'Join rallies', desc: 'Even low participation helps' },
    { task: 'Keep buildings/research queued', desc: 'No idle time' },
    { task: 'Collect Daybreak Island essence', desc: 'If unlocked (caps at 12hrs)' },
    { task: 'Arena battles', desc: 'Use your attempts for tokens. Do these as close to reset as possible for higher rankings.' },
    { task: 'Keep Furnace at MAX power', desc: 'Never let coal run out. Survivors freeze and become unhappy/sick without heat.' },
    { task: 'Activate utility pets', desc: 'Arctic Wolf (+Stamina), Musk Ox (resource tile), Giant Tapir (+Pet Food), Giant Elk (item) — free daily value.' },
  ];

  return (
    <>
      {/* Common Mistakes */}
      <div className="card">
        <h2 className="text-xl font-bold text-frost mb-4">Common Beginner Mistakes</h2>
        <div className="space-y-3">
          {mistakes.map((mistake, i) => (
            <div key={i} className="flex gap-3 p-3 bg-surface rounded-lg">
              <span className="text-fire shrink-0">✗</span>
              <div>
                <p className="font-medium text-frost">{mistake.title}</p>
                <p className="text-sm text-frost-muted">{mistake.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Daily Checklist */}
      <div className="card">
        <h2 className="text-xl font-bold text-frost mb-2">Daily Checklist</h2>
        <p className="text-frost-muted mb-4">Do these every day for steady progress:</p>
        <div className="space-y-2">
          {checklist.map((item, i) => (
            <div key={i} className="flex gap-3 p-3 bg-surface rounded-lg">
              <span className="text-ice font-bold shrink-0">{i + 1}.</span>
              <div>
                <p className="font-medium text-frost">{item.task}</p>
                <p className="text-sm text-frost-muted">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
