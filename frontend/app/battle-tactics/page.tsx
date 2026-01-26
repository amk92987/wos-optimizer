'use client';

import PageLayout from '@/components/PageLayout';

export default function BattleTacticsPage() {
  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Battle Tactics</h1>
          <p className="text-frost-muted mt-2">Strategic approaches for different combat scenarios</p>
        </div>

        {/* Rally Attack */}
        <div className="card mb-6">
          <h2 className="section-header">Rally Attack Strategy</h2>
          <div className="space-y-4">
            <div className="p-4 rounded-lg bg-fire/10 border border-fire/20">
              <h3 className="font-medium text-fire mb-2">Rally Leader</h3>
              <ul className="text-sm text-frost-muted space-y-1">
                <li>• Use your highest power heroes in ALL slots</li>
                <li>• Match troop composition to target (infantry vs marksman garrison)</li>
                <li>• Wait for full rally capacity before launching</li>
                <li>• Communicate timing with alliance</li>
              </ul>
            </div>

            <div className="p-4 rounded-lg bg-ice/10 border border-ice/20">
              <h3 className="font-medium text-ice mb-2">Rally Joiner</h3>
              <ul className="text-sm text-frost-muted space-y-1">
                <li>• <strong className="text-frost">Jessie FIRST</strong> - Stand of Arms (+5-25% DMG)</li>
                <li>• Only your first hero's top-right skill applies</li>
                <li>• Send your best troops (highest tier)</li>
                <li>• Match the rally leader's composition if possible</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Garrison Defense */}
        <div className="card mb-6">
          <h2 className="section-header">Garrison Defense Strategy</h2>
          <div className="space-y-4">
            <div className="p-4 rounded-lg bg-success/10 border border-success/20">
              <h3 className="font-medium text-success mb-2">Garrison Setup</h3>
              <ul className="text-sm text-frost-muted space-y-1">
                <li>• <strong className="text-frost">Sergey FIRST</strong> - Defenders' Edge (-4-20% DMG taken)</li>
                <li>• Use 60/25/15 troop ratio (Infantry/Lancer/Marksman)</li>
                <li>• Infantry-heavy composition survives longer</li>
                <li>• Fill all hero slots with your best heroes</li>
              </ul>
            </div>

            <div className="p-4 rounded-lg bg-warning/10 border border-warning/20">
              <h3 className="font-medium text-warning mb-2">Reinforcement Tactics</h3>
              <ul className="text-sm text-frost-muted space-y-1">
                <li>• Reinforce before enemy rally launches</li>
                <li>• Send maximum troops allowed</li>
                <li>• Coordinate with alliance for full garrison</li>
                <li>• Shield immediately after defense if wounded</li>
              </ul>
            </div>
          </div>
        </div>

        {/* SvS Field Combat */}
        <div className="card mb-6">
          <h2 className="section-header">SvS Field Combat</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-surface">
              <h3 className="font-medium text-frost mb-2">Attacking</h3>
              <ul className="text-sm text-frost-muted space-y-1">
                <li>• Use balanced 40/20/40 composition</li>
                <li>• Target isolated enemies</li>
                <li>• Group up with alliance members</li>
                <li>• Watch for teleport traps</li>
              </ul>
            </div>

            <div className="p-4 rounded-lg bg-surface">
              <h3 className="font-medium text-frost mb-2">Defending</h3>
              <ul className="text-sm text-frost-muted space-y-1">
                <li>• Keep shield active when offline</li>
                <li>• Shelter troops if shield drops</li>
                <li>• Stay near alliance territory</li>
                <li>• Don't attack if you can't shield after</li>
              </ul>
            </div>
          </div>

          <div className="mt-4 p-4 rounded-lg bg-error/10 border border-error/20">
            <p className="text-sm text-frost">
              <strong className="text-error">Warning:</strong> Attacking drops your shield for 30 minutes.
              Only attack if you can handle retaliation or reshield immediately.
            </p>
          </div>
        </div>

        {/* Event-Specific Tactics */}
        <div className="card mb-6">
          <h2 className="section-header">Event-Specific Tactics</h2>

          <div className="space-y-4">
            <div className="p-4 rounded-lg bg-surface">
              <h3 className="font-medium text-frost flex items-center gap-2">
                <span>🐻</span> Bear Trap
              </h3>
              <div className="mt-2 grid md:grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-frost-muted mb-1">Troop Ratio:</p>
                  <p className="font-medium text-ice">0/10/90 (Marksman heavy)</p>
                </div>
                <div>
                  <p className="text-frost-muted mb-1">Key Strategy:</p>
                  <p className="text-frost">Bear is slow - maximize ranged DPS</p>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-surface">
              <h3 className="font-medium text-frost flex items-center gap-2">
                <span>🤪</span> Crazy Joe
              </h3>
              <div className="mt-2 grid md:grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-frost-muted mb-1">Troop Ratio:</p>
                  <p className="font-medium text-red-400">90/10/0 (Infantry heavy)</p>
                </div>
                <div>
                  <p className="text-frost-muted mb-1">Key Strategy:</p>
                  <p className="text-frost">Kill Joe before backline attacks land</p>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-surface">
              <h3 className="font-medium text-frost flex items-center gap-2">
                <span>🏰</span> Castle Battle
              </h3>
              <div className="mt-2 grid md:grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-frost-muted mb-1">Troop Ratio:</p>
                  <p className="font-medium text-green-400">Varies by enemy composition</p>
                </div>
                <div>
                  <p className="text-frost-muted mb-1">Key Strategy:</p>
                  <p className="text-frost">Scout first, adapt to defender setup</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Advanced Tips */}
        <div className="card">
          <h2 className="section-header">Advanced Tactics</h2>
          <ul className="space-y-3 text-sm text-frost-muted">
            <li className="flex items-start gap-3">
              <span className="text-xl">🎯</span>
              <div>
                <p className="font-medium text-frost">Rally Timing</p>
                <p>Launch rallies at off-peak hours when defenders are asleep. Coordinate timezone-aware attacks.</p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-xl">🔄</span>
              <div>
                <p className="font-medium text-frost">Fake Rally</p>
                <p>Start a rally to bait reinforcements, then cancel and hit a different target.</p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-xl">⚡</span>
              <div>
                <p className="font-medium text-frost">Speed Rally</p>
                <p>Use rally speed boosts when target is online and may shield.</p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-xl">🛡️</span>
              <div>
                <p className="font-medium text-frost">Shield Baiting</p>
                <p>Attack then immediately shield to force enemy retaliation into your shield.</p>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </PageLayout>
  );
}
