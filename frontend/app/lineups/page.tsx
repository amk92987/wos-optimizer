'use client';

import { useState, useEffect, useRef } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';
import { lineupsApi, profileApi, getHeroDataVersion } from '@/lib/api';

interface LineupHero {
  hero: string;
  hero_class: string;
  slot: string;
  role: string;
  is_lead: boolean;
  status: string;
  power: number;
  image_filename?: string | null;
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
  { id: 'svs_attack', name: 'Rally Leader', icon: '⚔️' },
  { id: 'rally_attack', name: 'Rally Joiner', icon: '🎯' },
  { id: 'garrison', name: 'Garrison Leader', icon: '🏰' },
  { id: 'rally_defense', name: 'Garrison Joiner', icon: '🛡️' },
  { id: 'bear_trap', name: 'Bear Trap', icon: '🐻' },
];

/** Convert snake_case to Title Case for display */
function formatLabel(s: string): string {
  return s.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

type TabType = 'optimal' | 'joiner' | 'exploration' | 'reference' | 'how';

export default function LineupsPage() {
  const { token, user } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('optimal');
  const [selectedEvent, setSelectedEvent] = useState('svs_attack');
  const [selectedGeneration, setSelectedGeneration] = useState(8);
  const [personalizedLineup, setPersonalizedLineup] = useState<LineupResponse | null>(null);
  const [generalLineup, setGeneralLineup] = useState<LineupResponse | null>(null);
  const [templates, setTemplates] = useState<Record<string, LineupTemplate>>({});
  const [templateDetails, setTemplateDetails] = useState<LineupTemplate | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [joinerAttack, setJoinerAttack] = useState<JoinerRecommendation | null>(null);
  const [joinerDefense, setJoinerDefense] = useState<JoinerRecommendation | null>(null);
  const [hasHeroes, setHasHeroes] = useState<boolean | null>(null);
  const [usingGeneralFallback, setUsingGeneralFallback] = useState(false);
  const heroDataVersionRef = useRef(getHeroDataVersion());

  // Re-fetch lineup data when hero data changes (e.g. after bulk update on Heroes page)
  useEffect(() => {
    const checkForHeroUpdates = () => {
      const currentVersion = getHeroDataVersion();
      if (currentVersion !== heroDataVersionRef.current) {
        heroDataVersionRef.current = currentVersion;
        if (token) {
          fetchPersonalizedLineup();
          if (activeTab === 'joiner') {
            fetchJoinerRecommendations();
          }
        }
      }
    };

    // Check on visibility change (handles tab switching / bfcache)
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        checkForHeroUpdates();
      }
    };

    // Check on window focus (handles returning to browser)
    window.addEventListener('focus', checkForHeroUpdates);
    document.addEventListener('visibilitychange', handleVisibilityChange);

    // Check immediately on mount (handles SPA navigation after hero changes)
    checkForHeroUpdates();

    return () => {
      window.removeEventListener('focus', checkForHeroUpdates);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [token, activeTab]);

  // Fetch templates and profile gen on mount
  useEffect(() => {
    fetchTemplates();
    if (token) {
      profileApi.getCurrent(token).then(data => {
        if (data?.profile?.server_age_days) {
          const days = data.profile.server_age_days;
          // Estimate generation from server age
          let gen = 1;
          const genDays = [0, 40, 120, 200, 280, 360, 440, 520, 600, 680, 760, 840, 920, 1000];
          for (let i = genDays.length - 1; i >= 0; i--) {
            if (days >= genDays[i]) { gen = i + 1; break; }
          }
          setSelectedGeneration(gen);
        }
      }).catch(() => {});
    }
  }, [token]);

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
      const data = await lineupsApi.getTemplates();
      setTemplates(data);
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    }
  };

  const fetchTemplateDetails = async () => {
    try {
      const data = await lineupsApi.getTemplate(selectedEvent);
      setTemplateDetails(data);
    } catch (error) {
      console.error('Failed to fetch template details:', error);
    }
  };

  const fetchPersonalizedLineup = async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const data = await lineupsApi.buildForMode(token, selectedEvent);
      setPersonalizedLineup(data);
      const heroesExist = data?.heroes && data.heroes.length > 0;
      setHasHeroes(heroesExist);
      if (!heroesExist) {
        // Fall back to general lineup with estimated generation
        setUsingGeneralFallback(true);
        const generalData = await lineupsApi.getGeneral(selectedEvent, selectedGeneration);
        setGeneralLineup(generalData);
      } else {
        setUsingGeneralFallback(false);
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
      const data = await lineupsApi.getGeneral(selectedEvent, selectedGeneration);
      setGeneralLineup(data);
    } catch (error) {
      console.error('Failed to fetch general lineup:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchJoinerRecommendations = async () => {
    if (!token) return;
    try {
      const [attackData, defenseData] = await Promise.all([
        lineupsApi.getJoiner(token, 'attack'),
        lineupsApi.getJoiner(token, 'defense'),
      ]);
      setJoinerAttack(attackData);
      setJoinerDefense(defenseData);
    } catch (error) {
      console.error('Failed to fetch joiner recommendations:', error);
    }
  };

  const currentLineup = (token && !usingGeneralFallback) ? personalizedLineup : generalLineup;

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-frost">Lineup Builder</h1>
            <p className="text-frost-muted mt-2">Optimal hero compositions for every event</p>
          </div>
          {(!token || usingGeneralFallback) && (
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

        {/* Default Troop Ratio Callout */}
        <div className="card mb-6 border-fire/30 bg-fire/10">
          <div className="flex items-center gap-3">
            <span className="text-2xl">📊</span>
            <div>
              <p className="text-frost font-bold">Default Troop Ratio: 50/20/30 (Infantry/Lancer/Marksman)</p>
              <p className="text-sm text-frost-muted mt-1">
                This works for most situations. See event-specific recommendations below for optimal ratios.
              </p>
            </div>
          </div>
        </div>

        {/* PvE vs PvP Expandable */}
        <PvePvpExplanation />

        {/* Login/hero prompt */}
        {!token ? (
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
        ) : usingGeneralFallback ? (
          <div className="card mb-6 border-amber-500/30 bg-amber-500/5">
            <div className="flex items-center gap-3">
              <span className="text-2xl">📊</span>
              <div>
                <p className="text-frost">Showing general estimates for <strong className="text-ice">Gen {selectedGeneration}</strong></p>
                <p className="text-sm text-frost-muted mt-1">
                  Add your heroes in the <a href="/heroes" className="text-ice hover:underline">Hero Tracker</a> for
                  personalized lineup recommendations based on your actual roster.
                  Generation is estimated from your server age in <a href="/settings" className="text-ice hover:underline">Settings</a>.
                </p>
              </div>
            </div>
          </div>
        ) : null}

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-surface-border pb-2 overflow-x-auto">
          {[
            { id: 'optimal' as const, label: 'Optimal Lineups' },
            { id: 'joiner' as const, label: 'Rally Joiner Guide' },
            { id: 'exploration' as const, label: 'Exploration' },
            { id: 'reference' as const, label: 'Quick Reference' },
            { id: 'how' as const, label: 'How It Works' },
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
            isPersonalized={!!token && !usingGeneralFallback}
          />
        )}
        {activeTab === 'joiner' && (
          <RallyJoinerGuideTab
            token={token}
            joinerAttack={joinerAttack}
            joinerDefense={joinerDefense}
          />
        )}
        {activeTab === 'exploration' && <ExplorationTab />}
        {activeTab === 'reference' && <ReferenceTab templates={templates} />}
        {activeTab === 'how' && <HowItWorksTab />}
      </div>
    </PageLayout>
  );
}

function PvePvpExplanation() {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="card mb-6">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between w-full text-left"
      >
        <h2 className="text-sm font-medium text-ice">Understanding PvE vs PvP Content</h2>
        <span className="text-frost-muted text-sm">{expanded ? '▼' : '▶'}</span>
      </button>
      {expanded && (
        <div className="mt-4 space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-success/10 border border-success/20">
              <h3 className="font-medium text-success mb-2">PvE - Exploration Skills (Left Side)</h3>
              <p className="text-sm text-frost-muted mb-2">Fighting against the game:</p>
              <ul className="text-sm text-frost-muted space-y-1">
                <li>- Bear Trap, Labyrinth</li>
                <li>- Labyrinth, Exploration</li>
                <li>- Uses left-side skills on hero card</li>
                <li>- Upgraded with Exploration Manuals</li>
              </ul>
            </div>
            <div className="p-4 rounded-lg bg-fire/10 border border-fire/20">
              <h3 className="font-medium text-fire mb-2">PvP - Expedition Skills (Right Side)</h3>
              <p className="text-sm text-frost-muted mb-2">Fighting other players:</p>
              <ul className="text-sm text-frost-muted space-y-1">
                <li>- Rally Leader/Joiner, Garrison</li>
                <li>- SvS, Arena, Brothers in Arms</li>
                <li>- Uses right-side skills on hero card</li>
                <li>- Upgraded with Expedition Manuals</li>
              </ul>
            </div>
          </div>
          <div className="p-3 rounded-lg bg-ice/10 border border-ice/20">
            <p className="text-sm text-frost">
              <strong>Why this matters:</strong> A hero with S-tier exploration skills might only be B-tier for expedition content (and vice versa).
              Always check which skill type is used for the content you are building a lineup for. Lineup composition differs because
              PvE fights are against predictable AI patterns, while PvP fights require countering real player strategies.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

const BEAR_TRAP_JOINERS = [
  { name: 'Jessie', gen: 1, skill: 'Stand of Arms', effect: '+5-25% DMG dealt' },
  { name: 'Jasser', gen: 1, skill: 'Tactical Genius', effect: '+5-25% DMG dealt' },
  { name: 'Seo-yoon', gen: 1, skill: 'Rallying Beat', effect: '+5-25% ATK' },
  { name: 'Hervor', gen: 12, skill: 'Call For Blood', effect: '+5-25% DMG dealt' },
  { name: 'Hendrik', gen: 8, skill: "Worm's Ravage", effect: '-5-25% enemy DEF' },
  { name: 'Sonya', gen: 8, skill: 'Treasure Hunter', effect: '+4-20% DMG' },
];

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

  // Build personalized explanation text based on user's actual heroes
  const getPersonalizedExplanations = (): { heroLines: Array<{ name: string; text: string }>; ratioText: string | null } => {
    const heroLines: Array<{ name: string; text: string }> = [];
    const templateExplanations = template?.hero_explanations || {};

    if (isPersonalized && lineup?.heroes && lineup.heroes.length > 0) {
      // Show explanations mentioning the user's actual heroes by name and level
      for (const hero of lineup.heroes) {
        const templateExp = templateExplanations[hero.hero];
        if (templateExp) {
          const statusNote = hero.status ? ` (${hero.status})` : '';
          heroLines.push({
            name: hero.hero,
            text: `${templateExp}${statusNote}`,
          });
        } else {
          // Generate a contextual explanation from available data
          const roleNote = hero.is_lead ? 'Your lead hero for this event.' : `${hero.hero_class} slot.`;
          const statusNote = hero.status ? ` Currently ${hero.status}.` : '';
          heroLines.push({
            name: hero.hero,
            text: `${roleNote}${statusNote} ${hero.hero_class === 'Infantry' ? 'Provides frontline durability.' : hero.hero_class === 'Lancer' ? 'Provides healing and support.' : 'Provides ranged damage output.'}`,
          });
        }
      }

      // Check if any template key heroes are NOT in the user's lineup (potential upgrades)
      const userHeroNames = new Set(lineup.heroes.map(h => h.hero));
      const keyHeroes = template?.key_heroes || [];
      for (const keyHero of keyHeroes) {
        if (!userHeroNames.has(keyHero) && templateExplanations[keyHero]) {
          heroLines.push({
            name: keyHero,
            text: `(Not in your lineup) ${templateExplanations[keyHero]}. Consider unlocking or leveling this hero.`,
          });
        }
      }
    } else {
      // Not personalized - show general template explanations
      for (const [hero, explanation] of Object.entries(templateExplanations)) {
        heroLines.push({ name: hero, text: explanation });
      }
    }

    return {
      heroLines,
      ratioText: template?.ratio_explanation || null,
    };
  };

  return (
    <>
      {/* Event Selection */}
      <div id="event-selection" className="card mb-6">
        <h2 className="section-header">Select Event Type</h2>
        <div className="grid grid-cols-2 gap-3">
          {eventTypes.map((event: EventType, index: number) => (
            <button
              key={event.id}
              onClick={() => {
                setSelectedEvent(event.id);
                // Prevent page shift when scrolled by anchoring to event selection
                setTimeout(() => {
                  document.getElementById('event-selection')?.scrollIntoView({ behavior: 'instant', block: 'nearest' });
                }, 0);
              }}
              className={`p-4 rounded-lg text-center transition-all ${
                index === eventTypes.length - 1 ? 'col-span-2 max-w-[50%] w-full justify-self-center' : ''
              } ${
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
          <h2 className="text-xl font-bold text-frost">{template?.name || formatLabel(selectedEvent)}</h2>
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
              {selectedEvent === 'bear_trap' ? 'Rally Leader (Your Rally)' : isPersonalized ? 'Your Best Heroes' : 'Recommended Heroes'}
            </h3>
            <div className="flex gap-3 flex-wrap">
              {lineup.heroes.map((hero, i) => (
                <div
                  key={hero.hero}
                  className="flex-1 min-w-[120px] p-3 rounded-lg text-center bg-ice/5 border border-ice/25"
                >
                  <div className="w-12 h-12 mx-auto mb-2 rounded-full overflow-hidden flex items-center justify-center bg-surface-hover ring-2 ring-ice/20">
                    {hero.image_filename ? (
                      <img
                        src={`/images/heroes/${hero.image_filename}`}
                        alt={hero.hero}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <span className="text-xl">
                        {hero.hero_class === 'Infantry' ? '🛡️' : hero.hero_class === 'Lancer' ? '⚔️' : '🏹'}
                      </span>
                    )}
                  </div>
                  <p className="text-sm font-medium text-frost">{hero.hero}</p>
                  <p className="text-xs text-frost-muted">{hero.hero_class}</p>
                  {hero.status && (
                    <p className="text-xs text-success mt-1">{hero.status}</p>
                  )}
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

        {/* Why This Lineup - Expandable with personalized explanations */}
        {(template?.hero_explanations && Object.keys(template.hero_explanations).length > 0) || (isPersonalized && lineup?.heroes && lineup.heroes.length > 0) ? (
          <div className="mt-4">
            <button
              onClick={() => setShowExplanation(!showExplanation)}
              className="flex items-center gap-2 text-sm text-ice hover:text-ice/80"
            >
              <span>{showExplanation ? '▼' : '▶'}</span>
              Why This Lineup?
            </button>
            {showExplanation && (() => {
              const { heroLines, ratioText } = getPersonalizedExplanations();
              return (
                <div className="mt-3 p-4 rounded-lg bg-surface">
                  {isPersonalized && lineup?.heroes && lineup.heroes.length > 0 && (
                    <p className="text-xs text-ice mb-3">Personalized based on your hero roster</p>
                  )}
                  <h4 className="text-sm font-medium text-frost mb-2">Hero Explanations</h4>
                  <ul className="space-y-2 text-sm text-frost-muted">
                    {heroLines.map((line) => (
                      <li key={line.name}>
                        <strong className="text-frost">{line.name}:</strong> {line.text}
                      </li>
                    ))}
                  </ul>
                  {ratioText && (
                    <>
                      <h4 className="text-sm font-medium text-frost mt-4 mb-2">Troop Ratio</h4>
                      <p className="text-sm text-frost-muted">{ratioText}</p>
                    </>
                  )}
                </div>
              );
            })()}
          </div>
        ) : null}

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

      {/* Bear Trap Joiner Rallies - Separate Card */}
      {selectedEvent === 'bear_trap' && (
        <div className="card mb-6 border-orange-500/30">
          <h2 className="text-lg font-bold text-orange-400 mb-2">Joiner Rallies (up to 6)</h2>
          <p className="text-sm text-frost-muted mb-4">
            When joining someone else{"'"}s rally, only your <strong className="text-frost">first hero{"'"}s expedition skill</strong> matters.
            Heroes 2 and 3 contribute nothing except troop capacity.
          </p>

          <div className="space-y-2 mb-4">
            {BEAR_TRAP_JOINERS.map((joiner, i) => {
              const isConserve = i >= 3;
              return (
                <div
                  key={joiner.name}
                  className={`p-3 rounded-lg border flex items-center justify-between flex-wrap gap-2 ${
                    isConserve ? 'bg-surface border-surface-border' : 'bg-ice/5 border-ice/25'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className={`text-xs font-bold w-5 ${isConserve ? 'text-frost-muted' : 'text-ice'}`}>#{i + 1}</span>
                    <div>
                      <span className="text-sm font-medium text-frost">{joiner.name}</span>
                      <span className="text-xs text-frost-muted ml-2">Gen {joiner.gen}</span>
                      <p className="text-xs text-frost-muted">{joiner.skill}: {joiner.effect}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className={`text-xs font-medium ${isConserve ? 'text-frost-muted' : 'text-ice'}`}>
                      {isConserve ? '20/20/60' : '0/10/90'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* No good joiner callout */}
          <div className="p-4 rounded-lg bg-warning/10 border border-warning/30 mb-4">
            <p className="text-sm text-frost">
              <strong className="text-warning">Don{"'"}t have these heroes?</strong> Send troops with <strong className="text-frost">no hero at all</strong>.
              A hero whose expedition skill doesn{"'"}t boost damage (gathering speed, construction speed) actually wastes a skill slot
              that could go to an alliance mate with a real damage skill.
            </p>
          </div>

          {/* Two ratio explanation */}
          <div className="p-3 rounded-lg bg-surface">
            <p className="text-sm text-frost-muted">
              <strong className="text-frost">Why two ratios?</strong> Use <strong className="text-ice">0/10/90</strong> (max marksman)
              for your first 3 joins while you have plenty of marksmen. Switch to <strong className="text-frost">20/20/60</strong> for
              joins 4-6 to conserve marksman troops across all your rallies. If you have plenty of marksmen, use 0/10/90 for all 6.
            </p>
          </div>
        </div>
      )}
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
                <p className="text-xs text-frost-muted">Defenders&apos; Edge: -4-20% DMG taken</p>
                <p className="text-xs text-ice mt-1">Best for multi-wave defense - reduces all incoming damage</p>
              </div>
              <div className="p-3 rounded bg-surface">
                <p className="font-medium text-frost">Patrick (Gen 1)</p>
                <p className="text-xs text-frost-muted">Health boost: +25% HP to garrison troops</p>
                <p className="text-xs text-frost-muted mt-1">Alternative to Sergey - some leaders prefer raw HP over damage reduction</p>
              </div>
              <div className="p-3 rounded bg-surface">
                <p className="font-medium text-frost">Karol (Gen 12)</p>
                <p className="text-xs text-frost-muted">In the Wings: -4-20% DMG taken</p>
                <p className="text-xs text-frost-muted mt-1">Equivalent to Sergey - use higher skill level</p>
              </div>
            </div>
            <div className="mt-3 p-2 rounded bg-ice/5 border border-ice/10">
              <p className="text-xs text-frost-muted">
                <strong className="text-frost">Sergey vs Patrick:</strong> Sergey&apos;s -20% damage reduction is mathematically better against multiple attack waves (compounds over each hit). Patrick&apos;s +25% HP is a one-time buffer - better for surviving a single massive hit but less effective long-term.
              </p>
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

function ExplorationTab() {
  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="section-header">Exploration (5-Hero PvE Lineup)</h2>
        <p className="text-sm text-frost-muted mb-4">
          Exploration is the <strong className="text-frost">only common mode</strong> that uses 5 heroes.
          It uses <strong className="text-ice">Exploration skills (left side)</strong>, not Expedition skills.
        </p>

        <div className="p-3 rounded-lg bg-ice/10 border border-ice/20 mb-6">
          <p className="text-sm text-frost">
            <strong>Tip:</strong> Exploration skills are upgraded with Exploration Manuals.
            Heroes with great PvP skills may have weak PvE skills -- always check the left side.
          </p>
        </div>

        <div className="overflow-x-auto mb-6">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border">
                <th className="text-left p-2 text-frost-muted">Slot</th>
                <th className="text-left p-2 text-frost-muted">Class</th>
                <th className="text-left p-2 text-frost-muted">Role</th>
                <th className="text-left p-2 text-frost-muted">Best Heroes</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-surface-border/50">
                <td className="p-2 text-frost font-medium">1</td>
                <td className="p-2">
                  <span className="flex items-center gap-1 text-frost">🛡️ Infantry</span>
                </td>
                <td className="p-2 text-frost">Primary Tank</td>
                <td className="p-2 text-frost-muted">Natalia, Jeronimo, Wu Ming</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="p-2 text-frost font-medium">2</td>
                <td className="p-2">
                  <span className="flex items-center gap-1 text-frost">🛡️ Infantry</span>
                </td>
                <td className="p-2 text-frost">Secondary Tank</td>
                <td className="p-2 text-frost-muted">Flint, Logan, Hector</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="p-2 text-frost font-medium">3</td>
                <td className="p-2">
                  <span className="flex items-center gap-1 text-frost">⚔️ Lancer</span>
                </td>
                <td className="p-2 text-frost">Healer / Support</td>
                <td className="p-2 text-frost-muted">Molly, Philly, Norah</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="p-2 text-frost font-medium">4</td>
                <td className="p-2">
                  <span className="flex items-center gap-1 text-frost">🏹 Marksman</span>
                </td>
                <td className="p-2 text-frost">Main DPS</td>
                <td className="p-2 text-frost-muted">Alonso, Zinman, Greg</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="p-2 text-frost font-medium">5</td>
                <td className="p-2">
                  <span className="flex items-center gap-1 text-frost">🏹/⚔️ Flex</span>
                </td>
                <td className="p-2 text-frost">Support / Off-DPS</td>
                <td className="p-2 text-frost-muted">Seo-yoon, Mia, Gwen</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="p-3 rounded-lg bg-surface mb-4">
          <p className="text-sm text-frost">
            <strong>Why 2 Infantry?</strong> Double frontline survives longer in multi-wave PvE content.
            The first tank absorbs initial burst while the second provides backup when the first weakens.
          </p>
        </div>

        {/* Troop Ratio */}
        <div>
          <h3 className="text-sm font-medium text-frost-muted mb-3">Exploration Troop Ratio</h3>
          <div className="flex gap-1 h-8 rounded-lg overflow-hidden">
            <div className="bg-red-500 flex items-center justify-center text-xs font-bold text-white" style={{ width: '40%' }}>
              40%
            </div>
            <div className="bg-green-500 flex items-center justify-center text-xs font-bold text-white" style={{ width: '30%' }}>
              30%
            </div>
            <div className="bg-blue-500 flex items-center justify-center text-xs font-bold text-white" style={{ width: '30%' }}>
              30%
            </div>
          </div>
          <div className="flex justify-center gap-4 mt-2 text-xs text-frost-muted">
            <span className="flex items-center gap-1"><span className="w-3 h-3 bg-red-500 rounded" /> Infantry</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 bg-green-500 rounded" /> Lancer</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 bg-blue-500 rounded" /> Marksman</span>
          </div>
          <p className="text-xs text-frost-muted text-center mt-2">Balanced for multi-wave survival</p>
        </div>
      </div>

      <div className="card">
        <h2 className="section-header">Key PvE Heroes</h2>
        <p className="text-sm text-frost-muted mb-4">
          These heroes have strong <strong className="text-frost">exploration skills</strong> that make them
          excel in PvE content regardless of their PvP tier rating.
        </p>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">Tanks (Infantry)</h3>
            <ul className="space-y-2 text-sm text-frost-muted">
              <li><strong className="text-frost">Natalia (Gen 1)</strong> -- Essential tank with self-sustain and shields. Always slot 1.</li>
              <li><strong className="text-frost">Flint (Gen 2)</strong> -- Strong secondary tank with defender attack boost.</li>
              <li><strong className="text-frost">Logan (Gen 3)</strong> -- 25% troop health boost, great for difficult stages.</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-surface">
            <h3 className="font-medium text-frost mb-2">Healers and DPS</h3>
            <ul className="space-y-2 text-sm text-frost-muted">
              <li><strong className="text-frost">Molly (Gen 1)</strong> -- Primary healer, keeps the team alive through waves.</li>
              <li><strong className="text-frost">Alonso (Gen 2)</strong> -- Consistent sustained DPS, strong exploration skills.</li>
              <li><strong className="text-frost">Philly (Gen 2)</strong> -- Backup healer for difficult stages (double healer strategy).</li>
            </ul>
          </div>
        </div>
        <div className="mt-4 p-3 rounded-lg bg-warning/10 border border-warning/30">
          <p className="text-sm text-frost">
            <strong>For difficult stages:</strong> Use double healer (Molly + Philly) instead of the flex DPS slot.
            Survival matters more than speed in hard content.
          </p>
        </div>
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
              <tr className="border-b border-surface-border/50">
                <td className="p-2 text-frost font-medium">Labyrinth 2v2</td>
                <td className="p-2 text-center">52%</td>
                <td className="p-2 text-center">13%</td>
                <td className="p-2 text-center">35%</td>
                <td className="p-2 text-frost-muted">Multi-round survival</td>
              </tr>
              <tr className="border-b border-surface-border/50">
                <td className="p-2 text-frost font-medium">Floor 10</td>
                <td className="p-2 text-center">40%</td>
                <td className="p-2 text-center">15%</td>
                <td className="p-2 text-center">45%</td>
                <td className="p-2 text-frost-muted">Counter Infantry-heavy AI</td>
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
              <li>Bear Trap, Exploration</li>
              <li>Labyrinth, Frozen Stages</li>
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

      {/* Generation Advice */}
      <div className="card">
        <h2 className="section-header">Generation Advice</h2>
        <p className="text-sm text-frost-muted mb-4">
          Hero generations unlock over time as your server ages. Knowing which heroes to save for
          and which remain strong helps you invest wisely.
        </p>

        <div className="mb-6">
          <h3 className="text-sm font-medium text-frost mb-3">Evergreen Heroes (Strong at All Stages)</h3>
          <div className="grid md:grid-cols-3 gap-3">
            <div className="p-3 rounded-lg bg-success/10 border border-success/20">
              <p className="text-sm font-medium text-frost">Natalia (Gen 1)</p>
              <p className="text-xs text-frost-muted">Top Infantry tank from day 1 through endgame. Always worth maxing.</p>
            </div>
            <div className="p-3 rounded-lg bg-success/10 border border-success/20">
              <p className="text-sm font-medium text-frost">Molly (Gen 1)</p>
              <p className="text-xs text-frost-muted">Essential healer. No replacement exists -- she stays in every lineup.</p>
            </div>
            <div className="p-3 rounded-lg bg-success/10 border border-success/20">
              <p className="text-sm font-medium text-frost">Jessie (Gen 1)</p>
              <p className="text-xs text-frost-muted">Best attack joiner skill. Only need expedition skill leveled.</p>
            </div>
          </div>
        </div>

        <div className="mb-6">
          <h3 className="text-sm font-medium text-frost mb-3">Heroes Worth Saving For</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-surface-border">
                  <th className="text-left p-2 text-frost-muted">Gen</th>
                  <th className="text-left p-2 text-frost-muted">Hero</th>
                  <th className="text-left p-2 text-frost-muted">Class</th>
                  <th className="text-left p-2 text-frost-muted">Why Save</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-surface-border/50">
                  <td className="p-2 text-frost">3</td>
                  <td className="p-2 text-frost font-medium">Logan</td>
                  <td className="p-2 text-frost-muted">Infantry</td>
                  <td className="p-2 text-frost-muted">Best defensive tank, 25% troop health boost. Essential for garrison.</td>
                </tr>
                <tr className="border-b border-surface-border/50">
                  <td className="p-2 text-frost">5</td>
                  <td className="p-2 text-frost font-medium">Hector</td>
                  <td className="p-2 text-frost-muted">Infantry</td>
                  <td className="p-2 text-frost-muted">F2P rally leader option. Replaces Flint for Bear Trap.</td>
                </tr>
                <tr className="border-b border-surface-border/50">
                  <td className="p-2 text-frost">6</td>
                  <td className="p-2 text-frost font-medium">Wu Ming</td>
                  <td className="p-2 text-frost-muted">Infantry</td>
                  <td className="p-2 text-frost-muted">Sustain Infantry with self-healing. Great for extended fights.</td>
                </tr>
                <tr className="border-b border-surface-border/50">
                  <td className="p-2 text-frost">8</td>
                  <td className="p-2 text-frost font-medium">Gatot</td>
                  <td className="p-2 text-frost-muted">Infantry</td>
                  <td className="p-2 text-frost-muted">Top Infantry hero. Major power spike when unlocked.</td>
                </tr>
                <tr className="border-b border-surface-border/50">
                  <td className="p-2 text-frost">10</td>
                  <td className="p-2 text-frost font-medium">Blanchette</td>
                  <td className="p-2 text-frost-muted">Marksman</td>
                  <td className="p-2 text-frost-muted">Best F2P Marksman damage dealer. Strong exploration skills.</td>
                </tr>
                <tr className="border-b border-surface-border/50">
                  <td className="p-2 text-frost">12</td>
                  <td className="p-2 text-frost font-medium">Hervor</td>
                  <td className="p-2 text-frost-muted">Infantry</td>
                  <td className="p-2 text-frost-muted">Top-tier Infantry. Also provides Jessie-equivalent joiner skill.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div>
          <h3 className="text-sm font-medium text-frost mb-3">General Investment Advice</h3>
          <div className="space-y-3">
            <div className="p-3 rounded-lg bg-surface">
              <p className="text-sm text-frost-muted">
                <strong className="text-frost">Gen 1-2 heroes are your foundation.</strong> Natalia, Molly, Alonso, and Jessie will
                carry you from day 1 through endgame. Never regret investing in them early.
              </p>
            </div>
            <div className="p-3 rounded-lg bg-surface">
              <p className="text-sm text-frost-muted">
                <strong className="text-frost">Newer generation heroes are generally stronger</strong>, but take longer to max out.
                A maxed Gen 3 hero often outperforms a half-built Gen 8 hero. Focus on completion over collection.
              </p>
            </div>
            <div className="p-3 rounded-lg bg-surface">
              <p className="text-sm text-frost-muted">
                <strong className="text-frost">Save shards and resources</strong> when a new generation is 1-2 weeks away.
                The headline hero of each generation is usually the best investment for that cycle.
              </p>
            </div>
            <div className="p-3 rounded-lg bg-warning/10 border border-warning/30">
              <p className="text-sm text-frost">
                <strong>Avoid spreading thin.</strong> Three maxed heroes beat six half-built ones in every game mode.
                Only expand your roster when your core 3-4 heroes are near maximum for your generation.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function HowItWorksTab() {
  return (
    <div className="space-y-6">
      {/* Hero Skills: The Foundation */}
      <div className="card">
        <h2 className="text-lg font-bold text-frost mb-4">Which Hero Skills Matter?</h2>
        <p className="text-sm text-frost-muted mb-4">
          Every hero has <strong className="text-frost">two sets of skills</strong> that activate in completely different situations.
          Understanding this is the single most important thing for building lineups.
        </p>
        <div className="grid md:grid-cols-2 gap-4 mb-4">
          <div className="p-4 rounded-lg bg-success/10 border border-success/20">
            <h3 className="font-semibold text-success mb-2">Exploration Skills (Left Side)</h3>
            <p className="text-xs text-frost-muted mb-2">Upgraded with Exploration Manuals</p>
            <p className="text-sm text-frost-muted mb-3">
              These skills activate in <strong className="text-success">PvE content</strong> where your heroes fight game-controlled enemies.
            </p>
            <div className="space-y-1">
              <p className="text-xs text-success/80">Used in:</p>
              <ul className="text-xs text-frost-muted space-y-0.5 ml-3">
                <li>- Bear Trap</li>
                <li>- Crazy Joe</li>
                <li>- Exploration</li>
                <li>- Labyrinth</li>
              </ul>
            </div>
          </div>
          <div className="p-4 rounded-lg bg-fire/10 border border-fire/20">
            <h3 className="font-semibold text-fire mb-2">Expedition Skills (Right Side)</h3>
            <p className="text-xs text-frost-muted mb-2">Upgraded with Expedition Manuals</p>
            <p className="text-sm text-frost-muted mb-3">
              These skills activate in <strong className="text-fire">PvP content</strong> where your troops fight other players.
            </p>
            <div className="space-y-1">
              <p className="text-xs text-fire/80">Used in:</p>
              <ul className="text-xs text-frost-muted space-y-0.5 ml-3">
                <li>- Rally Leader & Joiner</li>
                <li>- Garrison Leader & Joiner</li>
                <li>- SvS Battles</li>
                <li>- Arena</li>
              </ul>
            </div>
          </div>
        </div>
        <div className="p-3 rounded-lg bg-warning/10 border border-warning/30">
          <p className="text-sm text-frost">
            <strong>Key takeaway:</strong> A hero with amazing exploration skills might have weak expedition skills.
            Always check which skill set matters for your game mode before investing manuals.
          </p>
        </div>
      </div>

      {/* Leader vs Joiner */}
      <div className="card">
        <h2 className="text-lg font-bold text-frost mb-4">Leader vs Joiner: Different Rules</h2>
        <div className="space-y-4">
          <div className="p-4 rounded-lg bg-surface border border-surface-border">
            <h3 className="font-semibold text-ice mb-2">Leading a Rally or Garrison</h3>
            <p className="text-sm text-frost-muted mb-2">
              When you lead, <strong className="text-frost">all 3 expedition skills</strong> from <strong className="text-frost">each of your 3 heroes</strong> activate.
            </p>
            <div className="flex items-center gap-2 mt-3">
              <div className="text-center px-3 py-2 rounded bg-ice/10 border border-ice/20">
                <p className="text-xs text-frost-muted">Hero 1</p>
                <p className="text-sm font-bold text-ice">3 skills</p>
              </div>
              <span className="text-frost-muted">+</span>
              <div className="text-center px-3 py-2 rounded bg-ice/10 border border-ice/20">
                <p className="text-xs text-frost-muted">Hero 2</p>
                <p className="text-sm font-bold text-ice">3 skills</p>
              </div>
              <span className="text-frost-muted">+</span>
              <div className="text-center px-3 py-2 rounded bg-ice/10 border border-ice/20">
                <p className="text-xs text-frost-muted">Hero 3</p>
                <p className="text-sm font-bold text-ice">3 skills</p>
              </div>
              <span className="text-frost-muted">=</span>
              <div className="text-center px-3 py-2 rounded bg-ice/20 border border-ice/30">
                <p className="text-xs text-frost-muted">Total</p>
                <p className="text-sm font-bold text-ice">9 skills</p>
              </div>
            </div>
            <p className="text-xs text-frost-muted mt-2">
              This is why hero selection and skill levels matter so much for leaders.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-surface border border-surface-border">
            <h3 className="font-semibold text-fire mb-2">Joining a Rally or Garrison</h3>
            <p className="text-sm text-frost-muted mb-2">
              When you join, <strong className="text-frost">ONLY your first hero&apos;s top-right expedition skill</strong> contributes.
              Your other 2 heroes and their skills don&apos;t count at all.
            </p>
            <div className="flex items-center gap-2 mt-3">
              <div className="text-center px-3 py-2 rounded bg-fire/10 border border-fire/20">
                <p className="text-xs text-frost-muted">Hero 1</p>
                <p className="text-sm font-bold text-fire">1 skill</p>
              </div>
              <span className="text-frost-muted">+</span>
              <div className="text-center px-3 py-2 rounded bg-surface border border-surface-border opacity-40">
                <p className="text-xs text-frost-muted">Hero 2</p>
                <p className="text-sm text-frost-muted">ignored</p>
              </div>
              <span className="text-frost-muted">+</span>
              <div className="text-center px-3 py-2 rounded bg-surface border border-surface-border opacity-40">
                <p className="text-xs text-frost-muted">Hero 3</p>
                <p className="text-sm text-frost-muted">ignored</p>
              </div>
            </div>
            <p className="text-xs text-frost-muted mt-2">
              This is why Jessie (Stand of Arms: +25% damage) and Sergey (Defenders&apos; Edge: -20% damage taken) are the best joiners
              regardless of their level or gear.
            </p>
          </div>
        </div>
      </div>

      {/* How the Optimizer Picks Heroes */}
      <div className="card">
        <h2 className="text-lg font-bold text-frost mb-4">How the Optimizer Picks Heroes</h2>
        <p className="text-sm text-frost-muted mb-4">
          The lineup optimizer evaluates every hero you own and picks the best combination for each game mode. Here&apos;s what it considers:
        </p>

        <div className="space-y-3 mb-4">
          <div className="flex gap-3 items-start">
            <div className="w-8 h-8 rounded-full bg-ice/20 border border-ice/30 flex items-center justify-center flex-shrink-0">
              <span className="text-ice text-sm font-bold">1</span>
            </div>
            <div>
              <p className="text-sm font-medium text-frost">Your Investment</p>
              <p className="text-xs text-frost-muted">Hero level, stars, ascension, gear quality, and skill levels. A well-built hero beats a neglected one.</p>
            </div>
          </div>
          <div className="flex gap-3 items-start">
            <div className="w-8 h-8 rounded-full bg-ice/20 border border-ice/30 flex items-center justify-center flex-shrink-0">
              <span className="text-ice text-sm font-bold">2</span>
            </div>
            <div>
              <p className="text-sm font-medium text-frost">Mode-Aware Skill Analysis</p>
              <p className="text-xs text-frost-muted">
                The optimizer reads each hero&apos;s skill descriptions and identifies what they do &mdash; healing, ATK buffs,
                damage reduction, etc. &mdash; then weights those effects based on what wins in each specific mode.
              </p>
            </div>
          </div>
          <div className="flex gap-3 items-start">
            <div className="w-8 h-8 rounded-full bg-ice/20 border border-ice/30 flex items-center justify-center flex-shrink-0">
              <span className="text-ice text-sm font-bold">3</span>
            </div>
            <div>
              <p className="text-sm font-medium text-frost">Composition Rules</p>
              <p className="text-xs text-frost-muted">
                Every 3-hero lineup must have exactly 1 Infantry, 1 Lancer, and 1 Marksman. The optimizer respects this constraint and picks the best hero of each class.
              </p>
            </div>
          </div>
        </div>

        {/* Example */}
        <div className="p-4 rounded-lg bg-surface border border-surface-border">
          <h3 className="text-sm font-semibold text-ice mb-3">Example: Garrison vs Rally</h3>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <p className="text-xs font-medium text-frost mb-2">Garrison Leader (survive repeated attacks)</p>
              <ul className="text-xs text-frost-muted space-y-1">
                <li>- Healing and HP buffs are critical</li>
                <li>- Damage reduction keeps troops alive</li>
                <li>- Pure offense skills have low value</li>
                <li>- A hero with +25% damage dealt is less useful than one with -20% damage taken</li>
              </ul>
            </div>
            <div>
              <p className="text-xs font-medium text-frost mb-2">Rally Leader (kill enemy fast)</p>
              <ul className="text-xs text-frost-muted space-y-1">
                <li>- ATK buffs and damage dealt are critical</li>
                <li>- Burst damage wins short fights</li>
                <li>- Healing has low value (fight ends fast)</li>
                <li>- A hero with +25% ATK for all troops is ideal</li>
              </ul>
            </div>
          </div>
          <p className="text-xs text-frost-muted mt-3 italic">
            The same hero can be a great pick for one mode and a poor pick for another.
            The optimizer evaluates this automatically for every hero in your roster.
          </p>
        </div>
      </div>

      {/* Lineup Composition */}
      <div className="card">
        <h2 className="text-lg font-bold text-frost mb-4">Lineup Composition</h2>
        <div className="space-y-3">
          <div className="p-3 rounded-lg bg-surface">
            <p className="text-sm text-frost-muted">
              <strong className="text-frost">3-hero lineups</strong> always require 1 of each class: Infantry + Lancer + Marksman.
              You cannot double up on a class in a 3-hero lineup.
            </p>
          </div>
          <div className="p-3 rounded-lg bg-surface">
            <p className="text-sm text-frost-muted">
              <strong className="text-frost">5-hero lineups</strong> (Arena) can have multiple heroes of the same class, giving you more flexibility.
            </p>
          </div>
          <div className="p-3 rounded-lg bg-surface">
            <p className="text-sm text-frost-muted">
              <strong className="text-frost">Multi-lineup events</strong> like Canyon Clash and Labyrinth use multiple 3-hero lineups.
              Each lineup still follows the 1-of-each-class rule, but you need enough heroes to fill all lineups.
            </p>
          </div>
          <div className="p-3 rounded-lg bg-surface">
            <p className="text-sm text-frost-muted">
              <strong className="text-frost">Troop ratios</strong> vary by mode. Bear Trap wants 90% Marksman (ranged DPS before the bear reaches melee),
              while Garrison wants 60% Infantry (survive incoming attacks). The optimizer recommends the best ratio for each mode.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
