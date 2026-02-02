'use client';

import { useState, useEffect } from 'react';
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

export default function EventsPage() {
  const [eventsGuide, setEventsGuide] = useState<EventsGuide | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedEvent, setSelectedEvent] = useState<{ id: string; event: Event } | null>(null);
  const [filterF2P, setFilterF2P] = useState<boolean>(false);
  const [filterPriority, setFilterPriority] = useState<string>('all');

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
    return eventsGuide?.cost_categories[category]?.label || category.replace('_', ' ');
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
        <div className="card mb-6 bg-gradient-to-r from-surface to-surface-hover">
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
        </div>

        {/* Category Tabs */}
        <div className="flex flex-wrap gap-2 mb-4">
          {Object.entries(EVENT_CATEGORIES).map(([key, cat]) => (
            <button
              key={key}
              onClick={() => setSelectedCategory(key)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                selectedCategory === key
                  ? 'bg-ice text-zinc-900'
                  : 'bg-surface text-frost-muted hover:text-frost'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

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
            <div className="text-4xl mb-4">⚠️</div>
            <h3 className="text-lg font-medium text-frost mb-2">Unable to load events</h3>
            <p className="text-frost-muted">Make sure the API server is running</p>
          </div>
        ) : filteredEvents.length === 0 ? (
          <div className="card text-center py-12">
            <div className="text-4xl mb-4">📅</div>
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
                        <span>{event.type.charAt(0).toUpperCase() + event.type.slice(1)}</span>
                        <span>•</span>
                        <span>{event.frequency}</span>
                        {event.duration && (
                          <>
                            <span>•</span>
                            <span>{event.duration}</span>
                          </>
                        )}
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      <span className={`px-2 py-1 rounded text-xs ${getCostColor(event.cost_category)}`}>
                        {getCostLabel(event.cost_category)}
                      </span>
                      <span className="text-xs text-ice">Details →</span>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        )}

        {/* Event Detail Modal */}
        {selectedEvent && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-surface rounded-xl border border-surface-border max-w-2xl w-full max-h-[90vh] overflow-y-auto animate-fadeIn">
              {/* Modal Header */}
              <div className="sticky top-0 bg-surface border-b border-surface-border/50 p-4 flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h2 className="text-xl font-bold text-frost">{selectedEvent.event.name}</h2>
                    <span className={`px-1.5 py-0.5 rounded text-xs font-bold ${getPriorityColor(selectedEvent.event.priority)}`}>
                      {selectedEvent.event.priority}
                    </span>
                  </div>
                  <p className="text-sm text-frost-muted">
                    {selectedEvent.event.type.charAt(0).toUpperCase() + selectedEvent.event.type.slice(1)} • {selectedEvent.event.frequency}
                    {selectedEvent.event.duration && ` • ${selectedEvent.event.duration}`}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedEvent(null)}
                  className="text-frost-muted hover:text-frost text-xl leading-none p-1"
                >
                  ×
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
                    {selectedEvent.event.rewards.backpack_items && (
                      <p className="text-xs text-frost-muted mt-2">
                        Backpack: {selectedEvent.event.rewards.backpack_items.join(', ')}
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
                  </div>
                )}

                {/* Wave Mechanics */}
                {selectedEvent.event.wave_mechanics && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-3">Wave Mechanics</h3>
                    <div className="space-y-2">
                      {Object.entries(selectedEvent.event.wave_mechanics).map(([key, value]) => {
                        const isHighlight = key.includes('online') || key.includes('high_value');
                        return (
                          <div
                            key={key}
                            className={`p-2 rounded text-sm ${
                              isHighlight ? 'bg-amber-500/10 border border-amber-500/30' : 'bg-surface'
                            }`}
                          >
                            <span className={`font-medium ${isHighlight ? 'text-amber-400' : 'text-frost'}`}>
                              {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                            </span>{' '}
                            <span className="text-frost-muted">{value}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Phases (SvS Prep days etc.) */}
                {selectedEvent.event.phases && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-3">Phase Breakdown</h3>
                    <div className="space-y-3">
                      {Object.entries(selectedEvent.event.phases).map(([phaseKey, phase]: [string, any]) => (
                        <details key={phaseKey} className="group">
                          <summary className="cursor-pointer p-3 rounded-lg bg-surface hover:bg-surface-hover transition-colors flex items-center justify-between">
                            <div>
                              <span className="font-medium text-frost">{phase.name || phaseKey}</span>
                              {phase.focus && <span className="text-xs text-frost-muted ml-2">- {phase.focus}</span>}
                            </div>
                            <svg className="w-4 h-4 text-frost-muted group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                          </summary>
                          <div className="mt-2 pl-3 space-y-2">
                            {/* Best value tasks */}
                            {phase.best_value_tasks && (
                              <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                  <thead>
                                    <tr className="text-frost-muted border-b border-border">
                                      <th className="text-left py-1 pr-3">Task</th>
                                      <th className="text-right py-1 pr-3">Points</th>
                                      <th className="text-right py-1">Per</th>
                                    </tr>
                                  </thead>
                                  <tbody className="text-frost">
                                    {phase.best_value_tasks.map((task: any, i: number) => (
                                      <tr key={i} className="border-b border-border/30">
                                        <td className="py-1 pr-3">{task.task}</td>
                                        <td className="py-1 pr-3 text-right font-medium text-amber">{typeof task.points === 'number' ? task.points.toLocaleString() : task.points}</td>
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
                                  <p className="text-sm text-amber p-2 rounded bg-amber/10 border border-amber/30">
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
                                <h4 className="text-xs font-semibold text-amber uppercase tracking-wide">Speedup vs Promotion Analysis</h4>
                                <p className="text-sm text-frost-muted">{phase.efficiency_analysis.description}</p>
                                {phase.efficiency_analysis.optimal_strategy && (
                                  <ul className="space-y-1">
                                    {phase.efficiency_analysis.optimal_strategy.map((step: string, i: number) => (
                                      <li key={i} className="flex items-start gap-2 text-sm text-frost-muted">
                                        <span className="text-amber mt-0.5">{i+1}.</span>
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
                                <span className="text-xs text-fire font-medium">Save:</span>
                                {phase.save_for_this_day.map((item: string, i: number) => (
                                  <span key={i} className="text-xs px-1.5 py-0.5 rounded bg-fire/10 text-fire/80">{item}</span>
                                ))}
                              </div>
                            )}

                            {/* Note */}
                            {phase.note && (
                              <p className="text-xs text-amber mt-1">{phase.note}</p>
                            )}
                          </div>
                        </details>
                      ))}
                    </div>
                  </div>
                )}

                {/* Preparation Tips */}
                {selectedEvent.event.preparation?.tips && (
                  <div className="card bg-background">
                    <h3 className="text-sm font-medium text-frost mb-2">Tips</h3>
                    <ul className="space-y-1">
                      {selectedEvent.event.preparation.tips.map((tip, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-frost-muted">
                          <span className="text-ice mt-0.5">•</span>
                          <span>{tip}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* What to Save */}
                {selectedEvent.event.preparation?.save_before && (
                  <div className="p-3 rounded-lg bg-fire/10 border border-fire/30">
                    <span className="text-fire font-medium text-sm">Save Before: </span>
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
      </div>
    </PageLayout>
  );
}
