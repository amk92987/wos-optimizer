'use client';

import { useState, useEffect } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';

interface LineupHero {
  hero: string;
  hero_class: string;
  slot: string;
  role: string;
  is_lead: boolean;
  status: string;
  power: number;
}

interface TroopRatio {
  infantry: number;
  lancer: number;
  marksman: number;
}

interface LineupResponse {
  game_mode: string;
  heroes: LineupHero[];
  troop_ratio: TroopRatio;
  notes: string;
  confidence: string;
  recommended_to_get: Array<{ hero: string; reason: string }>;
}

interface LineupTemplate {
  name: string;
  troop_ratio: TroopRatio;
  notes: string;
  key_heroes: string[];
  ratio_explanation: string;
  hero_explanations?: Record<string, string>;
}

interface JoinerRecommendation {
  hero: string | null;
  status: string;
  skill_level: number | null;
  max_skill: number;
  recommendation: string;
  action: string;
  critical_note: string;
}

interface EventType {
  id: string;
  name: string;
  icon: string;
}

const eventTypes: EventType[] = [
  { id: 'bear_trap', name: 'Bear Trap', icon: '🐻' },
  { id: 'crazy_joe', name: 'Crazy Joe', icon: '🤪' },
  { id: 'garrison', name: 'Garrison Defense', icon: '🏰' },
  { id: 'svs_attack', name: 'SvS March', icon: '⚔️' },
  { id: 'rally_attack', name: 'Rally Attack', icon: '🎯' },
  { id: 'rally_defense', name: 'Garrison Support', icon: '🛡️' },
];

type TabType = 'optimal' | 'joiner' | 'reference';

export default function LineupsPage() {
  const { token, user } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('optimal');
  const [selectedEvent, setSelectedEvent] = useState('bear_trap');
  const [selectedGeneration, setSelectedGeneration] = useState(8);
  const [personalizedLineup, setPersonalizedLineup] = useState<LineupResponse | null>(null);
  const [generalLineup, setGeneralLineup] = useState<LineupResponse | null>(null);
  const [templates, setTemplates] = useState<Record<string, LineupTemplate>>({});
  const [templateDetails, setTemplateDetails] = useState<LineupTemplate | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [joinerAttack, setJoinerAttack] = useState<JoinerRecommendation | null>(null);
  const [joinerDefense, setJoinerDefense] = useState<JoinerRecommendation | null>(null);

  // Fetch templates on mount
  useEffect(() => {
    fetchTemplates();
  }, []);

  // Fetch lineup when event changes
  useEffect(() => {
    if (token) {
      fetchPersonalizedLineup();
    } else {
      fetchGeneralLineup();
    }
    fetchTemplateDetails();
  }, [selectedEvent, selectedGeneration, token]);

  // Fetch joiner recommendations when tab changes
  useEffect(() => {
    if (activeTab === 'joiner' && token) {
      fetchJoinerRecommendations();
    }
  }, [activeTab, token]);

  const fetchTemplates = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/lineups/templates');
      if (res.ok) {
        setTemplates(await res.json());
      }
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    }
  };

  const fetchTemplateDetails = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/lineups/template/${selectedEvent}`);
      if (res.ok) {
        setTemplateDetails(await res.json());
      }
    } catch (error) {
      console.error('Failed to fetch template details:', error);
    }
  };

  const fetchPersonalizedLineup = async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/lineups/build/${selectedEvent}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setPersonalizedLineup(await res.json());
      }
    } catch (error) {
      console.error('Failed to fetch personalized lineup:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchGeneralLineup = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(
        `http://localhost:8000/api/lineups/general/${selectedEvent}?max_generation=${selectedGeneration}`
      );
      if (res.ok) {
        setGeneralLineup(await res.json());
      }
    } catch (error) {
      console.error('Failed to fetch general lineup:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchJoinerRecommendations = async () => {
    if (!token) return;
    try {
      const [attackRes, defenseRes] = await Promise.all([
        fetch('http://localhost:8000/api/lineups/joiner/attack', {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch('http://localhost:8000/api/lineups/joiner/defense', {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);
      if (attackRes.ok) setJoinerAttack(await attackRes.json());
      if (defenseRes.ok) setJoinerDefense(await defenseRes.json());
    } catch (error) {
      console.error('Failed to fetch joiner recommendations:', error);
    }
  };

  const currentLineup = token ? personalizedLineup : generalLineup;

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-frost">Lineup Builder</h1>
            <p className="text-frost-muted mt-2">Optimal hero compositions for every event</p>
          </div>
          {!token && (
            <div>
              <label className="text-xs text-frost-muted block mb-1">Your Generation</label>
              <select
                value={selectedGeneration}
                onChange={(e) => setSelectedGeneration(Number(e.target.value))}
                className="input w-32"
              >
                {[...Array(14)].map((_, i) => (
                  <option key={i + 1} value={i + 1}>
                    Gen {i + 1}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Login prompt for personalized recommendations */}
        {!token && (
          <div className="card mb-6 border-ice/30 bg-ice/5">
            <div className="flex items-center gap-3">
              <span className="text-2xl">💡</span>
              <div>
                <p className="text-frost">Want personalized recommendations based on YOUR heroes?</p>
                <p className="text-sm text-frost-muted mt-1">
                  Log in and add your heroes in the Hero Tracker for customized lineups.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-surface-border pb-2 overflow-x-auto">
          {[
            { id: 'optimal' as const, label: 'Optimal Lineups' },
            { id: 'joiner' as const, label: 'Rally Joiner Guide' },
            { id: 'reference' as const, label: 'Quick Reference' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
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
            lineup={currentLineup}
            template={templateDetails}
            isLoading={isLoading}
            isPersonalized={!!token}
          />
        )}
        {activeTab === 'joiner' && (
          <RallyJoinerGuideTab
            token={token}
            joinerAttack={joinerAttack}
            joinerDefense={joinerDefense}
          />
        )}
        {activeTab === 'reference' && <ReferenceTab templates={templates} />}
      </div>
    </PageLayout>
  );
}

function OptimalLineupsTab({
  eventTypes,
  selectedEvent,
  setSelectedEvent,
  lineup,
  template,
  isLoading,
  isPersonalized,
}: {
  eventTypes: EventType[];
  selectedEvent: string;
  setSelectedEvent: (id: string) => void;
  lineup: LineupResponse | null;
  template: LineupTemplate | null;
  isLoading: boolean;
  isPersonalized: boolean;
}) {
  const [showExplanation, setShowExplanation] = useState(false);

  const troopRatio = lineup?.troop_ratio || template?.troop_ratio || { infantry: 50, lancer: 20, marksman: 30 };

  return (
    <>
      {/* Event Selection */}
      <div className="card mb-6">
        <h2 className="section-header">Select Event Type</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {eventTypes.map((event: EventType) => (
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
        <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
          <h2 className="text-xl font-bold text-frost">{template?.name || selectedEvent}</h2>
          <div className="flex items-center gap-2">
            {isPersonalized && (
              <span className="badge badge-success text-xs">Personalized</span>
            )}
            {lineup?.confidence && (
              <span className="badge badge-info text-xs">{lineup.confidence} confidence</span>
            )}
          </div>
        </div>

        {/* Heroes */}
        {isLoading ? (
          <div className="flex gap-3 mb-6">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="flex-1 p-3 rounded-lg bg-surface animate-pulse">
                <div className="w-12 h-12 mx-auto mb-2 bg-surface-hover rounded-full" />
                <div className="h-4 bg-surface-hover rounded w-20 mx-auto" />
              </div>
            ))}
          </div>
        ) : lineup?.heroes && lineup.heroes.length > 0 ? (
          <div className="mb-6">
            <h3 className="text-sm font-medium text-frost-muted mb-3">
              {isPersonalized ? 'Your Best Heroes' : 'Recommended Heroes'}
            </h3>
            <div className="flex gap-3 flex-wrap">
              {lineup.heroes.map((hero, i) => (
                <div
                  key={hero.hero}
                  className={`flex-1 min-w-[120px] p-3 rounded-lg text-center ${
                    hero.is_lead ? 'bg-fire/20 border border-fire/30' : 'bg-surface'
                  }`}
                >
                  <div className="w-12 h-12 mx-auto mb-2 bg-surface-hover rounded-full flex items-center justify-center">
                    <span className="text-xl">
                      {hero.hero_class === 'Infantry' ? '🛡️' : hero.hero_class === 'Lancer' ? '⚔️' : '🏹'}
                    </span>
                  </div>
                  <p className="text-sm font-medium text-frost">{hero.hero}</p>
                  <p className="text-xs text-frost-muted">{hero.hero_class}</p>
                  {hero.status && (
                    <p className="text-xs text-success mt-1">{hero.status}</p>
                  )}
                  {hero.is_lead && <p className="text-xs text-fire mt-1">Lead</p>}
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="mb-6 p-4 rounded-lg bg-warning/10 border border-warning/30">
            <p className="text-sm text-frost">
              Add heroes in the Hero Tracker to see personalized recommendations.
            </p>
          </div>
        )}

        {/* Troop Ratio */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-frost-muted mb-3">Troop Ratio</h3>
          <div className="flex gap-1 h-8 rounded-lg overflow-hidden">
            {troopRatio.infantry > 0 && (
              <div
                className="bg-red-500 flex items-center justify-center text-xs font-bold text-white"
                style={{ width: `${troopRatio.infantry}%` }}
              >
                {troopRatio.infantry}%
              </div>
            )}
            {troopRatio.lancer > 0 && (
              <div
                className="bg-green-500 flex items-center justify-center text-xs font-bold text-white"
                style={{ width: `${troopRatio.lancer}%` }}
              >
                {troopRatio.lancer}%
              </div>
            )}
            {troopRatio.marksman > 0 && (
              <div
                className="bg-blue-500 flex items-center justify-center text-xs font-bold text-white"
                style={{ width: `${troopRatio.marksman}%` }}
              >
                {troopRatio.marksman}%
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
          <p className="text-sm text-frost">💡 {lineup?.notes || template?.notes || 'Select an event to see recommendations.'}</p>
        </div>

        {/* Why This Lineup - Expandable */}
        {template?.hero_explanations && Object.keys(template.hero_explanations).length > 0 && (
          <div className="mt-4">
            <button
              onClick={() => setShowExplanation(!showExplanation)}
              className="flex items-center gap-2 text-sm text-ice hover:text-ice/80"
            >
              <span>{showExplanation ? '▼' : '▶'}</span>
              Why This Lineup?
            </button>
            {showExplanation && (
              <div className="mt-3 p-4 rounded-lg bg-surface">
                <h4 className="text-sm font-medium text-frost mb-2">Hero Explanations</h4>
                <ul className="space-y-2 text-sm text-frost-muted">
                  {Object.entries(template.hero_explanations).map(([hero, explanation]) => (
                    <li key={hero}>
                      <strong className="text-frost">{hero}:</strong> {explanation}
                    </li>
                  ))}
                </ul>
                {template.ratio_explanation && (
                  <>
                    <h4 className="text-sm font-medium text-frost mt-4 mb-2">Troop Ratio</h4>
                    <p className="text-sm text-frost-muted">{template.ratio_explanation}</p>
                  </>
                )}
              </div>
            )}
          </div>
        )}

        {/* Recommended to Get */}
        {lineup?.recommended_to_get && lineup.recommended_to_get.length > 0 && (
          <div className="mt-4 p-4 rounded-lg bg-warning/10 border border-warning/30">
            <h4 className="text-sm font-medium text-warning mb-2">Recommended to Unlock</h4>
            <ul className="space-y-1 text-sm text-frost-muted">
              {lineup.recommended_to_get.map((rec, i) => (
                <li key={i}>
                  <strong className="text-frost">{rec.hero}:</strong> {rec.reason}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </>
  );
}

function RallyJoinerGuideTab({
  token,
  joinerAttack,
  joinerDefense,
}: {
  token: string | null;
  joinerAttack: JoinerRecommendation | null;
  joinerDefense: JoinerRecommendation | null;
}) {
  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="section-header">Rally Joiner Mechanics</h2>
        <div className="p-4 rounded-lg bg-error/10 border border-error/30 mb-4">
          <p className="text-sm text-frost">
            <strong>CRITICAL:</strong> When joining a rally, <strong className="text-ice">ONLY your leftmost hero's expedition skill matters!</strong>
          </p>
          <p className="text-xs text-frost-muted mt-2">
            Your 2nd and 3rd heroes contribute nothing except troop capacity. Choose slot 1 wisely.
          </p>
        </div>
        <div className="space-y-2 text-sm text-frost-muted">
          <p>
            <strong className="text-frost">Skill Level Priority:</strong> Only the top 4 highest LEVEL
            expedition skills from all joiners apply to the rally.
          </p>
        </div>
      </div>

      {/* Personalized Joiner Recommendations */}
      {token && (joinerAttack || joinerDefense) && (
        <div className="card">
          <h2 className="section-header">Your Joiner Setup</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {/* Attack */}
            <div className={`p-4 rounded-lg ${joinerAttack?.hero ? 'bg-success/10 border border-success/20' : 'bg-warning/10 border border-warning/20'}`}>
              <h3 className="font-medium text-frost mb-3">For Attack Rallies</h3>
              {joinerAttack?.hero ? (
                <>
                  <div className="p-3 rounded bg-surface mb-3">
                    <p className="font-medium text-frost">{joinerAttack.hero}</p>
                    <p className="text-xs text-frost-muted">
                      Skill Level: {joinerAttack.skill_level}/{joinerAttack.max_skill}
                    </p>
                  </div>
                  <p className="text-sm text-frost-muted">{joinerAttack.recommendation}</p>
                  {joinerAttack.action && (
                    <p className="text-xs text-success mt-2">{joinerAttack.action}</p>
                  )}
                </>
              ) : (
                <p className="text-sm text-warning">{joinerAttack?.critical_note || 'No attack joiner found'}</p>
              )}
            </div>

            {/* Defense */}
            <div className={`p-4 rounded-lg ${joinerDefense?.hero ? 'bg-ice/10 border border-ice/20' : 'bg-warning/10 border border-warning/20'}`}>
              <h3 className="font-medium text-frost mb-3">For Garrison Defense</h3>
              {joinerDefense?.hero ? (
                <>
                  <div className="p-3 rounded bg-surface mb-3">
                    <p className="font-medium text-frost">{joinerDefense.hero}</p>
                    <p className="text-xs text-frost-muted">
                      Skill Level: {joinerDefense.skill_level}/{joinerDefense.max_skill}
                    </p>
                  </div>
                  <p className="text-sm text-frost-muted">{joinerDefense.recommendation}</p>
                  {joinerDefense.action && (
                    <p className="text-xs text-ice mt-2">{joinerDefense.action}</p>
                  )}
                </>
              ) : (
                <p className="text-sm text-warning">{joinerDefense?.critical_note || 'No defense joiner found'}</p>
              )}
            </div>
          </div>
        </div>
      )}

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
                <p className="font-medium text-frost">Hervor (Gen 12)</p>
                <p className="text-xs text-frost-muted">Call For Blood: +5-25% DMG dealt</p>
                <p className="text-xs text-frost-muted mt-1">Equivalent to Jessie - use higher skill level</p>
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
                <p className="font-medium text-frost">Karol (Gen 12)</p>
                <p className="text-xs text-frost-muted">In the Wings: -4-20% DMG taken</p>
                <p className="text-xs text-frost-muted mt-1">Equivalent to Sergey - use higher skill level</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="section-header">Investment Priority</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border">
                <th className="text-left p-2 text-frost-muted">Priority</th>
                <th className="text-left p-2 text-frost-muted">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-surface-border/50">
                <td className="p-2 text-success">HIGH</td>
                <td className="p-2 text-frost">Level up Jessie/Sergey's expedition skill (right side)</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="p-2 text-warning">Medium</td>
                <td className="p-2 text-frost">Get them to functional gear (Legendary is fine)</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="p-2 text-error">LOW</td>
                <td className="p-2 text-frost">Don't waste premium resources on joiners</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p className="text-xs text-frost-muted mt-3">
          Only the skill level determines their contribution. Hero level, stars, and gear don't affect the rally buff.
        </p>
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

function ReferenceTab({ templates }: { templates: Record<string, LineupTemplate> }) {
  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="section-header">Troop Ratio Quick Reference</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border">
                <th className="text-left p-2 text-frost-muted">Situation</th>
                <th className="text-center p-2 text-red-400">Infantry</th>
                <th className="text-center p-2 text-green-400">Lancer</th>
                <th className="text-center p-2 text-blue-400">Marksman</th>
                <th className="text-left p-2 text-frost-muted">Notes</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-surface-border/50">
                <td className="p-2 text-frost font-medium">Castle / SvS</td>
                <td className="p-2 text-center">50%</td>
                <td className="p-2 text-center">20%</td>
                <td className="p-2 text-center">30%</td>
                <td className="p-2 text-frost-muted">Balanced for castle attacks</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="p-2 text-frost font-medium">Bear Trap</td>
                <td className="p-2 text-center">0%</td>
                <td className="p-2 text-center">10%</td>
                <td className="p-2 text-center">90%</td>
                <td className="p-2 text-frost-muted">Maximize ranged DPS</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="p-2 text-frost font-medium">Crazy Joe</td>
                <td className="p-2 text-center">90%</td>
                <td className="p-2 text-center">10%</td>
                <td className="p-2 text-center">0%</td>
                <td className="p-2 text-frost-muted">Kill before backline attacks</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="p-2 text-frost font-medium">Garrison Defense</td>
                <td className="p-2 text-center">60%</td>
                <td className="p-2 text-center">20%</td>
                <td className="p-2 text-center">20%</td>
                <td className="p-2 text-frost-muted">Heavy Infantry wall</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="p-2 text-frost font-medium">Labyrinth 3v3</td>
                <td className="p-2 text-center">50%</td>
                <td className="p-2 text-center">20%</td>
                <td className="p-2 text-center">30%</td>
                <td className="p-2 text-frost-muted">Standard</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="card">
        <h2 className="section-header">Joiner Skills Reference</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border">
                <th className="text-left p-2 text-frost-muted">Role</th>
                <th className="text-left p-2 text-frost-muted">Best Hero</th>
                <th className="text-left p-2 text-frost-muted">Gen 12+ Alt</th>
                <th className="text-left p-2 text-frost-muted">Skill Effect</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-surface-border/50">
                <td className="p-2 text-success">Attack Joiner</td>
                <td className="p-2 text-frost font-medium">Jessie (Gen 1)</td>
                <td className="p-2 text-frost">Hervor</td>
                <td className="p-2 text-frost-muted">+5/10/15/20/25% DMG dealt</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="p-2 text-ice">Defense Joiner</td>
                <td className="p-2 text-frost font-medium">Sergey (Gen 1)</td>
                <td className="p-2 text-frost">Karol</td>
                <td className="p-2 text-frost-muted">-4/8/12/16/20% DMG taken</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="card">
        <h2 className="section-header">Investment Priority by Spending Level</h2>
        <div className="space-y-4">
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">F2P / Low Spender</h3>
            <p className="text-sm text-frost-muted">
              Focus on 3-4 heroes maximum: Natalia (tank), Alonso (DPS), Molly (healer), Jessie (joiner skill only).
              Join rallies, don't lead them.
            </p>
          </div>
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">Medium Spender</h3>
            <p className="text-sm text-frost-muted">
              Develop 6-9 heroes. Add Flint (Arena), Jeronimo (rallies), Philly (healing).
              Can lead rallies occasionally.
            </p>
          </div>
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">Heavy Spender</h3>
            <p className="text-sm text-frost-muted">
              Develop 12+ heroes with mythic gear on top 6. Lead rallies, compete in all modes.
              Hero diversity wins Championships.
            </p>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="section-header">PvE vs PvP Content</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">PvE (Exploration Skills)</h3>
            <p className="text-sm text-frost-muted mb-2">Fighting against the game:</p>
            <ul className="text-sm text-frost-muted list-disc list-inside">
              <li>Bear Trap, Crazy Joe</li>
              <li>Labyrinth, Exploration</li>
              <li>Uses left-side skills</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">PvP (Expedition Skills)</h3>
            <p className="text-sm text-frost-muted mb-2">Fighting other players:</p>
            <ul className="text-sm text-frost-muted list-disc list-inside">
              <li>Rally Leader/Joiner</li>
              <li>Garrison, SvS, Arena</li>
              <li>Uses right-side skills</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
