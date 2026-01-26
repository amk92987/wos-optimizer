'use client';

import { useState, useEffect } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';

interface LineupSlot {
  position: number;
  heroName: string | null;
  role: string;
}

interface TroopRatio {
  infantry: number;
  lancer: number;
  marksman: number;
}

interface LineupTemplate {
  name: string;
  description: string;
  heroes: string[];
  troops: TroopRatio;
  notes: string;
}

interface SavedLineup {
  id: number;
  name: string;
  event_type: string;
  heroes: string[];
  troops: TroopRatio;
  created_at: string;
}

const eventTypes = [
  { id: 'bear_trap', name: 'Bear Trap', icon: '🐻' },
  { id: 'crazy_joe', name: 'Crazy Joe', icon: '🤪' },
  { id: 'garrison', name: 'Garrison Defense', icon: '🏰' },
  { id: 'svs_march', name: 'SvS March', icon: '⚔️' },
  { id: 'rally_attack', name: 'Rally Attack', icon: '🎯' },
  { id: 'rally_defense', name: 'Rally Defense', icon: '🛡️' },
];

const lineupTemplates: Record<string, LineupTemplate> = {
  bear_trap: {
    name: 'Bear Trap',
    description: 'Bear is slow - maximize marksman DPS',
    heroes: ['Jessie', 'Molly', 'Natalia', 'Sergey', 'Jeronimo'],
    troops: { infantry: 0, lancer: 10, marksman: 90 },
    notes: 'Marksman-heavy because Bear moves slowly. Jessie for ATK buff, Molly for marksman power.',
  },
  crazy_joe: {
    name: 'Crazy Joe',
    description: 'Kill Joe before backline attacks',
    heroes: ['Jeronimo', 'Hector', 'Gatot', 'Wu Ming', 'Jessie'],
    troops: { infantry: 90, lancer: 10, marksman: 0 },
    notes: 'Infantry-heavy to kill Joe quickly before his abilities hit your backline.',
  },
  garrison: {
    name: 'Garrison Defense',
    description: 'Survive incoming rallies',
    heroes: ['Sergey', 'Jeronimo', 'Hector', 'Jessie', 'Natalia'],
    troops: { infantry: 60, lancer: 25, marksman: 15 },
    notes: 'Sergey MUST be first for Defenders Edge skill. Infantry-heavy for defense.',
  },
  svs_march: {
    name: 'SvS March',
    description: 'Balanced field combat',
    heroes: ['Jessie', 'Jeronimo', 'Molly', 'Sergey', 'Natalia'],
    troops: { infantry: 40, lancer: 20, marksman: 40 },
    notes: 'Balanced composition for unpredictable field encounters.',
  },
  rally_attack: {
    name: 'Rally Joiner (Attack)',
    description: 'Support rally leader composition',
    heroes: ['Jessie', 'Molly', 'Jeronimo', 'Natalia', 'Sergey'],
    troops: { infantry: 30, lancer: 20, marksman: 50 },
    notes: 'Put your highest level Jessie FIRST for Stand of Arms buff.',
  },
  rally_defense: {
    name: 'Rally Joiner (Defense)',
    description: 'Support garrison defense',
    heroes: ['Sergey', 'Jeronimo', 'Hector', 'Jessie', 'Natalia'],
    troops: { infantry: 50, lancer: 30, marksman: 20 },
    notes: 'Put Sergey FIRST for Defenders Edge damage reduction.',
  },
};

type TabType = 'optimal' | 'joiner' | 'mylineups' | 'debate';

export default function LineupsPage() {
  const { token } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('optimal');
  const [selectedEvent, setSelectedEvent] = useState('bear_trap');
  const [savedLineups, setSavedLineups] = useState<SavedLineup[]>([]);

  useEffect(() => {
    if (token) {
      fetchSavedLineups();
    }
  }, [token]);

  const fetchSavedLineups = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/lineups', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setSavedLineups(await res.json());
      }
    } catch (error) {
      console.error('Failed to fetch lineups:', error);
    }
  };

  const template = lineupTemplates[selectedEvent];

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Lineup Builder</h1>
          <p className="text-frost-muted mt-2">Optimal hero compositions for every event</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-surface-border pb-2">
          {[
            { id: 'optimal' as const, label: 'Optimal Lineups' },
            { id: 'joiner' as const, label: 'Rally Joiner Guide' },
            { id: 'mylineups' as const, label: 'My Lineups' },
            { id: 'debate' as const, label: 'Natalia vs Jeronimo' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-ice/20 text-ice'
                  : 'text-frost-muted hover:text-frost hover:bg-surface'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === 'optimal' && (
          <OptimalLineupsTab
            eventTypes={eventTypes}
            selectedEvent={selectedEvent}
            setSelectedEvent={setSelectedEvent}
            template={template}
          />
        )}
        {activeTab === 'joiner' && <RallyJoinerGuideTab />}
        {activeTab === 'mylineups' && (
          <MyLineupsTab
            token={token!}
            savedLineups={savedLineups}
            onRefresh={fetchSavedLineups}
          />
        )}
        {activeTab === 'debate' && <DebateTab />}
      </div>
    </PageLayout>
  );
}

function OptimalLineupsTab({
  eventTypes,
  selectedEvent,
  setSelectedEvent,
  template,
}: {
  eventTypes: typeof eventTypes;
  selectedEvent: string;
  setSelectedEvent: (id: string) => void;
  template: LineupTemplate;
}) {
  return (
    <>
      {/* Event Selection */}
      <div className="card mb-6">
        <h2 className="section-header">Select Event Type</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {eventTypes.map((event) => (
            <button
              key={event.id}
              onClick={() => setSelectedEvent(event.id)}
              className={`p-4 rounded-lg text-center transition-all ${
                selectedEvent === event.id
                  ? 'bg-ice/20 border-2 border-ice text-ice'
                  : 'bg-surface border-2 border-transparent text-frost-muted hover:text-frost hover:bg-surface-hover'
              }`}
            >
              <span className="text-2xl block mb-1">{event.icon}</span>
              <span className="text-sm font-medium">{event.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Lineup Display */}
      <div className="card mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-frost">{template.name}</h2>
          <span className="badge-info">{template.description}</span>
        </div>

        {/* Heroes */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-frost-muted mb-3">Recommended Heroes</h3>
          <div className="flex gap-3">
            {template.heroes.map((hero, i) => (
              <div
                key={hero}
                className={`flex-1 p-3 rounded-lg text-center ${
                  i === 0 ? 'bg-fire/20 border border-fire/30' : 'bg-surface'
                }`}
              >
                <div className="w-12 h-12 mx-auto mb-2 bg-surface-hover rounded-full flex items-center justify-center">
                  <span className="text-2xl">🦸</span>
                </div>
                <p className="text-sm font-medium text-frost">{hero}</p>
                {i === 0 && <p className="text-xs text-fire mt-1">Lead</p>}
              </div>
            ))}
          </div>
        </div>

        {/* Troop Ratio */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-frost-muted mb-3">Troop Ratio</h3>
          <div className="flex gap-2 h-8 rounded-lg overflow-hidden">
            {template.troops.infantry > 0 && (
              <div
                className="bg-red-500 flex items-center justify-center text-xs font-bold text-white"
                style={{ width: `${template.troops.infantry}%` }}
              >
                {template.troops.infantry}%
              </div>
            )}
            {template.troops.lancer > 0 && (
              <div
                className="bg-green-500 flex items-center justify-center text-xs font-bold text-white"
                style={{ width: `${template.troops.lancer}%` }}
              >
                {template.troops.lancer}%
              </div>
            )}
            {template.troops.marksman > 0 && (
              <div
                className="bg-blue-500 flex items-center justify-center text-xs font-bold text-white"
                style={{ width: `${template.troops.marksman}%` }}
              >
                {template.troops.marksman}%
              </div>
            )}
          </div>
          <div className="flex justify-center gap-4 mt-2 text-xs text-frost-muted">
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 bg-red-500 rounded" /> Infantry
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 bg-green-500 rounded" /> Lancer
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 bg-blue-500 rounded" /> Marksman
            </span>
          </div>
        </div>

        {/* Notes */}
        <div className="p-4 rounded-lg bg-ice/10 border border-ice/20">
          <p className="text-sm text-frost">💡 {template.notes}</p>
        </div>
      </div>
    </>
  );
}

function RallyJoinerGuideTab() {
  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="section-header">Rally Joiner Mechanics</h2>
        <div className="space-y-4 text-sm text-frost-muted">
          <p>
            <strong className="text-frost">Critical:</strong> When joining a rally, only the{' '}
            <strong className="text-ice">leftmost hero's top-right expedition skill</strong> is used.
          </p>
          <p>
            <strong className="text-frost">Skill Level Priority:</strong> Only the top 4 highest LEVEL
            expedition skills from all joiners apply to the rally.
          </p>
        </div>
      </div>

      <div className="card">
        <h2 className="section-header">Best Joiner Heroes</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-success/10 border border-success/20">
            <h3 className="font-medium text-success mb-3">For Attack Rallies</h3>
            <div className="space-y-3">
              <div className="p-3 rounded bg-surface">
                <p className="font-medium text-frost">Jessie (Gen 1)</p>
                <p className="text-xs text-frost-muted">Stand of Arms: +5-25% DMG dealt</p>
                <p className="text-xs text-success mt-1">Best for Bear Trap, Castle attacks</p>
              </div>
              <div className="p-3 rounded bg-surface">
                <p className="font-medium text-frost">Jeronimo (Gen 1)</p>
                <p className="text-xs text-frost-muted">Infantry ATK buff</p>
                <p className="text-xs text-success mt-1">Good for Crazy Joe</p>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-ice/10 border border-ice/20">
            <h3 className="font-medium text-ice mb-3">For Garrison Defense</h3>
            <div className="space-y-3">
              <div className="p-3 rounded bg-surface">
                <p className="font-medium text-frost">Sergey (Gen 1)</p>
                <p className="text-xs text-frost-muted">Defenders' Edge: -4-20% DMG taken</p>
                <p className="text-xs text-ice mt-1">Essential for all garrison defense</p>
              </div>
              <div className="p-3 rounded bg-surface">
                <p className="font-medium text-frost">Hector (Gen 5)</p>
                <p className="text-xs text-frost-muted">Infantry defense boost</p>
                <p className="text-xs text-ice mt-1">Good secondary tank</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="section-header">Joiner Skill Reference</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border">
                <th className="text-left p-2 text-frost-muted">Hero</th>
                <th className="text-left p-2 text-frost-muted">Gen</th>
                <th className="text-left p-2 text-frost-muted">Top-Right Skill</th>
                <th className="text-left p-2 text-frost-muted">Effect</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-surface-border/50">
                <td className="p-2 font-medium text-frost">Jessie</td>
                <td className="p-2 text-frost-muted">1</td>
                <td className="p-2 text-frost">Stand of Arms</td>
                <td className="p-2 text-success">+5-25% DMG dealt</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="p-2 font-medium text-frost">Sergey</td>
                <td className="p-2 text-frost-muted">1</td>
                <td className="p-2 text-frost">Defenders' Edge</td>
                <td className="p-2 text-ice">-4-20% DMG taken</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="p-2 font-medium text-frost">Jeronimo</td>
                <td className="p-2 text-frost-muted">1</td>
                <td className="p-2 text-frost">Infantry ATK</td>
                <td className="p-2 text-warning">Scales with level</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="p-2 font-medium text-frost">Molly</td>
                <td className="p-2 text-frost-muted">1</td>
                <td className="p-2 text-frost">Marksman ATK</td>
                <td className="p-2 text-warning">Scales with level</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="card border-warning/30 bg-warning/5">
        <h2 className="section-header">Common Mistakes</h2>
        <ul className="space-y-2 text-sm text-frost-muted">
          <li className="flex items-start gap-2">
            <span className="text-warning">✗</span>
            <span>Putting Sergey first for attack rallies (his skill is defensive)</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-warning">✗</span>
            <span>Putting Jessie first for garrison defense (her skill is offensive)</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-warning">✗</span>
            <span>Not leveling expedition skills on joiner heroes</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-warning">✗</span>
            <span>Sending low-tier troops (always send your best)</span>
          </li>
        </ul>
      </div>
    </div>
  );
}

function MyLineupsTab({
  token,
  savedLineups,
  onRefresh,
}: {
  token: string;
  savedLineups: SavedLineup[];
  onRefresh: () => void;
}) {
  const [isCreating, setIsCreating] = useState(false);

  const handleDelete = async (id: number) => {
    try {
      await fetch(`http://localhost:8000/api/lineups/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      onRefresh();
    } catch (error) {
      console.error('Failed to delete lineup:', error);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="section-header mb-0">Your Saved Lineups</h2>
          <button onClick={() => setIsCreating(true)} className="btn-primary">
            Create Lineup
          </button>
        </div>
        <p className="text-sm text-frost-muted">
          Save custom lineups for quick reference during events.
        </p>
      </div>

      {savedLineups.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-4xl mb-4">📋</div>
          <h3 className="text-lg font-medium text-frost mb-2">No saved lineups</h3>
          <p className="text-frost-muted mb-4">
            Create a custom lineup based on your available heroes
          </p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          {savedLineups.map((lineup) => (
            <div key={lineup.id} className="card">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-medium text-frost">{lineup.name}</h3>
                  <p className="text-xs text-frost-muted">
                    {lineup.event_type} · {formatDate(lineup.created_at)}
                  </p>
                </div>
                <button
                  onClick={() => handleDelete(lineup.id)}
                  className="text-frost-muted hover:text-error"
                >
                  ✕
                </button>
              </div>
              <div className="flex gap-2 mb-3">
                {lineup.heroes.map((hero, i) => (
                  <span
                    key={i}
                    className={`px-2 py-1 rounded text-xs ${
                      i === 0 ? 'bg-fire/20 text-fire' : 'bg-surface text-frost-muted'
                    }`}
                  >
                    {hero}
                  </span>
                ))}
              </div>
              <div className="flex gap-1 h-4 rounded overflow-hidden">
                {lineup.troops.infantry > 0 && (
                  <div className="bg-red-500" style={{ width: `${lineup.troops.infantry}%` }} />
                )}
                {lineup.troops.lancer > 0 && (
                  <div className="bg-green-500" style={{ width: `${lineup.troops.lancer}%` }} />
                )}
                {lineup.troops.marksman > 0 && (
                  <div className="bg-blue-500" style={{ width: `${lineup.troops.marksman}%` }} />
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal - simplified for now */}
      {isCreating && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-surface rounded-xl border border-surface-border max-w-md w-full p-6 animate-fadeIn">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-frost">Create Lineup</h2>
              <button onClick={() => setIsCreating(false)} className="text-frost-muted hover:text-frost">
                ✕
              </button>
            </div>
            <p className="text-frost-muted text-sm mb-4">
              This feature is coming soon. Use the Optimal Lineups tab as a reference for now.
            </p>
            <button onClick={() => setIsCreating(false)} className="btn-secondary w-full">
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function DebateTab() {
  return (
    <div className="card">
      <h2 className="section-header">The Great Debate: Natalia vs Jeronimo</h2>
      <p className="text-frost-muted mb-6">
        A common question among players - which Gen 1 hero deserves your investment?
      </p>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Natalia */}
        <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
          <h3 className="text-lg font-bold text-blue-400 mb-3">🏹 Natalia (Marksman)</h3>
          <ul className="space-y-2 text-sm text-frost-muted">
            <li>✓ High single-target damage</li>
            <li>✓ Great for Bear Trap (slow target)</li>
            <li>✓ Strong expedition skills</li>
            <li>✓ Works well in marksman-heavy lineups</li>
            <li className="text-warning">△ Less effective vs fast enemies</li>
            <li className="text-warning">△ Squishy in garrison</li>
          </ul>
        </div>

        {/* Jeronimo */}
        <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20">
          <h3 className="text-lg font-bold text-red-400 mb-3">⚔️ Jeronimo (Infantry)</h3>
          <ul className="space-y-2 text-sm text-frost-muted">
            <li>✓ Excellent tank and bruiser</li>
            <li>✓ Great for Crazy Joe (quick kill)</li>
            <li>✓ Strong infantry ATK buff</li>
            <li>✓ Versatile across all content</li>
            <li className="text-warning">△ Less burst damage</li>
            <li className="text-warning">△ Needs infantry support</li>
          </ul>
        </div>
      </div>

      <div className="mt-6 p-4 rounded-lg bg-surface">
        <h4 className="font-medium text-frost mb-2">Verdict</h4>
        <p className="text-sm text-frost-muted">
          <strong className="text-frost">Both are excellent investments.</strong> Prioritize based on your playstyle:
        </p>
        <ul className="mt-2 text-sm text-frost-muted list-disc list-inside">
          <li>Rally focus → Jeronimo (infantry rallies dominate)</li>
          <li>Bear Trap focus → Natalia (marksman shreds slow targets)</li>
          <li>Balanced play → Level both, use situationally</li>
        </ul>
      </div>
    </div>
  );
}
