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
          Castle Battles are coordinated alliance events where each player has <strong className="text-fire">one castle</strong> to attack and defend.
          Timing, garrison management, and communication are everything.
        </p>
      </div>

      {/* Attack Tactics */}
      <div className="card">
        <h2 className="section-header text-fire">Attack Tactics</h2>
        <p className="text-frost-muted mb-4">How to take and hold enemy castles:</p>

        <div className="space-y-3">
          {[
            { priority: 'critical', title: 'Scout Before Attacking', desc: 'Always scout the target castle to see troop composition and garrison strength. Adjust your composition to counter.' },
            { priority: 'critical', title: 'Coordinate Rally Timing', desc: 'Don\'t launch random rallies. Coordinate with alliance for simultaneous attacks to overwhelm the garrison.' },
            { priority: 'critical', title: 'Refill Garrison Immediately After Capture', desc: 'The garrison is depleted after the assault. Send a full squad of troops as soon as you take control to prevent easy recapture.' },
            { priority: 'high', title: 'Swap to Sergey After Capture', desc: 'Once you take the castle, send a Sergey-led squad and recall the current garrison at the last second. Sergey\'s Defenders\' Edge (-20% DMG taken) makes holding much easier.' },
            { priority: 'high', title: 'Fill Rallies Completely', desc: 'A 75% full rally is often worse than waiting for 100%. Patience wins battles.' },
            { priority: 'high', title: 'Continuously Refill Garrison', desc: 'Don\'t just take the castle and forget it. Keep sending squads to maintain full garrison strength.' },
            { priority: 'medium', title: 'Rally Leader Composition', desc: 'Rally leader should use highest power heroes. Put best expedition skill heroes in slot 1.' },
            { priority: 'medium', title: 'Joiner Strategy', desc: 'Jessie FIRST for attack joiners (+25% DMG at max skill). Only first hero\'s top-right skill applies.' },
            { priority: 'low', title: 'Fake Rallies', desc: 'Start a rally to draw reinforcements, cancel, then hit the actual target. Use sparingly - wastes rally timer.' },
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
        <p className="text-frost-muted mb-4">How to hold your castle against coordinated attacks:</p>

        <div className="space-y-3">
          {[
            { priority: 'critical', title: 'Reinforce Before Rally Launches', desc: 'Once a rally starts, you have limited time. Reinforce immediately when you see a rally forming.' },
            { priority: 'critical', title: 'Sergey First for Defense', desc: 'Put Sergey in slot 1 of garrison. Defenders\' Edge reduces ALL incoming damage (-20% at max skill).' },
            { priority: 'critical', title: 'Time Reinforcements Between Enemy Rallies', desc: 'Enemy alliances will coordinate rallies as close together as possible. Send garrison reinforcements to arrive between their attacks so troops are refilled before the next wave hits.' },
            { priority: 'high', title: 'Infantry-Heavy Garrison', desc: 'Use 60/25/15 ratio (Infantry/Lancer/Marksman). Infantry survives longer under sustained attacks.' },
            { priority: 'high', title: 'Fill All Hero Slots', desc: 'Empty hero slots = wasted stats. Put any hero rather than leaving slots empty.' },
            { priority: 'medium', title: 'Bait and Switch', desc: 'Show weak garrison, wait for rally, then swap in strong garrison at last second. Risky but effective.' },
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
              <li>• Troops fully healed</li>
              <li>• Heroes assigned to march slots</li>
              <li>• Rally speedups ready</li>
              <li>• Sergey squad ready to swap in after capture</li>
              <li>• Comms channel open</li>
            </ul>
          </div>
          <div>
            <h3 className="font-medium text-ice mb-2">Defenders</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Garrison heroes set (Sergey slot 1)</li>
              <li>• Troop ratio configured (60/25/15)</li>
              <li>• Reinforcement troops ready to send between enemy rallies</li>
              <li>• Hospital capacity available</li>
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
          The bear is slow-moving, making <span className={troopColors.marksman}>Marksman-heavy</span> compositions optimal for DPS.
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
              <li>• Only each joiner{"'"}s <strong className="text-frost">first hero{"'"}s top-right expedition skill</strong> counts</li>
              <li>• Higher level bear = better rewards</li>
              <li>• Hero class doesn{"'"}t need to match troop type - <strong className="text-frost">skill level matters most</strong></li>
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

      {/* Key Concept: Hero Class vs Skill */}
      <div className="card border-yellow-500/30">
        <h2 className="section-header text-yellow-400">Hero Class Doesn{"'"}t Matter for Joining</h2>
        <p className="text-frost-muted mb-4">
          Common misconception: you need marksman heroes for Bear Trap. In reality, <strong className="text-frost">Jessie (a Lancer)</strong> is the #1 attack joiner because her expedition skill buffs ALL troop damage.
        </p>

        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/30">
            <h3 className="font-medium text-green-400 mb-2">What Matters (Joiners)</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">Expedition skill level</strong> - higher = better</li>
              <li>• <strong className="text-frost">Skill effect</strong> - damage buffs are best</li>
              <li>• Only the first hero{"'"}s top-right skill is used</li>
              <li>• Top 4 highest skill LEVELS from all joiners apply</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30">
            <h3 className="font-medium text-red-400 mb-2">What Doesn{"'"}t Matter (Joiners)</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Hero class (Infantry/Lancer/Marksman)</li>
              <li>• Hero power or level</li>
              <li>• Hero gear (only rally leader{"'"}s gear matters)</li>
              <li>• Your troop composition (rally leader sets it)</li>
            </ul>
          </div>
        </div>

        <div className="mt-4 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
          <p className="text-sm text-frost">
            <strong className="text-yellow-400">Bottom Line:</strong> Put your hero with the highest expedition skill level first,
            regardless of their class. Jessie the Lancer is the best attack joiner in the game.
          </p>
        </div>
      </div>

      {/* Best Attack Joiner Heroes */}
      <div className="card">
        <h2 className="section-header">Best Attack Joiner Heroes</h2>
        <p className="text-frost-muted mb-4">Heroes with the best top-right expedition skills for boosting rally damage:</p>

        <div className="space-y-2">
          {[
            { name: 'Jessie', gen: 1, class: 'Lancer', skill: 'Stand of Arms', effect: '+5-25% DMG dealt (ALL troops)', priority: 'critical' },
            { name: 'Jasser', gen: 1, class: 'Marksman', skill: 'Tactical Genius', effect: '+5-25% DMG dealt (ALL troops)', priority: 'critical' },
            { name: 'Seo-yoon', gen: 1, class: 'Marksman', skill: 'Rallying Beat', effect: '+5-25% ATK (ALL troops)', priority: 'critical' },
            { name: 'Hervor', gen: 12, class: 'Infantry', skill: 'Call For Blood', effect: '+5-25% DMG dealt (ALL troops)', priority: 'high' },
            { name: 'Hendrik', gen: 8, class: 'Marksman', skill: "Worm's Ravage", effect: '-5-25% enemy DEF (ALL enemies)', priority: 'high' },
            { name: 'Sonya', gen: 8, class: 'Lancer', skill: 'Treasure Hunter', effect: '+4-20% DMG (ALL troops)', priority: 'medium' },
            { name: 'Lynn', gen: 4, class: 'Marksman', skill: 'Song of Lion', effect: '40% chance +10-50% DMG dealt', priority: 'medium' },
          ].map((hero, i) => {
            const colors = priorityColors[hero.priority];
            const classColor = troopColors[hero.class.toLowerCase() as keyof typeof troopColors] || 'text-frost';
            return (
              <div key={i} className={`p-3 rounded ${colors.bg} border ${colors.border}`}>
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-bold uppercase ${colors.text} w-6`}>#{i + 1}</span>
                    <span className="font-medium text-frost">{hero.name}</span>
                    <span className={`text-xs ${classColor}`}>({hero.class})</span>
                    <span className="text-xs text-frost-muted">Gen {hero.gen}</span>
                  </div>
                  <span className="text-xs text-frost-muted">{hero.effect}</span>
                </div>
                <p className="text-xs text-frost-muted mt-1 ml-8">Skill: {hero.skill}</p>
              </div>
            );
          })}
        </div>

        <div className="mt-4 p-3 rounded-lg bg-ice/10 border border-ice/30">
          <p className="text-sm text-frost">
            <strong className="text-ice">For garrison defense:</strong> Use <strong>Sergey</strong> (Gen 1, Infantry) first - his
            Defender{"'"}s Edge skill reduces ALL damage taken by up to 20%.
          </p>
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
                <td className="py-2">Highest power hero</td>
                <td className="py-2">0/10/90</td>
                <td className="py-2 text-frost-muted">You set the composition</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="py-2">Joiner (Best)</td>
                <td className="py-2 text-green-400">Jessie (Lancer)</td>
                <td className="py-2">0/10/90</td>
                <td className="py-2 text-frost-muted">Stand of Arms: +25% DMG at skill 5</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="py-2">Joiner (Alt)</td>
                <td className="py-2">Jasser / Seo-yoon</td>
                <td className="py-2">0/10/90</td>
                <td className="py-2 text-frost-muted">Same +25% buff as Jessie (all Gen 1)</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="py-2">Joiner (Fallback)</td>
                <td className="py-2">Highest combat skill hero</td>
                <td className="py-2">0/10/90</td>
                <td className="py-2 text-frost-muted">Any hero with offensive expedition skill</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="py-2 text-red-400">AVOID</td>
                <td className="py-2 text-frost-muted">No hero (troops only)</td>
                <td className="py-2">0/10/90</td>
                <td className="py-2 text-frost-muted">Better than a non-combat skill (gathering, building speed)</td>
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
          Canyon Clash is a <strong className="text-purple-400">3-way alliance PvP battle</strong> where three alliances fight for control of buildings and the Frozen Citadel.
          <strong className="text-fire ml-1">Fuel management is everything.</strong>
        </p>
      </div>

      {/* Arena Map Layout */}
      <div className="card">
        <h2 className="section-header">Arena Map</h2>
        <div className="max-w-md mx-auto py-6">
          <div className="flex flex-col items-center gap-2">
            <div className="w-24 h-24 rounded-full bg-amber-500/20 border-2 border-amber-500 flex items-center justify-center text-center">
              <span className="text-xs text-amber-400 font-bold leading-tight">Frozen<br/>Citadel</span>
            </div>
            <div className="flex items-center gap-1 text-frost-muted text-xs">
              <span className="w-8 border-t border-dashed border-frost-muted"></span>
              <span>bridges</span>
              <span className="w-8 border-t border-dashed border-frost-muted"></span>
            </div>
            <div className="grid grid-cols-3 gap-8 w-full">
              {['Alliance 1', 'Alliance 2', 'Alliance 3'].map((name, i) => (
                <div key={i} className="flex flex-col items-center gap-1">
                  <div className={`w-16 h-16 rounded-lg flex items-center justify-center text-center ${
                    i === 0 ? 'bg-red-500/20 border border-red-500/50' :
                    i === 1 ? 'bg-blue-500/20 border border-blue-500/50' :
                    'bg-green-500/20 border border-green-500/50'
                  }`}>
                    <span className={`text-[10px] font-medium ${
                      i === 0 ? 'text-red-400' : i === 1 ? 'text-blue-400' : 'text-green-400'
                    }`}>{name}</span>
                  </div>
                  <span className="text-[10px] text-frost-muted">Island {i + 1}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
        <p className="text-xs text-frost-muted text-center">
          Three alliances start on separate islands, connected by bridges to the central Frozen Citadel
        </p>
      </div>

      {/* How It Works */}
      <div className="card">
        <h2 className="section-header">How Canyon Clash Works</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">Event Basics</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">3-way battle</strong> - Top 20 alliances compete</li>
              <li>• <strong className="text-frost">60 minutes</strong> across 4 phases</li>
              <li>• <strong className="text-frost">Fuel</strong> is required for ALL actions (moving, attacking, reviving)</li>
              <li>• <strong className="text-frost">Min 15 players</strong> per Legion to participate</li>
              <li>• <strong className="text-frost">Furnace 16+</strong> required</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">Weekly Schedule</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">Mon-Tue:</strong> Vote for battle timezone</li>
              <li>• <strong className="text-frost">Wed-Thu:</strong> Registration opens</li>
              <li>• <strong className="text-frost">Friday:</strong> Matchmaking (random opponent)</li>
              <li>• <strong className="text-frost">Sat/Sun:</strong> Battle day (based on vote)</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Battle Phases */}
      <div className="card">
        <h2 className="section-header">Battle Phases (60 min total)</h2>

        <div className="space-y-4">
          <div className="p-4 rounded-lg bg-surface border border-surface-border">
            <h3 className="font-medium text-frost mb-2">Phase 1: Preparation (3 min)</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Position your marches, plan team assignments</li>
              <li>• <strong className="text-frost">Pre-assign roles in Discord</strong> before match starts</li>
              <li>• Put your strongest player on Citadel assault team (needs most fuel)</li>
            </ul>
          </div>

          <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/30">
            <h3 className="font-medium text-blue-400 mb-2">Phase 2: Seize & Conquer (17 min)</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">Secure YOUR island first</strong> - send 1 player to each neutral building</li>
              <li>• Block enemy bridges by stationing defenders at bridge exits</li>
              <li>• Don't overextend - capture only what you can hold</li>
              <li>• Each uncaptured building drains fuel to retake later</li>
            </ul>
          </div>

          <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
            <h3 className="font-medium text-yellow-400 mb-2">Phase 3: Fortress Occupation (20 min)</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Hold fortresses for points, prepare for Citadel</li>
              <li>• Designate lower-fuel players as Guardians at captured buildings</li>
              <li>• Monitor fuel levels - save for final push</li>
            </ul>
          </div>

          <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30">
            <h3 className="font-medium text-red-400 mb-2">Phase 4: Final Battle (20 min)</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-fire">All-out assault on Frozen Citadel!</strong></li>
              <li>• Citadel control = MASSIVE point multiplier</li>
              <li>• Use all remaining fuel - coordinate the push</li>
              <li>• <strong className="text-frost">Whoever holds citadel at end wins</strong></li>
            </ul>
          </div>
        </div>
      </div>

      {/* Fuel Management */}
      <div className="card">
        <h2 className="section-header">Fuel Management (CRITICAL)</h2>
        <div className="p-4 rounded-lg bg-fire/10 border border-fire/30 mb-4">
          <p className="text-frost font-medium">
            Fuel is required for EVERYTHING: moving, attacking, reviving. Run out = you're useless.
          </p>
        </div>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">Fuel Costs</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">Moving:</strong> Consumes fuel per tile</li>
              <li>• <strong className="text-frost">Attacking:</strong> Large fuel cost per attack</li>
              <li>• <strong className="text-frost">Reviving:</strong> Costs fuel to respawn</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">Fuel Tips</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">Save 30%</strong> of fuel for Phase 4</li>
              <li>• Don't chase kills - wastes fuel</li>
              <li>• Capture buildings = fuel income</li>
              <li>• <strong className="text-fire">Running out early = game over</strong></li>
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
          Foundry is a <strong className="text-amber-400">biweekly alliance event</strong> (every 2 weeks, 60 minutes).
          <strong className="text-ice ml-1">NO troop deaths!</strong> - troops don't permanently die, making this very F2P-friendly.
        </p>
      </div>

      {/* Battlefield Map */}
      <div className="card">
        <h2 className="section-header">Battlefield Map</h2>
        <div className="flex justify-center">
          <img
            src="https://cdn-www.bluestacks.com/bs-images/WhiteoutSurvival_Guide_FoundryBattleGuide_EN2.jpg"
            alt="Foundry Battle Map"
            className="max-w-full rounded-lg border border-surface-border"
            style={{ maxHeight: '350px', imageRendering: 'auto', filter: 'contrast(1.15) brightness(1.02) saturate(1.1)' }}
          />
        </div>
        <p className="text-xs text-frost-muted text-center mt-2">
          Key locations: Imperial Foundry (center), Transit Station (50% teleport CD reduction), Boiler Room (faster captures)
        </p>
      </div>

      {/* How It Works */}
      <div className="card">
        <h2 className="section-header">How Foundry Works</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">Event Basics</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">60 minutes</strong> - 3 phases</li>
              <li>• <strong className="text-ice">NO troop deaths</strong> - troops are unlimited</li>
              <li>• <strong className="text-frost">30 alliance members</strong> can participate</li>
              <li>• Capture buildings AND gather loot for points</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">Winning Strategy</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-amber-400">Gather loot</strong> - often more valuable than holding!</li>
              <li>• Split teams: Garrison + Attackers + Gatherers</li>
              <li>• <strong className="text-frost">Voice chat</strong> is essential for coordination</li>
              <li>• Keep buildings changing hands to generate loot</li>
            </ul>
          </div>
        </div>
      </div>

      {/* CRITICAL: Loot Mechanic */}
      <div className="card border-amber-500/50 bg-gradient-to-r from-amber-500/10 to-transparent">
        <h2 className="section-header text-amber-400">CRITICAL: The Loot Mechanic</h2>
        <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 mb-4">
          <p className="text-frost font-medium">
            <span className="text-red-400">WARNING:</span> You can hold ALL buildings and STILL LOSE!
            Controlling buildings alone is NOT enough to win.
          </p>
        </div>

        <div className="space-y-4">
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-amber-400 mb-2">How Loot Works</h3>
            <ul className="text-sm text-frost-muted space-y-2">
              <li>• When a building <strong className="text-frost">changes hands</strong>, it releases <strong className="text-amber-400">loot</strong> onto the map</li>
              <li>• <strong className="text-ice">The longer a building is held, the MORE loot it releases</strong> when captured</li>
              <li>• Loot appears as gatherable resources on the battlefield</li>
              <li>• <strong className="text-amber-400">Gathering loot gives MORE points than just holding buildings!</strong></li>
              <li>• Capturing a building gives instant points + triggers loot spawn</li>
            </ul>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/30">
              <h3 className="font-medium text-green-400 mb-2">Winning Team Strategy</h3>
              <ul className="text-sm text-frost-muted space-y-1">
                <li>• <strong className="text-frost">Garrison Team:</strong> Hold key buildings</li>
                <li>• <strong className="text-frost">Attack Team:</strong> Teleport around, capture enemy buildings</li>
                <li>• <strong className="text-frost">Gather Team:</strong> Collect ALL loot immediately</li>
                <li>• Keep buildings flipping to generate more loot!</li>
              </ul>
            </div>
            <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30">
              <h3 className="font-medium text-red-400 mb-2">Common Mistake (Why You Lost)</h3>
              <ul className="text-sm text-frost-muted space-y-1">
                <li>• Sitting in buildings just garrisoning</li>
                <li>• Ignoring loot spawns on the map</li>
                <li>• Not attacking enemy buildings</li>
                <li>• Letting enemy gather YOUR loot when they cap</li>
              </ul>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/30">
            <h3 className="font-medium text-amber-400 mb-2">Pro Tip: The "Flip & Gather" Strategy</h3>
            <p className="text-sm text-frost-muted mb-2">
              If you have MORE players than the enemy alliance:
            </p>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">Intentionally let some buildings get taken</strong> (especially ones held a long time)</li>
              <li>• <strong className="text-frost">Immediately retake them</strong> - triggers HUGE loot drop</li>
              <li>• <strong className="text-frost">Have gatherers ready</strong> to collect the loot instantly</li>
              <li>• Repeat! More flips = more loot = more points</li>
            </ul>
          </div>
        </div>
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

      {/* Team Roles */}
      <div className="card">
        <h2 className="section-header">Team Roles (Revised Strategy)</h2>
        <p className="text-frost-muted mb-4">Optimal team organization including loot gathering:</p>

        <div className="grid md:grid-cols-3 gap-4">
          <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30">
            <h3 className="font-medium text-red-400 mb-2">Garrison Team (30-40%)</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Strongest players</li>
              <li>• Hold high-value buildings</li>
              <li>• Defend against enemy attacks</li>
              <li>• Call out incoming enemies</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-orange-500/10 border border-orange-500/30">
            <h3 className="font-medium text-orange-400 mb-2">Attack Team (30-40%)</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Fast, mobile players</li>
              <li>• Teleport around the map</li>
              <li>• Capture enemy buildings</li>
              <li>• Generate loot by flipping buildings</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/30">
            <h3 className="font-medium text-amber-400 mb-2">Gather Team (20-30%)</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-amber-400">CRITICAL ROLE!</strong></li>
              <li>• Collect ALL loot immediately</li>
              <li>• Follow attack team's captures</li>
              <li>• Never leave loot on the ground</li>
            </ul>
          </div>
        </div>

        <div className="mt-4 p-3 rounded-lg bg-ice/10 border border-ice/30">
          <p className="text-sm text-frost">
            <strong className="text-ice">Adapt based on enemy numbers:</strong> If you outnumber them, focus more on Attack + Gather.
            If outnumbered, focus more on Garrison + opportunistic gathering.
          </p>
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
          Frostfire Mine is a <strong className="text-cyan-400">30-minute competitive mining event</strong> with PvP elements.
          <strong className="text-ice ml-1">NO troop losses!</strong> Gather Orichalcum by occupying veins, defeating patrols, and rushing Vein Outbursts.
        </p>
      </div>

      {/* Event Basics */}
      <div className="card">
        <h2 className="section-header">Event Basics</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">Key Info</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">Duration:</strong> 30 min active + 3 min prep</li>
              <li>• <strong className="text-frost">Frequency:</strong> Biweekly (every 2 weeks)</li>
              <li>• <strong className="text-frost">Requirement:</strong> Furnace 16+</li>
              <li>• <strong className="text-ice">NO troop deaths</strong> - troops are unlimited!</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-fire/10 border border-fire/30">
            <h3 className="font-medium text-fire mb-2">Rewards</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">Charm Designs</strong> and <strong className="text-frost">Charm Guides</strong></li>
              <li>• Key materials for Chief Charm upgrades (FC25+)</li>
              <li>• Milestone rewards at 10K-150K Orichalcum</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Skill Build */}
      <div className="card border-yellow-500/30">
        <h2 className="section-header text-yellow-400">Skill Build: R-R-L-L-R</h2>
        <p className="text-frost-muted mb-4">
          Defeat Mine Patrols on map edges to earn XP and unlock skills. Choose LEFT or RIGHT at each level:
        </p>

        <div className="flex flex-wrap gap-3 mb-4">
          {[
            { choice: 'R', label: 'Right', desc: '1,500 Orichalcum per patrol' },
            { choice: 'R', label: 'Right', desc: '25% march speed' },
            { choice: 'L', label: 'Left', desc: '5,000/60s while on vein' },
            { choice: 'L', label: 'Left', desc: '15% gathering efficiency' },
            { choice: 'R', label: 'Right', desc: '+50 speed for 60s (SAVE FOR OUTBURSTS!)' },
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

        <div className="p-3 rounded-lg bg-fire/10 border border-fire/30">
          <p className="text-sm text-frost">
            <strong className="text-fire">CRITICAL:</strong> Save Skill 5 for Vein Outbursts ONLY!
            The +50 gathering speed for 60 seconds is wasted on regular veins.
          </p>
        </div>
      </div>

      {/* Minute-by-Minute Guide */}
      <div className="card">
        <h2 className="section-header">Minute-by-Minute Strategy</h2>
        <p className="text-frost-muted mb-4 text-sm">Event time counts DOWN from 30:00 to 0:00</p>

        <div className="space-y-3">
          {[
            { time: '30:00-27:00', phase: 'Opening Rush', priority: 'high', action: 'Hunt Mine Patrols on map edges for skill XP', tip: 'Don\'t waste time on veins yet!' },
            { time: '27:00-23:00', phase: 'Skill Building', priority: 'medium', action: 'Continue patrols, unlock skills 1-3. Send ONE squad to a vein.', tip: 'Watch for first Outburst alert at ~23:00' },
            { time: '22:00-20:00', phase: 'OUTBURST WAVE 1', priority: 'critical', action: 'DROP EVERYTHING! Outbursts at min 8, 9, 10. Activate Skill 5!', tip: '4,000 Orichalcum in 20 seconds each!' },
            { time: '20:00-13:00', phase: 'Mid-Game Grind', priority: 'medium', action: 'Resume patrols if skills not maxed. Occupy Level 2-3 veins.', tip: 'Avoid unnecessary PvP - save heroes for Outbursts' },
            { time: '12:00-10:00', phase: 'OUTBURST WAVE 2', priority: 'critical', action: 'DROP EVERYTHING! Outbursts at min 18, 19, 20. Skill 5 again!', tip: 'Same priority as first wave' },
            { time: '10:00-7:30', phase: 'Pre-Smelter', priority: 'medium', action: 'Max skills if not done. Occupy highest-value veins.', tip: 'Prepare for Smelter decision' },
            { time: '7:30-0:00', phase: 'Smelter Opens', priority: 'situational', action: 'Top 3? Rush smelter. Mid-tier? Stay on veins.', tip: 'Don\'t waste time fighting stronger players' },
          ].map((step, i) => (
            <div key={i} className={`p-3 rounded-lg ${
              step.priority === 'critical' ? 'bg-fire/10 border border-fire/30' :
              step.priority === 'situational' ? 'bg-purple-500/10 border border-purple-500/30' :
              step.priority === 'high' ? 'bg-orange-500/10 border border-orange-500/30' :
              'bg-surface'
            }`}>
              <div className="flex flex-wrap items-start gap-3">
                <span className="font-mono text-sm text-ice whitespace-nowrap">{step.time}</span>
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                  step.priority === 'critical' ? 'bg-fire/20 text-fire' :
                  step.priority === 'situational' ? 'bg-purple-500/20 text-purple-400' :
                  step.priority === 'high' ? 'bg-orange-500/20 text-orange-400' :
                  'bg-blue-500/20 text-blue-400'
                }`}>{step.phase}</span>
                <div className="flex-1">
                  <p className="text-sm text-frost">{step.action}</p>
                  <p className="text-xs text-frost-muted mt-1">{step.tip}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Vein Outbursts - CRITICAL */}
      <div className="card border-fire/50">
        <h2 className="section-header text-fire">Vein Outbursts (MOST IMPORTANT!)</h2>
        <div className="p-4 rounded-lg bg-fire/10 border border-fire/30 mb-4">
          <p className="text-frost font-medium text-lg">
            4,000 Orichalcum in 20 seconds! DROP EVERYTHING when these spawn!
          </p>
        </div>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">Spawn Times (NOT Random!)</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-fire">Wave 1:</strong> Minutes 8, 9, 10</li>
              <li>• <strong className="text-fire">Wave 2:</strong> Minutes 18, 19, 20</li>
              <li>• Banner appears 60s and 10s before</li>
              <li>• Worth more than 10 min of regular veins!</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">How to Maximize</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• <strong className="text-frost">Activate Skill 5</strong> right as they spawn</li>
              <li>• Teleport to outburst location immediately</li>
              <li>• Prioritize over EVERYTHING including smelter</li>
              <li>• These are the #1 source of points!</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Vein Levels */}
      <div className="card">
        <h2 className="section-header">Vein Levels (What "Deep Ores" Means)</h2>
        <p className="text-frost-muted mb-4">Higher level veins give MORE ore per second. Level 3 = 4x better than Level 1!</p>
        <div className="grid md:grid-cols-3 gap-4">
          <div className="p-4 rounded-lg bg-surface text-center">
            <h3 className="font-medium text-frost mb-2">Level 1</h3>
            <p className="text-2xl font-bold text-blue-400">+8/s</p>
            <p className="text-xs text-frost-muted">Near spawn</p>
          </div>
          <div className="p-4 rounded-lg bg-surface text-center">
            <h3 className="font-medium text-frost mb-2">Level 2</h3>
            <p className="text-2xl font-bold text-yellow-400">+16/s</p>
            <p className="text-xs text-frost-muted">Middle areas</p>
          </div>
          <div className="p-4 rounded-lg bg-surface text-center border border-fire/30">
            <h3 className="font-medium text-fire mb-2">Level 3</h3>
            <p className="text-2xl font-bold text-fire">+32/s</p>
            <p className="text-xs text-frost-muted">Deep in mine</p>
          </div>
        </div>
      </div>

      {/* Smelter Decision */}
      <div className="card">
        <h2 className="section-header">Smelter (Is It Worth It?)</h2>
        <div className="p-4 rounded-lg bg-fire/10 border border-fire/30 mb-4">
          <p className="text-lg font-bold text-fire">
            NO for most players!
          </p>
          <p className="text-frost mt-2">
            The Smelter is a BONUS objective in the center. Opens at 7:30 remaining.
            Only the strongest players who get there first benefit.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-3 rounded-lg bg-green-500/10">
            <h4 className="font-medium text-green-400 mb-2">Go for it IF:</h4>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• You're top 3 strongest in the match</li>
              <li>• You can teleport there immediately</li>
              <li>• Your heroes are NOT on cooldown</li>
            </ul>
          </div>
          <div className="p-3 rounded-lg bg-red-500/10">
            <h4 className="font-medium text-red-400 mb-2">Skip it IF:</h4>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• You're mid-tier or below in power</li>
              <li>• Others are already fighting over it</li>
              <li>• Vein Outbursts are spawning soon (min 18-20)</li>
            </ul>
          </div>
        </div>
        <p className="text-sm text-frost-muted mt-4 text-center">
          <strong className="text-ice">Better alternative:</strong> Focus on Vein Outbursts at min 18-20 instead - guaranteed 4,000 each!
        </p>
      </div>

      {/* Quick Reference */}
      <div className="card">
        <h2 className="section-header">Quick Reference Card</h2>
        <div className="p-4 rounded-lg bg-surface font-mono text-sm">
          <pre className="text-frost-muted whitespace-pre-wrap">{`FROSTFIRE MINE CHEAT SHEET
========================

Skill Build: R → R → L → L → R
(Ore bonus → March speed → Vein bonus → Efficiency → SAVE FOR OUTBURSTS)

Priority Order:
1. VEIN OUTBURSTS (min 8-10 and 18-20) - 4,000 each!
2. Mine Patrols for skill XP (early game)
3. Level 3 veins (deep in mine, +32/s)
4. Smelter ONLY if you're top 3 power

Key Timing:
- Min 8-10: First Outburst wave
- Min 18-20: Second Outburst wave
- 7:30 remaining: Smelter opens

Don't forget:
- Use Skill 5 ONLY on Outbursts
- Higher level veins = more ore/second
- Teleport has 6 min cooldown - use it!`}</pre>
        </div>
      </div>
    </div>
  );
}

function LabyrinthTab() {
  const zones = [
    { zone: 'Land of the Brave', days: 'Mon - Tue', statSource: 'Heroes, Hero Gear, Exclusive Gear', unlock: 'Furnace 19', color: 'red' },
    { zone: 'Cave of Monsters', days: 'Wed - Thu', statSource: 'Pets & Pet Skills', unlock: 'Furnace 19 + Pets (~55 days)', color: 'green' },
    { zone: 'Glowstone Mine', days: 'Wed - Thu', statSource: 'Chief Charms', unlock: 'Furnace 25', color: 'purple' },
    { zone: 'Earthlab', days: 'Fri - Sat', statSource: 'Research & War Academy Tech', unlock: 'Furnace 19', color: 'blue' },
    { zone: 'Dark Forge', days: 'Fri - Sat', statSource: 'Chief Gear', unlock: 'Furnace 22', color: 'amber' },
    { zone: 'Gaia Heart', days: 'Sunday', statSource: 'ALL stats (heroes, gear, pets, charms, research, chief gear)', unlock: 'Furnace 19', color: 'yellow' },
  ];

  const colorMap: Record<string, { bg: string; border: string; text: string }> = {
    red: { bg: 'bg-red-500/10', border: 'border-red-500/30', text: 'text-red-400' },
    green: { bg: 'bg-green-500/10', border: 'border-green-500/30', text: 'text-green-400' },
    purple: { bg: 'bg-purple-500/10', border: 'border-purple-500/30', text: 'text-purple-400' },
    blue: { bg: 'bg-blue-500/10', border: 'border-blue-500/30', text: 'text-blue-400' },
    amber: { bg: 'bg-amber-500/10', border: 'border-amber-500/30', text: 'text-amber-400' },
    yellow: { bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', text: 'text-yellow-400' },
  };

  return (
    <div className="space-y-6">
      <div className="card bg-gradient-to-r from-indigo-500/10 to-transparent border-indigo-500/30">
        <p className="text-frost">
          Labyrinth is a <strong className="text-indigo-400">weekly combat challenge</strong> with 6 zones.
          Each zone only uses <strong className="text-frost">specific stat sources</strong> - your other upgrades don{"'"}t count!
          Unlocks at <strong className="text-frost">Furnace 19</strong>. 5 attempts per zone per day. Stages reset weekly on Monday.
        </p>
      </div>

      {/* Key Mechanic */}
      <div className="card border-fire/30">
        <h2 className="section-header text-fire">Critical: Each Zone Uses Different Stats!</h2>
        <p className="text-frost-muted mb-4">
          Unlike other events, the Labyrinth <strong className="text-frost">only reads specific stat sources per zone</strong>.
          Your hero levels might be maxed, but in Cave of Monsters only your Pet stats matter.
        </p>
        <div className="p-3 rounded-lg bg-fire/10 border border-fire/30">
          <p className="text-sm text-frost">
            <strong className="text-fire">Weekday zones (Mon-Sat):</strong> The game provides <strong>Level 10 troops</strong> for you - your own troop levels don{"'"}t matter.
          </p>
          <p className="text-sm text-frost mt-1">
            <strong className="text-yellow-400">Sunday (Gaia Heart):</strong> You use <strong>your own troops</strong> (but no casualties), and ALL stat sources apply.
          </p>
        </div>
      </div>

      {/* Zone Schedule Table */}
      <div className="card">
        <h2 className="section-header">Zone Schedule</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border">
                <th className="text-left py-2 text-frost-muted">Zone</th>
                <th className="text-center py-2 text-frost-muted">Days</th>
                <th className="text-left py-2 text-frost-muted">Stats That Matter</th>
                <th className="text-left py-2 text-frost-muted">Unlock</th>
              </tr>
            </thead>
            <tbody className="text-frost">
              {zones.map((zone, i) => {
                const colors = colorMap[zone.color];
                return (
                  <tr key={i} className="border-b border-surface-border/50">
                    <td className={`py-2 font-medium ${colors.text}`}>{zone.zone}</td>
                    <td className="text-center py-2 text-frost-muted">{zone.days}</td>
                    <td className="py-2 text-frost-muted text-xs">{zone.statSource}</td>
                    <td className="py-2 text-frost-muted text-xs">{zone.unlock}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Zone Details */}
      <div className="card">
        <h2 className="section-header">Zone Details</h2>
        <div className="space-y-4">
          {zones.map((zone, i) => {
            const colors = colorMap[zone.color];
            const details: Record<string, string[]> = {
              'Land of the Brave': [
                'Only hero levels, stars, ascension, skills, hero gear, and exclusive gear matter',
                'Pets, research, chief gear, and charms are all irrelevant here',
                'Players who invested heavily in hero gear and exclusive gear excel',
                'Hero skill levels (both exploration and expedition) contribute',
              ],
              'Cave of Monsters': [
                'Only pet levels and pet skills matter',
                'Requires pets to be unlocked (Furnace 18 + ~55 days server age)',
                'Hero levels, gear, research etc. do NOT factor in',
                'High-level pets with leveled skills dominate this zone',
              ],
              'Glowstone Mine': [
                'Only Chief Charms matter (unlocks at Furnace 25)',
                'Charm slot levels (up to level 16 with sub-levels) determine your power',
                'One of the harder zones for F2P players due to charm investment required',
                'Focus on leveling charm slots evenly across all gear pieces',
              ],
              'Earthlab': [
                'Only Research Center and War Academy technologies matter',
                'War Academy unlocks at Furnace 30 - pre-FC players rely on Research only',
                'Players who prioritized combat research perform best',
                'Good zone for older accounts with lots of research done',
              ],
              'Dark Forge': [
                'Only Chief Gear quality, level, and mastery matter',
                'Requires Furnace 22 to unlock Chief Gear',
                'High-quality, high-level chief gear (coat, pants, hat, watch, belt, weapon) dominates',
                'Mastery levels (Furnace 30+) give significant advantage',
              ],
              'Gaia Heart': [
                'ALL stat sources apply (heroes, hero gear, pets, charms, research, War Academy, chief gear)',
                'EXCEPTION: Castle buffs, alliance tech/territory, gem buffs, and facilities do NOT work',
                'You use YOUR OWN TROOPS (not provided Level 10) - troop tier matters!',
                'No casualties - troops are safe. This is the "ultimate test" zone',
              ],
            };
            return (
              <details key={i} className="group">
                <summary className={`cursor-pointer p-3 rounded-lg ${colors.bg} border ${colors.border} hover:opacity-80`}>
                  <span className={`font-medium ${colors.text}`}>{zone.zone}</span>
                  <span className="text-frost-muted text-sm ml-2">({zone.days})</span>
                </summary>
                <div className="mt-2 p-4 rounded-lg bg-surface">
                  <ul className="text-sm text-frost-muted space-y-2">
                    {(details[zone.zone] || []).map((detail, j) => (
                      <li key={j}>{detail}</li>
                    ))}
                  </ul>
                </div>
              </details>
            );
          })}
        </div>
      </div>

      {/* Troop Composition */}
      <div className="card">
        <h2 className="section-header">Troop Composition</h2>
        <p className="text-frost-muted mb-4">
          For weekday zones (Mon-Sat), the game provides Level 10 troops. Use a balanced composition for all stages:
        </p>

        <div className="p-4 rounded-lg bg-surface mb-4">
          <h3 className="font-medium text-frost mb-3">Recommended Ratio (All Stages)</h3>
          <div className="flex items-center justify-center gap-8">
            <div className="text-center">
              <p className={`text-3xl font-bold ${troopColors.infantry}`}>50%</p>
              <p className="text-xs text-frost-muted">Infantry</p>
            </div>
            <div className="text-center">
              <p className={`text-3xl font-bold ${troopColors.lancer}`}>20%</p>
              <p className="text-xs text-frost-muted">Lancer</p>
            </div>
            <div className="text-center">
              <p className={`text-3xl font-bold ${troopColors.marksman}`}>30%</p>
              <p className="text-xs text-frost-muted">Marksman</p>
            </div>
          </div>
          <p className="text-sm text-frost-muted text-center mt-3">
            This balanced ratio works consistently across all zones and stages 1-10.
            Infantry-heavy front absorbs damage while marksmen deal sustained DPS.
          </p>
        </div>
      </div>

      {/* Raid and Progression */}
      <div className="card">
        <h2 className="section-header">Progression Tips</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">Stage Clearing</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• 10 stages per zone, increasing difficulty</li>
              <li>• <strong className="text-frost">Raid unlocks after clearing Stage 10</strong> - instant rewards on future weeks</li>
              <li>• 5 attempts per zone per day, reset at 00:00 UTC</li>
              <li>• Stages reset every Monday</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">Reward Priorities</h3>
            <ul className="text-sm text-frost-muted space-y-1">
              <li>• Exchange Labyrinth currency for <strong className="text-frost">Mithril</strong> and <strong className="text-frost">FC Shards</strong> first</li>
              <li>• Treasure chests from stage clears</li>
              <li>• Milestone rewards via Labyrinth Cores</li>
              <li>• Decorations: Luminari Citadel, Hero{"'"}s Sanctum</li>
            </ul>
          </div>
        </div>

        <div className="mt-4 p-3 rounded-lg bg-ice/10 border border-ice/30">
          <p className="text-sm text-frost">
            <strong className="text-ice">Pro Tip:</strong> Align your upgrade priorities with the weekly schedule.
            If you{"'"}re upgrading hero gear, push Land of the Brave (Mon-Tue) right after upgrading for immediate benefit.
          </p>
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
