'use client';

import { useEffect, useState, useMemo } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';
import { recommendationsApi } from '@/lib/api';

interface Recommendation {
  priority: number;
  action: string;
  category: string;
  hero: string | null;
  reason: string;
  resources: string;
  relevance_tags: string[];
  source: string;
}

interface HeroInvestment {
  hero: string;
  hero_class: string;
  tier: string;
  generation: number;
  current_level: number;
  target_level: number;
  current_stars: number;
  target_stars: number;
  priority: number;
  reason: string;
}

type TabType = 'recommendations' | 'heroes' | 'gear' | 'analysis';

// ── Hero Gear Cost Data (from verified game data) ──────────────────────
// Mastery Forging: Gold gear levels 1-20, costs Essence Stones + Mythic Gear
const MASTERY_COSTS: { essence_stones: number; mythic_gear: number }[] = [
  { essence_stones: 10, mythic_gear: 0 },   // 0→1
  { essence_stones: 20, mythic_gear: 0 },   // 1→2
  { essence_stones: 30, mythic_gear: 0 },   // 2→3
  { essence_stones: 40, mythic_gear: 0 },   // 3→4
  { essence_stones: 50, mythic_gear: 0 },   // 4→5
  { essence_stones: 60, mythic_gear: 0 },   // 5→6
  { essence_stones: 70, mythic_gear: 0 },   // 6→7
  { essence_stones: 80, mythic_gear: 0 },   // 7→8
  { essence_stones: 90, mythic_gear: 0 },   // 8→9
  { essence_stones: 100, mythic_gear: 0 },  // 9→10
  { essence_stones: 110, mythic_gear: 1 },  // 10→11
  { essence_stones: 120, mythic_gear: 2 },  // 11→12
  { essence_stones: 130, mythic_gear: 3 },  // 12→13
  { essence_stones: 140, mythic_gear: 4 },  // 13→14
  { essence_stones: 150, mythic_gear: 5 },  // 14→15
  { essence_stones: 160, mythic_gear: 6 },  // 15→16
  { essence_stones: 170, mythic_gear: 7 },  // 16→17
  { essence_stones: 180, mythic_gear: 8 },  // 17→18
  { essence_stones: 190, mythic_gear: 9 },  // 18→19
  { essence_stones: 200, mythic_gear: 10 }, // 19→20
];

// Legendary Enhancement: levels 1-100, costs XP + Mithril/LegendaryGear at milestones
const LEGENDARY_COSTS: { xp: number; mithril: number; legendary_gear: number }[] = [
  { xp: 0, mithril: 0, legendary_gear: 2 },     // 0→1
  { xp: 2500, mithril: 0, legendary_gear: 0 },   // 1→2
  { xp: 2550, mithril: 0, legendary_gear: 0 },   // 2→3
  { xp: 2600, mithril: 0, legendary_gear: 0 },   // 3→4
  { xp: 2650, mithril: 0, legendary_gear: 0 },   // 4→5
  { xp: 2700, mithril: 0, legendary_gear: 0 },   // 5→6
  { xp: 2750, mithril: 0, legendary_gear: 0 },   // 6→7
  { xp: 2800, mithril: 0, legendary_gear: 0 },   // 7→8
  { xp: 2850, mithril: 0, legendary_gear: 0 },   // 8→9
  { xp: 2900, mithril: 0, legendary_gear: 0 },   // 9→10
  { xp: 2950, mithril: 0, legendary_gear: 0 },   // 10→11
  { xp: 3000, mithril: 0, legendary_gear: 0 },   // 11→12
  { xp: 3050, mithril: 0, legendary_gear: 0 },   // 12→13
  { xp: 3100, mithril: 0, legendary_gear: 0 },   // 13→14
  { xp: 3150, mithril: 0, legendary_gear: 0 },   // 14→15
  { xp: 3200, mithril: 0, legendary_gear: 0 },   // 15→16
  { xp: 3250, mithril: 0, legendary_gear: 0 },   // 16→17
  { xp: 3300, mithril: 0, legendary_gear: 0 },   // 17→18
  { xp: 3350, mithril: 0, legendary_gear: 0 },   // 18→19
  { xp: 0, mithril: 10, legendary_gear: 3 },     // 19→20
  { xp: 3500, mithril: 0, legendary_gear: 0 },   // 20→21
  { xp: 3550, mithril: 0, legendary_gear: 0 },   // 21→22
  { xp: 3600, mithril: 0, legendary_gear: 0 },   // 22→23
  { xp: 3650, mithril: 0, legendary_gear: 0 },   // 23→24
  { xp: 3700, mithril: 0, legendary_gear: 0 },   // 24→25
  { xp: 3750, mithril: 0, legendary_gear: 0 },   // 25→26
  { xp: 3800, mithril: 0, legendary_gear: 0 },   // 26→27
  { xp: 3850, mithril: 0, legendary_gear: 0 },   // 27→28
  { xp: 3900, mithril: 0, legendary_gear: 0 },   // 28→29
  { xp: 3950, mithril: 0, legendary_gear: 0 },   // 29→30
  { xp: 4000, mithril: 0, legendary_gear: 0 },   // 30→31
  { xp: 4050, mithril: 0, legendary_gear: 0 },   // 31→32
  { xp: 4100, mithril: 0, legendary_gear: 0 },   // 32→33
  { xp: 4150, mithril: 0, legendary_gear: 0 },   // 33→34
  { xp: 4200, mithril: 0, legendary_gear: 0 },   // 34→35
  { xp: 4250, mithril: 0, legendary_gear: 0 },   // 35→36
  { xp: 4300, mithril: 0, legendary_gear: 0 },   // 36→37
  { xp: 4350, mithril: 0, legendary_gear: 0 },   // 37→38
  { xp: 4400, mithril: 0, legendary_gear: 0 },   // 38→39
  { xp: 0, mithril: 20, legendary_gear: 5 },     // 39→40
  { xp: 4450, mithril: 0, legendary_gear: 0 },   // 40→41
  { xp: 4500, mithril: 0, legendary_gear: 0 },   // 41→42
  { xp: 4550, mithril: 0, legendary_gear: 0 },   // 42→43
  { xp: 4600, mithril: 0, legendary_gear: 0 },   // 43→44
  { xp: 4650, mithril: 0, legendary_gear: 0 },   // 44→45
  { xp: 4700, mithril: 0, legendary_gear: 0 },   // 45→46
  { xp: 4750, mithril: 0, legendary_gear: 0 },   // 46→47
  { xp: 4800, mithril: 0, legendary_gear: 0 },   // 47→48
  { xp: 4850, mithril: 0, legendary_gear: 0 },   // 48→49
  { xp: 4900, mithril: 0, legendary_gear: 0 },   // 49→50
  { xp: 4950, mithril: 0, legendary_gear: 0 },   // 50→51
  { xp: 5000, mithril: 0, legendary_gear: 0 },   // 51→52
  { xp: 5050, mithril: 0, legendary_gear: 0 },   // 52→53
  { xp: 5100, mithril: 0, legendary_gear: 0 },   // 53→54
  { xp: 5150, mithril: 0, legendary_gear: 0 },   // 54→55
  { xp: 5200, mithril: 0, legendary_gear: 0 },   // 55→56
  { xp: 5250, mithril: 0, legendary_gear: 0 },   // 56→57
  { xp: 5300, mithril: 0, legendary_gear: 0 },   // 57→58
  { xp: 5350, mithril: 0, legendary_gear: 0 },   // 58→59
  { xp: 0, mithril: 30, legendary_gear: 5 },     // 59→60
  { xp: 5500, mithril: 0, legendary_gear: 0 },   // 60→61
  { xp: 5600, mithril: 0, legendary_gear: 0 },   // 61→62
  { xp: 5700, mithril: 0, legendary_gear: 0 },   // 62→63
  { xp: 5800, mithril: 0, legendary_gear: 0 },   // 63→64
  { xp: 5900, mithril: 0, legendary_gear: 0 },   // 64→65
  { xp: 6000, mithril: 0, legendary_gear: 0 },   // 65→66
  { xp: 6100, mithril: 0, legendary_gear: 0 },   // 66→67
  { xp: 6200, mithril: 0, legendary_gear: 0 },   // 67→68
  { xp: 6300, mithril: 0, legendary_gear: 0 },   // 68→69
  { xp: 6400, mithril: 0, legendary_gear: 0 },   // 69→70
  { xp: 6500, mithril: 0, legendary_gear: 0 },   // 70→71
  { xp: 6600, mithril: 0, legendary_gear: 0 },   // 71→72
  { xp: 6700, mithril: 0, legendary_gear: 0 },   // 72→73
  { xp: 6800, mithril: 0, legendary_gear: 0 },   // 73→74
  { xp: 6900, mithril: 0, legendary_gear: 0 },   // 74→75
  { xp: 7000, mithril: 0, legendary_gear: 0 },   // 75→76
  { xp: 7100, mithril: 0, legendary_gear: 0 },   // 76→77
  { xp: 7200, mithril: 0, legendary_gear: 0 },   // 77→78
  { xp: 7300, mithril: 0, legendary_gear: 0 },   // 78→79
  { xp: 0, mithril: 40, legendary_gear: 10 },    // 79→80
  { xp: 7500, mithril: 0, legendary_gear: 0 },   // 80→81
  { xp: 7600, mithril: 0, legendary_gear: 0 },   // 81→82
  { xp: 7700, mithril: 0, legendary_gear: 0 },   // 82→83
  { xp: 7800, mithril: 0, legendary_gear: 0 },   // 83→84
  { xp: 7900, mithril: 0, legendary_gear: 0 },   // 84→85
  { xp: 8000, mithril: 0, legendary_gear: 0 },   // 85→86
  { xp: 8100, mithril: 0, legendary_gear: 0 },   // 86→87
  { xp: 8200, mithril: 0, legendary_gear: 0 },   // 87→88
  { xp: 8300, mithril: 0, legendary_gear: 0 },   // 88→89
  { xp: 8400, mithril: 0, legendary_gear: 0 },   // 89→90
  { xp: 8500, mithril: 0, legendary_gear: 0 },   // 90→91
  { xp: 8600, mithril: 0, legendary_gear: 0 },   // 91→92
  { xp: 8700, mithril: 0, legendary_gear: 0 },   // 92→93
  { xp: 8800, mithril: 0, legendary_gear: 0 },   // 93→94
  { xp: 8900, mithril: 0, legendary_gear: 0 },   // 94→95
  { xp: 9000, mithril: 0, legendary_gear: 0 },   // 95→96
  { xp: 9100, mithril: 0, legendary_gear: 0 },   // 96→97
  { xp: 9200, mithril: 0, legendary_gear: 0 },   // 97→98
  { xp: 9300, mithril: 0, legendary_gear: 0 },   // 98→99
  { xp: 0, mithril: 50, legendary_gear: 10 },    // 99→100
];

export default function UpgradesPage() {
  const { token } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('recommendations');
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [heroInvestments, setHeroInvestments] = useState<HeroInvestment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filterType, setFilterType] = useState('all');
  const [filterPriority, setFilterPriority] = useState('all');

  useEffect(() => {
    if (token) {
      fetchRecommendations();
    }
  }, [token]);

  const fetchRecommendations = async () => {
    setIsLoading(true);
    try {
      const [recData, investData] = await Promise.all([
        recommendationsApi.get(token!),
        recommendationsApi.getInvestments(token!),
      ]);

      setRecommendations(recData.recommendations || []);
      setHeroInvestments(investData.investments || []);
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const upgradeTypes = ['all', 'hero', 'gear', 'building', 'research', 'troop'];
  const priorityLevels = ['all', 'high', 'medium', 'low'];

  // Convert numeric priority to category (1-3 = high, 4-6 = medium, 7+ = low)
  const getPriorityLevel = (p: number) => p <= 3 ? 'high' : p <= 6 ? 'medium' : 'low';

  const filteredRecs = recommendations.filter((rec) => {
    if (filterType !== 'all' && rec.category !== filterType) return false;
    if (filterPriority !== 'all' && getPriorityLevel(rec.priority) !== filterPriority) return false;
    return true;
  });

  const priorityColors: Record<string, string> = {
    high: 'border-fire/50 bg-fire/10',
    medium: 'border-warning/50 bg-warning/10',
    low: 'border-ice/50 bg-ice/10',
  };

  const tierColors: Record<string, string> = {
    'S+': 'text-tier-splus',
    'S': 'text-tier-s',
    'A': 'text-tier-a',
    'B': 'text-tier-b',
    'C': 'text-tier-c',
    'D': 'text-tier-d',
  };

  const classColors: Record<string, string> = {
    Infantry: 'text-red-400',
    Lancer: 'text-green-400',
    Marksman: 'text-blue-400',
  };

  const categoryIcons: Record<string, string> = {
    hero: '🦸',
    gear: '🛡️',
    building: '🏗️',
    research: '🔬',
    troop: '⚔️',
  };

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Upgrade Recommendations</h1>
          <p className="text-frost-muted mt-2">Personalized upgrade priorities based on your profile</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-surface-border pb-2">
          <button
            onClick={() => setActiveTab('recommendations')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'recommendations'
                ? 'bg-ice/20 text-ice'
                : 'text-frost-muted hover:text-frost hover:bg-surface'
            }`}
          >
            Top Recommendations
          </button>
          <button
            onClick={() => setActiveTab('heroes')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'heroes'
                ? 'bg-ice/20 text-ice'
                : 'text-frost-muted hover:text-frost hover:bg-surface'
            }`}
          >
            Best Heroes to Invest
          </button>
          <button
            onClick={() => setActiveTab('gear')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'gear'
                ? 'bg-ice/20 text-ice'
                : 'text-frost-muted hover:text-frost hover:bg-surface'
            }`}
          >
            Gear Costs
          </button>
          <button
            onClick={() => setActiveTab('analysis')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'analysis'
                ? 'bg-ice/20 text-ice'
                : 'text-frost-muted hover:text-frost hover:bg-surface'
            }`}
          >
            Analysis
          </button>
        </div>

        {/* Content */}
        {isLoading ? (
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="card animate-pulse">
                <div className="h-20 bg-surface-hover rounded" />
              </div>
            ))}
          </div>
        ) : activeTab === 'recommendations' ? (
          <RecommendationsTab
            recommendations={filteredRecs}
            filterType={filterType}
            setFilterType={setFilterType}
            filterPriority={filterPriority}
            setFilterPriority={setFilterPriority}
            upgradeTypes={upgradeTypes}
            priorityLevels={priorityLevels}
            priorityColors={priorityColors}
            categoryIcons={categoryIcons}
            getPriorityLevel={getPriorityLevel}
          />
        ) : activeTab === 'heroes' ? (
          <HeroInvestmentsTab
            investments={heroInvestments}
            tierColors={tierColors}
            classColors={classColors}
          />
        ) : activeTab === 'gear' ? (
          <GearCostsTab />
        ) : (
          <AnalysisTab />
        )}
      </div>
    </PageLayout>
  );
}

function RecommendationsTab({
  recommendations,
  filterType,
  setFilterType,
  filterPriority,
  setFilterPriority,
  upgradeTypes,
  priorityLevels,
  priorityColors,
  categoryIcons,
  getPriorityLevel,
}: {
  recommendations: Recommendation[];
  filterType: string;
  setFilterType: (v: string) => void;
  filterPriority: string;
  setFilterPriority: (v: string) => void;
  upgradeTypes: string[];
  priorityLevels: string[];
  priorityColors: Record<string, string>;
  categoryIcons: Record<string, string>;
  getPriorityLevel: (p: number) => string;
}) {
  return (
    <>
      {/* Filters */}
      <div className="card mb-6">
        <div className="flex flex-wrap gap-4">
          <div>
            <label className="text-xs text-frost-muted block mb-1">Category</label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="input text-sm"
            >
              {upgradeTypes.map((type) => (
                <option key={type} value={type}>
                  {type === 'all' ? 'All Categories' : type.charAt(0).toUpperCase() + type.slice(1)}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-frost-muted block mb-1">Priority</label>
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              className="input text-sm"
            >
              {priorityLevels.map((p) => (
                <option key={p} value={p}>
                  {p === 'all' ? 'All Priorities' : p.charAt(0).toUpperCase() + p.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Recommendations List */}
      {recommendations.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-4xl mb-4">🎯</div>
          <h3 className="text-lg font-medium text-frost mb-2">No recommendations yet</h3>
          <p className="text-frost-muted">
            Add heroes to your tracker to get personalized upgrade recommendations
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {recommendations.map((rec, i) => {
            const level = getPriorityLevel(rec.priority);
            return (
              <div
                key={i}
                className={`card border-2 ${priorityColors[level] || 'border-surface-border'}`}
              >
                <div className="flex items-start gap-4">
                  <div className="text-3xl">{categoryIcons[rec.category] || '📋'}</div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      {rec.hero && (
                        <span className="font-bold text-frost">{rec.hero}</span>
                      )}
                      <span className="text-sm px-2 py-0.5 rounded bg-surface-hover text-frost-muted">
                        {rec.category}
                      </span>
                      {rec.relevance_tags?.length > 0 && (
                        <div className="flex gap-1">
                          {rec.relevance_tags.slice(0, 3).map((tag, j) => (
                            <span key={j} className="text-xs px-1.5 py-0.5 rounded bg-ice/10 text-ice">
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    <p className="text-frost">{rec.action}</p>
                    {rec.reason && (
                      <p className="text-sm text-frost-muted mt-2">{rec.reason}</p>
                    )}
                    {rec.resources && (
                      <p className="text-xs text-frost-muted mt-1">Resources: {rec.resources}</p>
                    )}
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                    level === 'high' ? 'bg-fire/20 text-fire' :
                    level === 'medium' ? 'bg-warning/20 text-warning' :
                    'bg-ice/20 text-ice'
                  }`}>
                    {level}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </>
  );
}

function HeroInvestmentsTab({
  investments,
  tierColors,
  classColors,
}: {
  investments: HeroInvestment[];
  tierColors: Record<string, string>;
  classColors: Record<string, string>;
}) {
  if (investments.length === 0) {
    return (
      <div className="card text-center py-12">
        <div className="text-4xl mb-4">🦸</div>
        <h3 className="text-lg font-medium text-frost mb-2">No hero investments calculated</h3>
        <p className="text-frost-muted">
          Add heroes and set your spending profile to see investment recommendations
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="card">
        <p className="text-sm text-frost-muted mb-4">
          Based on your spending profile and priorities, here are the heroes worth investing in:
        </p>
      </div>

      {investments.map((inv, i) => (
        <div key={inv.hero} className="card">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-surface-hover rounded-lg flex items-center justify-center text-2xl">
              {i + 1}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="font-bold text-frost">{inv.hero}</span>
                <span className={`text-sm ${tierColors[inv.tier] || 'text-frost-muted'}`}>
                  {inv.tier}
                </span>
                <span className={`text-sm ${classColors[inv.hero_class] || 'text-frost-muted'}`}>
                  {inv.hero_class}
                </span>
                <span className="text-xs text-frost-muted">Gen {inv.generation}</span>
              </div>
              <div className="flex items-center gap-4 text-sm text-frost-muted mb-2">
                <span>Lv.{inv.current_level} → Lv.{inv.target_level}</span>
                <span>{'★'.repeat(inv.current_stars)}{'☆'.repeat(5 - inv.current_stars)} → {'★'.repeat(inv.target_stars)}</span>
              </div>
              {inv.reason && (
                <p className="text-sm text-frost-muted">{inv.reason}</p>
              )}
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-ice">#{inv.priority}</p>
              <p className="text-xs text-frost-muted">priority</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function GearCostsTab() {
  type GearTrack = 'mastery' | 'legendary';
  const [track, setTrack] = useState<GearTrack>('legendary');
  const [fromLevel, setFromLevel] = useState(1);
  const [toLevel, setToLevel] = useState(20);
  const [slotCount, setSlotCount] = useState(4);

  const maxLevel = track === 'mastery' ? 20 : 100;

  // Clamp values when switching tracks
  const handleTrackChange = (t: GearTrack) => {
    setTrack(t);
    const max = t === 'mastery' ? 20 : 100;
    setFromLevel((prev) => Math.min(prev, max - 1));
    setToLevel((prev) => Math.min(prev, max));
  };

  const costs = useMemo(() => {
    if (fromLevel >= toLevel) return null;
    if (track === 'mastery') {
      let totalStones = 0;
      let totalGear = 0;
      for (let i = fromLevel; i < toLevel; i++) {
        totalStones += MASTERY_COSTS[i].essence_stones;
        totalGear += MASTERY_COSTS[i].mythic_gear;
      }
      return {
        per_slot: { essence_stones: totalStones, mythic_gear: totalGear },
        total: { essence_stones: totalStones * slotCount, mythic_gear: totalGear * slotCount },
      };
    } else {
      let totalXp = 0;
      let totalMithril = 0;
      let totalGear = 0;
      for (let i = fromLevel; i < toLevel; i++) {
        totalXp += LEGENDARY_COSTS[i].xp;
        totalMithril += LEGENDARY_COSTS[i].mithril;
        totalGear += LEGENDARY_COSTS[i].legendary_gear;
      }
      return {
        per_slot: { xp: totalXp, mithril: totalMithril, legendary_gear: totalGear },
        total: { xp: totalXp * slotCount, mithril: totalMithril * slotCount, legendary_gear: totalGear * slotCount },
      };
    }
  }, [track, fromLevel, toLevel, slotCount]);

  const milestones = track === 'legendary'
    ? [1, 20, 40, 60, 80, 100].filter((m) => m > fromLevel && m <= toLevel)
    : [];

  return (
    <div className="space-y-6">
      {/* Track Selector */}
      <div className="card">
        <div className="flex gap-3 mb-4">
          <button
            onClick={() => handleTrackChange('legendary')}
            className={`flex-1 py-3 px-4 rounded-lg text-sm font-medium transition-colors border-2 ${
              track === 'legendary'
                ? 'border-red-500/50 bg-red-500/10 text-red-400'
                : 'border-surface-border bg-surface text-frost-muted hover:text-frost'
            }`}
          >
            <div className="text-base font-bold">Legendary Enhancement</div>
            <div className="text-xs mt-1 opacity-75">Levels 1-100 (Red gear)</div>
          </button>
          <button
            onClick={() => handleTrackChange('mastery')}
            className={`flex-1 py-3 px-4 rounded-lg text-sm font-medium transition-colors border-2 ${
              track === 'mastery'
                ? 'border-amber-500/50 bg-amber-500/10 text-amber-400'
                : 'border-surface-border bg-surface text-frost-muted hover:text-frost'
            }`}
          >
            <div className="text-base font-bold">Mastery Forging</div>
            <div className="text-xs mt-1 opacity-75">Levels 1-20 (Gold gear)</div>
          </button>
        </div>

        {/* Inputs */}
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="text-xs text-frost-muted block mb-1">From Level</label>
            <input
              type="number"
              min={track === 'legendary' ? 0 : 0}
              max={maxLevel - 1}
              value={fromLevel}
              onChange={(e) => setFromLevel(Math.max(0, Math.min(maxLevel - 1, Number(e.target.value))))}
              className="input w-full text-center text-lg"
            />
          </div>
          <div>
            <label className="text-xs text-frost-muted block mb-1">To Level</label>
            <input
              type="number"
              min={1}
              max={maxLevel}
              value={toLevel}
              onChange={(e) => setToLevel(Math.max(1, Math.min(maxLevel, Number(e.target.value))))}
              className="input w-full text-center text-lg"
            />
          </div>
          <div>
            <label className="text-xs text-frost-muted block mb-1">Gear Slots</label>
            <select
              value={slotCount}
              onChange={(e) => setSlotCount(Number(e.target.value))}
              className="input w-full text-center text-lg"
            >
              <option value={1}>1 slot</option>
              <option value={2}>2 slots</option>
              <option value={3}>3 slots</option>
              <option value={4}>4 slots (all)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results */}
      {fromLevel >= toLevel ? (
        <div className="card text-center py-8">
          <p className="text-frost-muted">Set "From Level" lower than "To Level" to see costs</p>
        </div>
      ) : costs && (
        <div className="space-y-4">
          {/* Per Slot Costs */}
          <div className="card">
            <h3 className="text-sm font-medium text-frost-muted mb-3">
              Cost per slot (Level {fromLevel} → {toLevel})
            </h3>
            <div className={`grid gap-4 ${track === 'legendary' ? 'grid-cols-3' : 'grid-cols-2'}`}>
              {track === 'legendary' ? (
                <>
                  <CostCard label="XP" value={(costs.per_slot as any).xp} color="text-blue-400" />
                  <CostCard label="Mithril" value={(costs.per_slot as any).mithril} color="text-purple-400" />
                  <CostCard label="Legendary Gear" value={(costs.per_slot as any).legendary_gear} color="text-red-400" />
                </>
              ) : (
                <>
                  <CostCard label="Essence Stones" value={(costs.per_slot as any).essence_stones} color="text-amber-400" />
                  <CostCard label="Mythic Gear" value={(costs.per_slot as any).mythic_gear} color="text-orange-400" />
                </>
              )}
            </div>
          </div>

          {/* Total Costs (if multiple slots) */}
          {slotCount > 1 && (
            <div className="card border-2 border-ice/30">
              <h3 className="text-sm font-medium text-ice mb-3">
                Total for {slotCount} slots
              </h3>
              <div className={`grid gap-4 ${track === 'legendary' ? 'grid-cols-3' : 'grid-cols-2'}`}>
                {track === 'legendary' ? (
                  <>
                    <CostCard label="XP" value={(costs.total as any).xp} color="text-blue-400" large />
                    <CostCard label="Mithril" value={(costs.total as any).mithril} color="text-purple-400" large />
                    <CostCard label="Legendary Gear" value={(costs.total as any).legendary_gear} color="text-red-400" large />
                  </>
                ) : (
                  <>
                    <CostCard label="Essence Stones" value={(costs.total as any).essence_stones} color="text-amber-400" large />
                    <CostCard label="Mythic Gear" value={(costs.total as any).mythic_gear} color="text-orange-400" large />
                  </>
                )}
              </div>
            </div>
          )}

          {/* Milestone Breakdown (Legendary only) */}
          {track === 'legendary' && milestones.length > 0 && (
            <div className="card">
              <h3 className="text-sm font-medium text-frost-muted mb-3">Milestone Costs</h3>
              <p className="text-xs text-frost-muted mb-3">
                Every 20 levels requires Mithril and Legendary Gear to unlock the next batch
              </p>
              <div className="space-y-2">
                {milestones.map((m) => {
                  const edge = LEGENDARY_COSTS[m - 1]; // edge index is m-1 for reaching level m
                  return (
                    <div key={m} className="flex items-center justify-between py-2 px-3 rounded bg-surface-hover">
                      <span className="text-sm font-medium text-frost">Level {m}</span>
                      <div className="flex gap-4 text-sm">
                        {edge.mithril > 0 && (
                          <span className="text-purple-400">{edge.mithril} Mithril</span>
                        )}
                        {edge.legendary_gear > 0 && (
                          <span className="text-red-400">{edge.legendary_gear} Legendary Gear</span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Gear Info */}
          <div className="card">
            <h3 className="text-sm font-medium text-frost-muted mb-2">About Hero Gear</h3>
            <ul className="space-y-1.5 text-sm text-frost-muted">
              <li className="flex items-start gap-2">
                <span className="text-ice">•</span>
                <span>4 gear slots per hero: Goggles, Gauntlets, Belt, Boots</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-ice">•</span>
                <span>Gear is class-specific (Infantry/Marksman/Lancer) but <strong className="text-frost">transferable</strong> between heroes of the same class</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-ice">•</span>
                <span>Move gear to newer generation heroes as they become available</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-ice">•</span>
                <span>Mastery Forging unlocks at Gold quality + Enhancement Level 20</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-ice">•</span>
                <span>Legendary Ascension requires Gold gear at Enhancement 100 + Mastery 10 + 2 Mythic pieces</span>
              </li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

function CostCard({ label, value, color, large }: { label: string; value: number; color: string; large?: boolean }) {
  return (
    <div className="p-3 rounded-lg bg-surface text-center">
      <p className={`${large ? 'text-2xl' : 'text-xl'} font-bold ${color}`}>
        {value.toLocaleString()}
      </p>
      <p className="text-xs text-frost-muted mt-1">{label}</p>
    </div>
  );
}

function AnalysisTab() {
  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="section-header">Priority Settings</h2>
        <p className="text-sm text-frost-muted mb-4">
          Your current priority settings affect which recommendations appear first.
          To change these values, go to <a href="/settings" className="text-ice hover:underline">Settings</a>.
        </p>
        <div className="grid grid-cols-5 gap-4 text-center">
          {[
            { label: 'SvS', value: 4 },
            { label: 'Rally', value: 3 },
            { label: 'Castle Battle', value: 3 },
            { label: 'Exploration', value: 2 },
            { label: 'Gathering', value: 1 },
          ].map((p) => (
            <div key={p.label} className="p-3 rounded-lg bg-surface">
              <p className="text-lg font-bold text-ice">{'★'.repeat(p.value)}{'☆'.repeat(5 - p.value)}</p>
              <p className="text-xs text-frost-muted">{p.label}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h2 className="section-header">Recommendation Logic</h2>
        <ul className="space-y-2 text-sm text-frost-muted">
          <li className="flex items-start gap-2">
            <span className="text-ice">•</span>
            <span>Heroes are prioritized by tier (S+ → D) and generation relevance</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-ice">•</span>
            <span>Spending profile affects number of heroes recommended (F2P: 3-4, Whale: all)</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-ice">•</span>
            <span>Expedition skills are prioritized for combat-focused players</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-ice">•</span>
            <span>Farm accounts get specialized "focus on 1-2 heroes" advice</span>
          </li>
        </ul>
      </div>

      <div className="card">
        <h2 className="section-header">Tips for Better Recommendations</h2>
        <ul className="space-y-2 text-sm text-frost-muted">
          <li className="flex items-start gap-2">
            <span className="text-success">✓</span>
            <span>Set your correct spending profile in Settings</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-success">✓</span>
            <span>Adjust priority sliders to match your goals</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-success">✓</span>
            <span>Keep hero levels and skills up to date</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-success">✓</span>
            <span>Mark farm accounts correctly for specialized advice</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
