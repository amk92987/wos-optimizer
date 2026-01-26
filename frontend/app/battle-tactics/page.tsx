'use client';

import { useState } from 'react';
import PageLayout from '@/components/PageLayout';

type TabKey = 'castle-battles' | 'bear-trap' | 'canyon-clash' | 'foundry' | 'frostfire' | 'labyrinth';

const tabs: { key: TabKey; label: string; icon: string }[] = [
  { key: 'castle-battles', label: 'Castle Battles', icon: '🏰' },
  { key: 'bear-trap', label: 'Bear Trap', icon: '🐻' },
  { key: 'canyon-clash', label: 'Canyon Clash', icon: '⚔️' },
  { key: 'foundry', label: 'Foundry', icon: '🏭' },
  { key: 'frostfire', label: 'Frostfire Mine', icon: '🔥' },
  { key: 'labyrinth', label: 'Labyrinth', icon: '🌀' },
];

// Priority colors
const priorityColors: Record<string, { bg: string; border: string; text: string }> = {
  critical: { bg: 'bg-red-500/10', border: 'border-red-500/30', text: 'text-red-400' },
  high: { bg: 'bg-orange-500/10', border: 'border-orange-500/30', text: 'text-orange-400' },
  medium: { bg: 'bg-blue-500/10', border: 'border-blue-500/30', text: 'text-blue-400' },
  low: { bg: 'bg-slate-500/10', border: 'border-slate-500/30', text: 'text-slate-400' },
};

// Troop type colors
const troopColors = {
  infantry: 'text-red-400',
  lancer: 'text-green-400',
  marksman: 'text-blue-400',
};

function CastleBattlesTab() {
  return (
    <div className="space-y-6">
      <div className="card bg-gradient-to-r from-fire/10 to-transparent border-fire/30">
        <p className="text-frost">
          Castle Battles are coordinated alliance events where timing and target selection matter more than raw power.
          <strong className="text-fire ml-1">Communication is everything.</strong>
        </p>
      </div>

      {/* Attack Tactics */}
      <div className="card">
        <h2 className="section-header text-fire">Attack Tactics</h2>
        <p className="text-frost-muted mb-4">Priority order for attacking enemy castles:</p>

        <div className="space-y-3">
          {[
            { priority: 'critical', title: 'Scout Before Attacking', desc: 'Always scout target to see troop composition and garrison strength. Adjust your composition to counter.' },
            { priority: 'critical', title: 'Coordinate Rally Timing', desc: 'Don\'t launch random rallies. Coordinate with alliance for simultaneous multi-rally attacks.' },
            { priority: 'high', title: 'Target Selection', desc: 'Hit the weakest defended castles first to build momentum and reduce enemy reinforcement pools.' },
            { priority: 'high', title: 'Fill Rallies Completely', desc: 'A 75% full rally is often worse than waiting for 100%. Patience wins battles.' },
            { priority: 'medium', title: 'Rally Leader Composition', desc: 'Rally leader should use highest power heroes. Put best expedition skill heroes in slot 1.' },
            { priority: 'medium', title: 'Joiner Strategy', desc: 'Jessie FIRST for attack joiners (+25% DMG at max skill). Only first hero\'s top-right skill applies.' },
            { priority: 'low', title: 'Fake Rallies', desc: 'Start a rally, draw reinforcements, cancel, then hit a different target. Use sparingly - wastes rally timer.' },
          ].map((item, i) => {
            const colors = priorityColors[item.priority];
            return (
              <div key={i} className={`p-3 rounded-lg ${colors.bg} border ${colors.border}`}>
                <div className="flex items-start gap-3">
                  <span className={`text-xs font-bold uppercase ${colors.text}`}>{item.priority}</span>
                  <div>
                    <p className="font-medium text-frost">{item.title}</p>
                    <p className="text-sm text-frost-muted mt-1">{item.desc}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Defense Tactics */}
      <div className="card">
        <h2 className="section-header text-ice">Defense Tactics</h2>
        <p className="text-frost-muted mb-4">Priority order for defending your castles:</p>

        <div className="space-y-3">
          {[
            { priority: 'critical', title: 'Reinforce Before Rally Launches', desc: 'Once a rally starts, you have limited time. Reinforce immediately when you see rally starting.' },
            { priority: 'critical', title: 'Sergey First for Defense', desc: 'Put Sergey in slot 1 of garrison. Defenders\' Edge reduces ALL incoming damage (-20% at max skill).' },
            { priority: 'high', title: 'Infantry-Heavy Garrison', desc: 'Use 60/25/15 ratio (Infantry/Lancer/Marksman). Infantry survives longer under sustained attacks.' },
            { priority: 'high', title: 'Fill All Hero Slots', desc: 'Empty hero slots = wasted stats. Put any hero rather than leaving slots empty.' },
            { priority: 'medium', title: 'Shield After Defense', desc: 'If you took significant losses, shield immediately. Don\'t let them follow up while you\'re weakened.' },
            { priority: 'medium', title: 'Anti-Scout Shields', desc: 'If you\'re being scouted repeatedly, put up a shield. They\'re planning an attack.' },
            { priority: 'low', title: 'Bait and Switch', desc: 'Show weak garrison, wait for rally, then swap in strong garrison at last second. Risky but effective.' },
          ].map((item, i) => {
            const colors = priorityColors[item.priority];
            return (
              <div key={i} className={`p-3 rounded-lg ${colors.bg} border ${colors.border}`}>
                <div className="flex items-start gap-3">
                  <span className={`text-xs font-bold uppercase ${colors.text}`}>{item.priority}</span>
                  <div>
                    <p className="font-medium text-frost">{item.title}</p>
                    <p className="text-sm text-frost-muted mt-1">{item.desc}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Coordination Levels */}
      <div className="card">
        <h2 className="section-header">Coordination Requirements</h2>
        <p className="text-frost-muted mb-4">Success in castle battles depends on alliance coordination level:</p>

        <div className="grid md:grid-cols-3 gap-4">
          <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/30">
            <h3 className="font-medium text-green-400 mb-2">Basic Coordination</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Alliance chat for rally calls</li>
              <li>• Target announcement before rally</li>
              <li>• Basic reinforcement responses</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
            <h3 className="font-medium text-yellow-400 mb-2">Good Coordination</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Discord/Line for real-time comms</li>
              <li>• Assigned rally leaders</li>
              <li>• Defense rotation schedule</li>
              <li>• Troop composition guidelines</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-purple-500/10 border border-purple-500/30">
            <h3 className="font-medium text-purple-400 mb-2">Elite Coordination</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Voice chat during battles</li>
              <li>• Simultaneous multi-rally attacks</li>
              <li>• Counter-intel on enemy movements</li>
              <li>• Bait and trap strategies</li>
              <li>• Timezone coverage plan</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Checklist */}
      <div className="card">
        <h2 className="section-header">Pre-Battle Checklist</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <h3 className="font-medium text-fire mb-2">Attackers</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>☐ Troops fully healed</li>
              <li>☐ Heroes assigned to march slots</li>
              <li>☐ Rally speedups ready</li>
              <li>☐ Shields ready for after attack</li>
              <li>☐ Comms channel open</li>
            </ul>
          </div>
          <div>
            <h3 className="font-medium text-ice mb-2">Defenders</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>☐ Garrison heroes set (Sergey slot 1)</li>
              <li>☐ Troop ratio configured</li>
              <li>☐ Reinforcement troops ready</li>
              <li>☐ Shields in inventory</li>
              <li>☐ Hospital capacity available</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

function BearTrapTab() {
  return (
    <div className="space-y-6">
      <div className="card bg-gradient-to-r from-orange-500/10 to-transparent border-orange-500/30">
        <p className="text-frost">
          Bear Trap is a <strong className="text-orange-400">weekly rally boss event</strong> where your alliance works together to defeat increasingly difficult bears.
          The bear is slow-moving, making <span className={troopColors.marksman}>Marksman-heavy</span> compositions optimal.
        </p>
      </div>

      {/* Rally Mechanics */}
      <div className="card">
        <h2 className="section-header">Rally Mechanics</h2>

        <div className="grid md:grid-cols-2 gap-4 mb-4">
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">How Bear Trap Works</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Rally leader sets the march and starts rally</li>
              <li>• Alliance members join with troops</li>
              <li>• Only <strong className="text-frost">top 4 expedition skill LEVELS</strong> from all joiners apply</li>
              <li>• First hero's top-right expedition skill is what counts</li>
              <li>• Higher level bear = better rewards</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">Optimal Troop Ratio</h3>
            <div className="flex items-center gap-4 mt-2">
              <div className="text-center">
                <p className={`text-2xl font-bold ${troopColors.infantry}`}>0%</p>
                <p className="text-xs text-frost-muted">Infantry</p>
              </div>
              <div className="text-center">
                <p className={`text-2xl font-bold ${troopColors.lancer}`}>10%</p>
                <p className="text-xs text-frost-muted">Lancer</p>
              </div>
              <div className="text-center">
                <p className={`text-2xl font-bold ${troopColors.marksman}`}>90%</p>
                <p className="text-xs text-frost-muted">Marksman</p>
              </div>
            </div>
            <p className="text-sm text-frost-muted mt-3">
              Bear is slow - marksmen can attack from range without taking damage.
              10% lancers for minimal tanking if needed.
            </p>
          </div>
        </div>
      </div>

      {/* Jeronimo vs Natalia Decision Box */}
      <div className="card border-yellow-500/30">
        <h2 className="section-header text-yellow-400">Should I Use Jeronimo?</h2>
        <p className="text-frost-muted mb-4">
          Common question: Jeronimo is S+ tier infantry but Bear Trap uses marksman. Here's when to use him:
        </p>

        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/30">
            <h3 className="font-medium text-green-400 mb-2">Use Jeronimo When:</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• His expedition skill level is higher than alternatives</li>
              <li>• You don't have leveled marksman heroes</li>
              <li>• Rally leader specifically requests infantry lead</li>
              <li>• You're the rally leader with high Jeronimo gear</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30">
            <h3 className="font-medium text-red-400 mb-2">Don't Use Jeronimo When:</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• You have Molly/Natalia with same or higher skill</li>
              <li>• Rally is already marksman-heavy</li>
              <li>• His expedition skill is lower than your marksman heroes</li>
              <li>• You're joining (not leading) the rally</li>
            </ul>
          </div>
        </div>

        <div className="mt-4 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
          <p className="text-sm text-frost">
            <strong className="text-yellow-400">Bottom Line:</strong> For joiners, expedition skill LEVEL matters most.
            Put your highest skill-level hero first regardless of class. The rally leader sets the troop composition.
          </p>
        </div>
      </div>

      {/* Hero Recommendations by Generation */}
      <div className="card">
        <h2 className="section-header">Hero Selection by Generation</h2>
        <p className="text-frost-muted mb-4">Best heroes to put first when joining Bear Trap rallies:</p>

        <div className="space-y-4">
          {[
            {
              gen: 'Gen 1-3',
              days: '0-200 days',
              heroes: [
                { name: 'Jessie', class: 'Marksman', skill: 'Stand of Arms', effect: '+5-25% DMG dealt', priority: 'critical' },
                { name: 'Molly', class: 'Marksman', skill: 'Precise Shot', effect: 'Marksman ATK buff', priority: 'high' },
                { name: 'Natalia', class: 'Marksman', skill: 'Swift Stride', effect: 'March speed + damage', priority: 'high' },
              ],
            },
            {
              gen: 'Gen 4-6',
              days: '200-440 days',
              heroes: [
                { name: 'Jessie', class: 'Marksman', skill: 'Stand of Arms', effect: '+25% DMG at level 5', priority: 'critical' },
                { name: 'Wu Ming', class: 'Infantry', skill: 'Tactical Edge', effect: 'Strong buff if high level', priority: 'medium' },
                { name: 'Lynn', class: 'Marksman', skill: 'Eagle Eye', effect: 'Crit rate buff', priority: 'medium' },
              ],
            },
            {
              gen: 'Gen 7+',
              days: '440+ days',
              heroes: [
                { name: 'Jessie', class: 'Marksman', skill: 'Stand of Arms', effect: 'Still best attack joiner', priority: 'critical' },
                { name: 'Gatot', class: 'Infantry', skill: 'War Cry', effect: 'Team ATK buff', priority: 'high' },
                { name: 'Sonya', class: 'Lancer', skill: 'Battle Fury', effect: 'High damage buff', priority: 'high' },
              ],
            },
          ].map((tier, i) => (
            <div key={i} className="p-4 rounded-lg bg-surface">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-medium text-frost">{tier.gen}</h3>
                <span className="text-xs text-frost-muted">{tier.days}</span>
              </div>
              <div className="space-y-2">
                {tier.heroes.map((hero, j) => {
                  const colors = priorityColors[hero.priority];
                  const classColor = troopColors[hero.class.toLowerCase() as keyof typeof troopColors] || 'text-frost';
                  return (
                    <div key={j} className={`p-2 rounded ${colors.bg} border ${colors.border}`}>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className={`text-xs font-bold uppercase ${colors.text}`}>{hero.priority === 'critical' ? '1st' : hero.priority === 'high' ? '2nd' : '3rd'}</span>
                          <span className="font-medium text-frost">{hero.name}</span>
                          <span className={`text-xs ${classColor}`}>({hero.class})</span>
                        </div>
                        <span className="text-xs text-frost-muted">{hero.effect}</span>
                      </div>
                      <p className="text-xs text-frost-muted mt-1">Skill: {hero.skill}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Reference */}
      <div className="card">
        <h2 className="section-header">Quick Reference</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border">
                <th className="text-left py-2 text-frost-muted">Role</th>
                <th className="text-left py-2 text-frost-muted">First Hero</th>
                <th className="text-left py-2 text-frost-muted">Troop Ratio</th>
                <th className="text-left py-2 text-frost-muted">Notes</th>
              </tr>
            </thead>
            <tbody className="text-frost">
              <tr className="border-b border-surface-border/50">
                <td className="py-2">Rally Leader</td>
                <td className="py-2">Highest power marksman</td>
                <td className="py-2">0/10/90</td>
                <td className="py-2 text-frost-muted">You set the composition</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="py-2">Joiner (Optimal)</td>
                <td className="py-2 text-green-400">Jessie</td>
                <td className="py-2">0/10/90</td>
                <td className="py-2 text-frost-muted">+25% DMG at skill 5</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="py-2">Joiner (Alt)</td>
                <td className="py-2">Highest skill level hero</td>
                <td className="py-2">0/10/90</td>
                <td className="py-2 text-frost-muted">If Jessie skill is low</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function CanyonClashTab() {
  return (
    <div className="space-y-6">
      <div className="card bg-gradient-to-r from-purple-500/10 to-transparent border-purple-500/30">
        <p className="text-frost">
          Canyon Clash is a <strong className="text-purple-400">cross-server alliance battle</strong> held on weekends.
          Your alliance fights against another alliance for control of the Frozen Citadel.
        </p>
      </div>

      {/* Schedule */}
      <div className="card">
        <h2 className="section-header">Weekly Schedule</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">Timing</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">Saturday & Sunday</strong></li>
              <li>• Two 30-minute battle phases</li>
              <li>• Check your server's specific times</li>
              <li>• Usually 12:00 and 20:00 server time</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">Rewards</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Canyon Coins for shop purchases</li>
              <li>• Hero shards (varies by rank)</li>
              <li>• Speedups and resources</li>
              <li>• Ranking rewards for top performers</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Battle Phases */}
      <div className="card">
        <h2 className="section-header">Battle Phases</h2>

        <div className="space-y-4">
          <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/30">
            <h3 className="font-medium text-blue-400 mb-2">Phase 1: Resource Gathering (0-10 min)</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Collect resources scattered across the map</li>
              <li>• Build up fuel for your march</li>
              <li>• Scout enemy positions</li>
              <li>• <strong className="text-frost">Don't engage yet</strong> - build fuel first</li>
            </ul>
          </div>

          <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
            <h3 className="font-medium text-yellow-400 mb-2">Phase 2: Skirmish (10-20 min)</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Small engagements begin</li>
              <li>• Control key resource points</li>
              <li>• Don't overcommit - save fuel for final push</li>
              <li>• Coordinate with teammates for ganks</li>
            </ul>
          </div>

          <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30">
            <h3 className="font-medium text-red-400 mb-2">Phase 3: Citadel Fight (20-30 min)</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">All-out assault on Frozen Citadel</strong></li>
              <li>• Use all remaining fuel</li>
              <li>• Focus fire on same targets as team</li>
              <li>• Whoever holds citadel at end wins</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Team Strategy */}
      <div className="card">
        <h2 className="section-header">Three-Team Strategy</h2>
        <p className="text-frost-muted mb-4">Optimal alliance organization for Canyon Clash:</p>

        <div className="grid md:grid-cols-3 gap-4">
          <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30">
            <h3 className="font-medium text-red-400 mb-2">Attack Team</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Highest power players</li>
              <li>• Aggressive positioning</li>
              <li>• Push enemy citadel</li>
              <li>• Lead the final assault</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/30">
            <h3 className="font-medium text-blue-400 mb-2">Defense Team</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Guard your citadel</li>
              <li>• Tank-heavy compositions</li>
              <li>• Call out incoming attacks</li>
              <li>• Don't chase - hold position</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/30">
            <h3 className="font-medium text-green-400 mb-2">Resource Team</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Fast march speed</li>
              <li>• Collect all resources</li>
              <li>• Deny enemy resources</li>
              <li>• Join fights when full</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Fuel Management */}
      <div className="card">
        <h2 className="section-header">Fuel Management</h2>
        <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
          <p className="text-frost mb-3">
            <strong className="text-yellow-400">Fuel is your most important resource.</strong> Running out of fuel mid-fight is a death sentence.
          </p>
          <ul className="text-sm text-frost-muted space-y-2">
            <li>• <strong className="text-frost">Start of match:</strong> Gather resources, build to 80%+ fuel</li>
            <li>• <strong className="text-frost">Mid-match:</strong> Don't go below 50% unless retreating to gather</li>
            <li>• <strong className="text-frost">Final 5 minutes:</strong> Use everything, no point saving it</li>
            <li>• <strong className="text-frost">If low:</strong> Retreat to gather point, don't engage</li>
          </ul>
        </div>
      </div>

      {/* Frozen Citadel */}
      <div className="card">
        <h2 className="section-header">Frozen Citadel</h2>
        <p className="text-frost-muted mb-4">The central objective - whoever controls it at battle end wins:</p>

        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-fire mb-2">Attacking Citadel</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Coordinate full alliance push</li>
              <li>• Focus fire on defenders one by one</li>
              <li>• Use speed buffs to close distance</li>
              <li>• Don't trickle in - attack together</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-ice mb-2">Defending Citadel</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Tank-heavy compositions</li>
              <li>• Spread to cover all angles</li>
              <li>• Call out enemy positions</li>
              <li>• Don't chase - let them come to you</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

function FoundryTab() {
  return (
    <div className="space-y-6">
      <div className="card bg-gradient-to-r from-amber-500/10 to-transparent border-amber-500/30">
        <p className="text-frost">
          Foundry is a <strong className="text-amber-400">4-team alliance event</strong> where you coordinate attacks on buildings to accumulate points.
          Building selection and attack timing are critical for high scores.
        </p>
      </div>

      {/* Building Values */}
      <div className="card">
        <h2 className="section-header">Building Point Values</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border">
                <th className="text-left py-2 text-frost-muted">Building</th>
                <th className="text-center py-2 text-frost-muted">Points</th>
                <th className="text-center py-2 text-frost-muted">Priority</th>
                <th className="text-left py-2 text-frost-muted">Notes</th>
              </tr>
            </thead>
            <tbody className="text-frost">
              <tr className="border-b border-surface-border/50">
                <td className="py-2">Stronghold</td>
                <td className="text-center py-2 text-yellow-400 font-bold">1000</td>
                <td className="text-center py-2"><span className="px-2 py-0.5 rounded bg-red-500/20 text-red-400 text-xs">Critical</span></td>
                <td className="py-2 text-frost-muted">Main target - highest value</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="py-2">Barracks</td>
                <td className="text-center py-2 text-orange-400 font-bold">500</td>
                <td className="text-center py-2"><span className="px-2 py-0.5 rounded bg-orange-500/20 text-orange-400 text-xs">High</span></td>
                <td className="py-2 text-frost-muted">Good value, usually less defended</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="py-2">Arsenal</td>
                <td className="text-center py-2 text-blue-400 font-bold">300</td>
                <td className="text-center py-2"><span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 text-xs">Medium</span></td>
                <td className="py-2 text-frost-muted">Fill target when others occupied</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="py-2">Watchtower</td>
                <td className="text-center py-2 text-slate-400 font-bold">100</td>
                <td className="text-center py-2"><span className="px-2 py-0.5 rounded bg-slate-500/20 text-slate-400 text-xs">Low</span></td>
                <td className="py-2 text-frost-muted">Quick points, low competition</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* 4-Team Formation */}
      <div className="card">
        <h2 className="section-header">4-Team Formation</h2>
        <p className="text-frost-muted mb-4">Standard team organization for Foundry:</p>

        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30">
            <h3 className="font-medium text-red-400 mb-2">Team Alpha (Strongest)</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Top 5 players by power</li>
              <li>• Target: Stronghold</li>
              <li>• Lead the main assault</li>
              <li>• Double rally when possible</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-orange-500/10 border border-orange-500/30">
            <h3 className="font-medium text-orange-400 mb-2">Team Bravo</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Next 5 strongest</li>
              <li>• Target: Barracks</li>
              <li>• Support Alpha when needed</li>
              <li>• Secondary Stronghold if clear</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/30">
            <h3 className="font-medium text-blue-400 mb-2">Team Charlie</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Mid-power players</li>
              <li>• Target: Arsenal</li>
              <li>• Flexible - help where needed</li>
              <li>• Quick building clears</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/30">
            <h3 className="font-medium text-green-400 mb-2">Team Delta</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Remaining players</li>
              <li>• Target: Watchtowers</li>
              <li>• Quick point accumulation</li>
              <li>• Scout enemy positions</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Attack Rotation */}
      <div className="card">
        <h2 className="section-header">Attack Rotation</h2>
        <p className="text-frost-muted mb-4">Optimal attack timing for maximum efficiency:</p>

        <div className="space-y-3">
          {[
            { time: '0:00-2:00', action: 'Scout all buildings, identify weak points', priority: 'medium' },
            { time: '2:00-5:00', action: 'Teams position for assigned buildings', priority: 'medium' },
            { time: '5:00-10:00', action: 'First wave attacks - all teams hit simultaneously', priority: 'critical' },
            { time: '10:00-15:00', action: 'Secure buildings, start double rallies on Stronghold', priority: 'high' },
            { time: '15:00-20:00', action: 'Rotation - cleared teams move to next target', priority: 'high' },
            { time: '20:00-25:00', action: 'Final push - all remaining buildings', priority: 'critical' },
            { time: '25:00-30:00', action: 'Cleanup - grab any uncontested buildings', priority: 'low' },
          ].map((phase, i) => {
            const colors = priorityColors[phase.priority];
            return (
              <div key={i} className={`p-3 rounded-lg ${colors.bg} border ${colors.border}`}>
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm text-frost whitespace-nowrap">{phase.time}</span>
                  <span className="text-frost-muted">|</span>
                  <span className="text-sm text-frost">{phase.action}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Double Rally Script */}
      <div className="card">
        <h2 className="section-header">Double Rally Timing</h2>
        <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
          <p className="text-frost mb-3">
            <strong className="text-yellow-400">Double rally</strong> = Two rallies hitting the same building at nearly the same time.
            Requires precise coordination.
          </p>
          <div className="space-y-2 text-sm">
            <div className="p-2 rounded bg-surface">
              <p className="text-frost"><strong>Step 1:</strong> Rally Leader A starts rally (5 min timer)</p>
            </div>
            <div className="p-2 rounded bg-surface">
              <p className="text-frost"><strong>Step 2:</strong> Wait until 4:00 remaining</p>
            </div>
            <div className="p-2 rounded bg-surface">
              <p className="text-frost"><strong>Step 3:</strong> Rally Leader B starts second rally</p>
            </div>
            <div className="p-2 rounded bg-surface">
              <p className="text-frost"><strong>Step 4:</strong> Both rallies launch within 1 min of each other</p>
            </div>
          </div>
          <p className="text-xs text-frost-muted mt-3">
            Note: Exact timing depends on march speed. Practice with your alliance to perfect timing.
          </p>
        </div>
      </div>

      {/* Building Assignments */}
      <div className="card">
        <h2 className="section-header">Building Assignment Template</h2>
        <p className="text-frost-muted mb-4">Copy this to your alliance Discord/chat:</p>
        <div className="p-4 rounded-lg bg-surface font-mono text-sm text-frost-muted overflow-x-auto">
          <pre>{`🏭 FOUNDRY ASSIGNMENTS

Team Alpha (Stronghold):
- Leader: [Name]
- Rally 1: [Name]
- Rally 2: [Name]
- Joiners: [Names]

Team Bravo (Barracks):
- Leader: [Name]
- Members: [Names]

Team Charlie (Arsenal):
- Leader: [Name]
- Members: [Names]

Team Delta (Watchtowers):
- Leader: [Name]
- Members: [Names]

⏰ Attack Time: XX:XX Server Time
📢 Comms: [Discord Channel]`}</pre>
        </div>
      </div>
    </div>
  );
}

function FrostfireMineTab() {
  return (
    <div className="space-y-6">
      <div className="card bg-gradient-to-r from-cyan-500/10 to-transparent border-cyan-500/30">
        <p className="text-frost">
          Frostfire Mine is a <strong className="text-cyan-400">solo PvE event</strong> where you navigate a mine, collect ores, and make strategic decisions about skill upgrades.
          The key to success is following the optimal skill build path.
        </p>
      </div>

      {/* Skill Build */}
      <div className="card border-yellow-500/30">
        <h2 className="section-header text-yellow-400">Optimal Skill Build: R-R-L-L-R</h2>
        <p className="text-frost-muted mb-4">
          When you reach a fork, choose skills in this order for maximum efficiency:
        </p>

        <div className="flex flex-wrap gap-3 mb-4">
          {[
            { choice: 'R', label: 'Right', desc: 'Mining Speed' },
            { choice: 'R', label: 'Right', desc: 'Ore Capacity' },
            { choice: 'L', label: 'Left', desc: 'Combat Damage' },
            { choice: 'L', label: 'Left', desc: 'Combat Defense' },
            { choice: 'R', label: 'Right', desc: 'Final Mining Boost' },
          ].map((skill, i) => (
            <div key={i} className="flex items-center gap-2">
              <span className="text-frost-muted text-sm">{i + 1}.</span>
              <span className={`px-3 py-1 rounded font-bold ${skill.choice === 'R' ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-400'}`}>
                {skill.label}
              </span>
              <span className="text-xs text-frost-muted">({skill.desc})</span>
            </div>
          ))}
        </div>

        <div className="p-3 rounded-lg bg-yellow-500/10">
          <p className="text-sm text-frost">
            <strong className="text-yellow-400">Why this order?</strong> Mining skills early maximize total ore collected.
            Combat skills in middle handle mid-game difficulty spike. Final mining boost for endgame efficiency.
          </p>
        </div>
      </div>

      {/* Minute-by-Minute Guide */}
      <div className="card">
        <h2 className="section-header">Minute-by-Minute Guide</h2>

        <div className="space-y-3">
          {[
            { time: '0:00-1:00', phase: 'Start', action: 'Collect nearby ores, move toward first fork', tip: 'Don\'t fight anything yet' },
            { time: '1:00-3:00', phase: 'Fork 1', action: 'Choose RIGHT (Mining Speed)', tip: 'Increases ore per node' },
            { time: '3:00-5:00', phase: 'Mining', action: 'Clear ore nodes in main chamber', tip: 'Avoid monster aggro' },
            { time: '5:00-7:00', phase: 'Fork 2', action: 'Choose RIGHT (Ore Capacity)', tip: 'Carry more before smelter' },
            { time: '7:00-10:00', phase: 'Mid-Mine', action: 'Push deeper, collect high-value ores', tip: 'Monsters get stronger here' },
            { time: '10:00-12:00', phase: 'Fork 3', action: 'Choose LEFT (Combat Damage)', tip: 'Needed for upcoming fights' },
            { time: '12:00-15:00', phase: 'Combat Zone', action: 'Clear monster camps for bonus ores', tip: 'Use damage skill' },
            { time: '15:00-17:00', phase: 'Fork 4', action: 'Choose LEFT (Combat Defense)', tip: 'Survive harder enemies' },
            { time: '17:00-20:00', phase: 'Deep Mine', action: 'Access deepest ore veins', tip: 'Highest value ores here' },
            { time: '20:00-22:00', phase: 'Fork 5', action: 'Choose RIGHT (Final Mining Boost)', tip: 'Maximize remaining time' },
            { time: '22:00-25:00', phase: 'Cleanup', action: 'Collect remaining ores, visit smelter', tip: 'Don\'t get greedy' },
            { time: '25:00-30:00', phase: 'Exit', action: 'Return to entrance with ores', tip: 'Must exit to keep ores!' },
          ].map((step, i) => (
            <div key={i} className="p-3 rounded-lg bg-surface">
              <div className="flex flex-wrap items-start gap-3">
                <span className="font-mono text-sm text-ice whitespace-nowrap">{step.time}</span>
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                  step.phase.includes('Fork') ? 'bg-yellow-500/20 text-yellow-400' :
                  step.phase === 'Combat Zone' ? 'bg-red-500/20 text-red-400' :
                  'bg-slate-500/20 text-slate-400'
                }`}>{step.phase}</span>
                <div className="flex-1">
                  <p className="text-sm text-frost">{step.action}</p>
                  <p className="text-xs text-frost-muted mt-1">Tip: {step.tip}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Vein Outbursts */}
      <div className="card">
        <h2 className="section-header">Vein Outbursts</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">What Are They?</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Random events during mining</li>
              <li>• Ore vein "explodes" with bonus ores</li>
              <li>• Indicated by glowing animation</li>
              <li>• More common in deep mine</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">How to Handle</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">Drop everything and collect!</strong></li>
              <li>• Worth 3-5x normal ore value</li>
              <li>• Limited time before disappears</li>
              <li>• Don't fight during outburst</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Smelter Decision */}
      <div className="card">
        <h2 className="section-header">Smelter Strategy</h2>
        <div className="p-4 rounded-lg bg-purple-500/10 border border-purple-500/30">
          <p className="text-frost mb-3">
            The <strong className="text-purple-400">Smelter</strong> converts raw ores to refined ores (higher value).
            But it takes time - is it worth it?
          </p>

          <div className="grid md:grid-cols-2 gap-4">
            <div className="p-3 rounded-lg bg-green-500/10">
              <h4 className="font-medium text-green-400 mb-2">Use Smelter When:</h4>
              <ul className="text-sm text-frost-muted space-y-1">
                <li>• You have 5+ minutes remaining</li>
                <li>• Carrying maximum ore capacity</li>
                <li>• Clear path back to entrance</li>
              </ul>
            </div>
            <div className="p-3 rounded-lg bg-red-500/10">
              <h4 className="font-medium text-red-400 mb-2">Skip Smelter When:</h4>
              <ul className="text-sm text-frost-muted space-y-1">
                <li>• Less than 3 minutes left</li>
                <li>• Still have ore nodes to collect</li>
                <li>• Enemies between you and exit</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Reference */}
      <div className="card">
        <h2 className="section-header">Quick Reference Card</h2>
        <div className="p-4 rounded-lg bg-surface font-mono text-sm">
          <pre className="text-frost-muted whitespace-pre-wrap">{`FROSTFIRE MINE CHEAT SHEET
========================

Skill Build: R → R → L → L → R
(Mining → Mining → Combat → Combat → Mining)

Priority:
1. Ore collection > Combat
2. Vein outbursts > Everything
3. Smelter if 5+ min left
4. EXIT BEFORE TIME RUNS OUT

Don't forget:
- Must exit to keep ores
- Monsters respawn
- High-value ores are deep`}</pre>
        </div>
      </div>
    </div>
  );
}

function LabyrinthTab() {
  const zones = [
    { zone: 'Crystal Caverns', troops: '50/25/25', difficulty: 'Easy', reward: 'Crystals', tip: 'Good for beginners' },
    { zone: 'Magma Chamber', troops: '30/20/50', difficulty: 'Medium', reward: 'Fire Essence', tip: 'Marksman-heavy for range' },
    { zone: 'Frost Halls', troops: '40/40/20', difficulty: 'Medium', reward: 'Ice Shards', tip: 'Balanced composition' },
    { zone: 'Shadow Depths', troops: '60/20/20', difficulty: 'Hard', reward: 'Shadow Cores', tip: 'Tank-heavy, slow push' },
    { zone: 'Void Nexus', troops: '35/35/30', difficulty: 'Very Hard', reward: 'Void Essence', tip: 'All heroes maxed' },
    { zone: 'Ancient Ruins', troops: '45/30/25', difficulty: 'Hard', reward: 'Ancient Relics', tip: 'Mixed strategy' },
  ];

  return (
    <div className="space-y-6">
      <div className="card bg-gradient-to-r from-indigo-500/10 to-transparent border-indigo-500/30">
        <p className="text-frost">
          Labyrinth is a <strong className="text-indigo-400">dungeon exploration mode</strong> with multiple zones, each requiring different strategies.
          Clear zones for valuable rewards and progression.
        </p>
      </div>

      {/* Zone Summary Table */}
      <div className="card">
        <h2 className="section-header">Zone Summary</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border">
                <th className="text-left py-2 text-frost-muted">Zone</th>
                <th className="text-center py-2 text-frost-muted">Troop Ratio</th>
                <th className="text-center py-2 text-frost-muted">Difficulty</th>
                <th className="text-left py-2 text-frost-muted">Reward</th>
                <th className="text-left py-2 text-frost-muted">Tip</th>
              </tr>
            </thead>
            <tbody className="text-frost">
              {zones.map((zone, i) => {
                const diffColor = zone.difficulty === 'Easy' ? 'text-green-400' :
                  zone.difficulty === 'Medium' ? 'text-yellow-400' :
                  zone.difficulty === 'Hard' ? 'text-orange-400' : 'text-red-400';
                return (
                  <tr key={i} className="border-b border-surface-border/50">
                    <td className="py-2 font-medium">{zone.zone}</td>
                    <td className="text-center py-2">
                      <span className={troopColors.infantry}>{zone.troops.split('/')[0]}</span>/
                      <span className={troopColors.lancer}>{zone.troops.split('/')[1]}</span>/
                      <span className={troopColors.marksman}>{zone.troops.split('/')[2]}</span>
                    </td>
                    <td className={`text-center py-2 ${diffColor}`}>{zone.difficulty}</td>
                    <td className="py-2 text-frost-muted">{zone.reward}</td>
                    <td className="py-2 text-frost-muted text-xs">{zone.tip}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-frost-muted mt-3">
          Troop ratios shown as <span className={troopColors.infantry}>Infantry</span>/
          <span className={troopColors.lancer}>Lancer</span>/
          <span className={troopColors.marksman}>Marksman</span>
        </p>
      </div>

      {/* Detailed Zone Strategies */}
      <div className="card">
        <h2 className="section-header">Zone Strategies</h2>

        <div className="space-y-4">
          <details className="group">
            <summary className="cursor-pointer p-3 rounded-lg bg-green-500/10 border border-green-500/30 hover:bg-green-500/15">
              <span className="font-medium text-green-400">Crystal Caverns (Easy)</span>
            </summary>
            <div className="mt-2 p-4 rounded-lg bg-surface">
              <ul className="text-sm text-frost-muted space-y-2">
                <li><strong className="text-frost">Composition:</strong> 50/25/25 - Balanced with infantry lead</li>
                <li><strong className="text-frost">Key mechanic:</strong> Crystal nodes that heal enemies - destroy first</li>
                <li><strong className="text-frost">Boss:</strong> Crystal Golem - avoid AoE attacks, focus body</li>
                <li><strong className="text-frost">Rewards:</strong> Basic crystals for crafting and upgrades</li>
              </ul>
            </div>
          </details>

          <details className="group">
            <summary className="cursor-pointer p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/30 hover:bg-yellow-500/15">
              <span className="font-medium text-yellow-400">Magma Chamber (Medium)</span>
            </summary>
            <div className="mt-2 p-4 rounded-lg bg-surface">
              <ul className="text-sm text-frost-muted space-y-2">
                <li><strong className="text-frost">Composition:</strong> 30/20/50 - Marksman-heavy for range advantage</li>
                <li><strong className="text-frost">Key mechanic:</strong> Lava pools deal damage over time - stay mobile</li>
                <li><strong className="text-frost">Boss:</strong> Magma Elemental - kite around arena, avoid eruptions</li>
                <li><strong className="text-frost">Rewards:</strong> Fire Essence for hero skill upgrades</li>
              </ul>
            </div>
          </details>

          <details className="group">
            <summary className="cursor-pointer p-3 rounded-lg bg-cyan-500/10 border border-cyan-500/30 hover:bg-cyan-500/15">
              <span className="font-medium text-cyan-400">Frost Halls (Medium)</span>
            </summary>
            <div className="mt-2 p-4 rounded-lg bg-surface">
              <ul className="text-sm text-frost-muted space-y-2">
                <li><strong className="text-frost">Composition:</strong> 40/40/20 - Balanced, lancers for mobility</li>
                <li><strong className="text-frost">Key mechanic:</strong> Freeze traps slow movement - bring speed buffs</li>
                <li><strong className="text-frost">Boss:</strong> Frost Warden - burst damage phases, heal between</li>
                <li><strong className="text-frost">Rewards:</strong> Ice Shards for equipment enhancement</li>
              </ul>
            </div>
          </details>

          <details className="group">
            <summary className="cursor-pointer p-3 rounded-lg bg-purple-500/10 border border-purple-500/30 hover:bg-purple-500/15">
              <span className="font-medium text-purple-400">Shadow Depths (Hard)</span>
            </summary>
            <div className="mt-2 p-4 rounded-lg bg-surface">
              <ul className="text-sm text-frost-muted space-y-2">
                <li><strong className="text-frost">Composition:</strong> 60/20/20 - Tank-heavy for survivability</li>
                <li><strong className="text-frost">Key mechanic:</strong> Darkness reduces vision - stick together</li>
                <li><strong className="text-frost">Boss:</strong> Shadow Lord - phases with adds, AoE cleanse needed</li>
                <li><strong className="text-frost">Rewards:</strong> Shadow Cores for advanced crafting</li>
              </ul>
            </div>
          </details>

          <details className="group">
            <summary className="cursor-pointer p-3 rounded-lg bg-red-500/10 border border-red-500/30 hover:bg-red-500/15">
              <span className="font-medium text-red-400">Void Nexus (Very Hard)</span>
            </summary>
            <div className="mt-2 p-4 rounded-lg bg-surface">
              <ul className="text-sm text-frost-muted space-y-2">
                <li><strong className="text-frost">Composition:</strong> 35/35/30 - Perfectly balanced, all maxed</li>
                <li><strong className="text-frost">Key mechanic:</strong> Void rifts teleport troops randomly - adapt quickly</li>
                <li><strong className="text-frost">Boss:</strong> Void Harbinger - multiple phases, enrage timer</li>
                <li><strong className="text-frost">Rewards:</strong> Void Essence for top-tier equipment</li>
                <li><strong className="text-frost text-yellow-400">Note:</strong> Requires all heroes at max level with legendary gear</li>
              </ul>
            </div>
          </details>

          <details className="group">
            <summary className="cursor-pointer p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 hover:bg-amber-500/15">
              <span className="font-medium text-amber-400">Ancient Ruins (Hard)</span>
            </summary>
            <div className="mt-2 p-4 rounded-lg bg-surface">
              <ul className="text-sm text-frost-muted space-y-2">
                <li><strong className="text-frost">Composition:</strong> 45/30/25 - Infantry lead with lancer support</li>
                <li><strong className="text-frost">Key mechanic:</strong> Puzzle elements - solve to progress</li>
                <li><strong className="text-frost">Boss:</strong> Ancient Guardian - mechanical patterns, learn timing</li>
                <li><strong className="text-frost">Rewards:</strong> Ancient Relics for special hero abilities</li>
              </ul>
            </div>
          </details>
        </div>
      </div>

      {/* General Tips */}
      <div className="card">
        <h2 className="section-header">General Labyrinth Tips</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">Progression</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Complete Easy zones first for resources</li>
              <li>• Upgrade heroes before attempting Hard</li>
              <li>• Save stamina for event bonuses</li>
              <li>• Daily attempts reset at server time</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">Combat</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Learn boss patterns before going all-in</li>
              <li>• Retreat is better than wipe</li>
              <li>• Use hero skills at right moments</li>
              <li>• AoE heroes valuable for trash waves</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function BattleTacticsPage() {
  const [activeTab, setActiveTab] = useState<TabKey>('castle-battles');

  const renderTabContent = () => {
    switch (activeTab) {
      case 'castle-battles':
        return <CastleBattlesTab />;
      case 'bear-trap':
        return <BearTrapTab />;
      case 'canyon-clash':
        return <CanyonClashTab />;
      case 'foundry':
        return <FoundryTab />;
      case 'frostfire':
        return <FrostfireMineTab />;
      case 'labyrinth':
        return <LabyrinthTab />;
      default:
        return null;
    }
  };

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-frost">Battle Tactics</h1>
          <p className="text-frost-muted mt-2">Strategic guides for all combat events</p>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-2 mb-6">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 ${
                activeTab === tab.key
                  ? 'bg-ice text-background'
                  : 'bg-surface text-frost-muted hover:text-frost hover:bg-surface-hover'
              }`}
            >
              <span>{tab.icon}</span>
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {renderTabContent()}
      </div>
    </PageLayout>
  );
}
