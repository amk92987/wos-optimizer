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

type TabType = 'recommendations' | 'heroes' | 'calculators';
type CalcType = 'enhancement' | 'legendary' | 'mastery' | 'chief_gear' | 'charms' | 'war_academy';

/** Convert snake_case or slug text to clean Title Case */
function formatLabel(s: string): string {
  return s.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

// ══════════════════════════════════════════════════════════════════════
// COST DATA
// ══════════════════════════════════════════════════════════════════════

// Hero Gear Enhancement XP: pre-Legendary, levels 0→100 (73,320 total XP)
const ENHANCEMENT_COSTS: number[] = [
  10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105,
  110, 115, 120, 125, 130, 135, 140, 145, 150, 160, 170, 180, 190, 200, 210, 220, 230,
  240, 250, 270, 290, 310, 330, 350, 370, 390, 410, 430, 450, 470, 490, 510, 530, 550,
  570, 590, 610, 630, 650, 680, 710, 740, 770, 800, 830, 860, 890, 920, 950, 990, 1030,
  1070, 1110, 1150, 1190, 1230, 1270, 1310, 1350, 1400, 1450, 1500, 1550, 1600, 1650,
  1700, 1750, 1800, 1850, 1900, 1950, 2000, 2050, 2100, 2150, 2200, 2250, 2300, 2350, 2400,
];

// Mastery Forging: Gold gear levels 0→20, costs Essence Stones + Mythic Gear
const MASTERY_COSTS: { essence_stones: number; mythic_gear: number }[] = [
  { essence_stones: 10, mythic_gear: 0 },
  { essence_stones: 20, mythic_gear: 0 },
  { essence_stones: 30, mythic_gear: 0 },
  { essence_stones: 40, mythic_gear: 0 },
  { essence_stones: 50, mythic_gear: 0 },
  { essence_stones: 60, mythic_gear: 0 },
  { essence_stones: 70, mythic_gear: 0 },
  { essence_stones: 80, mythic_gear: 0 },
  { essence_stones: 90, mythic_gear: 0 },
  { essence_stones: 100, mythic_gear: 0 },
  { essence_stones: 110, mythic_gear: 1 },
  { essence_stones: 120, mythic_gear: 2 },
  { essence_stones: 130, mythic_gear: 3 },
  { essence_stones: 140, mythic_gear: 4 },
  { essence_stones: 150, mythic_gear: 5 },
  { essence_stones: 160, mythic_gear: 6 },
  { essence_stones: 170, mythic_gear: 7 },
  { essence_stones: 180, mythic_gear: 8 },
  { essence_stones: 190, mythic_gear: 9 },
  { essence_stones: 200, mythic_gear: 10 },
];

// Legendary Enhancement: levels 0→100, costs XP + Mithril/LegendaryGear at milestones
const LEGENDARY_COSTS: { xp: number; mithril: number; legendary_gear: number }[] = [
  { xp: 0, mithril: 0, legendary_gear: 2 },
  { xp: 2500, mithril: 0, legendary_gear: 0 },
  { xp: 2550, mithril: 0, legendary_gear: 0 },
  { xp: 2600, mithril: 0, legendary_gear: 0 },
  { xp: 2650, mithril: 0, legendary_gear: 0 },
  { xp: 2700, mithril: 0, legendary_gear: 0 },
  { xp: 2750, mithril: 0, legendary_gear: 0 },
  { xp: 2800, mithril: 0, legendary_gear: 0 },
  { xp: 2850, mithril: 0, legendary_gear: 0 },
  { xp: 2900, mithril: 0, legendary_gear: 0 },
  { xp: 2950, mithril: 0, legendary_gear: 0 },
  { xp: 3000, mithril: 0, legendary_gear: 0 },
  { xp: 3050, mithril: 0, legendary_gear: 0 },
  { xp: 3100, mithril: 0, legendary_gear: 0 },
  { xp: 3150, mithril: 0, legendary_gear: 0 },
  { xp: 3200, mithril: 0, legendary_gear: 0 },
  { xp: 3250, mithril: 0, legendary_gear: 0 },
  { xp: 3300, mithril: 0, legendary_gear: 0 },
  { xp: 3350, mithril: 0, legendary_gear: 0 },
  { xp: 0, mithril: 10, legendary_gear: 3 },
  { xp: 3500, mithril: 0, legendary_gear: 0 },
  { xp: 3550, mithril: 0, legendary_gear: 0 },
  { xp: 3600, mithril: 0, legendary_gear: 0 },
  { xp: 3650, mithril: 0, legendary_gear: 0 },
  { xp: 3700, mithril: 0, legendary_gear: 0 },
  { xp: 3750, mithril: 0, legendary_gear: 0 },
  { xp: 3800, mithril: 0, legendary_gear: 0 },
  { xp: 3850, mithril: 0, legendary_gear: 0 },
  { xp: 3900, mithril: 0, legendary_gear: 0 },
  { xp: 3950, mithril: 0, legendary_gear: 0 },
  { xp: 4000, mithril: 0, legendary_gear: 0 },
  { xp: 4050, mithril: 0, legendary_gear: 0 },
  { xp: 4100, mithril: 0, legendary_gear: 0 },
  { xp: 4150, mithril: 0, legendary_gear: 0 },
  { xp: 4200, mithril: 0, legendary_gear: 0 },
  { xp: 4250, mithril: 0, legendary_gear: 0 },
  { xp: 4300, mithril: 0, legendary_gear: 0 },
  { xp: 4350, mithril: 0, legendary_gear: 0 },
  { xp: 4400, mithril: 0, legendary_gear: 0 },
  { xp: 0, mithril: 20, legendary_gear: 5 },
  { xp: 4450, mithril: 0, legendary_gear: 0 },
  { xp: 4500, mithril: 0, legendary_gear: 0 },
  { xp: 4550, mithril: 0, legendary_gear: 0 },
  { xp: 4600, mithril: 0, legendary_gear: 0 },
  { xp: 4650, mithril: 0, legendary_gear: 0 },
  { xp: 4700, mithril: 0, legendary_gear: 0 },
  { xp: 4750, mithril: 0, legendary_gear: 0 },
  { xp: 4800, mithril: 0, legendary_gear: 0 },
  { xp: 4850, mithril: 0, legendary_gear: 0 },
  { xp: 4900, mithril: 0, legendary_gear: 0 },
  { xp: 4950, mithril: 0, legendary_gear: 0 },
  { xp: 5000, mithril: 0, legendary_gear: 0 },
  { xp: 5050, mithril: 0, legendary_gear: 0 },
  { xp: 5100, mithril: 0, legendary_gear: 0 },
  { xp: 5150, mithril: 0, legendary_gear: 0 },
  { xp: 5200, mithril: 0, legendary_gear: 0 },
  { xp: 5250, mithril: 0, legendary_gear: 0 },
  { xp: 5300, mithril: 0, legendary_gear: 0 },
  { xp: 5350, mithril: 0, legendary_gear: 0 },
  { xp: 0, mithril: 30, legendary_gear: 5 },
  { xp: 5500, mithril: 0, legendary_gear: 0 },
  { xp: 5600, mithril: 0, legendary_gear: 0 },
  { xp: 5700, mithril: 0, legendary_gear: 0 },
  { xp: 5800, mithril: 0, legendary_gear: 0 },
  { xp: 5900, mithril: 0, legendary_gear: 0 },
  { xp: 6000, mithril: 0, legendary_gear: 0 },
  { xp: 6100, mithril: 0, legendary_gear: 0 },
  { xp: 6200, mithril: 0, legendary_gear: 0 },
  { xp: 6300, mithril: 0, legendary_gear: 0 },
  { xp: 6400, mithril: 0, legendary_gear: 0 },
  { xp: 6500, mithril: 0, legendary_gear: 0 },
  { xp: 6600, mithril: 0, legendary_gear: 0 },
  { xp: 6700, mithril: 0, legendary_gear: 0 },
  { xp: 6800, mithril: 0, legendary_gear: 0 },
  { xp: 6900, mithril: 0, legendary_gear: 0 },
  { xp: 7000, mithril: 0, legendary_gear: 0 },
  { xp: 7100, mithril: 0, legendary_gear: 0 },
  { xp: 7200, mithril: 0, legendary_gear: 0 },
  { xp: 7300, mithril: 0, legendary_gear: 0 },
  { xp: 0, mithril: 40, legendary_gear: 10 },
  { xp: 7500, mithril: 0, legendary_gear: 0 },
  { xp: 7600, mithril: 0, legendary_gear: 0 },
  { xp: 7700, mithril: 0, legendary_gear: 0 },
  { xp: 7800, mithril: 0, legendary_gear: 0 },
  { xp: 7900, mithril: 0, legendary_gear: 0 },
  { xp: 8000, mithril: 0, legendary_gear: 0 },
  { xp: 8100, mithril: 0, legendary_gear: 0 },
  { xp: 8200, mithril: 0, legendary_gear: 0 },
  { xp: 8300, mithril: 0, legendary_gear: 0 },
  { xp: 8400, mithril: 0, legendary_gear: 0 },
  { xp: 8500, mithril: 0, legendary_gear: 0 },
  { xp: 8600, mithril: 0, legendary_gear: 0 },
  { xp: 8700, mithril: 0, legendary_gear: 0 },
  { xp: 8800, mithril: 0, legendary_gear: 0 },
  { xp: 8900, mithril: 0, legendary_gear: 0 },
  { xp: 9000, mithril: 0, legendary_gear: 0 },
  { xp: 9100, mithril: 0, legendary_gear: 0 },
  { xp: 9200, mithril: 0, legendary_gear: 0 },
  { xp: 9300, mithril: 0, legendary_gear: 0 },
  { xp: 0, mithril: 50, legendary_gear: 10 },
];

// Chief Gear: per-tier total costs (46 tiers). Cost to upgrade from this tier to the next.
// ha=Hardened Alloy, ps=Polishing Solution, dp=Design Plans, la=Lunar Amber
const CHIEF_GEAR_COSTS: { ha: number; ps: number; dp: number; la: number }[] = [
  // Green (tiers 1-2)
  { ha: 1500, ps: 15, dp: 0, la: 0 },
  { ha: 3800, ps: 40, dp: 0, la: 0 },
  // Blue (tiers 3-6)
  { ha: 7000, ps: 70, dp: 0, la: 0 },
  { ha: 9700, ps: 95, dp: 0, la: 0 },
  { ha: 0, ps: 0, dp: 45, la: 0 },
  { ha: 0, ps: 0, dp: 50, la: 0 },
  // Purple (tiers 7-14)
  { ha: 0, ps: 0, dp: 60, la: 0 },
  { ha: 0, ps: 0, dp: 70, la: 0 },
  { ha: 6500, ps: 65, dp: 40, la: 0 },
  { ha: 8000, ps: 80, dp: 50, la: 0 },
  { ha: 10000, ps: 95, dp: 60, la: 0 },
  { ha: 11000, ps: 110, dp: 70, la: 0 },
  { ha: 13000, ps: 130, dp: 85, la: 0 },
  { ha: 15000, ps: 160, dp: 100, la: 0 },
  // Gold (tiers 15-26)
  { ha: 22000, ps: 220, dp: 40, la: 0 },
  { ha: 23000, ps: 230, dp: 40, la: 0 },
  { ha: 25000, ps: 250, dp: 45, la: 0 },
  { ha: 26000, ps: 260, dp: 45, la: 0 },
  { ha: 28000, ps: 280, dp: 45, la: 0 },
  { ha: 30000, ps: 300, dp: 55, la: 0 },
  { ha: 32000, ps: 320, dp: 55, la: 0 },
  { ha: 35000, ps: 340, dp: 55, la: 0 },
  { ha: 38000, ps: 390, dp: 55, la: 0 },
  { ha: 43000, ps: 430, dp: 75, la: 0 },
  { ha: 45000, ps: 460, dp: 80, la: 0 },
  { ha: 48000, ps: 500, dp: 85, la: 0 },
  // Pink (tiers 27-46) — from verified step data
  { ha: 50000, ps: 530, dp: 85, la: 10 },
  { ha: 52000, ps: 560, dp: 90, la: 10 },
  { ha: 54000, ps: 590, dp: 95, la: 10 },
  { ha: 56000, ps: 620, dp: 100, la: 10 },
  { ha: 59000, ps: 670, dp: 110, la: 15 },
  { ha: 61000, ps: 700, dp: 115, la: 15 },
  { ha: 63000, ps: 730, dp: 120, la: 15 },
  { ha: 65000, ps: 760, dp: 125, la: 15 },
  { ha: 68000, ps: 810, dp: 135, la: 20 },
  { ha: 70000, ps: 840, dp: 140, la: 20 },
  { ha: 72000, ps: 870, dp: 145, la: 20 },
  { ha: 74000, ps: 900, dp: 150, la: 20 },
  { ha: 77000, ps: 950, dp: 160, la: 25 },
  { ha: 80000, ps: 990, dp: 165, la: 25 },
  { ha: 83000, ps: 1030, dp: 170, la: 25 },
  { ha: 86000, ps: 1070, dp: 180, la: 25 },
  { ha: 120000, ps: 1500, dp: 250, la: 40 },
  { ha: 140000, ps: 1650, dp: 275, la: 40 },
  { ha: 160000, ps: 1800, dp: 300, la: 40 },
  { ha: 144000, ps: 1560, dp: 260, la: 32 },
];

// Chief Gear tier names (matching chief/page.tsx GEAR_TIERS)
const CHIEF_TIER_NAMES = [
  "Green 0\u2605", "Green 1\u2605",
  "Blue 0\u2605", "Blue 1\u2605", "Blue 2\u2605", "Blue 3\u2605",
  "Purple 0\u2605", "Purple 1\u2605", "Purple 2\u2605", "Purple 3\u2605",
  "Purple T1 0\u2605", "Purple T1 1\u2605", "Purple T1 2\u2605", "Purple T1 3\u2605",
  "Gold 0\u2605", "Gold 1\u2605", "Gold 2\u2605", "Gold 3\u2605",
  "Gold T1 0\u2605", "Gold T1 1\u2605", "Gold T1 2\u2605", "Gold T1 3\u2605",
  "Gold T2 0\u2605", "Gold T2 1\u2605", "Gold T2 2\u2605", "Gold T2 3\u2605",
  "Pink 0\u2605", "Pink 1\u2605", "Pink 2\u2605", "Pink 3\u2605",
  "Pink T1 0\u2605", "Pink T1 1\u2605", "Pink T1 2\u2605", "Pink T1 3\u2605",
  "Pink T2 0\u2605", "Pink T2 1\u2605", "Pink T2 2\u2605", "Pink T2 3\u2605",
  "Pink T3 0\u2605", "Pink T3 1\u2605", "Pink T3 2\u2605", "Pink T3 3\u2605",
  "Pink T4 0\u2605", "Pink T4 1\u2605", "Pink T4 2\u2605", "Pink T4 3\u2605",
];

const CHIEF_TIER_COLORS: Record<string, string> = {
  Green: '#2ECC71', Blue: '#3498DB', Purple: '#9B59B6', Gold: '#F1C40F', Pink: '#E84393',
};

// Chief Gear bonus % per tier (Attack + Defense per piece)
const CHIEF_TIER_BONUSES: number[] = [
  9.35, 12.75,
  17.00, 20.25, 24.50, 29.75,
  34.00, 38.00, 42.50, 47.00, 48.50, 50.00, 52.00, 54.23,
  56.78, 59.50, 62.50, 66.00, 69.00, 72.00, 75.50, 79.00, 80.50, 82.00, 83.50, 85.00,
  89.25, 94.00, 99.00, 104.50, 110.00, 116.00, 122.50, 129.00,
  136.00, 143.50, 151.50, 160.00, 165.00, 171.00, 178.00, 187.00,
  193.00, 200.00, 208.00, 217.00,
];

// Chief Charms: per-level costs (16 levels)
const CHARM_COSTS: { charm_guide: number; charm_design: number; jewel_secrets: number }[] = [
  { charm_guide: 5, charm_design: 5, jewel_secrets: 0 },
  { charm_guide: 40, charm_design: 15, jewel_secrets: 0 },
  { charm_guide: 60, charm_design: 40, jewel_secrets: 0 },
  { charm_guide: 80, charm_design: 100, jewel_secrets: 0 },
  { charm_guide: 100, charm_design: 200, jewel_secrets: 0 },
  { charm_guide: 120, charm_design: 300, jewel_secrets: 0 },
  { charm_guide: 140, charm_design: 400, jewel_secrets: 0 },
  { charm_guide: 200, charm_design: 400, jewel_secrets: 0 },
  { charm_guide: 300, charm_design: 400, jewel_secrets: 0 },
  { charm_guide: 420, charm_design: 420, jewel_secrets: 0 },
  { charm_guide: 560, charm_design: 420, jewel_secrets: 0 },
  { charm_guide: 580, charm_design: 450, jewel_secrets: 15 },
  { charm_guide: 580, charm_design: 450, jewel_secrets: 30 },
  { charm_guide: 600, charm_design: 500, jewel_secrets: 45 },
  { charm_guide: 600, charm_design: 500, jewel_secrets: 70 },
  { charm_guide: 650, charm_design: 550, jewel_secrets: 100 },
];

// Charm bonus % per completed main level (Lethality & Health per slot)
const CHARM_BONUSES: number[] = [
  0, 9.0, 12.0, 16.0, 19.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 64.0, 73.0, 82.0, 91.0, 100.0,
];

function getCharmBonus(level: string): number {
  if (!level.includes('-')) {
    // Simple levels 1-4: return the completed level bonus (matches wiki)
    const lvl = parseInt(level) || 0;
    return CHARM_BONUSES[lvl] || 0;
  }
  const [mainStr, subStr] = level.split('-');
  const main = parseInt(mainStr);
  const sub = parseInt(subStr);
  if (sub === 0) return CHARM_BONUSES[main] || 0; // X-0: completed level X (matches wiki)
  // Sub-levels -1, -2, -3: partial progress from level main toward level main+1
  const prevBonus = CHARM_BONUSES[main] || 0;
  const nextBonus = CHARM_BONUSES[main + 1] || prevBonus;
  return prevBonus + (nextBonus - prevBonus) * sub / 4;
}

// Build charm level options: 1, 2, 3, 4, 4-1, 4-2, 4-3, 5-0, ..., 15-3, 16-0
const CHARM_LEVELS: string[] = ['1', '2', '3', '4', '4-1', '4-2', '4-3'];
for (let level = 5; level <= 15; level++) {
  CHARM_LEVELS.push(`${level}-0`, `${level}-1`, `${level}-2`, `${level}-3`);
}
CHARM_LEVELS.push('16-0');

function charmLevelIndex(level: string): number {
  return CHARM_LEVELS.indexOf(level);
}

function charmLevelCost(level: string): { charm_guide: number; charm_design: number; jewel_secrets: number } {
  const zero = { charm_guide: 0, charm_design: 0, jewel_secrets: 0 };
  if (!level.includes('-')) {
    // Levels 1-4: full cost (single step to reach this level)
    const lvl = parseInt(level);
    return CHARM_COSTS[lvl - 1] || zero;
  }
  const [mainStr, subStr] = level.split('-');
  const main = parseInt(mainStr);
  const sub = parseInt(subStr);
  // X-0 completes the previous level's transition; X-1/2/3 start the next
  const costIndex = sub === 0 ? main - 1 : main;
  const c = CHARM_COSTS[costIndex] || zero;
  return {
    charm_guide: Math.ceil(c.charm_guide / 4),
    charm_design: Math.ceil(c.charm_design / 4),
    jewel_secrets: Math.ceil(c.jewel_secrets / 4),
  };
}

// ══════════════════════════════════════════════════════════════════════
// MAIN PAGE
// ══════════════════════════════════════════════════════════════════════

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

  const getPriorityLevel = (p: number) => p <= 3 ? 'high' : p <= 6 ? 'medium' : 'low';

  const filteredRecs = recommendations.filter((rec) => {
    if (filterType !== 'all' && rec.category !== filterType) return false;
    if (filterPriority !== 'all' && getPriorityLevel(rec.priority) !== filterPriority) return false;
    return true;
  });

  const priorityColors: Record<string, string> = {
    high: 'border-ice/60 bg-ice/10',
    medium: 'border-ice/30 bg-ice/5',
    low: 'border-surface-border bg-surface',
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
    hero: '\uD83E\uDDB8',
    gear: '\uD83D\uDEE1\uFE0F',
    building: '\uD83C\uDFD7\uFE0F',
    research: '\uD83D\uDD2C',
    troop: '\u2694\uFE0F',
  };

  const tabs: { id: TabType; label: string }[] = [
    { id: 'recommendations', label: 'Top Recommendations' },
    { id: 'heroes', label: 'Best Heroes to Invest' },
    { id: 'calculators', label: 'Upgrade Calculators' },
  ];

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Upgrade Recommendations</h1>
          <p className="text-frost-muted mt-2">Personalized upgrade priorities based on your profile</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-surface-border pb-2">
          {tabs.map((tab) => (
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

        {/* Content */}
        {isLoading && activeTab !== 'calculators' ? (
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
        ) : (
          <UpgradeCalculatorsTab />
        )}
      </div>
    </PageLayout>
  );
}

// ══════════════════════════════════════════════════════════════════════
// RECOMMENDATIONS TAB (unchanged)
// ══════════════════════════════════════════════════════════════════════

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
                  {type === 'all' ? 'All Categories' : formatLabel(type)}
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
          <div className="text-4xl mb-4">&#127919;</div>
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
                  <div className="text-3xl">{categoryIcons[rec.category] || '\uD83D\uDCCB'}</div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      {rec.hero && (
                        <span className="font-bold text-frost">{rec.hero}</span>
                      )}
                      <span className="text-sm px-2 py-0.5 rounded bg-surface-hover text-frost-muted">
                        {formatLabel(rec.category)}
                      </span>
                      {rec.relevance_tags?.length > 0 && (
                        <div className="flex gap-1">
                          {rec.relevance_tags.slice(0, 3).map((tag, j) => (
                            <span key={j} className="text-xs px-1.5 py-0.5 rounded bg-ice/10 text-ice">
                              {formatLabel(tag)}
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
                      <p className="text-xs text-frost-muted mt-1">Resources: {formatLabel(rec.resources)}</p>
                    )}
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                    level === 'high' ? 'bg-ice/20 text-ice' :
                    level === 'medium' ? 'bg-ice/10 text-ice/70' :
                    'bg-surface-hover text-frost-muted'
                  }`}>
                    {formatLabel(level)}
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

// ══════════════════════════════════════════════════════════════════════
// HERO INVESTMENTS TAB (unchanged)
// ══════════════════════════════════════════════════════════════════════

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
        <div className="text-4xl mb-4">&#129464;</div>
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
                <span>{'\u2605'.repeat(inv.current_stars)}{'\u2606'.repeat(5 - inv.current_stars)} → {'\u2605'.repeat(inv.target_stars)}</span>
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

// ══════════════════════════════════════════════════════════════════════
// UPGRADE CALCULATORS TAB
// ══════════════════════════════════════════════════════════════════════

const CALC_DEFS: { id: CalcType; label: string; category: string; color: string; activeColor: string }[] = [
  { id: 'enhancement', label: 'Enhancement', category: 'Hero Gear', color: 'text-blue-400', activeColor: 'border-blue-500/50 bg-blue-500/10 text-blue-400' },
  { id: 'legendary', label: 'Legendary', category: 'Hero Gear', color: 'text-blue-400', activeColor: 'border-blue-500/50 bg-blue-500/10 text-blue-400' },
  { id: 'mastery', label: 'Mastery', category: 'Hero Gear', color: 'text-blue-400', activeColor: 'border-blue-500/50 bg-blue-500/10 text-blue-400' },
  { id: 'chief_gear', label: 'Chief Gear', category: 'Chief', color: 'text-pink-400', activeColor: 'border-pink-500/50 bg-pink-500/10 text-pink-400' },
  { id: 'charms', label: 'Charms', category: 'Chief', color: 'text-green-400', activeColor: 'border-green-500/50 bg-green-500/10 text-green-400' },
  { id: 'war_academy', label: 'War Academy', category: 'Buildings', color: 'text-orange-400', activeColor: 'border-orange-500/50 bg-orange-500/10 text-orange-400' },
];

function UpgradeCalculatorsTab() {
  const [calc, setCalc] = useState<CalcType>('enhancement');

  // Group calculators by category for the sub-tab selector
  const categories = ['Hero Gear', 'Chief', 'Buildings'];

  return (
    <div className="space-y-6">
      {/* Sub-tab Selector */}
      <div className="card">
        <div className="flex items-end gap-4 overflow-x-auto pb-1">
          {categories.map((cat, ci) => (
            <div key={cat} className="flex items-end gap-1">
              {ci > 0 && (
                <div className="w-px h-10 bg-surface-border mx-2 shrink-0" />
              )}
              <div>
                <div className="text-[10px] uppercase tracking-wider text-frost-muted mb-1.5 px-1">
                  {cat}
                </div>
                <div className="flex gap-1.5">
                  {CALC_DEFS.filter(d => d.category === cat).map((d) => (
                    <button
                      key={d.id}
                      onClick={() => setCalc(d.id)}
                      className={`px-3 py-2 rounded-lg text-xs font-medium transition-colors border whitespace-nowrap ${
                        calc === d.id
                          ? d.activeColor
                          : 'border-surface-border bg-surface text-frost-muted hover:text-frost hover:bg-surface-hover'
                      }`}
                    >
                      {d.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Calculator Content */}
      {calc === 'enhancement' && <EnhancementCalc />}
      {calc === 'legendary' && <LegendaryCalc />}
      {calc === 'mastery' && <MasteryCalc />}
      {calc === 'chief_gear' && <ChiefGearCalc />}
      {calc === 'charms' && <CharmsCalc />}
      {calc === 'war_academy' && <WarAcademyCalc />}
    </div>
  );
}

// ── Enhancement Calculator ──────────────────────────────────────────

function EnhancementCalc() {
  const [fromLevel, setFromLevel] = useState(0);
  const [toLevel, setToLevel] = useState(100);
  const [slotCount, setSlotCount] = useState(1);

  const costs = useMemo(() => {
    if (fromLevel >= toLevel) return null;
    let totalXp = 0;
    for (let i = fromLevel; i < toLevel; i++) {
      totalXp += ENHANCEMENT_COSTS[i];
    }
    return { perSlot: totalXp, total: totalXp * slotCount };
  }, [fromLevel, toLevel, slotCount]);

  return (
    <div className="space-y-4">
      {/* Info Banner */}
      <div className="card border border-blue-500/30 bg-blue-500/5">
        <p className="text-sm text-frost">
          Calculate <strong className="text-blue-400">Enhancement XP</strong> needed for pre-Legendary hero gear (Gold/Mythic quality).
          Gear must reach Enhancement 100 + Mastery 10 before it can ascend to Legendary.
        </p>
      </div>

      {/* Inputs */}
      <div className="card">
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="text-xs text-frost-muted block mb-1">From Level</label>
            <input
              type="number"
              min={0}
              max={99}
              value={fromLevel}
              onChange={(e) => setFromLevel(Math.max(0, Math.min(99, Number(e.target.value))))}
              className="input w-full text-center text-lg"
            />
          </div>
          <div>
            <label className="text-xs text-frost-muted block mb-1">To Level</label>
            <input
              type="number"
              min={1}
              max={100}
              value={toLevel}
              onChange={(e) => setToLevel(Math.max(1, Math.min(100, Number(e.target.value))))}
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
          <p className="text-frost-muted">Set &quot;From Level&quot; lower than &quot;To Level&quot; to see costs</p>
        </div>
      ) : costs && (
        <div className="card">
          <h3 className="section-header mb-4">
            Cost: Level {fromLevel} → {toLevel}
          </h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border">
                <th className="text-left py-2 px-3 text-frost-muted font-medium">Resource</th>
                <th className="text-right py-2 px-3 text-frost-muted font-medium">Per Slot</th>
                {slotCount > 1 && (
                  <th className="text-right py-2 px-3 text-ice font-medium">
                    Total ({slotCount} slots)
                  </th>
                )}
              </tr>
            </thead>
            <tbody>
              <CostRow
                label="Enhancement XP"
                perSlot={costs.perSlot}
                total={slotCount > 1 ? costs.total : undefined}
                color="text-blue-400"
              />
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ── Legendary Enhancement Calculator ────────────────────────────────

function LegendaryCalc() {
  const [fromLevel, setFromLevel] = useState(0);
  const [toLevel, setToLevel] = useState(100);
  const [slotCount, setSlotCount] = useState(1);

  const costs = useMemo(() => {
    if (fromLevel >= toLevel) return null;
    let totalXp = 0, totalMithril = 0, totalGear = 0;
    for (let i = fromLevel; i < toLevel; i++) {
      totalXp += LEGENDARY_COSTS[i].xp;
      totalMithril += LEGENDARY_COSTS[i].mithril;
      totalGear += LEGENDARY_COSTS[i].legendary_gear;
    }
    return {
      perSlot: { xp: totalXp, mithril: totalMithril, legendary_gear: totalGear },
      total: { xp: totalXp * slotCount, mithril: totalMithril * slotCount, legendary_gear: totalGear * slotCount },
    };
  }, [fromLevel, toLevel, slotCount]);

  const milestones = [1, 20, 40, 60, 80, 100].filter((m) => m > fromLevel && m <= toLevel);

  return (
    <div className="space-y-4">
      {/* Info Banner */}
      <div className="card border border-blue-500/30 bg-blue-500/5">
        <p className="text-sm text-frost">
          Calculate costs for <strong className="text-blue-400">Legendary Enhancement</strong> (post-ascension gear).
          Requires XP plus Mithril and Legendary Gear at every 20-level milestone.
        </p>
      </div>

      {/* Inputs */}
      <div className="card">
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="text-xs text-frost-muted block mb-1">From Level</label>
            <input
              type="number"
              min={0}
              max={99}
              value={fromLevel}
              onChange={(e) => setFromLevel(Math.max(0, Math.min(99, Number(e.target.value))))}
              className="input w-full text-center text-lg"
            />
          </div>
          <div>
            <label className="text-xs text-frost-muted block mb-1">To Level</label>
            <input
              type="number"
              min={1}
              max={100}
              value={toLevel}
              onChange={(e) => setToLevel(Math.max(1, Math.min(100, Number(e.target.value))))}
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
          <p className="text-frost-muted">Set &quot;From Level&quot; lower than &quot;To Level&quot; to see costs</p>
        </div>
      ) : costs && (
        <div className="space-y-4">
          <div className="card">
            <h3 className="section-header mb-4">
              Cost: Level {fromLevel} → {toLevel}
            </h3>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-surface-border">
                  <th className="text-left py-2 px-3 text-frost-muted font-medium">Resource</th>
                  <th className="text-right py-2 px-3 text-frost-muted font-medium">Per Slot</th>
                  {slotCount > 1 && (
                    <th className="text-right py-2 px-3 text-ice font-medium">
                      Total ({slotCount} slots)
                    </th>
                  )}
                </tr>
              </thead>
              <tbody>
                <CostRow label="Gear XP" perSlot={costs.perSlot.xp} total={slotCount > 1 ? costs.total.xp : undefined} color="text-blue-400" />
                <CostRow label="Mithril" perSlot={costs.perSlot.mithril} total={slotCount > 1 ? costs.total.mithril : undefined} color="text-purple-400" />
                <CostRow label="Legendary Gear" perSlot={costs.perSlot.legendary_gear} total={slotCount > 1 ? costs.total.legendary_gear : undefined} color="text-red-400" />
              </tbody>
            </table>
          </div>

          {/* Milestone Breakdown */}
          {milestones.length > 0 && (
            <div className="card">
              <h3 className="section-header mb-3">Milestone Unlocks</h3>
              <p className="text-xs text-frost-muted mb-3">
                Every 20 levels requires Mithril and Legendary Gear to unlock the next tier
              </p>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-surface-border">
                    <th className="text-left py-2 px-3 text-frost-muted font-medium">Level</th>
                    <th className="text-right py-2 px-3 text-frost-muted font-medium">Mithril</th>
                    <th className="text-right py-2 px-3 text-frost-muted font-medium">Legendary Gear</th>
                  </tr>
                </thead>
                <tbody>
                  {milestones.map((m) => {
                    const edge = LEGENDARY_COSTS[m - 1];
                    return (
                      <tr key={m} className="border-b border-surface-border/30">
                        <td className="py-2 px-3 font-medium text-frost">Level {m}</td>
                        <td className="py-2 px-3 text-right text-purple-400">
                          {edge.mithril > 0 ? edge.mithril : '-'}
                        </td>
                        <td className="py-2 px-3 text-right text-red-400">
                          {edge.legendary_gear > 0 ? edge.legendary_gear : '-'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Mastery Forging Calculator ──────────────────────────────────────

function MasteryCalc() {
  const [fromLevel, setFromLevel] = useState(0);
  const [toLevel, setToLevel] = useState(20);
  const [slotCount, setSlotCount] = useState(1);

  const costs = useMemo(() => {
    if (fromLevel >= toLevel) return null;
    let totalStones = 0, totalGear = 0;
    for (let i = fromLevel; i < toLevel; i++) {
      totalStones += MASTERY_COSTS[i].essence_stones;
      totalGear += MASTERY_COSTS[i].mythic_gear;
    }
    return {
      perSlot: { essence_stones: totalStones, mythic_gear: totalGear },
      total: { essence_stones: totalStones * slotCount, mythic_gear: totalGear * slotCount },
    };
  }, [fromLevel, toLevel, slotCount]);

  return (
    <div className="space-y-4">
      {/* Info Banner */}
      <div className="card border border-blue-500/30 bg-blue-500/5">
        <p className="text-sm text-frost">
          Calculate <strong className="text-blue-400">Mastery Forging</strong> costs for Gold-quality hero gear.
          Requires Essence Stones and Mythic Gear pieces (at level 11+). Unlocks at Enhancement 20.
        </p>
      </div>

      {/* Inputs */}
      <div className="card">
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="text-xs text-frost-muted block mb-1">From Level</label>
            <input
              type="number"
              min={0}
              max={19}
              value={fromLevel}
              onChange={(e) => setFromLevel(Math.max(0, Math.min(19, Number(e.target.value))))}
              className="input w-full text-center text-lg"
            />
          </div>
          <div>
            <label className="text-xs text-frost-muted block mb-1">To Level</label>
            <input
              type="number"
              min={1}
              max={20}
              value={toLevel}
              onChange={(e) => setToLevel(Math.max(1, Math.min(20, Number(e.target.value))))}
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
          <p className="text-frost-muted">Set &quot;From Level&quot; lower than &quot;To Level&quot; to see costs</p>
        </div>
      ) : costs && (
        <div className="card">
          <h3 className="section-header mb-4">
            Cost: Level {fromLevel} → {toLevel}
          </h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border">
                <th className="text-left py-2 px-3 text-frost-muted font-medium">Resource</th>
                <th className="text-right py-2 px-3 text-frost-muted font-medium">Per Slot</th>
                {slotCount > 1 && (
                  <th className="text-right py-2 px-3 text-ice font-medium">
                    Total ({slotCount} slots)
                  </th>
                )}
              </tr>
            </thead>
            <tbody>
              <CostRow label="Essence Stones" perSlot={costs.perSlot.essence_stones} total={slotCount > 1 ? costs.total.essence_stones : undefined} color="text-amber-400" />
              <CostRow label="Mythic Gear" perSlot={costs.perSlot.mythic_gear} total={slotCount > 1 ? costs.total.mythic_gear : undefined} color="text-orange-400" />
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ── Chief Gear Calculator ───────────────────────────────────────────

function ChiefGearCalc() {
  const [fromTier, setFromTier] = useState(0); // index into CHIEF_TIER_NAMES (0-based)
  const [toTier, setToTier] = useState(25);
  const [pieceCount, setPieceCount] = useState(1);

  const costs = useMemo(() => {
    if (fromTier >= toTier) return null;
    let ha = 0, ps = 0, dp = 0, la = 0;
    for (let i = fromTier; i < toTier; i++) {
      ha += CHIEF_GEAR_COSTS[i].ha;
      ps += CHIEF_GEAR_COSTS[i].ps;
      dp += CHIEF_GEAR_COSTS[i].dp;
      la += CHIEF_GEAR_COSTS[i].la;
    }
    return {
      perPiece: { ha, ps, dp, la },
      total: { ha: ha * pieceCount, ps: ps * pieceCount, dp: dp * pieceCount, la: la * pieceCount },
    };
  }, [fromTier, toTier, pieceCount]);

  const tierColor = (idx: number): string => {
    const name = CHIEF_TIER_NAMES[idx];
    const colorKey = name.split(' ')[0];
    return CHIEF_TIER_COLORS[colorKey] || '#ffffff';
  };

  return (
    <div className="space-y-4">
      {/* Info Banner */}
      <div className="card border border-pink-500/30 bg-pink-500/5">
        <p className="text-sm text-frost">
          Calculate materials to upgrade <strong className="text-pink-400">Chief Gear</strong> tiers.
          Each piece provides Attack &amp; Defense for its troop type (Infantry, Lancer, or Marksman).
        </p>
      </div>

      {/* Inputs */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="text-xs text-frost-muted block mb-1">From Tier</label>
            <select
              value={fromTier}
              onChange={(e) => setFromTier(Number(e.target.value))}
              className="input w-full text-sm"
              style={{ color: tierColor(fromTier) }}
            >
              {CHIEF_TIER_NAMES.map((name, i) => (
                <option key={i} value={i} style={{ color: CHIEF_TIER_COLORS[name.split(' ')[0]] }}>
                  {name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-frost-muted block mb-1">To Tier</label>
            <select
              value={toTier}
              onChange={(e) => setToTier(Number(e.target.value))}
              className="input w-full text-sm"
              style={{ color: tierColor(toTier) }}
            >
              {CHIEF_TIER_NAMES.map((name, i) => (
                <option key={i} value={i} style={{ color: CHIEF_TIER_COLORS[name.split(' ')[0]] }}>
                  {name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-frost-muted block mb-1">Gear Pieces</label>
            <select
              value={pieceCount}
              onChange={(e) => setPieceCount(Number(e.target.value))}
              className="input w-full text-center text-lg"
            >
              <option value={1}>1 piece</option>
              <option value={2}>2 pieces</option>
              <option value={3}>3 pieces</option>
              <option value={4}>4 pieces</option>
              <option value={5}>5 pieces</option>
              <option value={6}>6 pieces (all)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results */}
      {fromTier >= toTier ? (
        <div className="card text-center py-8">
          <p className="text-frost-muted">Set &quot;From Tier&quot; lower than &quot;To Tier&quot; to see costs</p>
        </div>
      ) : costs && (
        <div className="space-y-4">
          {/* Stat Bonus */}
          <div className="card border border-pink-500/20">
            <div className="flex items-center justify-between">
              <div className="text-sm text-frost-muted">Attack + Defense Bonus (per piece)</div>
              <div className="flex items-center gap-3">
                <span className="text-frost" style={{ color: tierColor(fromTier) }}>
                  +{CHIEF_TIER_BONUSES[fromTier]}%
                </span>
                <span className="text-frost-muted">&rarr;</span>
                <span className="font-bold text-lg" style={{ color: tierColor(toTier) }}>
                  +{CHIEF_TIER_BONUSES[toTier]}%
                </span>
                <span className="text-xs px-2 py-0.5 rounded bg-green-500/10 text-green-400">
                  +{(CHIEF_TIER_BONUSES[toTier] - CHIEF_TIER_BONUSES[fromTier]).toFixed(2)}%
                </span>
              </div>
            </div>
          </div>

          {/* Cost Table */}
          <div className="card">
            <h3 className="section-header mb-4">
              Cost: <span style={{ color: tierColor(fromTier) }}>{CHIEF_TIER_NAMES[fromTier]}</span>
              {' → '}
              <span style={{ color: tierColor(toTier) }}>{CHIEF_TIER_NAMES[toTier]}</span>
            </h3>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-surface-border">
                  <th className="text-left py-2 px-3 text-frost-muted font-medium">Resource</th>
                  <th className="text-right py-2 px-3 text-frost-muted font-medium">Per Piece</th>
                  {pieceCount > 1 && (
                    <th className="text-right py-2 px-3 text-ice font-medium">
                      Total ({pieceCount} pieces)
                    </th>
                  )}
                </tr>
              </thead>
              <tbody>
                {costs.perPiece.ha > 0 && (
                  <CostRow label="Hardened Alloy" perSlot={costs.perPiece.ha} total={pieceCount > 1 ? costs.total.ha : undefined} color="text-gray-300" />
                )}
                {costs.perPiece.ps > 0 && (
                  <CostRow label="Polishing Solution" perSlot={costs.perPiece.ps} total={pieceCount > 1 ? costs.total.ps : undefined} color="text-cyan-400" />
                )}
                {costs.perPiece.dp > 0 && (
                  <CostRow label="Design Plans" perSlot={costs.perPiece.dp} total={pieceCount > 1 ? costs.total.dp : undefined} color="text-yellow-400" />
                )}
                {costs.perPiece.la > 0 && (
                  <CostRow label="Lunar Amber" perSlot={costs.perPiece.la} total={pieceCount > 1 ? costs.total.la : undefined} color="text-amber-500" />
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Charms Calculator ───────────────────────────────────────────────

function CharmsCalc() {
  const [fromLevel, setFromLevel] = useState('1');
  const [toLevel, setToLevel] = useState('16-3');
  const [slotCount, setSlotCount] = useState(1);

  const costs = useMemo(() => {
    const fromIdx = charmLevelIndex(fromLevel);
    const toIdx = charmLevelIndex(toLevel);
    if (fromIdx < 0 || toIdx < 0 || fromIdx >= toIdx) return null;

    let totalGuide = 0, totalDesign = 0, totalSecrets = 0;
    for (let i = fromIdx; i < toIdx; i++) {
      const c = charmLevelCost(CHARM_LEVELS[i]);
      totalGuide += c.charm_guide;
      totalDesign += c.charm_design;
      totalSecrets += c.jewel_secrets;
    }
    return {
      perSlot: { charm_guide: totalGuide, charm_design: totalDesign, jewel_secrets: totalSecrets },
      total: {
        charm_guide: totalGuide * slotCount,
        charm_design: totalDesign * slotCount,
        jewel_secrets: totalSecrets * slotCount,
      },
    };
  }, [fromLevel, toLevel, slotCount]);

  // Check if range includes L12+
  const hasJewelSecrets = useMemo(() => {
    const toIdx = charmLevelIndex(toLevel);
    // L12 sub-levels start at index of "12-1"
    const l12Idx = charmLevelIndex('12-1');
    return toIdx >= l12Idx;
  }, [toLevel]);

  return (
    <div className="space-y-4">
      {/* Info Banner */}
      <div className="card border border-green-500/30 bg-green-500/5">
        <p className="text-sm text-frost">
          Calculate materials for <strong className="text-green-400">Chief Charm</strong> upgrades.
          Charms provide Lethality &amp; Health bonuses. Unlocks at Furnace 25.
          Each gear piece has 3 charm slots.
        </p>
      </div>

      {/* Jewel Secrets Warning */}
      {hasJewelSecrets && (
        <div className="card border border-amber-500/30 bg-amber-500/5">
          <p className="text-sm text-frost">
            <strong className="text-amber-400">Jewel Secrets required!</strong>{' '}
            Levels 12+ require Jewel Secrets, a rare material. Level 16 requires Gen 7 server age.
          </p>
        </div>
      )}

      {/* Inputs */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="text-xs text-frost-muted block mb-1">From Level</label>
            <select
              value={fromLevel}
              onChange={(e) => setFromLevel(e.target.value)}
              className="input w-full text-sm"
            >
              {CHARM_LEVELS.map((lvl) => (
                <option key={lvl} value={lvl}>{lvl}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-frost-muted block mb-1">To Level</label>
            <select
              value={toLevel}
              onChange={(e) => setToLevel(e.target.value)}
              className="input w-full text-sm"
            >
              {CHARM_LEVELS.map((lvl) => (
                <option key={lvl} value={lvl}>{lvl}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-frost-muted block mb-1">Charm Slots</label>
            <select
              value={slotCount}
              onChange={(e) => setSlotCount(Number(e.target.value))}
              className="input w-full text-sm"
            >
              <option value={1}>1 slot</option>
              <option value={3}>3 slots (1 piece)</option>
              <option value={6}>6 slots (2 pieces)</option>
              <option value={9}>9 slots (3 pieces)</option>
              <option value={12}>12 slots (4 pieces)</option>
              <option value={15}>15 slots (5 pieces)</option>
              <option value={18}>18 slots (all 6 pieces)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results */}
      {charmLevelIndex(fromLevel) >= charmLevelIndex(toLevel) ? (
        <div className="card text-center py-8">
          <p className="text-frost-muted">Set &quot;From Level&quot; lower than &quot;To Level&quot; to see costs</p>
        </div>
      ) : costs && (
        <div className="space-y-4">
          {/* Stat Bonus */}
          <div className="card border border-green-500/20">
            <div className="flex items-center justify-between">
              <div className="text-sm text-frost-muted">Lethality + Health Bonus (per slot)</div>
              <div className="flex items-center gap-3">
                <span className="text-frost">
                  +{getCharmBonus(fromLevel).toFixed(1)}%
                </span>
                <span className="text-frost-muted">&rarr;</span>
                <span className="font-bold text-lg text-green-400">
                  +{getCharmBonus(toLevel).toFixed(1)}%
                </span>
                <span className="text-xs px-2 py-0.5 rounded bg-green-500/10 text-green-400">
                  +{(getCharmBonus(toLevel) - getCharmBonus(fromLevel)).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>

          {/* Cost Table */}
          <div className="card">
            <h3 className="section-header mb-4">
              Cost: Level {fromLevel} → {toLevel}
            </h3>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-surface-border">
                  <th className="text-left py-2 px-3 text-frost-muted font-medium">Resource</th>
                  <th className="text-right py-2 px-3 text-frost-muted font-medium">Per Slot</th>
                  {slotCount > 1 && (
                    <th className="text-right py-2 px-3 text-ice font-medium">
                      Total ({slotCount} slots)
                    </th>
                  )}
                </tr>
              </thead>
              <tbody>
                <CostRow label="Charm Guides" perSlot={costs.perSlot.charm_guide} total={slotCount > 1 ? costs.total.charm_guide : undefined} color="text-cyan-400" />
                <CostRow label="Charm Designs" perSlot={costs.perSlot.charm_design} total={slotCount > 1 ? costs.total.charm_design : undefined} color="text-purple-400" />
                {costs.perSlot.jewel_secrets > 0 && (
                  <CostRow label="Jewel Secrets" perSlot={costs.perSlot.jewel_secrets} total={slotCount > 1 ? costs.total.jewel_secrets : undefined} color="text-amber-400" />
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// ── War Academy Calculator ────────────────────────────────────────

// Each sub-level within an FC tier. Format: { fcs: Fire Crystal Shards, rfc: Refined Fire Crystals, meat, wood, coal, iron, time: seconds, power }
// 45 steps: FC1-0→FC1-1 through FC9-4→FC10-0, condensed from war_academy.steps.json
const WA_LEVELS = [
  'FC1-0','FC1-1','FC1-2','FC1-3','FC1-4',
  'FC2-0','FC2-1','FC2-2','FC2-3','FC2-4',
  'FC3-0','FC3-1','FC3-2','FC3-3','FC3-4',
  'FC4-0','FC4-1','FC4-2','FC4-3','FC4-4',
  'FC5-0','FC5-1','FC5-2','FC5-3','FC5-4',
  'FC6-0','FC6-1','FC6-2','FC6-3','FC6-4',
  'FC7-0','FC7-1','FC7-2','FC7-3','FC7-4',
  'FC8-0','FC8-1','FC8-2','FC8-3','FC8-4',
  'FC9-0','FC9-1','FC9-2','FC9-3','FC9-4',
  'FC10-0',
];

// Cost to upgrade FROM each level TO the next (45 entries, index matches WA_LEVELS[0..44])
// { fcs, rfc, meat, wood, coal, iron, time (seconds), power, prereq (furnace FC level required) }
const WA_COSTS: { fcs: number; rfc: number; meat: number; wood: number; coal: number; iron: number; time: number; power: number; prereq: string }[] = [
  { fcs: 0, rfc: 0, meat: 0, wood: 0, coal: 0, iron: 0, time: 2, power: 6888, prereq: 'FC1' },
  { fcs: 71, rfc: 0, meat: 36e6, wood: 36e6, coal: 7.2e6, iron: 1.8e6, time: 155520, power: 6888, prereq: 'FC2' },
  { fcs: 71, rfc: 0, meat: 36e6, wood: 36e6, coal: 7.2e6, iron: 1.8e6, time: 155520, power: 6888, prereq: 'FC2' },
  { fcs: 71, rfc: 0, meat: 36e6, wood: 36e6, coal: 7.2e6, iron: 1.8e6, time: 155520, power: 6888, prereq: 'FC2' },
  { fcs: 71, rfc: 0, meat: 36e6, wood: 36e6, coal: 7.2e6, iron: 1.8e6, time: 155520, power: 6888, prereq: 'FC2' },
  // FC2-0→FC2-1
  { fcs: 71, rfc: 0, meat: 36e6, wood: 36e6, coal: 7.2e6, iron: 1.8e6, time: 155520, power: 6888, prereq: 'FC2' },
  { fcs: 107, rfc: 0, meat: 39e6, wood: 39e6, coal: 7.9e6, iron: 1.9e6, time: 190080, power: 6888, prereq: 'FC3' },
  { fcs: 107, rfc: 0, meat: 39e6, wood: 39e6, coal: 7.9e6, iron: 1.9e6, time: 190080, power: 6888, prereq: 'FC3' },
  { fcs: 107, rfc: 0, meat: 39e6, wood: 39e6, coal: 7.9e6, iron: 1.9e6, time: 190080, power: 6888, prereq: 'FC3' },
  { fcs: 107, rfc: 0, meat: 39e6, wood: 39e6, coal: 7.9e6, iron: 1.9e6, time: 190080, power: 6888, prereq: 'FC3' },
  // FC3-0→FC3-1
  { fcs: 107, rfc: 0, meat: 39e6, wood: 39e6, coal: 7.9e6, iron: 1.9e6, time: 190080, power: 7584, prereq: 'FC3' },
  { fcs: 126, rfc: 0, meat: 41e6, wood: 41e6, coal: 8.2e6, iron: 2e6, time: 206160, power: 7584, prereq: 'FC4' },
  { fcs: 126, rfc: 0, meat: 41e6, wood: 41e6, coal: 8.2e6, iron: 2e6, time: 206160, power: 7584, prereq: 'FC4' },
  { fcs: 126, rfc: 0, meat: 41e6, wood: 41e6, coal: 8.2e6, iron: 2e6, time: 206160, power: 7584, prereq: 'FC4' },
  { fcs: 126, rfc: 0, meat: 41e6, wood: 41e6, coal: 8.2e6, iron: 2e6, time: 206160, power: 7584, prereq: 'FC4' },
  // FC4-0→FC4-1
  { fcs: 126, rfc: 0, meat: 41e6, wood: 41e6, coal: 8.2e6, iron: 2e6, time: 206160, power: 7584, prereq: 'FC4' },
  { fcs: 150, rfc: 0, meat: 42e6, wood: 42e6, coal: 8.2e6, iron: 2.1e6, time: 241920, power: 7584, prereq: 'FC5' },
  { fcs: 150, rfc: 0, meat: 42e6, wood: 42e6, coal: 8.2e6, iron: 2.1e6, time: 241920, power: 7584, prereq: 'FC5' },
  { fcs: 150, rfc: 0, meat: 42e6, wood: 42e6, coal: 8.2e6, iron: 2.1e6, time: 241920, power: 7584, prereq: 'FC5' },
  { fcs: 150, rfc: 0, meat: 42e6, wood: 42e6, coal: 8.2e6, iron: 2.1e6, time: 241920, power: 7584, prereq: 'FC5' },
  // FC5-0→FC5-1
  { fcs: 150, rfc: 0, meat: 42e6, wood: 42e6, coal: 8.2e6, iron: 2.1e6, time: 241920, power: 8112, prereq: 'FC5' },
  { fcs: 90, rfc: 4, meat: 48e6, wood: 48e6, coal: 9.6e6, iron: 2.4e6, time: 259200, power: 8112, prereq: 'FC6' },
  { fcs: 90, rfc: 4, meat: 48e6, wood: 48e6, coal: 9.6e6, iron: 2.4e6, time: 259200, power: 8112, prereq: 'FC6' },
  { fcs: 90, rfc: 4, meat: 48e6, wood: 48e6, coal: 9.6e6, iron: 2.4e6, time: 259200, power: 8112, prereq: 'FC6' },
  { fcs: 90, rfc: 4, meat: 48e6, wood: 48e6, coal: 9.6e6, iron: 2.4e6, time: 259200, power: 8112, prereq: 'FC6' },
  // FC6-0→FC6-1
  { fcs: 45, rfc: 9, meat: 48e6, wood: 48e6, coal: 9.6e6, iron: 2.4e6, time: 259200, power: 8112, prereq: 'FC6' },
  { fcs: 108, rfc: 6, meat: 54e6, wood: 54e6, coal: 10e6, iron: 2.7e6, time: 310560, power: 8112, prereq: 'FC7' },
  { fcs: 108, rfc: 6, meat: 54e6, wood: 54e6, coal: 10e6, iron: 2.7e6, time: 310560, power: 8112, prereq: 'FC7' },
  { fcs: 108, rfc: 6, meat: 54e6, wood: 54e6, coal: 10e6, iron: 2.7e6, time: 310560, power: 8112, prereq: 'FC7' },
  { fcs: 108, rfc: 6, meat: 54e6, wood: 54e6, coal: 10e6, iron: 2.7e6, time: 310560, power: 8112, prereq: 'FC7' },
  // FC7-0→FC7-1
  { fcs: 54, rfc: 13, meat: 54e6, wood: 54e6, coal: 10e6, iron: 2.7e6, time: 310560, power: 8112, prereq: 'FC7' },
  { fcs: 108, rfc: 9, meat: 66e6, wood: 66e6, coal: 13e6, iron: 3.3e6, time: 345600, power: 8112, prereq: 'FC8' },
  { fcs: 108, rfc: 9, meat: 66e6, wood: 66e6, coal: 13e6, iron: 3.3e6, time: 345600, power: 8112, prereq: 'FC8' },
  { fcs: 108, rfc: 9, meat: 66e6, wood: 66e6, coal: 13e6, iron: 3.3e6, time: 345600, power: 8112, prereq: 'FC8' },
  { fcs: 108, rfc: 9, meat: 66e6, wood: 66e6, coal: 13e6, iron: 3.3e6, time: 345600, power: 8112, prereq: 'FC8' },
  // FC8-0→FC8-1
  { fcs: 54, rfc: 19, meat: 66e6, wood: 66e6, coal: 13e6, iron: 3.3e6, time: 345600, power: 8664, prereq: 'FC8' },
  { fcs: 126, rfc: 13, meat: 72e6, wood: 72e6, coal: 14e6, iron: 3.6e6, time: 223200, power: 8664, prereq: 'FC9' },
  { fcs: 126, rfc: 13, meat: 72e6, wood: 72e6, coal: 14e6, iron: 3.6e6, time: 223200, power: 8664, prereq: 'FC9' },
  { fcs: 126, rfc: 13, meat: 72e6, wood: 72e6, coal: 14e6, iron: 3.6e6, time: 223200, power: 8664, prereq: 'FC9' },
  { fcs: 126, rfc: 13, meat: 72e6, wood: 72e6, coal: 14e6, iron: 3.6e6, time: 223200, power: 8664, prereq: 'FC9' },
  // FC9-0→FC9-1
  { fcs: 63, rfc: 27, meat: 72e6, wood: 72e6, coal: 14e6, iron: 3.6e6, time: 223200, power: 8664, prereq: 'FC9' },
  { fcs: 157, rfc: 31, meat: 84e6, wood: 84e6, coal: 16e6, iron: 7.2e6, time: 345600, power: 8664, prereq: 'FC10' },
  { fcs: 157, rfc: 31, meat: 84e6, wood: 84e6, coal: 16e6, iron: 7.2e6, time: 345600, power: 8664, prereq: 'FC10' },
  { fcs: 157, rfc: 31, meat: 84e6, wood: 84e6, coal: 16e6, iron: 7.2e6, time: 345600, power: 8664, prereq: 'FC10' },
  { fcs: 157, rfc: 31, meat: 84e6, wood: 84e6, coal: 16e6, iron: 7.2e6, time: 345600, power: 8784, prereq: 'FC10' },
];

function formatTime(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const parts: string[] = [];
  if (days > 0) parts.push(`${days}d`);
  if (hours > 0) parts.push(`${hours}h`);
  if (mins > 0) parts.push(`${mins}m`);
  return parts.join(' ') || '0m';
}

function formatM(n: number): string {
  if (n >= 1e6) return `${(n / 1e6).toFixed(1)}M`;
  if (n >= 1e3) return `${(n / 1e3).toFixed(1)}K`;
  return n.toLocaleString();
}

function WarAcademyCalc() {
  const [fromIdx, setFromIdx] = useState(0);
  const [toIdx, setToIdx] = useState(WA_LEVELS.length - 1);

  const costs = useMemo(() => {
    if (fromIdx >= toIdx) return null;
    let fcs = 0, rfc = 0, meat = 0, wood = 0, coal = 0, iron = 0, time = 0, power = 0;
    const prereqs: string[] = [];
    for (let i = fromIdx; i < toIdx; i++) {
      const c = WA_COSTS[i];
      fcs += c.fcs; rfc += c.rfc; meat += c.meat; wood += c.wood;
      coal += c.coal; iron += c.iron; time += c.time; power += c.power;
      if (!prereqs.includes(c.prereq)) prereqs.push(c.prereq);
    }
    return { fcs, rfc, meat, wood, coal, iron, time, power, highestPrereq: prereqs[prereqs.length - 1] };
  }, [fromIdx, toIdx]);

  // Build milestone breakdown at each major FC boundary
  const milestones = useMemo(() => {
    if (fromIdx >= toIdx) return [];
    const fcBoundaries: { label: string; idx: number }[] = [];
    for (let i = 0; i < WA_LEVELS.length; i++) {
      if (WA_LEVELS[i].endsWith('-0') && i > fromIdx && i <= toIdx) {
        fcBoundaries.push({ label: WA_LEVELS[i], idx: i });
      }
    }
    return fcBoundaries;
  }, [fromIdx, toIdx]);

  return (
    <div className="space-y-4">
      {/* Info Banner */}
      <div className="card border border-orange-500/30 bg-orange-500/5">
        <p className="text-sm text-frost">
          The <strong className="text-orange-400">War Academy</strong> is a late-game military research building that unlocks at{' '}
          <strong className="text-frost">Furnace 30</strong> and requires your server to be{' '}
          <strong className="text-frost">~220 days old</strong> (~40 days after Gen 4 heroes).
          Inside, you conduct <strong className="text-orange-400">Helios Research</strong> to strengthen troops and eventually unlock{' '}
          <strong className="text-frost">T11 (Helios) troops</strong> - the highest troop tier in the game.
        </p>
        <div className="mt-3 p-3 rounded-lg bg-surface">
          <p className="text-xs text-frost-muted">
            <strong className="text-frost">How it works:</strong> The building upgrades from FC1-0 to FC10-0 with 5 sub-levels per FC tier
            (like other FC buildings). Each upgrade requires your <strong>Furnace</strong> to be at a higher FC level first.
            Starting at FC5, Helios Research becomes available using Fire Crystal Shards and Refined Steel.
          </p>
        </div>
      </div>

      {/* Inputs */}
      <div className="card">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs text-frost-muted block mb-1">From Level</label>
            <select
              value={fromIdx}
              onChange={(e) => setFromIdx(Number(e.target.value))}
              className="input w-full text-center text-lg"
            >
              {WA_LEVELS.slice(0, -1).map((lvl, i) => (
                <option key={lvl} value={i}>{lvl}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-frost-muted block mb-1">To Level</label>
            <select
              value={toIdx}
              onChange={(e) => setToIdx(Number(e.target.value))}
              className="input w-full text-center text-lg"
            >
              {WA_LEVELS.slice(1).map((lvl, i) => (
                <option key={lvl} value={i + 1}>{lvl}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Results */}
      {fromIdx >= toIdx ? (
        <div className="card text-center py-8">
          <p className="text-frost-muted">Set &quot;From Level&quot; lower than &quot;To Level&quot; to see costs</p>
        </div>
      ) : costs && (
        <div className="space-y-4">
          {/* Prerequisite + Time + Power summary */}
          <div className="grid grid-cols-3 gap-3">
            <div className="card text-center border border-orange-500/20">
              <p className="text-xs text-frost-muted mb-1">Furnace Required</p>
              <p className="text-lg font-bold text-orange-400">{costs.highestPrereq}</p>
            </div>
            <div className="card text-center border border-ice/20">
              <p className="text-xs text-frost-muted mb-1">Base Build Time</p>
              <p className="text-lg font-bold text-ice">{formatTime(costs.time)}</p>
            </div>
            <div className="card text-center border border-purple-500/20">
              <p className="text-xs text-frost-muted mb-1">Power Gain</p>
              <p className="text-lg font-bold text-purple-400">+{costs.power.toLocaleString()}</p>
            </div>
          </div>

          {/* Resource costs */}
          <div className="card">
            <h3 className="section-header mb-4">
              Cost: {WA_LEVELS[fromIdx]} → {WA_LEVELS[toIdx]}
            </h3>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-surface-border">
                  <th className="text-left py-2 px-3 text-frost-muted font-medium">Resource</th>
                  <th className="text-right py-2 px-3 text-frost-muted font-medium">Amount</th>
                </tr>
              </thead>
              <tbody>
                <CostRow label="Fire Crystal Shards" perSlot={costs.fcs} color="text-orange-400" />
                {costs.rfc > 0 && (
                  <CostRow label="Refined Fire Crystals" perSlot={costs.rfc} color="text-red-400" />
                )}
                <CostRow label="Meat" perSlot={costs.meat} color="text-red-300" />
                <CostRow label="Wood" perSlot={costs.wood} color="text-green-400" />
                <CostRow label="Coal" perSlot={costs.coal} color="text-gray-300" />
                <CostRow label="Iron" perSlot={costs.iron} color="text-blue-300" />
              </tbody>
            </table>
          </div>

          {/* Milestone breakdown */}
          {milestones.length > 0 && (
            <div className="card">
              <h3 className="section-header mb-4">FC Milestones in Range</h3>
              <div className="space-y-2">
                {milestones.map((ms) => {
                  // Calculate cost from previous milestone (or from start)
                  const prevMsIdx = milestones.indexOf(ms) > 0
                    ? milestones[milestones.indexOf(ms) - 1].idx
                    : fromIdx;
                  let segFcs = 0, segRfc = 0, segTime = 0;
                  for (let i = prevMsIdx; i < ms.idx; i++) {
                    segFcs += WA_COSTS[i].fcs;
                    segRfc += WA_COSTS[i].rfc;
                    segTime += WA_COSTS[i].time;
                  }
                  return (
                    <div key={ms.label} className="flex items-center justify-between p-3 rounded-lg bg-surface">
                      <div>
                        <span className="font-medium text-frost">{ms.label}</span>
                        <span className="text-xs text-frost-muted ml-2">
                          (requires Furnace {WA_COSTS[ms.idx - 1]?.prereq || '?'})
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-xs">
                        <span className="text-orange-400">{segFcs.toLocaleString()} Shards</span>
                        {segRfc > 0 && <span className="text-red-400">{segRfc} Refined</span>}
                        <span className="text-frost-muted">{formatTime(segTime)}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Tips */}
          <div className="card border border-surface-border">
            <details>
              <summary className="cursor-pointer text-sm font-medium text-frost hover:text-ice">
                Tips & Strategy
              </summary>
              <div className="mt-3 space-y-2 text-sm text-frost-muted">
                <p>
                  <strong className="text-frost">Priority:</strong> War Academy is essential for endgame - T11 troops are a massive power jump.
                  Upgrade it alongside your Furnace FC progression.
                </p>
                <p>
                  <strong className="text-frost">Refined Fire Crystals</strong> appear starting at FC5 upgrades. These are harder to obtain,
                  so plan ahead. Exchange rate: 10 Fire Crystals = 13 Shards, or 5,000 Steel = 1 Shard.
                </p>
                <p>
                  <strong className="text-frost">Helios Research</strong> unlocks at War Academy FC5 + Furnace FC5.
                  There are 3 research trees (Infantry, Lancer, Marksman) - completing all 6 chains in one tree unlocks T11 for that troop type.
                </p>
                <p>
                  <strong className="text-frost">Build times are base values</strong> - actual times will be reduced by construction speed buffs,
                  VIP bonuses, and alliance help.
                </p>
              </div>
            </details>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Shared Components ───────────────────────────────────────────────

function CostRow({ label, perSlot, total, color }: {
  label: string;
  perSlot: number;
  total?: number;
  color: string;
}) {
  return (
    <tr className="border-b border-surface-border/30">
      <td className="py-3 px-3 text-frost">{label}</td>
      <td className={`py-3 px-3 text-right font-bold ${color}`}>
        {perSlot.toLocaleString()}
      </td>
      {total !== undefined && (
        <td className={`py-3 px-3 text-right font-bold text-lg ${color}`}>
          {total.toLocaleString()}
        </td>
      )}
    </tr>
  );
}
