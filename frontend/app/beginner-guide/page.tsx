'use client';

import PageLayout from '@/components/PageLayout';

const sections = [
  {
    title: 'First Week Priorities',
    icon: '🎯',
    items: [
      'Rush Furnace upgrades - they unlock everything',
      'Join an active alliance immediately',
      'Complete all daily tasks for rewards',
      'Save speedups for SvS events',
      'Don\'t spread resources across many heroes',
    ],
  },
  {
    title: 'Hero Investment (Early Game)',
    icon: '🦸',
    items: [
      'Focus on 3-4 heroes max as F2P',
      'Jessie is your most important hero (Gen 1) - keep her first in rallies',
      'Sergey is essential for garrison defense',
      'Level exploration skills for PvE, expedition skills for PvP',
      'Don\'t waste shards on B-tier or lower heroes',
    ],
  },
  {
    title: 'Resource Management',
    icon: '💰',
    items: [
      'Never use speedups outside of events',
      'Fire crystals are extremely valuable - use wisely',
      'Keep resources under protection threshold or spend before going offline',
      'Build multiple farms if you\'re serious about the game',
      'Weekly events often have the best rewards',
    ],
  },
  {
    title: 'Combat Basics',
    icon: '⚔️',
    items: [
      'Troop type matters: Infantry > Lancer > Marksman > Infantry (rock-paper-scissors)',
      'Higher tier troops are always better - focus on unlocking T10+',
      'Chief gear provides massive stat boosts - don\'t neglect it',
      'Hero gear becomes important at FC30+',
      'Join rallies even if weak - your joiner skill helps the whole team',
    ],
  },
  {
    title: 'SvS (State vs State)',
    icon: '🏆',
    items: [
      'Speedups only give points on Day 1, 2, and 5',
      'Shield when offline during SvS or you WILL be attacked',
      'Coordinate with alliance on rally targets',
      'Field Triage heals 30-90% of troops after SvS ends',
      'Losing SvS means enemy state controls your state for 3 days',
    ],
  },
  {
    title: 'Common Mistakes to Avoid',
    icon: '⚠️',
    items: [
      'Spreading resources across too many heroes',
      'Using speedups outside of events',
      'Ignoring chief gear progression',
      'Not joining an active alliance',
      'Going offline unshielded during SvS',
      'Buying packs without checking their value first',
    ],
  },
];

const keyMilestones = [
  { furnace: 9, unlock: 'Research Tree', description: 'Start upgrading research immediately' },
  { furnace: 18, unlock: 'Pets', description: 'Unlocks at 55 days + F18' },
  { furnace: 19, unlock: 'Daybreak Island', description: 'Major combat stat source' },
  { furnace: 25, unlock: 'Chief Charms', description: 'Significant power boost' },
  { furnace: 30, unlock: 'FC Mode', description: 'Furnace becomes infinite progression' },
];

export default function BeginnerGuidePage() {
  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Beginner Guide</h1>
          <p className="text-frost-muted mt-2">
            Essential tips for new Whiteout Survival players
          </p>
        </div>

        {/* Quick Start Banner */}
        <div className="card mb-8 border-ice/30 bg-gradient-to-r from-ice/10 to-ice/5">
          <div className="flex items-start gap-4">
            <span className="text-4xl">❄️</span>
            <div>
              <h2 className="text-lg font-bold text-frost mb-2">TL;DR for New Players</h2>
              <ol className="text-sm text-frost-muted space-y-1 list-decimal list-inside">
                <li>Rush to Furnace 30 - everything else is secondary</li>
                <li>Focus on 3-4 heroes max (Jessie, Sergey, Jeronimo, Molly)</li>
                <li>Save ALL speedups for SvS events</li>
                <li>Join an active alliance on day 1</li>
                <li>Shield before going offline during SvS</li>
              </ol>
            </div>
          </div>
        </div>

        {/* Key Milestones */}
        <div className="card mb-8">
          <h2 className="section-header">Key Furnace Milestones</h2>
          <div className="space-y-3">
            {keyMilestones.map((milestone) => (
              <div
                key={milestone.furnace}
                className="flex items-center gap-4 p-3 rounded-lg bg-surface"
              >
                <div className="w-12 h-12 bg-fire/20 rounded-lg flex items-center justify-center">
                  <span className="text-lg font-bold text-fire">F{milestone.furnace}</span>
                </div>
                <div className="flex-1">
                  <p className="font-medium text-frost">{milestone.unlock}</p>
                  <p className="text-sm text-frost-muted">{milestone.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Guide Sections */}
        <div className="space-y-6">
          {sections.map((section) => (
            <div key={section.title} className="card">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-2xl">{section.icon}</span>
                <h2 className="text-lg font-bold text-frost">{section.title}</h2>
              </div>
              <ul className="space-y-2">
                {section.items.map((item, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-frost-muted">
                    <span className="text-ice">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Generation Reference */}
        <div className="card mt-8">
          <h2 className="section-header">Hero Generations Reference</h2>
          <p className="text-sm text-frost-muted mb-4">
            Heroes unlock as your server ages. Focus on available heroes first.
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
            <div className="p-2 rounded bg-surface">
              <p className="font-medium text-frost">Gen 1 (0-40 days)</p>
              <p className="text-frost-muted text-xs">Jessie, Sergey, Jeronimo, Molly, Natalia...</p>
            </div>
            <div className="p-2 rounded bg-surface">
              <p className="font-medium text-frost">Gen 2 (40-120 days)</p>
              <p className="text-frost-muted text-xs">Alonso, Flint, Philly</p>
            </div>
            <div className="p-2 rounded bg-surface">
              <p className="font-medium text-frost">Gen 3 (120-200 days)</p>
              <p className="text-frost-muted text-xs">Logan, Mia, Greg</p>
            </div>
            <div className="p-2 rounded bg-surface">
              <p className="font-medium text-frost">Gen 4+ (200+ days)</p>
              <p className="text-frost-muted text-xs">Better heroes as server ages</p>
            </div>
          </div>
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
