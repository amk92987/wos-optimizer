'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';

interface Recommendation {
  hero_name: string;
  hero_class: string;
  tier: string;
  generation: number;
  upgrade_type: string;
  current_value: string;
  target_value: string;
  priority: 'high' | 'medium' | 'low';
  reason: string;
}

interface HeroInvestment {
  name: string;
  hero_class: string;
  tier: string;
  generation: number;
  current_level: number;
  target_level: number;
  current_stars: number;
  target_stars: number;
  priority_score: number;
  reasons: string[];
}

type TabType = 'recommendations' | 'heroes' | 'analysis';

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
      const [recRes, investRes] = await Promise.all([
        fetch('http://localhost:8000/api/recommendations', {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch('http://localhost:8000/api/recommendations/investments', {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);

      if (recRes.ok) setRecommendations(await recRes.json());
      if (investRes.ok) setHeroInvestments(await investRes.json());
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const upgradeTypes = ['all', 'level', 'stars', 'exploration_skill', 'expedition_skill', 'gear'];
  const priorityLevels = ['all', 'high', 'medium', 'low'];

  const filteredRecs = recommendations.filter((rec) => {
    if (filterType !== 'all' && rec.upgrade_type !== filterType) return false;
    if (filterPriority !== 'all' && rec.priority !== filterPriority) return false;
    return true;
  });

  const priorityColors = {
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

  const upgradeIcons: Record<string, string> = {
    level: '📊',
    stars: '⭐',
    exploration_skill: '🗺️',
    expedition_skill: '⚔️',
    gear: '🛡️',
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
            tierColors={tierColors}
            classColors={classColors}
            upgradeIcons={upgradeIcons}
          />
        ) : activeTab === 'heroes' ? (
          <HeroInvestmentsTab
            investments={heroInvestments}
            tierColors={tierColors}
            classColors={classColors}
          />
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
  tierColors,
  classColors,
  upgradeIcons,
}: {
  recommendations: Recommendation[];
  filterType: string;
  setFilterType: (v: string) => void;
  filterPriority: string;
  setFilterPriority: (v: string) => void;
  upgradeTypes: string[];
  priorityLevels: string[];
  priorityColors: Record<string, string>;
  tierColors: Record<string, string>;
  classColors: Record<string, string>;
  upgradeIcons: Record<string, string>;
}) {
  return (
    <>
      {/* Filters */}
      <div className="card mb-6">
        <div className="flex flex-wrap gap-4">
          <div>
            <label className="text-xs text-frost-muted block mb-1">Upgrade Type</label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="input text-sm"
            >
              {upgradeTypes.map((type) => (
                <option key={type} value={type}>
                  {type === 'all' ? 'All Types' : type.replace('_', ' ')}
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
                  {p === 'all' ? 'All Priorities' : p}
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
          {recommendations.map((rec, i) => (
            <div
              key={i}
              className={`card border-2 ${priorityColors[rec.priority]}`}
            >
              <div className="flex items-start gap-4">
                <div className="text-3xl">{upgradeIcons[rec.upgrade_type] || '📋'}</div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-bold text-frost">{rec.hero_name}</span>
                    <span className={`text-sm ${tierColors[rec.tier] || 'text-frost-muted'}`}>
                      {rec.tier}
                    </span>
                    <span className={`text-sm ${classColors[rec.hero_class] || 'text-frost-muted'}`}>
                      {rec.hero_class}
                    </span>
                    <span className="text-xs text-frost-muted">Gen {rec.generation}</span>
                  </div>
                  <p className="text-frost">
                    {rec.upgrade_type.replace('_', ' ')}: {rec.current_value} → {rec.target_value}
                  </p>
                  <p className="text-sm text-frost-muted mt-2">{rec.reason}</p>
                </div>
                <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                  rec.priority === 'high' ? 'bg-fire/20 text-fire' :
                  rec.priority === 'medium' ? 'bg-warning/20 text-warning' :
                  'bg-ice/20 text-ice'
                }`}>
                  {rec.priority}
                </div>
              </div>
            </div>
          ))}
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

      {investments.map((hero, i) => (
        <div key={hero.name} className="card">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-surface-hover rounded-lg flex items-center justify-center text-2xl">
              {i + 1}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="font-bold text-frost">{hero.name}</span>
                <span className={`text-sm ${tierColors[hero.tier] || 'text-frost-muted'}`}>
                  {hero.tier}
                </span>
                <span className={`text-sm ${classColors[hero.hero_class] || 'text-frost-muted'}`}>
                  {hero.hero_class}
                </span>
              </div>
              <div className="flex items-center gap-4 text-sm text-frost-muted mb-2">
                <span>Lv.{hero.current_level} → Lv.{hero.target_level}</span>
                <span>{'★'.repeat(hero.current_stars)}{'☆'.repeat(5 - hero.current_stars)} → {'★'.repeat(hero.target_stars)}</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {hero.reasons.map((reason, j) => (
                  <span key={j} className="text-xs px-2 py-1 rounded bg-surface text-frost-muted">
                    {reason}
                  </span>
                ))}
              </div>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-ice">{hero.priority_score}</p>
              <p className="text-xs text-frost-muted">score</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function AnalysisTab() {
  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="section-header">Priority Settings</h2>
        <p className="text-sm text-frost-muted mb-4">
          Your current priority settings affect which recommendations appear first:
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
