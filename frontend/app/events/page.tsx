'use client';

import { useState } from 'react';
import PageLayout from '@/components/PageLayout';

interface Event {
  name: string;
  description: string;
  frequency: string;
  tips: string[];
  rewards: string[];
}

const events: Event[] = [
  {
    name: 'SvS (State vs State)',
    description: 'Week-long competition against another state',
    frequency: 'Every 2 weeks',
    tips: [
      'Speedups only give points on Day 1, 2, and 5',
      'Fire Crystals: 2,000 points each (Day 1)',
      'Lucky Wheel: 8,000 points per spin',
      'Mithril: 40,000 points each (Day 4)',
      'ALWAYS shield before going offline',
    ],
    rewards: ['Prestige', 'Exclusive skins', 'Titles', 'Resources'],
  },
  {
    name: 'Bear Trap',
    description: 'Alliance event - defeat the Bear boss',
    frequency: 'Weekly',
    tips: [
      'Use 0/10/90 troop ratio (marksman heavy)',
      'Bear moves slowly - maximize ranged damage',
      'Put Jessie first for ATK buff',
      'Coordinate with alliance on timing',
    ],
    rewards: ['Bear Trap tokens', 'Hero shards', 'Speedups'],
  },
  {
    name: 'Crazy Joe',
    description: 'Alliance event - defeat Crazy Joe',
    frequency: 'Weekly',
    tips: [
      'Use 90/10/0 troop ratio (infantry heavy)',
      'Kill Joe before his backline attacks',
      'Infantry-focused lineup recommended',
      'Speed is key - coordinate attacks',
    ],
    rewards: ['Crazy Joe tokens', 'Hero shards', 'Resources'],
  },
  {
    name: 'Frost Star Event',
    description: 'Resource gathering competition',
    frequency: 'Monthly',
    tips: [
      'Save speedups for this event',
      'Pre-build troops before event starts',
      'Focus on highest point activities',
      'Coordinate with alliance',
    ],
    rewards: ['Frost Stars', 'Hero shards', 'Premium items'],
  },
  {
    name: 'Lucky Wheel',
    description: 'Spin for random rewards',
    frequency: 'During SvS',
    tips: [
      '8,000 SvS points per spin',
      'Save coins for SvS days 2-3',
      'Can get hero shards and rare items',
      'Don\'t spin outside of SvS unless whale',
    ],
    rewards: ['Hero shards', 'Speedups', 'Resources', 'Premium items'],
  },
  {
    name: 'Troop Promotion',
    description: 'Promote troops to higher tiers',
    frequency: 'SvS Day 4',
    tips: [
      'Better points than speedups on Day 4',
      'Pre-train troops before event',
      'Focus on your main troop type',
      'Massive point potential',
    ],
    rewards: ['SvS points', 'Stronger troops'],
  },
];

export default function EventsPage() {
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Events</h1>
          <p className="text-frost-muted mt-2">Event calendar and strategy guides</p>
        </div>

        {/* SvS Day Reference */}
        <div className="card mb-6 border-fire/30 bg-gradient-to-r from-fire/10 to-fire/5">
          <h2 className="section-header text-fire">SvS Point Reference</h2>
          <div className="grid grid-cols-5 gap-2 text-center">
            <div className="p-3 rounded-lg bg-surface">
              <p className="font-bold text-frost">Day 1</p>
              <p className="text-xs text-frost-muted">Speedups</p>
              <p className="text-xs text-frost-muted">Fire Crystals</p>
            </div>
            <div className="p-3 rounded-lg bg-surface">
              <p className="font-bold text-frost">Day 2</p>
              <p className="text-xs text-frost-muted">Speedups</p>
              <p className="text-xs text-frost-muted">Lucky Wheel</p>
            </div>
            <div className="p-3 rounded-lg bg-surface">
              <p className="font-bold text-frost">Day 3</p>
              <p className="text-xs text-frost-muted">Lucky Wheel</p>
              <p className="text-xs text-frost-muted">Exploration</p>
            </div>
            <div className="p-3 rounded-lg bg-surface">
              <p className="font-bold text-frost">Day 4</p>
              <p className="text-xs text-frost-muted">Troop Promo</p>
              <p className="text-xs text-frost-muted">Mithril</p>
            </div>
            <div className="p-3 rounded-lg bg-surface">
              <p className="font-bold text-frost">Day 5</p>
              <p className="text-xs text-frost-muted">Speedups</p>
              <p className="text-xs text-frost-muted">Final Push</p>
            </div>
          </div>
        </div>

        {/* Events Grid */}
        <div className="grid md:grid-cols-2 gap-4">
          {events.map((event) => (
            <button
              key={event.name}
              onClick={() => setSelectedEvent(event)}
              className="card text-left hover:border-ice/30 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-bold text-frost">{event.name}</h3>
                  <p className="text-sm text-frost-muted mt-1">{event.description}</p>
                </div>
                <span className="badge-secondary text-xs">{event.frequency}</span>
              </div>
              <p className="text-xs text-ice mt-3">Click for tips →</p>
            </button>
          ))}
        </div>

        {/* Event Detail Modal */}
        {selectedEvent && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-surface rounded-xl border border-surface-border max-w-lg w-full p-6 animate-fadeIn">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-xl font-bold text-frost">{selectedEvent.name}</h2>
                  <p className="text-sm text-frost-muted">{selectedEvent.frequency}</p>
                </div>
                <button
                  onClick={() => setSelectedEvent(null)}
                  className="text-frost-muted hover:text-frost"
                >
                  ✕
                </button>
              </div>

              <p className="text-frost-muted mb-4">{selectedEvent.description}</p>

              <div className="mb-4">
                <h3 className="font-medium text-frost mb-2">Tips</h3>
                <ul className="space-y-1">
                  {selectedEvent.tips.map((tip, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-frost-muted">
                      <span className="text-ice">•</span>
                      <span>{tip}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="font-medium text-frost mb-2">Rewards</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedEvent.rewards.map((reward, i) => (
                    <span key={i} className="badge-secondary text-xs">
                      {reward}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </PageLayout>
  );
}
