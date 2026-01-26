'use client';

import PageLayout from '@/components/PageLayout';

const treeOfLifeLevels = [
  { level: 1, requirement: 'Initial', buff: 'Base stats' },
  { level: 2, requirement: 'Upgrade', buff: 'Minor buffs' },
  { level: 3, requirement: 'Upgrade', buff: 'Minor buffs' },
  { level: 4, requirement: 'Upgrade', buff: '+5% Defense (all troops)' },
  { level: 5, requirement: 'Upgrade', buff: 'Minor buffs' },
  { level: 6, requirement: 'Upgrade', buff: '+5% Attack (all troops)' },
  { level: 7, requirement: 'Upgrade', buff: 'Minor buffs' },
  { level: 8, requirement: 'Upgrade', buff: 'Minor buffs' },
  { level: 9, requirement: 'Upgrade', buff: '+5% Health (all troops)' },
  { level: 10, requirement: 'Max', buff: '+5% Lethality (all troops)' },
];

const mythicDecorations = [
  { name: 'Floating Market', type: 'Infantry ATK', maxBonus: '10%', levels: 10 },
  { name: 'Snow Castle', type: 'Infantry DEF', maxBonus: '10%', levels: 10 },
  { name: 'Amphitheatre', type: 'Lancer ATK', maxBonus: '10%', levels: 10 },
  { name: 'Elegant Villa', type: 'Lancer DEF', maxBonus: '10%', levels: 10 },
  { name: 'Observation Deck', type: 'Marksman ATK', maxBonus: '10%', levels: 10 },
  { name: 'Art Gallery', type: 'Marksman DEF', maxBonus: '10%', levels: 10 },
];

const epicDecorations = [
  { name: 'Various', type: 'Infantry', maxBonus: '2.5%', levels: 5 },
  { name: 'Various', type: 'Lancer', maxBonus: '2.5%', levels: 5 },
  { name: 'Various', type: 'Marksman', maxBonus: '2.5%', levels: 5 },
];

export default function DaybreakPage() {
  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Daybreak Island</h1>
          <p className="text-frost-muted mt-2">
            Major combat stat source - unlocks at Furnace 19
          </p>
        </div>

        {/* Quick Overview */}
        <div className="card mb-6 border-ice/30 bg-gradient-to-r from-ice/10 to-ice/5">
          <div className="flex items-start gap-4">
            <span className="text-4xl">🏝️</span>
            <div>
              <h2 className="text-lg font-bold text-frost mb-2">Why Daybreak Island Matters</h2>
              <p className="text-sm text-frost-muted">
                Battle Enhancer Decorations provide <strong className="text-ice">permanent combat stat bonuses</strong> that
                apply to all PvP content. Mythic decorations alone can give up to 10% ATK and 10% DEF
                per troop type - a massive power boost that rivals chief gear.
              </p>
            </div>
          </div>
        </div>

        {/* Tree of Life */}
        <div className="card mb-6">
          <h2 className="section-header">Tree of Life (Universal Buffs)</h2>
          <p className="text-sm text-frost-muted mb-4">
            Provides bonuses to ALL troop types. Priority upgrade target.
          </p>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-surface-border">
                  <th className="text-left p-2 text-frost-muted">Level</th>
                  <th className="text-left p-2 text-frost-muted">Key Buff</th>
                </tr>
              </thead>
              <tbody>
                {treeOfLifeLevels.filter(l => l.buff.includes('%')).map((level) => (
                  <tr key={level.level} className="border-b border-surface-border/50">
                    <td className="p-2 text-frost font-medium">Level {level.level}</td>
                    <td className="p-2 text-success">{level.buff}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Battle Enhancer Decorations */}
        <div className="card mb-6">
          <h2 className="section-header">Battle Enhancer Decorations</h2>
          <p className="text-sm text-frost-muted mb-4">
            <strong className="text-frost">CRITICAL:</strong> These are the main source of combat stats from Daybreak Island!
          </p>

          {/* Mythic Decorations */}
          <h3 className="font-medium text-frost mb-3">Mythic Decorations (10 levels × 1% = 10% max each)</h3>
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            {/* Attack Column */}
            <div>
              <h4 className="text-sm text-frost-muted mb-2">Attack Decorations</h4>
              <div className="space-y-2">
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                  <p className="font-medium text-red-400">Floating Market</p>
                  <p className="text-xs text-frost-muted">Infantry ATK +10% (max)</p>
                </div>
                <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/20">
                  <p className="font-medium text-green-400">Amphitheatre</p>
                  <p className="text-xs text-frost-muted">Lancer ATK +10% (max)</p>
                </div>
                <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
                  <p className="font-medium text-blue-400">Observation Deck</p>
                  <p className="text-xs text-frost-muted">Marksman ATK +10% (max)</p>
                </div>
              </div>
            </div>

            {/* Defense Column */}
            <div>
              <h4 className="text-sm text-frost-muted mb-2">Defense Decorations</h4>
              <div className="space-y-2">
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                  <p className="font-medium text-red-400">Snow Castle</p>
                  <p className="text-xs text-frost-muted">Infantry DEF +10% (max)</p>
                </div>
                <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/20">
                  <p className="font-medium text-green-400">Elegant Villa</p>
                  <p className="text-xs text-frost-muted">Lancer DEF +10% (max)</p>
                </div>
                <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
                  <p className="font-medium text-blue-400">Art Gallery</p>
                  <p className="text-xs text-frost-muted">Marksman DEF +10% (max)</p>
                </div>
              </div>
            </div>
          </div>

          {/* Epic Decorations */}
          <h3 className="font-medium text-frost mb-3">Epic Decorations (5 levels × 0.5% = 2.5% max each)</h3>
          <p className="text-sm text-frost-muted">
            Various epic decorations provide smaller bonuses. Focus on Mythic first, then Epic.
          </p>
        </div>

        {/* Upgrade Priority */}
        <div className="card mb-6">
          <h2 className="section-header">Upgrade Priority</h2>
          <ol className="space-y-3">
            <li className="flex items-start gap-3">
              <span className="w-6 h-6 rounded-full bg-fire flex items-center justify-center text-white text-sm font-bold">1</span>
              <div>
                <p className="font-medium text-frost">Tree of Life</p>
                <p className="text-sm text-frost-muted">Universal buffs affect all content</p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="w-6 h-6 rounded-full bg-fire/80 flex items-center justify-center text-white text-sm font-bold">2</span>
              <div>
                <p className="font-medium text-frost">Your Main Troop Type Mythic ATK</p>
                <p className="text-sm text-frost-muted">10% ATK is huge for your primary army</p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="w-6 h-6 rounded-full bg-fire/60 flex items-center justify-center text-white text-sm font-bold">3</span>
              <div>
                <p className="font-medium text-frost">Your Main Troop Type Mythic DEF</p>
                <p className="text-sm text-frost-muted">Survivability matters for longer fights</p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="w-6 h-6 rounded-full bg-fire/40 flex items-center justify-center text-white text-sm font-bold">4</span>
              <div>
                <p className="font-medium text-frost">Secondary Troop Mythics</p>
                <p className="text-sm text-frost-muted">Then work on your secondary troop type</p>
              </div>
            </li>
          </ol>
        </div>

        {/* Tips */}
        <div className="card">
          <h2 className="section-header">Tips</h2>
          <ul className="space-y-2 text-sm text-frost-muted">
            <li className="flex items-start gap-2">
              <span className="text-ice">•</span>
              <span>Rush to F19 to unlock Daybreak Island as early as possible</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-ice">•</span>
              <span>Decorations require materials from Daybreak Island exploration</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-ice">•</span>
              <span>Focus on ONE troop type's decorations first for maximum impact</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-ice">•</span>
              <span>Don't neglect this system - it's as important as chief gear for combat power</span>
            </li>
          </ul>
        </div>
      </div>
    </PageLayout>
  );
}
