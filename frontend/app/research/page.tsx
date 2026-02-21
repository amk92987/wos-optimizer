'use client';

import { useState } from 'react';
import PageLayout from '@/components/PageLayout';

type TabKey = 'overview' | 'growth' | 'battle' | 'economy' | 'fc-research' | 'buffs' | 'stacking-tips';

const tabs: { key: TabKey; label: string }[] = [
  { key: 'overview', label: 'Overview' },
  { key: 'growth', label: 'Growth Tree' },
  { key: 'battle', label: 'Battle Tree' },
  { key: 'economy', label: 'Economy Tree' },
  { key: 'fc-research', label: 'FC Research' },
  { key: 'buffs', label: 'Buffs & Boosts' },
  { key: 'stacking-tips', label: 'Stacking Tips' },
];

const priorityColors: Record<string, { bg: string; border: string; text: string; label: string }> = {
  critical: { bg: 'bg-red-500/10', border: 'border-red-500/30', text: 'text-red-400', label: 'CRITICAL' },
  high: { bg: 'bg-orange-500/10', border: 'border-orange-500/30', text: 'text-orange-400', label: 'Important' },
  medium: { bg: 'bg-blue-500/10', border: 'border-blue-500/30', text: 'text-blue-400', label: 'Useful' },
  low: { bg: 'bg-slate-500/10', border: 'border-slate-500/30', text: 'text-slate-400', label: 'Optional' },
};

// ─── Overview Tab ───────────────────────────────────────────────────────────

function OverviewTab() {
  return (
    <div className="space-y-6">
      <div className="card bg-gradient-to-r from-ice/10 to-transparent border-ice/30">
        <p className="text-frost">
          The <strong className="text-ice">Research Center</strong> unlocks at <strong>Furnace Level 9</strong> and
          provides permanent buffs across three trees: Growth, Battle, and Economy. Research is one of the biggest
          long-term investments in the game — the three main trees alone take <strong>~1,980 days</strong> without
          speed bonuses. With proper buff stacking, you can cut that nearly in half.
        </p>
      </div>

      {/* Three Trees Overview */}
      <div className="card">
        <h2 className="section-header">Three Research Trees</h2>
        <div className="grid md:grid-cols-3 gap-4">
          {[
            { name: 'Growth', items: 7, tiers: 'I-VII', days: 883, color: 'text-green-400', desc: 'Research speed, construction speed, training speed, healing, march queues' },
            { name: 'Battle', items: 17, tiers: 'I-VI', days: 931, color: 'text-red-400', desc: 'Troop ATK, DEF, Lethality, Health for all troops + each troop type' },
            { name: 'Economy', items: 8, tiers: 'I-VI', days: 166, color: 'text-yellow-400', desc: 'Resource output and gathering speed for Meat, Wood, Coal, Iron' },
          ].map((tree) => (
            <div key={tree.name} className="bg-surface/50 rounded-lg p-4 border border-surface-border">
              <h3 className={`font-bold text-lg ${tree.color}`}>{tree.name}</h3>
              <p className="text-frost-muted text-sm mt-1">{tree.desc}</p>
              <div className="mt-3 space-y-1 text-sm">
                <p className="text-frost"><span className="text-frost-muted">Items:</span> {tree.items}</p>
                <p className="text-frost"><span className="text-frost-muted">Tiers:</span> {tree.tiers}</p>
                <p className="text-frost"><span className="text-frost-muted">Total Time:</span> {tree.days} days (no bonuses)</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* #1 Rule */}
      <div className={`card ${priorityColors.critical.bg} border ${priorityColors.critical.border}`}>
        <div className="flex items-start gap-3">
          <span className={`text-xs font-bold uppercase ${priorityColors.critical.text} whitespace-nowrap mt-1`}>RULE #1</span>
          <div>
            <p className="font-bold text-frost text-lg">Tool Enhancement FIRST at Every Tier</p>
            <p className="text-frost-muted mt-1">
              Tool Enhancement I-VII provides <strong className="text-green-400">+27.80% research speed</strong> total.
              This is the single most important research because it accelerates everything else.
              Always max Tool Enhancement at each tier before moving to other research.
            </p>
          </div>
        </div>
      </div>

      {/* Priority Order */}
      <div className="card">
        <h2 className="section-header">Research Priority Order</h2>
        <div className="space-y-3">
          {[
            { num: '1', title: 'Tool Enhancement (at each tier)', desc: 'Research speed buff that accelerates all future research. Do this FIRST at every tier.', priority: 'critical' },
            { num: '2', title: 'Battle Tree (main troop type)', desc: 'ATK, Lethality, DEF, Health for your primary troop. Direct combat power.', priority: 'high' },
            { num: '3', title: 'Growth Tree (other items)', desc: 'Tooling Up, Trainer Tools, Command Tactics, Ward Expansion, Bandaging.', priority: 'high' },
            { num: '4', title: 'Battle Tree (secondary troops)', desc: 'Fill in other troop type stats after your main type is solid.', priority: 'medium' },
            { num: '5', title: 'Economy Tree', desc: 'Resource output and gathering. Lowest combat priority — do after Battle/Growth.', priority: 'low' },
          ].map((item) => {
            const colors = priorityColors[item.priority];
            return (
              <div key={item.num} className={`p-3 rounded-lg ${colors.bg} border ${colors.border}`}>
                <div className="flex items-start gap-3">
                  <span className={`text-lg font-bold ${colors.text}`}>#{item.num}</span>
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

      {/* Key Mechanic */}
      <div className="card">
        <h2 className="section-header">Key Mechanic: Lethality Multiplier</h2>
        <p className="text-frost-muted">
          Attack and Lethality <strong className="text-ice">multiply together</strong> in the damage formula.
          This means +10% Attack and +10% Lethality = <strong className="text-green-400">+21% total damage</strong> (not +20%).
          Always research the stat that&apos;s lower — the multiplicative effect makes balanced investment more efficient.
        </p>
      </div>
    </div>
  );
}

// ─── Growth Tree Tab ────────────────────────────────────────────────────────

const growthItems = [
  {
    name: 'Tool Enhancement', tiers: 'I-VII', effect: 'Research Speed', total: '+27.80%', priority: 'critical',
    tierData: [
      { tier: 'I', levels: 3, buffPerLevel: '+0.40%', finalLevel: '+0.50%', tierTotal: '+1.30%' },
      { tier: 'II', levels: 3, buffPerLevel: '+0.60%', finalLevel: '+1.00%', tierTotal: '+2.20%' },
      { tier: 'III', levels: 3, buffPerLevel: '+1.00%', finalLevel: '+1.00%', tierTotal: '+3.00%' },
      { tier: 'IV', levels: 3, buffPerLevel: '+1.20%', finalLevel: '+1.50%', tierTotal: '+3.90%' },
      { tier: 'V', levels: 3, buffPerLevel: '+1.60%', finalLevel: '+2.00%', tierTotal: '+5.20%' },
      { tier: 'VI', levels: 3, buffPerLevel: '+1.80%', finalLevel: '+2.50%', tierTotal: '+6.10%' },
      { tier: 'VII', levels: 3, buffPerLevel: '+1.80%', finalLevel: '+2.50%', tierTotal: '+6.10%' },
    ],
  },
  {
    name: 'Tooling Up', tiers: 'I-VII', effect: 'Construction Speed', total: '+27.80%', priority: 'high',
    tierData: [
      { tier: 'I', levels: 3, buffPerLevel: '+0.40%', finalLevel: '+0.50%', tierTotal: '+1.30%' },
      { tier: 'II', levels: 3, buffPerLevel: '+0.60%', finalLevel: '+1.00%', tierTotal: '+2.20%' },
      { tier: 'III', levels: 3, buffPerLevel: '+1.00%', finalLevel: '+1.00%', tierTotal: '+3.00%' },
      { tier: 'IV', levels: 3, buffPerLevel: '+1.20%', finalLevel: '+1.50%', tierTotal: '+3.90%' },
      { tier: 'V', levels: 3, buffPerLevel: '+1.60%', finalLevel: '+2.00%', tierTotal: '+5.20%' },
      { tier: 'VI', levels: 3, buffPerLevel: '+1.80%', finalLevel: '+2.50%', tierTotal: '+6.10%' },
      { tier: 'VII', levels: 3, buffPerLevel: '+1.80%', finalLevel: '+2.50%', tierTotal: '+6.10%' },
    ],
  },
  {
    name: 'Trainer Tools', tiers: 'I-VII', effect: 'Training Speed', total: '+202.20%', priority: 'high',
    tierData: [
      { tier: 'I', levels: 3, buffPerLevel: '+2.20%', finalLevel: '+3.00%', tierTotal: '+7.40%' },
      { tier: 'II', levels: 3, buffPerLevel: '+3.50%', finalLevel: '+5.00%', tierTotal: '+12.00%' },
      { tier: 'III', levels: 3, buffPerLevel: '+5.00%', finalLevel: '+7.00%', tierTotal: '+17.00%' },
      { tier: 'IV', levels: 3, buffPerLevel: '+7.00%', finalLevel: '+10.00%', tierTotal: '+24.00%' },
      { tier: 'V', levels: 3, buffPerLevel: '+9.00%', finalLevel: '+13.00%', tierTotal: '+31.00%' },
      { tier: 'VI', levels: 3, buffPerLevel: '+14.00%', finalLevel: '+20.00%', tierTotal: '+48.00%' },
      { tier: 'VII', levels: 3, buffPerLevel: '+18.00%', finalLevel: '+26.80%', tierTotal: '+62.80%' },
    ],
  },
  {
    name: 'Command Tactics', tiers: 'I-III', effect: 'March Queues', total: '+3', priority: 'high',
    tierData: [
      { tier: 'I', levels: 1, buffPerLevel: '+1 Queue', finalLevel: '+1 Queue', tierTotal: '+1' },
      { tier: 'II', levels: 1, buffPerLevel: '+1 Queue', finalLevel: '+1 Queue', tierTotal: '+1' },
      { tier: 'III', levels: 1, buffPerLevel: '+1 Queue', finalLevel: '+1 Queue', tierTotal: '+1' },
    ],
  },
  {
    name: 'Bandaging', tiers: 'I-VII', effect: 'Healing Speed', total: '+40.80%', priority: 'medium',
    tierData: [
      { tier: 'I', levels: 3, buffPerLevel: '+4.60%', finalLevel: '+6.00%', tierTotal: '+15.20%' },
      { tier: 'II-VII', levels: 3, buffPerLevel: 'Scaling', finalLevel: 'Higher %', tierTotal: '+25.60% combined' },
    ],
  },
  {
    name: 'Ward Expansion', tiers: 'I-VII', effect: 'Infirmary Capacity', total: '+163,300', priority: 'medium',
    tierData: [
      { tier: 'I', levels: 3, buffPerLevel: '+540', finalLevel: '+720', tierTotal: '+1,800' },
      { tier: 'II-VII', levels: 3, buffPerLevel: 'Scaling', finalLevel: 'Higher cap', tierTotal: '+161,500 combined' },
    ],
  },
  {
    name: 'Camp Expansion', tiers: 'I-VII', effect: 'Training Capacity', total: '+204', priority: 'medium',
    tierData: [
      { tier: 'I-VII', levels: 3, buffPerLevel: 'Scaling', finalLevel: 'Higher cap', tierTotal: '+204 total' },
    ],
  },
];

function GrowthTreeTab() {
  return (
    <div className="space-y-6">
      <div className="card bg-gradient-to-r from-green-500/10 to-transparent border-green-500/30">
        <p className="text-frost">
          The Growth tree has <strong>7 research items</strong> across <strong>Tiers I-VII</strong>.
          Each item has 3 levels per tier (except Command Tactics which has 1 level per tier).
          Total time: <strong className="text-green-400">883 days</strong> without speed bonuses.
        </p>
      </div>

      <div className="card">
        <h2 className="section-header text-green-400">Growth Tree Items</h2>
        <div className="space-y-3">
          {growthItems.map((item) => {
            const colors = priorityColors[item.priority];
            return (
              <details key={item.name} className={`rounded-lg ${colors.bg} border ${colors.border}`}>
                <summary className="p-3 cursor-pointer">
                  <div className="inline-flex items-center gap-3 w-full">
                    <span className={`text-xs font-bold uppercase ${colors.text}`}>{colors.label}</span>
                    <span className="font-medium text-frost flex-1">{item.name} <span className="text-frost-muted text-sm">({item.tiers})</span></span>
                    <span className="text-sm text-frost-muted">{item.effect}</span>
                    <span className="font-bold text-green-400">{item.total}</span>
                  </div>
                </summary>
                <div className="px-3 pb-3 pt-1">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-frost-muted border-b border-surface-border">
                        <th className="text-left py-1 pr-3">Tier</th>
                        <th className="text-left py-1 pr-3">Levels</th>
                        <th className="text-left py-1 pr-3">Per Level</th>
                        <th className="text-left py-1 pr-3">Final Level</th>
                        <th className="text-right py-1">Tier Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {item.tierData.map((td) => (
                        <tr key={td.tier} className="border-b border-surface-border/30">
                          <td className="py-1 pr-3 text-frost">{td.tier}</td>
                          <td className="py-1 pr-3 text-frost-muted">{td.levels}</td>
                          <td className="py-1 pr-3 text-frost-muted">{td.buffPerLevel}</td>
                          <td className="py-1 pr-3 text-green-400">{td.finalLevel}</td>
                          <td className="py-1 text-right font-medium text-frost">{td.tierTotal}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  <p className="text-xs text-frost-muted mt-2 italic">
                    Pattern: Early levels give a smaller buff, final level of each tier gives a larger bonus.
                  </p>
                </div>
              </details>
            );
          })}
        </div>
      </div>

      {/* Growth Tree Tip */}
      <div className={`card ${priorityColors.high.bg} border ${priorityColors.high.border}`}>
        <div className="flex items-start gap-3">
          <span className={`text-xs font-bold uppercase ${priorityColors.high.text} whitespace-nowrap mt-1`}>TIP</span>
          <p className="text-frost-muted">
            Growth tree has a <strong className="text-frost">dependency chain</strong>: Tool Enhancement requires
            Ward Expansion + Camp Expansion at the same tier. So you&apos;ll need to keep those close to the same
            tier to unlock Tool Enhancement.
          </p>
        </div>
      </div>
    </div>
  );
}

// ─── Battle Tree Tab ────────────────────────────────────────────────────────

function BattleTreeTab() {
  return (
    <div className="space-y-6">
      <div className="card bg-gradient-to-r from-red-500/10 to-transparent border-red-500/30">
        <p className="text-frost">
          The Battle tree has <strong>17 research items</strong> across <strong>Tiers I-VI</strong> —
          5 &quot;All Troops&quot; items and 12 troop-specific items (4 stats &times; 3 types).
          Total time: <strong className="text-red-400">931 days</strong> without speed bonuses.
          Levels per tier escalate: 3 &rarr; 3 &rarr; 4 &rarr; 5 &rarr; 6 &rarr; 6.
        </p>
      </div>

      {/* All Troops */}
      <div className="card">
        <h2 className="section-header text-red-400">All Troops (Universal)</h2>
        <p className="text-frost-muted text-sm mb-4">These buff Infantry, Marksman, and Lancer equally.</p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-frost-muted border-b border-surface-border">
                <th className="text-left py-2 pr-3">Research</th>
                <th className="text-left py-2 pr-3">Stat</th>
                <th className="text-right py-2">Grand Total</th>
              </tr>
            </thead>
            <tbody>
              {[
                { name: 'Weapons Prep', stat: 'All Troops Attack', total: '+47.25%' },
                { name: 'Special Defensive Training', stat: 'All Troops Defense', total: '+47.25%' },
                { name: 'Assault Techniques', stat: 'All Troops Lethality', total: '+47.25%' },
                { name: 'Survival Techniques', stat: 'All Troops Health', total: '+47.25%' },
                { name: 'Regimental Expansion', stat: 'Deployment Capacity', total: 'Up to +13,480' },
              ].map((item) => (
                <tr key={item.name} className="border-b border-surface-border/30">
                  <td className="py-2 pr-3 font-medium text-frost">{item.name}</td>
                  <td className="py-2 pr-3 text-frost-muted">{item.stat}</td>
                  <td className="py-2 text-right font-bold text-red-400">{item.total}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Tier escalation */}
      <div className="card">
        <h2 className="section-header">Battle Tier Progression</h2>
        <p className="text-frost-muted text-sm mb-3">Battle tiers have increasing numbers of levels — later tiers take dramatically longer.</p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-frost-muted border-b border-surface-border">
                <th className="text-left py-2 pr-3">Tier</th>
                <th className="text-center py-2 pr-3">Levels</th>
                <th className="text-left py-2 pr-3">Per-Level Buff (Troop-Specific)</th>
                <th className="text-left py-2 pr-3">Final Level Buff</th>
                <th className="text-left py-2">Time Range</th>
              </tr>
            </thead>
            <tbody>
              {[
                { tier: 'I', levels: 3, buff: '+1.25%', final: '+1.50%', time: '1 min - 14 min' },
                { tier: 'II', levels: 3, buff: '+1.25%', final: '+1.50%', time: '2 min - 20 min' },
                { tier: 'III', levels: 4, buff: 'varies', final: 'higher', time: '30 min - 3 hours' },
                { tier: 'IV', levels: 5, buff: '+1.75%', final: '+3.00%', time: '14 hours - 4.5 days' },
                { tier: 'V', levels: 6, buff: '+2.00%', final: '+3.50%', time: '2 days - 16 days' },
                { tier: 'VI', levels: 6, buff: '+5.50%', final: '+9.00%', time: '18 days - 90 days' },
              ].map((t) => (
                <tr key={t.tier} className="border-b border-surface-border/30">
                  <td className="py-2 pr-3 font-medium text-frost">Tier {t.tier}</td>
                  <td className="py-2 pr-3 text-center text-frost-muted">{t.levels}</td>
                  <td className="py-2 pr-3 text-frost-muted">{t.buff}</td>
                  <td className="py-2 pr-3 text-green-400">{t.final}</td>
                  <td className="py-2 text-frost-muted">{t.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-red-400/80 mt-2 italic">
          Tier VI Level 6 alone can take 90+ days. These are endgame research goals.
        </p>
      </div>

      {/* Troop-Specific */}
      <div className="card">
        <h2 className="section-header text-red-400">Troop-Specific Research</h2>
        <p className="text-frost-muted text-sm mb-4">
          Each troop type has 4 stats with <strong className="text-frost">+111.75%</strong> grand total each.
          Research your <strong className="text-ice">main troop type first</strong> before touching others.
        </p>
        <div className="grid md:grid-cols-3 gap-4">
          {[
            {
              type: 'Infantry', color: 'text-red-400', borderColor: 'border-red-500/30',
              items: [
                { name: 'Reprisal Tactics', stat: 'Attack' },
                { name: 'Defensive Formation', stat: 'Defense' },
                { name: 'Close Combat', stat: 'Lethality' },
                { name: 'Shield Upgrade', stat: 'Health' },
              ],
            },
            {
              type: 'Marksman', color: 'text-blue-400', borderColor: 'border-blue-500/30',
              items: [
                { name: 'Precision Targeting', stat: 'Attack' },
                { name: 'Picket Lines', stat: 'Defense' },
                { name: 'Targeted Sniping', stat: 'Lethality' },
                { name: 'Marksman Armor', stat: 'Health' },
              ],
            },
            {
              type: 'Lancer', color: 'text-green-400', borderColor: 'border-green-500/30',
              items: [
                { name: 'Skirmishing', stat: 'Attack' },
                { name: 'Bulwark Formations', stat: 'Defense' },
                { name: 'Lancer Upgrade', stat: 'Lethality' },
                { name: 'Lancer Armor', stat: 'Health' },
              ],
            },
          ].map((troop) => (
            <div key={troop.type} className={`bg-surface/50 rounded-lg p-4 border ${troop.borderColor}`}>
              <h3 className={`font-bold ${troop.color} mb-3`}>{troop.type}</h3>
              <div className="space-y-2">
                {troop.items.map((item) => (
                  <div key={item.name} className="flex justify-between text-sm">
                    <span className="text-frost-muted">{item.name}</span>
                    <span className="text-frost">{item.stat}</span>
                  </div>
                ))}
                <div className="border-t border-surface-border pt-2 mt-2">
                  <div className="flex justify-between text-sm font-medium">
                    <span className="text-frost">Each stat total:</span>
                    <span className={troop.color}>+111.75%</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Battle Tree dependency */}
      <div className="card">
        <h2 className="section-header">Battle Tree Dependency Chain</h2>
        <p className="text-frost-muted text-sm mb-3">Research unlocks follow this order within each tier:</p>
        <div className="bg-surface/50 rounded-lg p-4 text-sm font-mono text-frost-muted space-y-1">
          <p>Weapons Prep <span className="text-ice">(All ATK)</span></p>
          <p className="pl-4">&rarr; Troop-Specific ATK &rarr; Troop-Specific DEF</p>
          <p className="pl-8">&rarr; Special Defensive Training <span className="text-ice">(All DEF)</span></p>
          <p className="pl-12">&rarr; Assault Techniques <span className="text-ice">(All Lethality)</span></p>
          <p className="pl-16">&rarr; Troop-Specific Lethality</p>
          <p className="pl-12">&rarr; Survival Techniques <span className="text-ice">(All Health)</span></p>
          <p className="pl-16">&rarr; Troop-Specific Health</p>
          <p className="pl-20">&rarr; Regimental Expansion <span className="text-ice">(Deployment)</span></p>
        </div>
      </div>
    </div>
  );
}

// ─── Economy Tree Tab ───────────────────────────────────────────────────────

function EconomyTreeTab() {
  return (
    <div className="space-y-6">
      <div className="card bg-gradient-to-r from-yellow-500/10 to-transparent border-yellow-500/30">
        <p className="text-frost">
          The Economy tree has <strong>8 items</strong> across <strong>Tiers I-VI</strong> (3 levels per tier).
          Total time: <strong className="text-yellow-400">166 days</strong> without speed bonuses — the shortest tree.
          <span className="text-frost-muted"> Lowest priority for combat-focused players.</span>
        </p>
      </div>

      {/* Output Items */}
      <div className="card">
        <h2 className="section-header text-yellow-400">Resource Output</h2>
        <p className="text-frost-muted text-sm mb-4">Increase production from your city buildings.</p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-frost-muted border-b border-surface-border">
                <th className="text-left py-2 pr-3">Research</th>
                <th className="text-left py-2 pr-3">Building</th>
                <th className="text-left py-2 pr-3">Tiers</th>
                <th className="text-right py-2">Grand Total</th>
              </tr>
            </thead>
            <tbody>
              {[
                { name: 'Meat Output', building: "Hunter's Hut", tiers: 'I-VI', total: '+119.50%' },
                { name: 'Wood Output', building: 'Sawmill', tiers: 'I-VI', total: '+119.50%' },
                { name: 'Coal Output', building: 'Coal Mine', tiers: 'I-VI', total: '+119.50%' },
                { name: 'Iron Output', building: 'Ironworks', tiers: 'I-VI', total: '+116.00%' },
              ].map((item) => (
                <tr key={item.name} className="border-b border-surface-border/30">
                  <td className="py-2 pr-3 font-medium text-frost">{item.name}</td>
                  <td className="py-2 pr-3 text-frost-muted">{item.building}</td>
                  <td className="py-2 pr-3 text-frost-muted">{item.tiers}</td>
                  <td className="py-2 text-right font-bold text-yellow-400">{item.total}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Gathering Items */}
      <div className="card">
        <h2 className="section-header text-yellow-400">Gathering Speed</h2>
        <p className="text-frost-muted text-sm mb-4">Increase speed when gathering resources on the world map.</p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-frost-muted border-b border-surface-border">
                <th className="text-left py-2 pr-3">Research</th>
                <th className="text-left py-2 pr-3">Resource</th>
                <th className="text-left py-2 pr-3">Tiers</th>
                <th className="text-right py-2">Grand Total</th>
              </tr>
            </thead>
            <tbody>
              {[
                { name: 'Food Gathering', resource: 'Meat', tiers: 'I-VI', total: '+242.50%' },
                { name: 'Wood Gathering', resource: 'Wood', tiers: 'I-VI', total: '+242.50%' },
                { name: 'Coal Mining', resource: 'Coal', tiers: 'I-VI', total: '+242.50%' },
                { name: 'Iron Mining', resource: 'Iron', tiers: 'I-VI', total: '+242.50%' },
              ].map((item) => (
                <tr key={item.name} className="border-b border-surface-border/30">
                  <td className="py-2 pr-3 font-medium text-frost">{item.name}</td>
                  <td className="py-2 pr-3 text-frost-muted">{item.resource}</td>
                  <td className="py-2 pr-3 text-frost-muted">{item.tiers}</td>
                  <td className="py-2 text-right font-bold text-yellow-400">{item.total}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Economy Tips */}
      <div className="card">
        <h2 className="section-header">Economy Tree Tips</h2>
        <div className="space-y-3">
          {[
            { priority: 'high', title: 'Farm Accounts Benefit Most', desc: 'Economy research is more valuable on farm accounts that focus on resource gathering. Main accounts should prioritize Battle tree.' },
            { priority: 'medium', title: 'Output Before Gathering', desc: 'Resource Output unlocks before Gathering at each tier. Output boosts passive city production, Gathering boosts world map collection.' },
            { priority: 'medium', title: 'Unlock Order: Meat/Wood First', desc: 'Resources unlock in order: Meat/Wood first, then Coal, then Iron. Each requires the previous tier.' },
          ].map((tip, i) => {
            const colors = priorityColors[tip.priority];
            return (
              <div key={i} className={`p-3 rounded-lg ${colors.bg} border ${colors.border}`}>
                <div className="flex items-start gap-3">
                  <span className={`text-xs font-bold uppercase ${colors.text} whitespace-nowrap mt-0.5`}>{colors.label}</span>
                  <div>
                    <p className="font-medium text-frost">{tip.title}</p>
                    <p className="text-sm text-frost-muted mt-1">{tip.desc}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// ─── FC Research Tab ────────────────────────────────────────────────────────

function FCResearchTab() {
  return (
    <div className="space-y-6">
      <div className="card bg-gradient-to-r from-purple-500/10 to-transparent border-purple-500/30">
        <p className="text-frost">
          FC Research unlocks at <strong>Furnace 30 (FC1)</strong> via the <strong>War Academy</strong>.
          Uses <strong className="text-purple-400">Fire Crystal Shards</strong> as additional currency.
          Each troop type has 7 research lines taking <strong>~271 days</strong> total.
          Focus your <strong>main troop type first</strong>.
        </p>
      </div>

      {/* Shared Items */}
      <div className="card">
        <h2 className="section-header text-purple-400">Shared Research</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-frost-muted border-b border-surface-border">
                <th className="text-left py-2 pr-3">Research</th>
                <th className="text-center py-2 pr-3">Levels</th>
                <th className="text-left py-2 pr-3">Effect</th>
                <th className="text-right py-2">Grand Total</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-surface-border/30">
                <td className="py-2 pr-3 font-medium text-frost">Flame Squad</td>
                <td className="py-2 pr-3 text-center text-frost-muted">5</td>
                <td className="py-2 pr-3 text-frost-muted">Deployment Capacity</td>
                <td className="py-2 text-right font-bold text-purple-400">+1,000</td>
              </tr>
              <tr className="border-b border-surface-border/30">
                <td className="py-2 pr-3 font-medium text-frost">Flame Legion</td>
                <td className="py-2 pr-3 text-center text-frost-muted">12</td>
                <td className="py-2 pr-3 text-frost-muted">Rally Capacity</td>
                <td className="py-2 text-right font-bold text-purple-400">+30,000+</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Per-Troop Research */}
      <div className="card">
        <h2 className="section-header text-purple-400">Per-Troop Research Lines</h2>
        <p className="text-frost-muted text-sm mb-4">
          Each troop type (Infantry, Marksman, Lancer) has identical research lines with different names.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-frost-muted border-b border-surface-border">
                <th className="text-left py-2 pr-3">Research Line</th>
                <th className="text-center py-2 pr-3">Levels</th>
                <th className="text-left py-2 pr-3">Effect</th>
                <th className="text-right py-2">Total Per Type</th>
              </tr>
            </thead>
            <tbody>
              {[
                { line: 'Attack', levels: 12, effect: 'Troop Attack', total: '+39.00%', names: 'Flame Tomahawk / Crystal Arrow / Blazing Lance' },
                { line: 'Defense', levels: 12, effect: 'Troop Defense', total: '+39.00%', names: 'Flame Protection / Crystal Protection / Blazing Guardian' },
                { line: 'Lethality', levels: 8, effect: 'Troop Lethality', total: '+25.00%', names: 'Flame Strike / Crystal Vision / Blazing Charge' },
                { line: 'Health', levels: 8, effect: 'Troop Health', total: '+25.00%', names: 'Flame Shield / Crystal Armor / Blazing Armor' },
                { line: 'T11 Unlock', levels: 1, effect: 'Unlocks T11 Troops', total: '91 days', names: 'Helios Infantry / Marksman / Lancer' },
                { line: 'First Aid', levels: 10, effect: 'Heal Time & Defense', total: '-15% Heal, +20% DEF', names: 'Helios First Aid (per type)' },
                { line: 'Training', levels: 10, effect: 'Training Cost & Deploy', total: '-50% Cost, +1K Deploy', names: 'Helios Training (per type)' },
              ].map((item) => (
                <tr key={item.line} className="border-b border-surface-border/30">
                  <td className="py-2 pr-3">
                    <p className="font-medium text-frost">{item.line}</p>
                    <p className="text-xs text-frost-muted">{item.names}</p>
                  </td>
                  <td className="py-2 pr-3 text-center text-frost-muted">{item.levels}</td>
                  <td className="py-2 pr-3 text-frost-muted">{item.effect}</td>
                  <td className="py-2 text-right font-bold text-purple-400">{item.total}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* FC Research Tip */}
      <div className={`card ${priorityColors.critical.bg} border ${priorityColors.critical.border}`}>
        <div className="flex items-start gap-3">
          <span className={`text-xs font-bold uppercase ${priorityColors.critical.text} whitespace-nowrap mt-1`}>TIP</span>
          <div>
            <p className="font-medium text-frost">Helios T11 Unlock: 91 Days Single Research</p>
            <p className="text-sm text-frost-muted mt-1">
              The T11 troop unlock is one of the longest single research items in the game.
              This is where buff stacking is critical — stack every research speed buff you can before starting it.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Buffs & Boosts Tab ─────────────────────────────────────────────────────

function BuffsTab() {
  return (
    <div className="space-y-6">
      {/* Chief's House */}
      <div className="card">
        <h2 className="section-header text-yellow-400">Chief&apos;s House Orders</h2>
        <p className="text-frost-muted text-sm mb-4">
          Unlocks at <strong className="text-frost">Furnace Level 6</strong>. Provides 6 orders using <strong>Contentment</strong> currency.
          (50,000 Contentment = 50 Gems)
        </p>
        <div className="space-y-3">
          {[
            { name: 'Double Time', effect: '-20% construction time for builds started within 5 min', cost: '800K', cooldown: '24h', side: null, priority: 'critical' },
            { name: 'Productivity Day', effect: '+100% resource output for 24h (Survivor Time)', cost: '50K', cooldown: '12h', side: '-10 Mood', priority: 'high' },
            { name: 'Rush Job', effect: 'Instant 5 days of resources from all worksites', cost: '150K', cooldown: '24h', side: null, priority: 'high' },
            { name: 'Urgent Mobilization', effect: 'Force all survivors to work 48h straight', cost: '50K', cooldown: '8h', side: '-10 Mood', priority: 'medium' },
            { name: 'Comprehensive Care', effect: 'Instantly heal all sick survivors', cost: '150K', cooldown: '4h', side: null, priority: 'medium' },
            { name: 'Festivities', effect: '+50 Mood, +30 Comfort', cost: '50K', cooldown: '24h', side: 'Survivors stop working', priority: 'low' },
          ].map((order) => {
            const colors = priorityColors[order.priority];
            return (
              <div key={order.name} className={`p-3 rounded-lg ${colors.bg} border ${colors.border}`}>
                <div className="flex flex-col sm:flex-row sm:items-center gap-2">
                  <div className="flex-1">
                    <p className="font-medium text-frost">{order.name}</p>
                    <p className="text-sm text-frost-muted">{order.effect}</p>
                  </div>
                  <div className="flex gap-3 text-xs text-frost-muted whitespace-nowrap">
                    <span>Cost: <span className="text-frost">{order.cost}</span></span>
                    <span>CD: <span className="text-frost">{order.cooldown}</span></span>
                    {order.side && <span className="text-red-400">{order.side}</span>}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* President Appointments */}
      <div className="card">
        <h2 className="section-header text-purple-400">President Appointments</h2>
        <p className="text-frost-muted text-sm mb-4">
          6 Minister positions with personal buffs. Requires <strong>Furnace 16+</strong> to apply.
          Supreme President gets boosted values shown in parentheses.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-frost-muted border-b border-surface-border">
                <th className="text-left py-2 pr-3">Position</th>
                <th className="text-left py-2">Buffs (Supreme)</th>
              </tr>
            </thead>
            <tbody>
              {[
                { position: 'Vice President', buffs: '+10% Construction, Research, Training Speed (+15%)' },
                { position: 'Minister of Interior', buffs: '+80% Resource Production (+120%)' },
                { position: 'Minister of Health', buffs: '+100% Healing Speed, +5K Infirmary (+150%, +7.5K)' },
                { position: 'Minister of Defense', buffs: '+10% Troop Lethality (+15%)' },
                { position: 'Minister of Strategy', buffs: '+5% Troop ATK, +2.5K Deploy (+8%, +3.75K)' },
                { position: 'Minister of Education', buffs: '+50% Training Speed, +200 Capacity (+75%, +300)' },
              ].map((m) => (
                <tr key={m.position} className="border-b border-surface-border/30">
                  <td className="py-2 pr-3 font-medium text-frost whitespace-nowrap">{m.position}</td>
                  <td className="py-2 text-frost-muted">{m.buffs}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Presidential Skills */}
      <div className="card">
        <h2 className="section-header text-purple-400">Presidential State-Wide Skills</h2>
        <p className="text-frost-muted text-sm mb-4">
          State-wide buffs activated by the President. <strong>24h duration</strong>, <strong>~7 day cooldown</strong>, costs 45K Authority each.
        </p>
        <div className="grid md:grid-cols-2 gap-3">
          {[
            { name: 'Mobilize', effect: '+30% Training Speed', color: 'text-green-400' },
            { name: 'Mercantilism', effect: '+10% Construction Speed', color: 'text-yellow-400' },
            { name: 'Research Advancement', effect: '+10% Research Speed', color: 'text-blue-400' },
            { name: 'Medical Advancement', effect: '+50% Healing Speed', color: 'text-red-400' },
          ].map((skill) => (
            <div key={skill.name} className="bg-surface/50 rounded-lg p-3 border border-surface-border">
              <p className="font-medium text-frost">{skill.name}</p>
              <p className={`text-sm ${skill.color}`}>{skill.effect}</p>
              <p className="text-xs text-frost-muted mt-1">24h duration, ~7d cooldown</p>
            </div>
          ))}
        </div>
      </div>

      {/* Supreme President */}
      <div className="card bg-gradient-to-r from-purple-500/10 to-transparent border-purple-500/30">
        <h3 className="font-bold text-purple-400 mb-2">Supreme President Personal Buff</h3>
        <p className="text-frost-muted text-sm mb-2">
          When one state wins <strong>both phases</strong> of SvS, the President becomes Supreme President and gains:
        </p>
        <div className="flex flex-wrap gap-3">
          {['Attack', 'Defense', 'Lethality', 'Health'].map((stat) => (
            <span key={stat} className="bg-purple-500/20 text-purple-400 px-3 py-1 rounded text-sm font-medium">
              +7.5% Troop {stat}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Stacking Tips Tab ──────────────────────────────────────────────────────

function StackingTipsTab() {
  return (
    <div className="space-y-6">
      <div className="card bg-gradient-to-r from-fire/10 to-transparent border-fire/30">
        <p className="text-frost">
          The single biggest efficiency trick in WoS: <strong className="text-fire">stack your buffs before using speedups</strong>.
          A 50-day research can drop to 26 days by combining research speed bonuses, presidential skills,
          VP appointment, VIP, and Alliance Tech. Timing is everything.
        </p>
      </div>

      {/* Research Speed Stacking */}
      <div className="card">
        <h2 className="section-header text-ice">Research Speed Sources</h2>
        <p className="text-frost-muted text-sm mb-4">All sources that reduce research time. Stack as many as possible before starting big research.</p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-frost-muted border-b border-surface-border">
                <th className="text-left py-2 pr-3">Source</th>
                <th className="text-left py-2 pr-3">Type</th>
                <th className="text-right py-2 pr-3">Bonus</th>
                <th className="text-left py-2">Notes</th>
              </tr>
            </thead>
            <tbody>
              {[
                { source: 'Tool Enhancement VII', type: 'Permanent', bonus: '+27.80%', notes: 'Research tree — do this first' },
                { source: 'VIP 12', type: 'Permanent', bonus: '+35%', notes: 'VIP level — passive' },
                { source: 'Alliance Tech', type: 'Permanent', bonus: 'Up to +30%', notes: 'Alliance must research it' },
                { source: 'VP Appointment', type: 'While held', bonus: '+10-15%', notes: 'Personal buff for VP holder' },
                { source: 'Research Advancement', type: '24h', bonus: '+10%', notes: 'Presidential skill, ~7d cooldown' },
                { source: 'Speed Items', type: 'Temporary', bonus: '+10-50%', notes: 'Consumable buff items' },
              ].map((row) => (
                <tr key={row.source} className="border-b border-surface-border/30">
                  <td className="py-2 pr-3 font-medium text-frost">{row.source}</td>
                  <td className="py-2 pr-3 text-frost-muted">{row.type}</td>
                  <td className="py-2 pr-3 text-right text-green-400 font-medium">{row.bonus}</td>
                  <td className="py-2 text-frost-muted text-xs">{row.notes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Construction Speed Stacking */}
      <div className="card">
        <h2 className="section-header text-yellow-400">Construction Speed Sources</h2>
        <p className="text-frost-muted text-sm mb-4">All confirmed to stack additively (20% + 15% = 35%).</p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-frost-muted border-b border-surface-border">
                <th className="text-left py-2 pr-3">Source</th>
                <th className="text-left py-2 pr-3">Type</th>
                <th className="text-right py-2 pr-3">Bonus</th>
                <th className="text-left py-2">Notes</th>
              </tr>
            </thead>
            <tbody>
              {[
                { source: 'Tooling Up VII', type: 'Permanent', bonus: '+27.80%', notes: 'Research tree' },
                { source: 'Double Time (Chief Order)', type: '5-min window', bonus: '-20%', notes: '800K Contentment, 24h cooldown' },
                { source: 'Cave Hyena (Pet)', type: '5-min window', bonus: '+15%', notes: 'Activate before building' },
                { source: 'Zinman (Hero)', type: 'Permanent', bonus: '+15%', notes: 'Gen 1 hero skill' },
                { source: 'VIP 12', type: 'Permanent', bonus: '+35%', notes: 'VIP level' },
                { source: 'VP Appointment', type: 'While held', bonus: '+10-15%', notes: 'Personal buff' },
                { source: 'Mercantilism', type: '24h', bonus: '+10%', notes: 'Presidential skill' },
                { source: 'Alliance Tech', type: 'Permanent', bonus: 'Up to +5%', notes: 'Adaptive Tools' },
              ].map((row) => (
                <tr key={row.source} className="border-b border-surface-border/30">
                  <td className="py-2 pr-3 font-medium text-frost">{row.source}</td>
                  <td className="py-2 pr-3 text-frost-muted">{row.type}</td>
                  <td className="py-2 pr-3 text-right text-green-400 font-medium">{row.bonus}</td>
                  <td className="py-2 text-frost-muted text-xs">{row.notes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* When to Stack */}
      <div className="card">
        <h2 className="section-header text-fire">When to Stack Buffs</h2>
        <div className="space-y-3">
          {[
            {
              priority: 'critical',
              title: 'Before Starting Long Research (Tier V+)',
              desc: 'Wait for Presidential "Research Advancement" (+10%) before starting any 20+ day research. Ask your President to activate it. Time your VIP boost and VP appointment too.',
            },
            {
              priority: 'critical',
              title: 'SvS Prep Days',
              desc: 'Presidents typically activate state-wide skills during SvS events. This is the best time to start big research, use training speedups, and begin construction. Coordinate with your alliance.',
            },
            {
              priority: 'high',
              title: 'Before Using Speedups',
              desc: 'Speedups reduce the REMAINING time. If you reduce the base time first (via buffs), then use speedups, you save more total time. Always buff first, speedup second.',
            },
            {
              priority: 'high',
              title: 'Before Big Construction',
              desc: 'Activate Double Time (Chief Order) + Cave Hyena (Pet) within 5 minutes of starting. Both have 5-minute activation windows. Combined 35% reduction.',
            },
            {
              priority: 'medium',
              title: 'Resource Gathering Days',
              desc: 'Stack Productivity Day + Urgent Mobilization from Chief\'s House when you need resources. Use Minister of Interior buff (+80% production) if available.',
            },
          ].map((tip, i) => {
            const colors = priorityColors[tip.priority];
            return (
              <div key={i} className={`p-3 rounded-lg ${colors.bg} border ${colors.border}`}>
                <div className="flex items-start gap-3">
                  <span className={`text-xs font-bold uppercase ${colors.text} whitespace-nowrap mt-0.5`}>{colors.label}</span>
                  <div>
                    <p className="font-medium text-frost">{tip.title}</p>
                    <p className="text-sm text-frost-muted mt-1">{tip.desc}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Checklists */}
      <div className="card">
        <h2 className="section-header">Pre-Activity Checklists</h2>
        <div className="grid md:grid-cols-2 gap-4">
          {[
            {
              title: 'Before Big Research',
              color: 'text-blue-400',
              borderColor: 'border-blue-500/30',
              items: [
                'Max Tool Enhancement at current tier',
                'Check VIP level (higher = faster)',
                'Request VP appointment if available',
                'Wait for Presidential Research Advancement',
                'Use research speed buff items',
                'Then start research + use speedups',
              ],
            },
            {
              title: 'Before Big Construction',
              color: 'text-yellow-400',
              borderColor: 'border-yellow-500/30',
              items: [
                'Activate Double Time (Chief Order)',
                'Activate Cave Hyena pet skill',
                'Request VP appointment if available',
                'Wait for Presidential Mercantilism',
                'Start build within 5-minute window',
                'Then use construction speedups',
              ],
            },
            {
              title: 'Before Mass Training',
              color: 'text-green-400',
              borderColor: 'border-green-500/30',
              items: [
                'Wait for Presidential Mobilize (+30%)',
                'Education Minister buff (+50-75%)',
                'Max Trainer Tools at current tier',
                'Use training speed buff items',
                'Start all training queues',
                'Then use training speedups',
              ],
            },
            {
              title: 'Before Mass Healing',
              color: 'text-red-400',
              borderColor: 'border-red-500/30',
              items: [
                'Wait for Presidential Medical Advancement',
                'Health Minister buff (+100-150%)',
                'Max Bandaging at current tier',
                'Use healing speed buff items',
                'Start healing queues',
                'Then use healing speedups',
              ],
            },
          ].map((checklist) => (
            <div key={checklist.title} className={`bg-surface/50 rounded-lg p-4 border ${checklist.borderColor}`}>
              <h3 className={`font-bold ${checklist.color} mb-3`}>{checklist.title}</h3>
              <ul className="space-y-2">
                {checklist.items.map((item, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-frost-muted">
                    <span className="text-frost-muted/50 mt-0.5">{i + 1}.</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Real Example */}
      <div className="card bg-gradient-to-r from-green-500/10 to-transparent border-green-500/30">
        <h3 className="font-bold text-green-400 mb-2">Real Example: 50 Days &rarr; 26 Days</h3>
        <p className="text-frost-muted text-sm">
          By stacking Tool Enhancement, VIP, Alliance Tech, VP Appointment, Presidential Research Advancement,
          and research speed items, a 50-day research was cut to just 26 days — <strong className="text-green-400">nearly half</strong>.
          The key is patience: wait for the right moment when all buffs align before starting the timer and using speedups.
        </p>
      </div>
    </div>
  );
}

// ─── Main Page ──────────────────────────────────────────────────────────────

export default function ResearchGuidePage() {
  const [activeTab, setActiveTab] = useState<TabKey>('overview');

  return (
    <PageLayout>
      <h1 className="text-2xl font-bold text-frost mb-1">Research & Buffs</h1>
      <p className="text-frost-muted text-sm mb-6">Research Center guide, buff sources, and stacking strategies</p>

      {/* Tab bar */}
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

      {/* Tab content */}
      {activeTab === 'overview' && <OverviewTab />}
      {activeTab === 'growth' && <GrowthTreeTab />}
      {activeTab === 'battle' && <BattleTreeTab />}
      {activeTab === 'economy' && <EconomyTreeTab />}
      {activeTab === 'fc-research' && <FCResearchTab />}
      {activeTab === 'buffs' && <BuffsTab />}
      {activeTab === 'stacking-tips' && <StackingTipsTab />}
    </PageLayout>
  );
}
