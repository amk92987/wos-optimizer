'use client';

import PageLayout from '@/components/PageLayout';

export default function CombatPage() {
  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Combat Guide</h1>
          <p className="text-frost-muted mt-2">Understanding combat mechanics and optimization</p>
        </div>

        {/* Type Advantage */}
        <div className="card mb-6">
          <h2 className="section-header">Troop Type Advantage</h2>
          <div className="flex items-center justify-center gap-4 py-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-2">
                <span className="text-2xl">⚔️</span>
              </div>
              <p className="font-medium text-red-400">Infantry</p>
            </div>
            <div className="text-2xl text-frost">→</div>
            <div className="text-center">
              <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-2">
                <span className="text-2xl">🗡️</span>
              </div>
              <p className="font-medium text-green-400">Lancer</p>
            </div>
            <div className="text-2xl text-frost">→</div>
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-2">
                <span className="text-2xl">🏹</span>
              </div>
              <p className="font-medium text-blue-400">Marksman</p>
            </div>
            <div className="text-2xl text-frost">→</div>
            <div className="text-center opacity-50">
              <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-2">
                <span className="text-2xl">⚔️</span>
              </div>
              <p className="font-medium text-red-400">Infantry</p>
            </div>
          </div>
          <p className="text-center text-sm text-frost-muted">
            Attacking a weaker type deals <strong className="text-success">+25% damage</strong>
          </p>
        </div>

        {/* Stat Sources */}
        <div className="card mb-6">
          <h2 className="section-header">Combat Stat Sources</h2>
          <div className="space-y-4">
            <div className="flex items-start gap-4 p-4 rounded-lg bg-surface">
              <span className="text-2xl">👑</span>
              <div className="flex-1">
                <h3 className="font-medium text-frost">Chief Gear</h3>
                <p className="text-sm text-frost-muted">
                  Major stat source. Focus on one troop type. Gold quality unlocks mastery for extra stats.
                </p>
                <p className="text-xs text-ice mt-1">Unlocks: Always available</p>
              </div>
            </div>

            <div className="flex items-start gap-4 p-4 rounded-lg bg-surface">
              <span className="text-2xl">🏝️</span>
              <div className="flex-1">
                <h3 className="font-medium text-frost">Daybreak Island</h3>
                <p className="text-sm text-frost-muted">
                  Battle Enhancer Decorations provide up to 10% ATK/DEF per troop type. Massive impact.
                </p>
                <p className="text-xs text-ice mt-1">Unlocks: Furnace 19</p>
              </div>
            </div>

            <div className="flex items-start gap-4 p-4 rounded-lg bg-surface">
              <span className="text-2xl">🦸</span>
              <div className="flex-1">
                <h3 className="font-medium text-frost">Hero Gear</h3>
                <p className="text-sm text-frost-muted">
                  Gear equipped on heroes. Becomes important at FC30+. Focus on main heroes first.
                </p>
                <p className="text-xs text-ice mt-1">Unlocks: FC30+</p>
              </div>
            </div>

            <div className="flex items-start gap-4 p-4 rounded-lg bg-surface">
              <span className="text-2xl">🔬</span>
              <div className="flex-1">
                <h3 className="font-medium text-frost">Research</h3>
                <p className="text-sm text-frost-muted">
                  Combat research provides permanent stat boosts. Long-term investment.
                </p>
                <p className="text-xs text-ice mt-1">Unlocks: Furnace 9</p>
              </div>
            </div>

            <div className="flex items-start gap-4 p-4 rounded-lg bg-surface">
              <span className="text-2xl">💎</span>
              <div className="flex-1">
                <h3 className="font-medium text-frost">Chief Charms</h3>
                <p className="text-sm text-frost-muted">
                  3 slots per gear piece. Significant boost at higher levels. Gen 7 materials for L16.
                </p>
                <p className="text-xs text-ice mt-1">Unlocks: Furnace 25</p>
              </div>
            </div>
          </div>
        </div>

        {/* Key Combat Stats */}
        <div className="card mb-6">
          <h2 className="section-header">Key Combat Stats</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-surface">
              <h3 className="font-medium text-red-400 mb-2">Attack (ATK)</h3>
              <p className="text-sm text-frost-muted">
                Increases damage dealt. Priority for offense-focused players and rally attackers.
              </p>
            </div>
            <div className="p-4 rounded-lg bg-surface">
              <h3 className="font-medium text-blue-400 mb-2">Defense (DEF)</h3>
              <p className="text-sm text-frost-muted">
                Reduces damage taken. Priority for garrison defenders and fillers.
              </p>
            </div>
            <div className="p-4 rounded-lg bg-surface">
              <h3 className="font-medium text-green-400 mb-2">Health (HP)</h3>
              <p className="text-sm text-frost-muted">
                Increases troop survivability. Important for all combat scenarios.
              </p>
            </div>
            <div className="p-4 rounded-lg bg-surface">
              <h3 className="font-medium text-fire mb-2">Lethality</h3>
              <p className="text-sm text-frost-muted">
                Increases kill rate. Important for preventing wounded troops from being healed.
              </p>
            </div>
          </div>
        </div>

        {/* Troop Tier Priority */}
        <div className="card mb-6">
          <h2 className="section-header">Troop Tier Priority</h2>
          <p className="text-sm text-frost-muted mb-4">
            Higher tier troops are ALWAYS better. Focus on unlocking and training the highest tier available.
          </p>
          <div className="flex items-center gap-2 flex-wrap">
            {['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12'].map((tier, i) => (
              <div
                key={tier}
                className={`px-3 py-1 rounded text-sm font-medium ${
                  i >= 9 ? 'bg-fire/20 text-fire' :
                  i >= 6 ? 'bg-warning/20 text-warning' :
                  i >= 3 ? 'bg-ice/20 text-ice' :
                  'bg-surface text-frost-muted'
                }`}
              >
                {tier}
              </div>
            ))}
          </div>
          <p className="text-xs text-frost-muted mt-3">
            T10+ troops are considered competitive. Rush to unlock them.
          </p>
        </div>

        {/* Combat Tips */}
        <div className="card">
          <h2 className="section-header">Combat Tips</h2>
          <ul className="space-y-2 text-sm text-frost-muted">
            <li className="flex items-start gap-2">
              <span className="text-ice">•</span>
              <span>Match your lineup to the content - Bear Trap needs marksman, Crazy Joe needs infantry</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-ice">•</span>
              <span>Rally joiner skills matter - put Jessie first for attack, Sergey first for defense</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-ice">•</span>
              <span>Don't have more troops than your hospital can heal - losing troops is expensive</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-ice">•</span>
              <span>Field Triage after SvS heals 30-90% of casualties - take calculated risks</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-ice">•</span>
              <span>Coordinate with alliance on rally targets - solo attacks rarely succeed</span>
            </li>
          </ul>
        </div>
      </div>
    </PageLayout>
  );
}
