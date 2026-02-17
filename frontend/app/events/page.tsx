'use client';

import { useState, useEffect, useMemo } from 'react';
import PageLayout from '@/components/PageLayout';
import { eventsApi } from '@/lib/api';

interface EventReward {
  primary: string[];
  quality?: string;
  backpack_items?: string[];
}

interface EventPreparation {
  save_before?: string[];
  heroes_needed?: string;
  tips?: string[];
  key_heroes?: string[];
}

interface TroopRatio {
  infantry: string;
  lancer: string;
  marksman: string;
  reasoning: string;
}

interface Event {
  name: string;
  type: string;
  frequency: string;
  duration?: string;
  cost_category: string;
  priority: string;
  description: string;
  gameplay?: string;
  rewards: EventReward;
  preparation?: EventPreparation;
  troop_ratio?: TroopRatio | { leader: TroopRatio; joiner: TroopRatio };
  f2p_friendly: boolean | string;
  notes?: string;
  wave_mechanics?: Record<string, string>;
  phases?: Record<string, any>;
  mechanics?: Record<string, string>;
  intel_strategy?: any;
  spending_priority?: any;
  daily_stages?: any;
  victory_points?: any;
  star_system?: any;
  tundra_trade_route?: any;
  medal_system?: any;
  f2p_strategy?: any;
  fuel_management?: any;
  phase_strategy?: Record<string, string>;
  scoring?: any;
  structure?: any;
  stamina_costs?: any;
  stat_bonuses?: any;
  alternative_ratios?: any[];
  eligibility?: any;
  zones?: string[];
  ranking_tiers?: any;
}

interface EventsGuide {
  cost_categories: Record<string, { label: string; description: string; color: string }>;
  priority_tiers: Record<string, { label: string; description: string }>;
  events: Record<string, Event>;
  resource_saving_guide?: Record<string, { save_for: string[]; tip: string }>;
}

// Event categories for filtering
const EVENT_CATEGORIES = {
  all: { label: 'All Events', description: 'All events sorted by priority' },
  alliance_pve: {
    label: 'Alliance PvE',
    description: 'Alliance rallies against PvE bosses',
    events: ['bear_trap', 'crazy_joe', 'mercenary_prestige', 'frostdragon_tyrant', 'labyrinth', 'frostfire_mine']
  },
  pvp_svs: {
    label: 'PvP / SvS',
    description: 'State vs State and alliance combat',
    events: ['svs_prep', 'svs_battle', 'alliance_showdown', 'king_of_icefield', 'canyon_clash', 'foundry_battle', 'brother_in_arms', 'alliance_championship', 'tundra_arms_league']
  },
  growth: {
    label: 'Growth',
    description: 'Power growth and progression',
    events: ['hall_of_chiefs', 'hero_rally', 'flame_and_fang', 'tundra_album']
  },
  solo_gacha: {
    label: 'Solo / Gacha',
    description: 'Individual rewards and draws',
    events: ['lucky_wheel', 'artisans_trove', 'flame_lotto', 'mix_and_match', 'treasure_hunter', 'tundra_trading', 'snowbusters', 'fishing_tournament']
  }
};

const PRIORITY_ORDER: Record<string, number> = { 'S': 0, 'A': 1, 'B': 2, 'C': 3, 'D': 4 };

// --- Collapsible Section Component ---
function Expander({ title, defaultOpen = false, children }: { title: string; defaultOpen?: boolean; children: React.ReactNode }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border border-surface-border rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-3 bg-surface hover:bg-surface-hover transition-colors text-left"
      >
        <span className="font-medium text-frost text-sm">{title}</span>
        <svg className={`w-4 h-4 text-frost-muted transition-transform ${open ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && <div className="p-3 border-t border-surface-border">{children}</div>}
    </div>
  );
}

// --- Helper: get event name from ID ---
function getEventName(eventId: string, eventsGuide: EventsGuide | null): string {
  if (eventsGuide?.events?.[eventId]?.name) return eventsGuide.events[eventId].name;
  return eventId.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// --- Intel Strategy Timeline (Flame and Fang) ---
function IntelStrategyTimeline({ intelStrategy }: { intelStrategy: any }) {
  const timeline = intelStrategy.timeline || [];
  const normalTotal = intelStrategy.normal_total || 168;
  const trickTotal = intelStrategy.with_trick_total || 184;
  const refreshTimes = intelStrategy.refresh_times || [];

  const getStepStyles = (type: string) => {
    switch (type) {
      case 'warning': return { border: 'border-2 border-red-500 bg-red-500/10', timeColor: 'text-red-400', actionColor: 'text-red-400 font-bold' };
      case 'claim': return { border: 'border-2 border-green-500 bg-green-500/10', timeColor: 'text-green-400', actionColor: 'text-green-400 font-bold' };
      case 'final': return { border: 'border-2 border-amber-400 bg-amber-400/10', timeColor: 'text-amber-400', actionColor: 'text-amber-400 font-bold' };
      default: return { border: 'border-l-4 border-l-blue-500 bg-blue-500/5', timeColor: 'text-blue-400', actionColor: 'text-frost-muted' };
    }
  };

  return (
    <div className="space-y-4">
      {/* Header comparison */}
      <div className="p-5 rounded-xl border-2 border-amber-500 bg-gradient-to-r from-red-500/10 to-green-500/10">
        <h4 className="text-center text-amber-400 font-bold text-lg mb-2">The Extra 16 Cores Trick</h4>
        <p className="text-center text-frost-muted text-sm mb-4">
          Intel refreshes at: <span className="text-blue-400 font-bold">{refreshTimes.join(' | ')}</span> server time
        </p>
        <div className="flex justify-center items-center gap-8">
          <div className="text-center">
            <div className="text-3xl font-bold text-zinc-400">{normalTotal}</div>
            <div className="text-xs text-zinc-400">Normal</div>
          </div>
          <div className="text-2xl text-amber-500 font-bold">vs</div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-400">{trickTotal}</div>
            <div className="text-xs text-green-400">With Trick</div>
          </div>
        </div>
      </div>

      {/* Timeline steps */}
      <h4 className="text-sm font-medium text-frost">Claiming Timeline</h4>
      <div className="space-y-2">
        {timeline.map((step: any, i: number) => {
          const styles = getStepStyles(step.type || 'normal');
          return (
            <div key={i} className={`${styles.border} p-3 rounded-lg flex items-center gap-4`}>
              <div className="min-w-[60px] text-center">
                <div className={`text-xl font-bold ${styles.timeColor}`}>{step.time}</div>
              </div>
              <div className="flex-1">
                <div className="text-xs text-frost-muted">{step.day}</div>
                <div className={`text-sm mt-0.5 ${styles.actionColor}`}>{step.action}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// --- Spending Priority (Flame and Fang) ---
function SpendingPriority({ spendingPriority }: { spendingPriority: any }) {
  const order = spendingPriority.order || [];
  const avoid = spendingPriority.avoid || [];
  const warning = spendingPriority.warning || '';

  return (
    <div className="space-y-3">
      {order.map((item: any, i: number) => {
        const color = item.priority <= 2 ? 'bg-green-500' : item.priority === 3 ? 'bg-amber-500' : 'bg-zinc-500';
        return (
          <div key={i} className="flex items-center gap-3">
            <div className={`${color} text-black w-7 h-7 rounded-full flex items-center justify-center font-bold text-sm`}>
              {item.priority}
            </div>
            <div>
              <span className="text-frost font-bold">{item.item}</span>
              <span className="text-frost-muted text-xs ml-2">({item.note})</span>
            </div>
          </div>
        );
      })}

      {avoid.length > 0 && (
        <div className="p-3 rounded bg-red-500/10 border-l-4 border-l-red-500 mt-3">
          <span className="text-red-400 font-bold">AVOID: </span>
          <span className="text-frost">{avoid.join(', ')}</span>
        </div>
      )}

      {warning && (
        <div className="p-3 rounded-lg bg-amber-500/10 border-2 border-amber-400 text-center mt-3">
          <span className="text-amber-400 font-bold">{warning}</span>
        </div>
      )}
    </div>
  );
}

// --- Daily Stages (Hall of Chiefs / King of Icefield) ---
function DailyStages({ dailyStages }: { dailyStages: any }) {
  // Hall of Chiefs format: gen_1_season_1 / gen_2_season_2_plus
  const isHoC = dailyStages.gen_1_season_1 || dailyStages.gen_2_season_2_plus;

  if (isHoC) {
    return (
      <div className="space-y-3">
        {Object.entries(dailyStages).map(([seasonKey, seasonData]: [string, any]) => {
          if (!seasonKey.startsWith('gen_')) return null;
          const hero = seasonData.featured_hero || '';
          const duration = seasonData.duration || '';
          const stages = seasonData.stages || [];
          const isDefault = seasonKey === 'gen_2_season_2_plus';

          return (
            <Expander key={seasonKey} title={`${hero} Season (${duration})`} defaultOpen={isDefault}>
              <div className="space-y-2">
                {stages.map((stage: any, i: number) => (
                  <div key={i} className="p-3 rounded bg-blue-500/5 border-l-4 border-l-blue-500">
                    <div className="flex items-center gap-2">
                      <span className="text-amber-400 font-bold">Day {stage.day}:</span>
                      <span className="text-frost font-bold">{stage.focus}</span>
                    </div>
                    <div className="text-frost-muted text-sm mt-1">{stage.activities}</div>
                  </div>
                ))}
              </div>
            </Expander>
          );
        })}
      </div>
    );
  }

  // King of Icefield format: description + stages array
  const desc = dailyStages.description || '';
  const stages = dailyStages.stages || [];

  return (
    <div className="space-y-2">
      {desc && <p className="text-frost-muted text-sm mb-2">{desc}</p>}
      {stages.map((stage: any, i: number) => {
        const isGold = stage.reward && stage.reward.includes('Shards');
        return (
          <div key={i} className={`p-3 rounded border-l-4 ${isGold ? 'border-l-amber-400 bg-amber-500/5' : 'border-l-blue-500 bg-blue-500/5'}`}>
            <div className="flex items-center justify-between">
              <span className="text-amber-400 font-bold">Day {stage.day}: {stage.focus}</span>
              {stage.reward && (
                <span className={`text-xs ${isGold ? 'text-amber-400' : 'text-blue-400'}`}>Reward: {stage.reward}</span>
              )}
            </div>
            <div className="text-frost-muted text-sm mt-1">{stage.activities}</div>
          </div>
        );
      })}
    </div>
  );
}

// --- Victory Points (Alliance Showdown) ---
function VictoryPoints({ victoryPoints }: { victoryPoints: any }) {
  const desc = victoryPoints.description || '';
  const breakdown = victoryPoints.breakdown || [];
  const strategy = victoryPoints.strategy || '';

  return (
    <div className="space-y-3">
      {desc && <div className="p-3 rounded bg-blue-500/10 border border-blue-500/30 text-sm text-blue-300">{desc}</div>}

      {breakdown.length > 0 && (
        <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
          {breakdown.map((day: any, i: number) => {
            const isCritical = day.points >= 4;
            return (
              <div key={i} className={`p-2 rounded-lg border-2 text-center ${isCritical ? 'border-red-500 bg-red-500/10' : 'border-blue-500/50 bg-blue-500/5'}`}>
                <div className="text-xs text-frost-muted">Day {day.day}</div>
                <div className={`text-2xl font-bold ${isCritical ? 'text-red-400' : 'text-blue-400'}`}>{day.points}</div>
                <div className="text-[10px] text-frost-muted">VP</div>
              </div>
            );
          })}
        </div>
      )}

      {strategy && (
        <div className="p-3 rounded bg-green-500/10 border border-green-500/30">
          <span className="text-green-400 font-medium text-sm">Strategy: </span>
          <span className="text-frost text-sm">{strategy}</span>
        </div>
      )}
    </div>
  );
}

// --- Scoring Section (Foundry Battle, Hall of Chiefs, King of Icefield) ---
function ScoringSection({ scoring }: { scoring: any }) {
  const combatPts = scoring.combat_points || {};
  const buildingPts = scoring.building_points || {};
  const lootMechanic = scoring.loot_mechanic || '';

  // Flat key-value scoring (Hall of Chiefs, King of Icefield)
  const flatEntries = Object.entries(scoring).filter(
    ([k]) => !['combat_points', 'building_points', 'loot_mechanic'].includes(k)
  );

  return (
    <div className="space-y-3">
      {/* Flat scoring entries (Hall of Chiefs/KoI style) */}
      {flatEntries.length > 0 && Object.keys(combatPts).length === 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-frost-muted border-b border-surface-border">
                <th className="text-left py-1.5 pr-3">Item</th>
                <th className="text-right py-1.5">Points</th>
              </tr>
            </thead>
            <tbody className="text-frost">
              {flatEntries.map(([key, value]) => (
                <tr key={key} className="border-b border-surface-border/30">
                  <td className="py-1.5 pr-3">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</td>
                  <td className="py-1.5 text-right text-amber-400 font-medium">{String(value)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Combat points (Foundry Battle) */}
      {Object.keys(combatPts).length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-frost-muted uppercase tracking-wide mb-2">Combat Points</h4>
          <div className="space-y-1">
            {Object.entries(combatPts).map(([action, pts]) => (
              <div key={action} className="flex justify-between text-sm">
                <span className="text-frost">{action.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                <span className="text-amber-400 font-medium">{String(pts)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Building points (Foundry Battle) */}
      {Object.keys(buildingPts).length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-frost-muted uppercase tracking-wide mb-2 mt-3">Building Points</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-frost-muted border-b border-surface-border">
                  <th className="text-left py-1.5">Building</th>
                  <th className="text-right py-1.5">First Capture</th>
                  <th className="text-right py-1.5">Per Min</th>
                </tr>
              </thead>
              <tbody className="text-frost">
                {Object.entries(buildingPts).map(([building, data]: [string, any]) => (
                  <tr key={building} className="border-b border-surface-border/30">
                    <td className="py-1.5 font-medium">{building.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</td>
                    <td className="py-1.5 text-right text-amber-400">{typeof data.first_capture === 'number' ? data.first_capture.toLocaleString() : data.first_capture}</td>
                    <td className="py-1.5 text-right text-frost-muted">{typeof data.per_minute === 'number' ? data.per_minute.toLocaleString() : data.per_minute}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {lootMechanic && (
        <div className="p-3 rounded bg-blue-500/10 border border-blue-500/30 text-sm text-blue-300 mt-2">
          <span className="font-medium">Loot Mechanic: </span>{lootMechanic}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// STATE TRANSFER GUIDE
// =============================================================================

const TRANSFER_GROUPS = [
  { group: 1, states: '4-19', min: 4, max: 19, count: 16 },
  { group: 2, states: '21-132', min: 21, max: 132, count: 112 },
  { group: 3, states: '140-312', min: 140, max: 312, count: 173 },
  { group: 4, states: '313-433', min: 313, max: 433, count: 121 },
  { group: 5, states: '434-529', min: 434, max: 529, count: 96 },
  { group: 6, states: '530-804', min: 530, max: 804, count: 275 },
  { group: 7, states: '805-931', min: 805, max: 931, count: 127 },
  { group: 8, states: '932-1070', min: 932, max: 1070, count: 139 },
  { group: 9, states: '1071-1308', min: 1071, max: 1308, count: 238 },
  { group: 10, states: '1309-1427', min: 1309, max: 1427, count: 119 },
  { group: 11, states: '1428-1491', min: 1428, max: 1491, count: 64 },
  { group: 12, states: '1492-1615', min: 1492, max: 1615, count: 124 },
];

const PASS_RANGES = [
  { label: 'Low-Level (F26-F30)', min: 1, max: 3, note: 'Transferring to a weaker/newer state', color: 'text-green-400' },
  { label: 'F2P / Low Spender', min: 6, max: 12, note: 'Most common range', color: 'text-blue-400' },
  { label: 'Mid Spender', min: 20, max: 30, note: 'Post-upgrade transfers', color: 'text-amber-400' },
  { label: 'Whale / Top Player', min: 30, max: 50, note: 'Transferring to Leading States', color: 'text-red-400' },
];

const SHOP_PACKS = [
  { tier: 1, cost: '$4.99', passes: 1 },
  { tier: 2, cost: '$9.99', passes: 2 },
  { tier: 3, cost: '$19.99', passes: 3 },
  { tier: 4, cost: '$49.99', passes: 4 },
  { tier: 5, cost: '$99.99', passes: 5 },
];

function StateTransferGuide() {
  const [lookupState, setLookupState] = useState('');

  const foundGroup = useMemo(() => {
    const num = parseInt(lookupState);
    if (!num || num < 1) return null;
    return TRANSFER_GROUPS.find(g => num >= g.min && num <= g.max) || null;
  }, [lookupState]);

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Overview Card */}
      <div className="card bg-gradient-to-r from-cyan-500/10 via-surface to-blue-500/10 border-cyan-500/30">
        <h2 className="text-xl font-bold text-frost mb-3">State Transfer Guide</h2>
        <p className="text-frost-muted text-sm mb-4">
          State Transfer is a periodic 7-day event that lets you move to a different state. It runs approximately every 4-6 weeks
          and is announced 3-4 days before on X/Twitter (@WOS_Global) and in-game mail.
        </p>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-3 rounded-lg bg-surface border border-surface-border text-center">
            <div className="text-2xl font-bold text-cyan-400">7</div>
            <div className="text-xs text-frost-muted">Day Event</div>
          </div>
          <div className="p-3 rounded-lg bg-surface border border-surface-border text-center">
            <div className="text-2xl font-bold text-cyan-400">FC5</div>
            <div className="text-xs text-frost-muted">State Unlock</div>
          </div>
          <div className="p-3 rounded-lg bg-surface border border-surface-border text-center">
            <div className="text-2xl font-bold text-cyan-400">25d</div>
            <div className="text-xs text-frost-muted">Cooldown</div>
          </div>
          <div className="p-3 rounded-lg bg-surface border border-surface-border text-center">
            <div className="text-2xl font-bold text-cyan-400">12</div>
            <div className="text-xs text-frost-muted">Transfer Groups</div>
          </div>
        </div>
      </div>

      {/* 3 Phases */}
      <div className="card">
        <h3 className="text-lg font-bold text-frost mb-4">Event Phases</h3>
        <div className="space-y-3">
          {[
            { phase: 1, name: 'Presidential Review', days: '3 days', desc: 'State Presidents set Power Cap thresholds. Browse eligible states and contact Presidents. No transfers happen yet.', color: 'border-l-amber-500 bg-amber-500/5' },
            { phase: 2, name: 'Invitational Transfer', days: '2 days', desc: 'Presidents send invitations (Ordinary or Special) to Chiefs. Invited Chiefs can transfer during this phase.', color: 'border-l-purple-500 bg-purple-500/5' },
            { phase: 3, name: 'Open Transfer', days: '2 days', desc: 'Any eligible Chief meeting the Power Cap can transfer freely, first-come first-served.', color: 'border-l-green-500 bg-green-500/5' },
          ].map(p => (
            <div key={p.phase} className={`p-4 rounded-lg border-l-4 ${p.color}`}>
              <div className="flex items-center gap-3 mb-1">
                <span className="w-7 h-7 rounded-full bg-surface flex items-center justify-center text-sm font-bold text-frost">{p.phase}</span>
                <span className="font-bold text-frost">{p.name}</span>
                <span className="text-xs text-frost-muted ml-auto">{p.days}</span>
              </div>
              <p className="text-sm text-frost-muted ml-10">{p.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Transfer Passes */}
      <div className="card">
        <h3 className="text-lg font-bold text-frost mb-2">Transfer Passes</h3>
        <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 mb-4">
          <p className="text-sm text-amber-400">
            The number of passes needed depends on your <span className="font-bold">Transfer Score</span> vs the target state's <span className="font-bold">Transfer Rating</span> (top 100 chiefs' scores combined). Roughly ~1 pass per 20M Transfer Score points.
          </p>
        </div>

        {/* Pass ranges */}
        <h4 className="text-sm font-medium text-frost-muted mb-2 uppercase tracking-wide">Estimated Passes Needed</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-4">
          {PASS_RANGES.map(r => (
            <div key={r.label} className="p-3 rounded-lg bg-surface border border-surface-border">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-frost">{r.label}</span>
                <span className={`text-lg font-bold ${r.color}`}>{r.min}-{r.max}</span>
              </div>
              <p className="text-xs text-frost-muted">{r.note}</p>
            </div>
          ))}
        </div>

        {/* Transfer Score Components */}
        <Expander title="What counts toward Transfer Score?">
          <div className="space-y-3">
            <div>
              <h4 className="text-xs font-semibold text-green-400 uppercase tracking-wide mb-2">Included in Score</h4>
              <div className="flex flex-wrap gap-1">
                {['Furnace Level', 'Chief Gear & Charms', 'Hero Power (base)', 'Hero Gear Power', 'Pet Power', 'Expert Power'].map(c => (
                  <span key={c} className="px-2 py-1 bg-green-500/10 text-green-400 text-xs rounded">{c}</span>
                ))}
              </div>
            </div>
            <div>
              <h4 className="text-xs font-semibold text-red-400 uppercase tracking-wide mb-2">NOT Included (Cannot Game It)</h4>
              <span className="px-2 py-1 bg-red-500/10 text-red-400 text-xs rounded">Troop Power (dismissing troops does NOT lower your score)</span>
            </div>
          </div>
        </Expander>

        {/* How to Get Passes */}
        <div className="mt-4">
          <Expander title="How to get Transfer Passes">
            <div className="space-y-3">
              <div className="p-3 rounded-lg bg-blue-500/5 border-l-4 border-l-blue-500">
                <div className="font-medium text-frost text-sm mb-1">Alliance Shop</div>
                <p className="text-xs text-frost-muted">150,000 Alliance Tokens per pass. Refreshes weekly (1 per week).</p>
              </div>
              <div>
                <h4 className="text-xs font-semibold text-frost-muted uppercase tracking-wide mb-2">In-Game Shop Packs (Monthly Reset)</h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-frost-muted border-b border-surface-border">
                        <th className="text-left py-1.5 pr-3">Tier</th>
                        <th className="text-right py-1.5 pr-3">Cost</th>
                        <th className="text-right py-1.5">Passes</th>
                      </tr>
                    </thead>
                    <tbody>
                      {SHOP_PACKS.map(p => (
                        <tr key={p.tier} className="border-b border-surface-border/30 text-frost">
                          <td className="py-1.5 pr-3">Pack {p.tier}</td>
                          <td className="py-1.5 pr-3 text-right text-amber-400">{p.cost}</td>
                          <td className="py-1.5 text-right font-bold">{p.passes}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <p className="text-xs text-frost-muted mt-2">Max 85 passes purchasable per month. Pack tiers unlock progressively.</p>
              </div>
            </div>
          </Expander>
        </div>
      </div>

      {/* Transfer Groups — with lookup */}
      <div className="card">
        <h3 className="text-lg font-bold text-frost mb-2">Transfer Groups</h3>
        <p className="text-sm text-frost-muted mb-4">
          States are assigned to 1 of 12 groups. You can <span className="text-red-400 font-medium">only transfer within your group</span> — no exceptions. Groups change slightly each event but follow similar server-age ranges.
        </p>

        {/* State Lookup */}
        <div className="p-4 rounded-lg bg-surface border border-ice/20 mb-4">
          <label className="block text-sm font-medium text-frost mb-2">Find Your Transfer Group</label>
          <div className="flex gap-3 items-center">
            <input
              type="number"
              value={lookupState}
              onChange={e => setLookupState(e.target.value)}
              placeholder="Enter your state number..."
              className="input flex-1 max-w-[200px]"
              min={1}
              max={9999}
            />
            {foundGroup ? (
              <div className="flex items-center gap-2">
                <span className="text-cyan-400 font-bold text-lg">Group {foundGroup.group}</span>
                <span className="text-xs text-frost-muted">(States {foundGroup.states} - {foundGroup.count} states)</span>
              </div>
            ) : lookupState ? (
              <span className="text-frost-muted text-sm">State not found in Jan 2026 groups</span>
            ) : null}
          </div>
        </div>

        {/* Groups Table */}
        <Expander title="All Transfer Groups (January 2026)" defaultOpen={false}>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-frost-muted border-b border-surface-border">
                  <th className="text-left py-1.5 pr-3">Group</th>
                  <th className="text-left py-1.5 pr-3">States</th>
                  <th className="text-right py-1.5">Count</th>
                </tr>
              </thead>
              <tbody>
                {TRANSFER_GROUPS.map(g => (
                  <tr key={g.group} className={`border-b border-surface-border/30 ${
                    foundGroup?.group === g.group ? 'bg-cyan-500/10' : ''
                  }`}>
                    <td className="py-1.5 pr-3 font-bold text-frost">Group {g.group}</td>
                    <td className="py-1.5 pr-3 text-frost-muted">{g.states}</td>
                    <td className="py-1.5 text-right text-cyan-400">{g.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-xs text-frost-muted mt-2">Groups change each event but follow similar server-age ranges.</p>
        </Expander>
      </div>

      {/* Eligibility Requirements */}
      <div className="card">
        <h3 className="text-lg font-bold text-frost mb-4">Eligibility Requirements</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Personal Requirements */}
          <div>
            <h4 className="text-sm font-semibold text-frost-muted uppercase tracking-wide mb-3">Personal Requirements</h4>
            <div className="space-y-2">
              {[
                { label: 'Furnace Level', value: 'Must reach required minimum (max F30)', icon: 'check' },
                { label: 'Power Cap', value: 'Must not exceed President\'s cap (unless Special Invite)', icon: 'check' },
                { label: 'Alliance', value: 'Must NOT be in any alliance', icon: 'warn' },
                { label: 'Combat', value: 'City cannot be in active combat or scouting', icon: 'warn' },
                { label: 'Cooldown', value: '25 days since last transfer', icon: 'check' },
                { label: 'Per Event', value: 'Maximum 1 transfer per event', icon: 'check' },
              ].map(r => (
                <div key={r.label} className="flex items-start gap-2 text-sm">
                  <span className={`mt-0.5 ${r.icon === 'warn' ? 'text-amber-400' : 'text-cyan-400'}`}>
                    {r.icon === 'warn' ? '!' : '-'}
                  </span>
                  <div>
                    <span className="text-frost font-medium">{r.label}: </span>
                    <span className="text-frost-muted">{r.value}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-3 p-3 rounded-lg bg-red-500/10 border border-red-500/30">
              <p className="text-xs text-red-400 font-medium mb-1">Cannot Transfer If You Are:</p>
              <p className="text-xs text-frost-muted">Current President, Former President during interregnum, Transfer Manager, or Tyrant</p>
            </div>
          </div>

          {/* State Compatibility */}
          <div>
            <h4 className="text-sm font-semibold text-frost-muted uppercase tracking-wide mb-3">State Must Match</h4>
            <div className="space-y-2">
              {[
                { label: 'Hero Generation', value: 'Same latest hero generation' },
                { label: 'Fire Crystal Level', value: 'Must match between states' },
                { label: 'Furnace Era', value: 'Same era of progression' },
                { label: 'Buildings', value: 'Unlocked buildings must match' },
                { label: 'Beasts', value: 'Available beasts must match' },
                { label: 'Equipment', value: 'Chief and hero equipment systems must match' },
                { label: 'State Age', value: 'Character age cannot exceed target by 45-180 days' },
                { label: 'Transfer Group', value: 'Must be in same group (12 groups)' },
              ].map(r => (
                <div key={r.label} className="flex items-start gap-2 text-sm">
                  <span className="text-cyan-400 mt-0.5">-</span>
                  <div>
                    <span className="text-frost font-medium">{r.label}: </span>
                    <span className="text-frost-muted">{r.value}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Alliance Transfers */}
      <div className="card">
        <h3 className="text-lg font-bold text-frost mb-2">Alliance Transfers</h3>
        <div className="p-3 rounded-lg bg-red-500/10 border-2 border-red-500/30 mb-4">
          <p className="text-sm text-red-400 font-bold mb-1">There is NO alliance transfer feature</p>
          <p className="text-xs text-frost-muted">Each member must transfer individually. Coordination required.</p>
        </div>

        <div className="space-y-2 mb-4">
          <h4 className="text-sm font-medium text-frost">Coordination Steps</h4>
          {[
            'Every member must leave the alliance before transferring',
            'Each member needs their own Transfer Passes',
            'Each member must individually meet all requirements',
            'After transferring, rejoin or create a new alliance in the destination state',
          ].map((step, i) => (
            <div key={i} className="flex items-start gap-2 text-sm">
              <span className="text-cyan-400 font-bold mt-0.5">{i + 1}.</span>
              <span className="text-frost-muted">{step}</span>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="p-3 rounded-lg bg-surface border border-surface-border">
            <div className="text-sm font-medium text-frost mb-1">Ordinary States</div>
            <div className="text-2xl font-bold text-cyan-400">58</div>
            <div className="text-xs text-frost-muted">max transfers (38 invite + 20 open)</div>
          </div>
          <div className="p-3 rounded-lg bg-surface border border-surface-border">
            <div className="text-sm font-medium text-frost mb-1">Leading States</div>
            <div className="text-2xl font-bold text-amber-400">30</div>
            <div className="text-xs text-frost-muted">max transfers (20 invite + 10 open)</div>
          </div>
        </div>
      </div>

      {/* What You Lose / Keep */}
      <div className="card">
        <h3 className="text-lg font-bold text-frost mb-4">What Happens When You Transfer</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Lost */}
          <div>
            <h4 className="text-sm font-semibold text-red-400 uppercase tracking-wide mb-3">Lost or Reset</h4>
            <div className="space-y-2">
              {[
                { item: 'Resources', detail: 'Anything over Storehouse Protection limit is LOST' },
                { item: 'Arena Points', detail: 'Reset to 1,000; ranking deleted' },
                { item: 'Event Progress', detail: 'Active events terminated; unclaimed rewards mailed' },
                { item: 'Group Chats', detail: 'All group chats removed' },
                { item: 'Alliance', detail: 'Must leave before transfer; lose shop progress' },
                { item: 'Emporium Thorns', detail: 'Only transfer if Emporium active in new state' },
              ].map(r => (
                <div key={r.item} className="flex items-start gap-2 text-sm">
                  <span className="text-red-400 mt-0.5">x</span>
                  <div>
                    <span className="text-frost font-medium">{r.item}: </span>
                    <span className="text-frost-muted">{r.detail}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Kept */}
          <div>
            <h4 className="text-sm font-semibold text-green-400 uppercase tracking-wide mb-3">Kept or Beneficial</h4>
            <div className="space-y-2">
              {[
                { item: 'Heroes & Gear', detail: 'All heroes, gear, and progression transfer' },
                { item: 'Friends List', detail: 'Friends and private chats preserved' },
                { item: 'Chief Gear & Charms', detail: 'All chief equipment transfers' },
                { item: 'Pets & Experts', detail: 'All pet and expert progress keeps' },
                { item: 'Pack Purchase Counts', detail: 'RESET — you can rebuy all packs!' },
              ].map(r => (
                <div key={r.item} className="flex items-start gap-2 text-sm">
                  <span className="text-green-400 mt-0.5">+</span>
                  <div>
                    <span className="text-frost font-medium">{r.item}: </span>
                    <span className="text-frost-muted">{r.detail}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Tips */}
      <div className="card">
        <h3 className="text-lg font-bold text-frost mb-3">Tips</h3>
        <div className="space-y-2">
          {[
            'Use resources down to your Storehouse Protection limit before transferring to avoid losing them',
            'Contact the target state\'s President during Phase 1 to secure a Special Invite (bypasses Power Cap)',
            'Plan ahead — start buying passes from Alliance Shop weeks in advance (1/week)',
            'If moving with your alliance, use wos-transfer.com to coordinate group transfers',
            'Pack purchase counts reset after transfer — time your transfer before buying packs to double dip',
            'Check @WOS_Global on X/Twitter for transfer event announcements 3-4 days before they start',
          ].map((tip, i) => (
            <div key={i} className="flex items-start gap-2 text-sm">
              <span className="text-cyan-400 mt-0.5">-</span>
              <span className="text-frost-muted">{tip}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function EventsPage() {
  const [eventsGuide, setEventsGuide] = useState<EventsGuide | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedEvent, setSelectedEvent] = useState<{ id: string; event: Event } | null>(null);
  const [filterF2P, setFilterF2P] = useState<boolean>(false);
  const [filterPriority, setFilterPriority] = useState<string>('all');
  const [showStateTransfer, setShowStateTransfer] = useState(false);

  useEffect(() => {
    setIsLoading(true);
    eventsApi.getGuide()
      .then(data => {
        if (data && data.events) {
          setEventsGuide(data);
        }
      })
      .catch((err) => {
        console.error('Failed to load events guide:', err);
        setEventsGuide(null);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'S': return 'bg-amber-500/20 text-amber-400 border-amber-500';
      case 'A': return 'bg-purple-500/20 text-purple-400 border-purple-500';
      case 'B': return 'bg-blue-500/20 text-blue-400 border-blue-500';
      case 'C': return 'bg-zinc-500/20 text-zinc-400 border-zinc-500';
      case 'D': return 'bg-red-500/20 text-red-400 border-red-500';
      default: return 'bg-zinc-700 text-zinc-500 border-zinc-600';
    }
  };

  const getCostColor = (category: string) => {
    switch (category) {
      case 'free': return 'bg-success/20 text-success';
      case 'light_spend': return 'bg-amber-500/20 text-amber-400';
      case 'medium_spend': return 'bg-orange-500/20 text-orange-400';
      case 'heavy_spend': return 'bg-red-500/20 text-red-400';
      case 'whale_event': return 'bg-purple-500/20 text-purple-400';
      default: return 'bg-zinc-700 text-zinc-400';
    }
  };

  const getCostLabel = (category: string) => {
    if (!category) return 'Unknown';
    return eventsGuide?.cost_categories[category]?.label || category.replace(/_/g, ' ');
  };

  const getF2PBadge = (f2p: boolean | string) => {
    if (f2p === true) return { text: 'F2P Friendly', color: 'bg-success/20 text-success border-success/30' };
    if (f2p === 'partially') return { text: 'Partial F2P', color: 'bg-amber-500/20 text-amber-400 border-amber-500/30' };
    return { text: 'Pay to Progress', color: 'bg-red-500/20 text-red-400 border-red-500/30' };
  };

  // Filter and sort events
  const getFilteredEvents = () => {
    if (!eventsGuide || !eventsGuide.events) return [];

    let events = Object.entries(eventsGuide.events);

    // Filter by category
    if (selectedCategory !== 'all') {
      const categoryEvents = EVENT_CATEGORIES[selectedCategory as keyof typeof EVENT_CATEGORIES];
      if ('events' in categoryEvents) {
        events = events.filter(([id]) => categoryEvents.events.includes(id));
      }
    }

    // Filter by F2P
    if (filterF2P) {
      events = events.filter(([, event]) => event.f2p_friendly === true);
    }

    // Filter by priority
    if (filterPriority !== 'all') {
      events = events.filter(([, event]) => event.priority === filterPriority);
    }

    // Sort by priority
    return events.sort((a, b) => {
      const priorityA = PRIORITY_ORDER[a[1].priority] ?? 5;
      const priorityB = PRIORITY_ORDER[b[1].priority] ?? 5;
      return priorityA - priorityB;
    });
  };

  const filteredEvents = getFilteredEvents();

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-frost">Events Guide</h1>
          <p className="text-frost-muted mt-2">Which events are worth your time - ranked by value</p>
        </div>

        {/* Priority Legend */}
        {!showStateTransfer && <div className="card mb-6 bg-gradient-to-r from-surface to-surface-hover">
          <h2 className="text-sm font-medium text-frost-muted mb-3 uppercase tracking-wide">Priority Guide</h2>
          <div className="grid grid-cols-5 gap-2">
            {['S', 'A', 'B', 'C', 'D'].map((tier) => {
              const labels: Record<string, string> = {
                'S': 'Must Do',
                'A': 'High Priority',
                'B': 'Do If Active',
                'C': 'Low Priority',
                'D': 'Skip/Whale'
              };
              return (
                <div key={tier} className={`text-center p-2 rounded-lg border ${getPriorityColor(tier)}`}>
                  <div className="text-xl font-bold">{tier}</div>
                  <div className="text-[10px] opacity-80">{labels[tier]}</div>
                </div>
              );
            })}
          </div>
        </div>}

        {/* Resource Saving Guide */}
        {!showStateTransfer && eventsGuide?.resource_saving_guide && (
          <div className="mb-6">
            <Expander title="What to Save & When" defaultOpen={true}>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-frost-muted border-b border-surface-border">
                      <th className="text-left py-2 pr-3 w-1/5">Resource</th>
                      <th className="text-left py-2 pr-3 w-1/4">Save For</th>
                      <th className="text-left py-2">Tip</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(eventsGuide.resource_saving_guide).map(([resource, data]) => (
                      <tr key={resource} className="border-b border-surface-border/30 hover:bg-surface-hover/30">
                        <td className="py-2 pr-3 font-bold text-frost">
                          {resource.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </td>
                        <td className="py-2 pr-3 text-amber-400 text-xs">
                          {data.save_for.map((id: string) => getEventName(id, eventsGuide)).join(', ')}
                        </td>
                        <td className="py-2 text-frost-muted text-xs">{data.tip}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Expander>
          </div>
        )}

        {/* Category Tabs */}
        <div className="flex flex-wrap gap-2 mb-4">
          {Object.entries(EVENT_CATEGORIES).map(([key, cat]) => (
            <button
              key={key}
              onClick={() => { setSelectedCategory(key); setShowStateTransfer(false); }}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                selectedCategory === key && !showStateTransfer
                  ? 'bg-ice text-zinc-900'
                  : 'bg-surface text-frost-muted hover:text-frost'
              }`}
            >
              {cat.label}
            </button>
          ))}
          <div className="w-px bg-surface-border mx-1 self-stretch" />
          <button
            onClick={() => setShowStateTransfer(true)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              showStateTransfer
                ? 'bg-cyan-500 text-zinc-900'
                : 'bg-surface text-cyan-400 hover:text-cyan-300 border border-cyan-500/30'
            }`}
          >
            State Transfer
          </button>
        </div>

        {/* State Transfer Guide */}
        {showStateTransfer && <StateTransferGuide />}

        {/* Events Content (hidden when State Transfer is shown) */}
        {!showStateTransfer && <>
        {/* Filters Row */}
        <div className="flex flex-wrap gap-3 items-center mb-6">
          <label className="flex items-center gap-2 text-sm text-frost-muted cursor-pointer">
            <input
              type="checkbox"
              checked={filterF2P}
              onChange={(e) => setFilterF2P(e.target.checked)}
              className="w-4 h-4 rounded bg-surface border-surface-border text-ice focus:ring-ice"
            />
            <span>F2P Only</span>
          </label>

          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
            className="input py-1 px-2 text-sm w-auto"
          >
            <option value="all">All Priorities</option>
            <option value="S">S - Must Do</option>
            <option value="A">A - High</option>
            <option value="B">B - Medium</option>
            <option value="C">C - Low</option>
            <option value="D">D - Skip</option>
          </select>

          <span className="text-xs text-frost-muted ml-auto">
            {filteredEvents.length} events
          </span>
        </div>

        {/* Events List */}
        {isLoading ? (
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="card animate-pulse">
                <div className="h-6 bg-surface-hover rounded w-1/3 mb-2"></div>
                <div className="h-4 bg-surface-hover rounded w-2/3 mb-3"></div>
                <div className="h-3 bg-surface-hover rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : !eventsGuide ? (
          <div className="card text-center py-12">
            <div className="text-4xl mb-4">Warning</div>
            <h3 className="text-lg font-medium text-frost mb-2">Unable to load events</h3>
            <p className="text-frost-muted">Make sure the API server is running</p>
          </div>
        ) : filteredEvents.length === 0 ? (
          <div className="card text-center py-12">
            <h3 className="text-lg font-medium text-frost mb-2">No events match your filters</h3>
            <p className="text-frost-muted">Try adjusting your filters</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredEvents.map(([eventId, event]) => {
              const f2pBadge = getF2PBadge(event.f2p_friendly);

              return (
                <button
                  key={eventId}
                  onClick={() => setSelectedEvent({ id: eventId, event })}
                  className={`card w-full text-left hover:border-ice/30 transition-all border-l-4 ${
                    event.priority === 'S' ? 'border-l-amber-500' :
                    event.priority === 'A' ? 'border-l-purple-500' :
                    event.priority === 'B' ? 'border-l-blue-500' :
                    event.priority === 'C' ? 'border-l-zinc-500' :
                    'border-l-red-500'
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <h3 className="font-bold text-frost">{event.name}</h3>
                        <span className={`px-1.5 py-0.5 rounded text-xs font-bold ${getPriorityColor(event.priority)}`}>
                          {event.priority}
                        </span>
                        <span className={`px-1.5 py-0.5 rounded text-xs border ${f2pBadge.color}`}>
                          {f2pBadge.text}
                        </span>
                      </div>
                      <p className="text-sm text-frost-muted line-clamp-2">{event.description}</p>
                      <div className="flex items-center gap-3 mt-2 text-xs text-frost-muted">
                        <span>{event.type.split('_').map((w: string) => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}</span>
                        <span>-</span>
                        <span>{event.frequency}</span>
                        {event.duration && (
                          <>
                            <span>-</span>
                            <span>{event.duration}</span>
                          </>
                        )}
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      <span className={`px-2 py-1 rounded text-xs ${getCostColor(event.cost_category)}`}>
                        {getCostLabel(event.cost_category)}
                      </span>
                      <span className="text-xs text-ice">Details &rarr;</span>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        )}

        {/* Cost Categories Legend */}
        {eventsGuide && (
          <div className="mt-6">
            <Expander title="Cost Categories Explained" defaultOpen={false}>
              <div className="space-y-2">
                {Object.entries(eventsGuide.cost_categories).map(([catId, catData]) => (
                  <div key={catId} className="flex items-center gap-3">
                    <span className={`px-2 py-1 rounded text-xs whitespace-nowrap ${getCostColor(catId)}`}>
                      {catData.label}
                    </span>
                    <span className="text-frost-muted text-sm">{catData.description}</span>
                  </div>
                ))}
              </div>
            </Expander>
          </div>
        )}

        {/* Event Detail Modal */}
        {selectedEvent && (
          <div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={(e) => { if (e.target === e.currentTarget) setSelectedEvent(null); }}
          >
            <div className="bg-surface rounded-xl border border-surface-border max-w-2xl w-full max-h-[90vh] overflow-y-auto animate-fadeIn">
              {/* Modal Header */}
              <div className="sticky top-0 bg-surface border-b border-surface-border/50 p-4 flex items-start justify-between z-10">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h2 className="text-xl font-bold text-frost">{selectedEvent.event.name}</h2>
                    <span className={`px-1.5 py-0.5 rounded text-xs font-bold ${getPriorityColor(selectedEvent.event.priority)}`}>
                      {selectedEvent.event.priority}
                    </span>
                  </div>
                  <p className="text-sm text-frost-muted">
                    {selectedEvent.event.type.split('_').map((w: string) => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')} - {selectedEvent.event.frequency}
                    {selectedEvent.event.duration && ` - ${selectedEvent.event.duration}`}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedEvent(null)}
                  className="text-frost-muted hover:text-frost text-xl leading-none p-1"
                >
                  x
                </button>
              </div>

              {/* Modal Content */}
              <div className="p-4 space-y-4">
                {/* Description */}
                <div>
                  <p className="text-frost">{selectedEvent.event.description}</p>
                  {selectedEvent.event.gameplay && (
                    <p className="text-frost-muted text-sm mt-2 italic">{selectedEvent.event.gameplay}</p>
                  )}
                </div>

                {/* Badges Row */}
                <div className="flex flex-wrap gap-2">
                  <span className={`px-2 py-1 rounded text-xs ${getCostColor(selectedEvent.event.cost_category)}`}>
                    {getCostLabel(selectedEvent.event.cost_category)}
                  </span>
                  {(() => {
                    const badge = getF2PBadge(selectedEvent.event.f2p_friendly);
                    return (
                      <span className={`px-2 py-1 rounded text-xs border ${badge.color}`}>
                        {badge.text}
                      </span>
                    );
                  })()}
                </div>

                {/* Eligibility (Alliance Showdown) */}
                {selectedEvent.event.eligibility && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-2">Eligibility</h3>
                    <div className="space-y-1">
                      {Object.entries(selectedEvent.event.eligibility).map(([key, value]) => (
                        <div key={key} className="text-sm">
                          <span className="text-frost font-medium">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}: </span>
                          <span className="text-frost-muted">{String(value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Rewards */}
                {selectedEvent.event.rewards && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-2">Rewards</h3>
                    <div className="flex flex-wrap gap-1">
                      {selectedEvent.event.rewards.primary.map((reward, i) => (
                        <span key={i} className="px-2 py-1 bg-ice/10 text-ice text-xs rounded">
                          {reward}
                        </span>
                      ))}
                    </div>
                    {selectedEvent.event.rewards.backpack_items && selectedEvent.event.rewards.backpack_items.length > 0 && (
                      <p className="text-xs text-frost-muted mt-2">
                        Backpack: {selectedEvent.event.rewards.backpack_items.join(', ')}
                      </p>
                    )}
                  </div>
                )}

                {/* Key Heroes */}
                {selectedEvent.event.preparation?.key_heroes && selectedEvent.event.preparation.key_heroes.length > 0 && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-2">Key Heroes</h3>
                    <div className="flex flex-wrap gap-1">
                      {selectedEvent.event.preparation.key_heroes.map((hero, i) => (
                        <span key={i} className="px-2 py-1 bg-purple-500/10 text-purple-400 text-xs rounded border border-purple-500/30">
                          {hero}
                        </span>
                      ))}
                    </div>
                    {selectedEvent.event.preparation.heroes_needed && selectedEvent.event.preparation.heroes_needed !== 'none' && (
                      <p className="text-xs text-frost-muted mt-2">
                        Uses <span className="text-ice">{selectedEvent.event.preparation.heroes_needed}</span> skills
                      </p>
                    )}
                  </div>
                )}

                {/* Troop Ratio */}
                {selectedEvent.event.troop_ratio && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-3">Troop Ratio</h3>
                    {'leader' in selectedEvent.event.troop_ratio ? (
                      // Multi-ratio format
                      <div className="space-y-3">
                        {['leader', 'joiner'].map((role) => {
                          const ratio = (selectedEvent.event.troop_ratio as any)[role];
                          if (!ratio) return null;
                          return (
                            <div key={role} className="p-3 rounded-lg bg-surface border-l-4 border-l-amber-500">
                              <div className="text-xs text-amber-400 font-medium mb-2">
                                {role === 'leader' ? 'Rally Leader' : 'Rally Joiner'}
                              </div>
                              <div className="grid grid-cols-3 gap-4 mb-2">
                                <div className="text-center">
                                  <div className="text-lg font-bold text-red-400">{ratio.infantry}</div>
                                  <div className="text-[10px] text-frost-muted">Infantry</div>
                                </div>
                                <div className="text-center">
                                  <div className="text-lg font-bold text-green-400">{ratio.lancer}</div>
                                  <div className="text-[10px] text-frost-muted">Lancer</div>
                                </div>
                                <div className="text-center">
                                  <div className="text-lg font-bold text-blue-400">{ratio.marksman}</div>
                                  <div className="text-[10px] text-frost-muted">Marksman</div>
                                </div>
                              </div>
                              <p className="text-xs text-frost-muted">{ratio.reasoning}</p>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      // Simple ratio
                      <div className="p-3 rounded-lg bg-surface">
                        <div className="grid grid-cols-3 gap-4 mb-2">
                          <div className="text-center">
                            <div className="text-xl font-bold text-red-400">{(selectedEvent.event.troop_ratio as TroopRatio).infantry}</div>
                            <div className="text-xs text-frost-muted">Infantry</div>
                          </div>
                          <div className="text-center">
                            <div className="text-xl font-bold text-green-400">{(selectedEvent.event.troop_ratio as TroopRatio).lancer}</div>
                            <div className="text-xs text-frost-muted">Lancer</div>
                          </div>
                          <div className="text-center">
                            <div className="text-xl font-bold text-blue-400">{(selectedEvent.event.troop_ratio as TroopRatio).marksman}</div>
                            <div className="text-xs text-frost-muted">Marksman</div>
                          </div>
                        </div>
                        <p className="text-xs text-frost-muted">{(selectedEvent.event.troop_ratio as TroopRatio).reasoning}</p>
                      </div>
                    )}

                    {/* Alternative ratios (Alliance Championship) */}
                    {selectedEvent.event.alternative_ratios && (
                      <div className="mt-3 space-y-1">
                        <h4 className="text-xs font-semibold text-frost-muted uppercase tracking-wide">Alternative Ratios</h4>
                        {selectedEvent.event.alternative_ratios.map((alt: any, i: number) => (
                          <div key={i} className="flex items-center gap-2 text-sm">
                            <span className="text-ice font-mono font-bold">{alt.ratio}</span>
                            <span className="text-frost-muted">- {alt.note}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Wave Mechanics (Crazy Joe) */}
                {selectedEvent.event.wave_mechanics && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-3">Wave Breakdown</h3>

                    {/* Key waves callout */}
                    {(selectedEvent.event.wave_mechanics.online_waves || selectedEvent.event.wave_mechanics.high_value_waves) && (
                      <div className="p-3 rounded-lg bg-amber-500/10 border-2 border-amber-400/50 mb-3">
                        <div className="text-amber-400 font-bold text-sm mb-1">Key Waves</div>
                        {selectedEvent.event.wave_mechanics.online_waves && (
                          <div className="text-frost text-sm">{selectedEvent.event.wave_mechanics.online_waves}</div>
                        )}
                        {selectedEvent.event.wave_mechanics.high_value_waves && (
                          <div className="text-green-400 text-sm mt-1">{selectedEvent.event.wave_mechanics.high_value_waves}</div>
                        )}
                      </div>
                    )}

                    {/* Wave list */}
                    <div className="space-y-2">
                      {['waves_1_9', 'wave_10', 'waves_11_19', 'wave_20', 'wave_21'].map((waveKey) => {
                        const desc = selectedEvent.event.wave_mechanics?.[waveKey];
                        if (!desc) return null;
                        const isHQ = desc.includes('HQ');
                        return (
                          <div
                            key={waveKey}
                            className={`p-2 rounded text-sm border-l-4 ${isHQ ? 'border-l-red-500 bg-red-500/5' : 'border-l-blue-500 bg-blue-500/5'}`}
                          >
                            <span className="font-medium text-frost">
                              {waveKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                            </span>{' '}
                            <span className="text-frost-muted">{desc}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Battle Mechanics (SvS Battle) */}
                {selectedEvent.event.mechanics && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-3">Battle Mechanics</h3>
                    <div className="space-y-2">
                      {Object.entries(selectedEvent.event.mechanics).map(([key, value]) => (
                        <div key={key} className="text-sm">
                          <span className="text-frost font-medium">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}: </span>
                          <span className="text-frost-muted">{String(value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Intel Strategy Timeline (Flame and Fang) */}
                {selectedEvent.event.intel_strategy && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-3">Intel Strategy</h3>
                    <IntelStrategyTimeline intelStrategy={selectedEvent.event.intel_strategy} />
                  </div>
                )}

                {/* Spending Priority (Flame and Fang) */}
                {selectedEvent.event.spending_priority && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-3">Spending Priority</h3>
                    <SpendingPriority spendingPriority={selectedEvent.event.spending_priority} />
                  </div>
                )}

                {/* Phases (SvS Prep days etc.) */}
                {selectedEvent.event.phases && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-3">Day-by-Day Breakdown</h3>
                    <div className="space-y-3">
                      {Object.entries(selectedEvent.event.phases).map(([phaseKey, phase]: [string, any]) => (
                        <Expander key={phaseKey} title={phase.name || phaseKey}>
                          <div className="space-y-3">
                            {phase.focus && (
                              <p className="text-sm"><span className="text-frost font-medium">Focus: </span><span className="text-frost-muted">{phase.focus}</span></p>
                            )}

                            {/* Best value tasks */}
                            {phase.best_value_tasks && (
                              <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                  <thead>
                                    <tr className="text-frost-muted border-b border-surface-border">
                                      <th className="text-left py-1 pr-3">Task</th>
                                      <th className="text-right py-1 pr-3">Points</th>
                                      <th className="text-right py-1">Per</th>
                                    </tr>
                                  </thead>
                                  <tbody className="text-frost">
                                    {phase.best_value_tasks.map((task: any, i: number) => (
                                      <tr key={i} className="border-b border-surface-border/30">
                                        <td className="py-1 pr-3">{task.task}</td>
                                        <td className="py-1 pr-3 text-right font-medium text-amber-400">{typeof task.points === 'number' ? task.points.toLocaleString() : task.points}</td>
                                        <td className="py-1 text-right text-frost-muted">{task.per}</td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            )}

                            {/* Hunting strategy (Day 3 specific) */}
                            {phase.hunting_strategy && (
                              <div className="space-y-2 mt-2">
                                <h4 className="text-xs font-semibold text-green-400 uppercase tracking-wide">Hunting Strategy: Auto-Hunt AFK</h4>
                                <p className="text-sm text-frost-muted">{phase.hunting_strategy.auto_hunt_strategy?.description}</p>
                                {phase.hunting_strategy.auto_hunt_strategy?.formation && (
                                  <div className="space-y-1">
                                    {phase.hunting_strategy.auto_hunt_strategy.formation.map((hero: string, i: number) => (
                                      <p key={i} className="text-sm text-frost-muted"><span className="text-green-400">Slot {i+1}:</span> {hero}</p>
                                    ))}
                                  </div>
                                )}
                                {phase.hunting_strategy.auto_hunt_strategy?.important && (
                                  <p className="text-sm text-amber-400 p-2 rounded bg-amber-500/10 border border-amber-500/30">
                                    {phase.hunting_strategy.auto_hunt_strategy.important}
                                  </p>
                                )}
                                {/* Efficiency comparison */}
                                {phase.hunting_strategy.efficiency && (
                                  <div className="grid grid-cols-2 gap-2 text-xs">
                                    <div className="p-2 rounded bg-surface">
                                      <span className="text-frost-muted">Rally (w/ Gina):</span>
                                      <span className="text-green-400 font-medium ml-1">{phase.hunting_strategy.efficiency.rally_with_gina}</span>
                                    </div>
                                    <div className="p-2 rounded bg-surface">
                                      <span className="text-frost-muted">Solo Lv26-30 (w/ Gina):</span>
                                      <span className="text-green-400 font-medium ml-1">{phase.hunting_strategy.efficiency.solo_26_30_with_gina}</span>
                                    </div>
                                  </div>
                                )}
                              </div>
                            )}

                            {/* Day 4 efficiency analysis */}
                            {phase.efficiency_analysis && (
                              <div className="space-y-2 mt-2">
                                <h4 className="text-xs font-semibold text-amber-400 uppercase tracking-wide">Speedup vs Promotion Analysis</h4>
                                <p className="text-sm text-frost-muted">{phase.efficiency_analysis.description}</p>

                                {/* Promotion rates */}
                                {phase.efficiency_analysis.promotion_rates && (
                                  <div className="space-y-1">
                                    {Object.entries(phase.efficiency_analysis.promotion_rates).map(([tier, rate]) => (
                                      <div key={tier} className="flex justify-between text-xs px-2 py-1 rounded bg-surface">
                                        <span className="text-frost">{tier.replace(/_/g, ' ').toUpperCase()}</span>
                                        <span className="text-amber-400 font-medium">{String(rate)}</span>
                                      </div>
                                    ))}
                                  </div>
                                )}

                                {phase.efficiency_analysis.conclusion && (
                                  <p className="text-sm text-green-400 font-medium p-2 rounded bg-green-500/10 border border-green-500/30">
                                    {phase.efficiency_analysis.conclusion}
                                  </p>
                                )}

                                {phase.efficiency_analysis.optimal_strategy && (
                                  <ul className="space-y-1">
                                    {phase.efficiency_analysis.optimal_strategy.map((step: string, i: number) => (
                                      <li key={i} className="flex items-start gap-2 text-sm text-frost-muted">
                                        <span className="text-amber-400 mt-0.5">{i+1}.</span>
                                        <span>{step}</span>
                                      </li>
                                    ))}
                                  </ul>
                                )}
                              </div>
                            )}

                            {/* Save for this day */}
                            {phase.save_for_this_day && (
                              <div className="flex flex-wrap gap-1 mt-1">
                                <span className="text-xs text-red-400 font-medium">Save:</span>
                                {phase.save_for_this_day.map((item: string, i: number) => (
                                  <span key={i} className="text-xs px-1.5 py-0.5 rounded bg-red-500/10 text-red-400/80">{item}</span>
                                ))}
                              </div>
                            )}

                            {/* Note */}
                            {phase.note && (
                              <p className="text-xs text-amber-400 mt-1 p-2 rounded bg-amber-500/10">{phase.note}</p>
                            )}
                          </div>
                        </Expander>
                      ))}
                    </div>
                  </div>
                )}

                {/* Daily Stages (Hall of Chiefs, King of Icefield) */}
                {selectedEvent.event.daily_stages && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-3">Daily Stages</h3>
                    <DailyStages dailyStages={selectedEvent.event.daily_stages} />
                  </div>
                )}

                {/* Victory Points (Alliance Showdown) */}
                {selectedEvent.event.victory_points && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-3">Victory Points</h3>
                    <VictoryPoints victoryPoints={selectedEvent.event.victory_points} />
                  </div>
                )}

                {/* Star Rating System (Alliance Showdown) */}
                {selectedEvent.event.star_system && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-3">Star Rating System</h3>
                    {selectedEvent.event.star_system.description && (
                      <p className="text-frost-muted text-sm mb-2">{selectedEvent.event.star_system.description}</p>
                    )}
                    <div className="grid grid-cols-2 gap-3">
                      <div className="text-sm">
                        <span className="text-green-400 font-medium">Win: </span>
                        <span className="text-frost-muted">{selectedEvent.event.star_system.win_effect}</span>
                      </div>
                      <div className="text-sm">
                        <span className="text-red-400 font-medium">Lose: </span>
                        <span className="text-frost-muted">{selectedEvent.event.star_system.loss_effect}</span>
                      </div>
                    </div>
                    {selectedEvent.event.star_system.star_rewards && (
                      <p className="text-sm text-amber-400 mt-2">Rewards: {selectedEvent.event.star_system.star_rewards}</p>
                    )}
                  </div>
                )}

                {/* Tundra Trade Route (Alliance Showdown companion) */}
                {selectedEvent.event.tundra_trade_route && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-2">Tundra Trade Route (Concurrent Event)</h3>
                    {selectedEvent.event.tundra_trade_route.description && (
                      <p className="text-frost-muted text-sm mb-2">{selectedEvent.event.tundra_trade_route.description}</p>
                    )}
                    {selectedEvent.event.tundra_trade_route.tips && (
                      <ul className="space-y-1">
                        {selectedEvent.event.tundra_trade_route.tips.map((tip: string, i: number) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-frost-muted">
                            <span className="text-ice mt-0.5">-</span>
                            <span>{tip}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}

                {/* Medal System (King of Icefield) */}
                {selectedEvent.event.medal_system && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-2">Medal System</h3>
                    {selectedEvent.event.medal_system.description && (
                      <p className="text-frost-muted text-sm mb-2">{selectedEvent.event.medal_system.description}</p>
                    )}
                    <div className="space-y-1 text-sm">
                      <p><span className="text-frost font-medium">Medals per day: </span><span className="text-amber-400">{selectedEvent.event.medal_system.medals_per_day}</span></p>
                      <p><span className="text-frost font-medium">Medal Shop: </span><span className="text-frost-muted">{selectedEvent.event.medal_system.medal_shop}</span></p>
                    </div>
                  </div>
                )}

                {/* Ranking Tiers (King of Icefield) */}
                {selectedEvent.event.ranking_tiers && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-2">Rankings</h3>
                    <div className="space-y-1 text-sm">
                      {Object.entries(selectedEvent.event.ranking_tiers).map(([key, value]) => (
                        <p key={key}>
                          <span className="text-frost font-medium">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}: </span>
                          <span className="text-frost-muted">{String(value)}</span>
                        </p>
                      ))}
                    </div>
                  </div>
                )}

                {/* Scoring (Foundry Battle, Hall of Chiefs, King of Icefield) */}
                {selectedEvent.event.scoring && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-3">Scoring</h3>
                    <ScoringSection scoring={selectedEvent.event.scoring} />
                  </div>
                )}

                {/* Phase Strategy (Canyon Clash, Foundry Battle) */}
                {selectedEvent.event.phase_strategy && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-3">Phase Strategy</h3>
                    <div className="space-y-2">
                      {Object.entries(selectedEvent.event.phase_strategy).map(([phaseKey, phaseDesc]) => {
                        const isCritical = String(phaseDesc).toUpperCase().includes('CITADEL') || String(phaseDesc).toUpperCase().includes('FOUNDRY') || String(phaseDesc).toUpperCase().includes('IMPERIAL');
                        return (
                          <div
                            key={phaseKey}
                            className={`p-3 rounded text-sm border-l-4 ${isCritical ? 'border-l-amber-400 bg-amber-500/5' : 'border-l-blue-500 bg-blue-500/5'}`}
                          >
                            <span className="text-frost font-bold">
                              {phaseKey.replace(/_/g, ' ').replace(/\bphase\b/gi, 'Phase').replace(/\b\w/g, l => l.toUpperCase())}:
                            </span>{' '}
                            <span className="text-frost-muted">{String(phaseDesc)}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Fuel Management (Canyon Clash) */}
                {selectedEvent.event.fuel_management && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-3">Fuel Management</h3>
                    {selectedEvent.event.fuel_management.critical_rule && (
                      <div className="p-3 rounded bg-amber-500/10 border-2 border-amber-400/50 mb-3">
                        <span className="text-amber-400 font-bold">CRITICAL: </span>
                        <span className="text-frost">{selectedEvent.event.fuel_management.critical_rule}</span>
                      </div>
                    )}
                    {selectedEvent.event.fuel_management.tips && (
                      <ul className="space-y-1">
                        {selectedEvent.event.fuel_management.tips.map((tip: string, i: number) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-frost-muted">
                            <span className="text-ice mt-0.5">-</span>
                            <span>{tip}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}

                {/* Structure (Mercenary Prestige) */}
                {selectedEvent.event.structure && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-3">Event Structure</h3>
                    <div className="space-y-3">
                      {selectedEvent.event.structure.personal_challenge && (
                        <div className="p-3 rounded bg-blue-500/5 border-l-4 border-l-blue-500">
                          <div className="text-blue-400 font-medium text-sm mb-1">Personal Challenge</div>
                          <div className="space-y-1 text-sm text-frost-muted">
                            {Object.entries(selectedEvent.event.structure.personal_challenge).map(([key, value]) => (
                              <p key={key}>
                                <span className="text-frost font-medium">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}: </span>
                                {String(value)}
                              </p>
                            ))}
                          </div>
                        </div>
                      )}
                      {selectedEvent.event.structure.alliance_challenge && (
                        <div className="p-3 rounded bg-purple-500/5 border-l-4 border-l-purple-500">
                          <div className="text-purple-400 font-medium text-sm mb-1">
                            {selectedEvent.event.structure.alliance_challenge.name || 'Alliance Challenge'}
                          </div>
                          <div className="space-y-1 text-sm text-frost-muted">
                            {Object.entries(selectedEvent.event.structure.alliance_challenge).filter(([k]) => k !== 'name').map(([key, value]) => (
                              <p key={key}>
                                <span className="text-frost font-medium">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}: </span>
                                {String(value)}
                              </p>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Stamina Costs (Mercenary Prestige) */}
                {selectedEvent.event.stamina_costs && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-2">Stamina Costs</h3>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      {Object.entries(selectedEvent.event.stamina_costs).map(([key, value]) => (
                        <div key={key} className="p-2 rounded bg-surface">
                          <span className="text-frost-muted text-xs">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                          <div className="text-frost font-medium">{String(value)}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Zones (Labyrinth) */}
                {selectedEvent.event.zones && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-2">Zones</h3>
                    <div className="flex flex-wrap gap-1">
                      {selectedEvent.event.zones.map((zone: string, i: number) => (
                        <span key={i} className="px-2 py-1 bg-purple-500/10 text-purple-300 text-xs rounded border border-purple-500/20">
                          {zone}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Stat Bonuses (Tundra Album) */}
                {selectedEvent.event.stat_bonuses && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-2">Stat Bonuses</h3>
                    {selectedEvent.event.stat_bonuses.types && (
                      <div className="flex flex-wrap gap-1 mb-2">
                        {selectedEvent.event.stat_bonuses.types.map((type: string, i: number) => (
                          <span key={i} className="px-2 py-1 bg-green-500/10 text-green-400 text-xs rounded">
                            {type}
                          </span>
                        ))}
                      </div>
                    )}
                    {selectedEvent.event.stat_bonuses.note && (
                      <p className="text-frost-muted text-xs">{selectedEvent.event.stat_bonuses.note}</p>
                    )}
                  </div>
                )}

                {/* F2P Strategy */}
                {selectedEvent.event.f2p_strategy && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-2">F2P Strategy</h3>
                    {selectedEvent.event.f2p_strategy.focus_stages && (
                      <p className="text-sm mb-2">
                        <span className="text-frost font-medium">Focus on: </span>
                        <span className="text-green-400">{selectedEvent.event.f2p_strategy.focus_stages.join(', ')}</span>
                      </p>
                    )}
                    {selectedEvent.event.f2p_strategy.tips && (
                      <ul className="space-y-1">
                        {selectedEvent.event.f2p_strategy.tips.map((tip: string, i: number) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-frost-muted">
                            <span className="text-green-400 mt-0.5">-</span>
                            <span>{tip}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}

                {/* Preparation Tips */}
                {selectedEvent.event.preparation?.tips && selectedEvent.event.preparation.tips.length > 0 && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-2">Tips</h3>
                    <ul className="space-y-1">
                      {selectedEvent.event.preparation.tips.map((tip, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-frost-muted">
                          <span className="text-ice mt-0.5">-</span>
                          <span>{tip}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* What to Save */}
                {selectedEvent.event.preparation?.save_before && selectedEvent.event.preparation.save_before.length > 0 && (
                  <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30">
                    <span className="text-red-400 font-medium text-sm">Save Before: </span>
                    <span className="text-frost-muted text-sm">
                      {selectedEvent.event.preparation.save_before.join(', ')}
                    </span>
                  </div>
                )}

                {/* Notes */}
                {selectedEvent.event.notes && (
                  <div className="p-3 rounded-lg bg-ice/10 border border-ice/30">
                    <p className="text-sm text-ice">{selectedEvent.event.notes}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
        </>}
      </div>
    </PageLayout>
  );
}
