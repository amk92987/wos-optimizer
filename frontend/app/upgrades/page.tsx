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
type CalcType = 'enhancement' | 'legendary' | 'mastery' | 'chief_gear' | 'charms' | 'war_academy' | 'pet_leveling' | 'expert_skills' | 'expert_affinity' | 'crystal_lab';

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

// Expert Skills: 7 experts, each with 4 skills at varying max levels
// Costs are { exp, books } per level upgrade. Level 1 is free (starting level).
interface ExpertSkillDef {
  name: string;
  max_level: number;
  description: string;
  costs: { level: number; exp: number; books: number }[];
}

interface ExpertDef {
  name: string;
  class_name: string;
  affinity_bonus: string;
  skills: ExpertSkillDef[];
}

const EXPERTS: ExpertDef[] = [
  {
    name: 'Agnes', class_name: 'Elite Politician', affinity_bonus: 'Troops Defense +15%',
    skills: [
      { name: 'Efficient Recon', max_level: 5, description: '+8 daily Intel missions',
        costs: [{ level: 2, exp: 43200, books: 500 }, { level: 3, exp: 86400, books: 1000 }, { level: 4, exp: 172800, books: 2000 }, { level: 5, exp: 345600, books: 4000 }] },
      { name: 'Optimization', max_level: 5, description: '+40 Storehouse Stamina gain',
        costs: [{ level: 2, exp: 34200, books: 400 }, { level: 3, exp: 69000, books: 800 }, { level: 4, exp: 138000, books: 1600 }, { level: 5, exp: 276000, books: 3200 }] },
      { name: 'Project Management', max_level: 5, description: '-8h construction time per build',
        costs: [{ level: 2, exp: 13800, books: 200 }, { level: 3, exp: 27600, books: 400 }, { level: 4, exp: 55200, books: 800 }, { level: 5, exp: 110400, books: 1600 }] },
      { name: 'Covert Knowledge', max_level: 10, description: '+120 Mystery Badges daily, +4 shop refreshes',
        costs: [{ level: 2, exp: 10200, books: 100 }, { level: 3, exp: 20400, books: 200 }, { level: 4, exp: 30600, books: 300 }, { level: 5, exp: 41400, books: 400 }, { level: 6, exp: 51600, books: 500 }, { level: 7, exp: 61800, books: 600 }, { level: 8, exp: 72600, books: 700 }, { level: 9, exp: 82800, books: 800 }, { level: 10, exp: 93000, books: 900 }] },
    ],
  },
  {
    name: 'Valeria', class_name: 'High Marshal', affinity_bonus: 'Troops Lethality +20%, Health +20%',
    skills: [
      { name: 'Well Prepared', max_level: 10, description: '+20% SvS Prep Phase points, +3 daily reward tier',
        costs: [{ level: 2, exp: 0, books: 500 }, { level: 3, exp: 0, books: 1000 }, { level: 4, exp: 0, books: 1500 }, { level: 5, exp: 0, books: 2000 }, { level: 6, exp: 0, books: 2500 }, { level: 7, exp: 0, books: 3000 }, { level: 8, exp: 0, books: 3500 }, { level: 9, exp: 0, books: 4000 }, { level: 10, exp: 0, books: 4500 }] },
      { name: 'Radiant Honor', max_level: 10, description: '+50 Sunfire Tokens, +3 SvS Shop items',
        costs: [{ level: 2, exp: 0, books: 500 }, { level: 3, exp: 0, books: 1000 }, { level: 4, exp: 0, books: 1500 }, { level: 5, exp: 0, books: 2000 }, { level: 6, exp: 0, books: 2500 }, { level: 7, exp: 0, books: 3000 }, { level: 8, exp: 0, books: 3500 }, { level: 9, exp: 0, books: 4000 }, { level: 10, exp: 0, books: 4500 }] },
      { name: 'Battle Concerto', max_level: 20, description: '+30% Lethality & Health in SvS Battle',
        costs: [{ level: 2, exp: 0, books: 500 }, { level: 3, exp: 0, books: 500 }, { level: 4, exp: 0, books: 500 }, { level: 5, exp: 0, books: 750 }, { level: 6, exp: 0, books: 750 }, { level: 7, exp: 0, books: 750 }, { level: 8, exp: 0, books: 750 }, { level: 9, exp: 0, books: 750 }, { level: 10, exp: 0, books: 750 }, { level: 11, exp: 0, books: 1000 }, { level: 12, exp: 0, books: 1000 }, { level: 13, exp: 0, books: 1000 }, { level: 14, exp: 0, books: 1000 }, { level: 15, exp: 0, books: 1000 }, { level: 16, exp: 0, books: 1000 }, { level: 17, exp: 0, books: 1000 }, { level: 18, exp: 0, books: 1000 }, { level: 19, exp: 0, books: 1000 }, { level: 20, exp: 0, books: 1000 }] },
      { name: 'Crushing Force', max_level: 20, description: '+150K SvS Rally Capacity',
        costs: [{ level: 2, exp: 0, books: 500 }, { level: 3, exp: 0, books: 500 }, { level: 4, exp: 0, books: 500 }, { level: 5, exp: 0, books: 750 }, { level: 6, exp: 0, books: 750 }, { level: 7, exp: 0, books: 750 }, { level: 8, exp: 0, books: 750 }, { level: 9, exp: 0, books: 750 }, { level: 10, exp: 0, books: 750 }, { level: 11, exp: 0, books: 1000 }, { level: 12, exp: 0, books: 1000 }, { level: 13, exp: 0, books: 1000 }, { level: 14, exp: 0, books: 1000 }, { level: 15, exp: 0, books: 1000 }, { level: 16, exp: 0, books: 1000 }, { level: 17, exp: 0, books: 1000 }, { level: 18, exp: 0, books: 1000 }, { level: 19, exp: 0, books: 1000 }, { level: 20, exp: 0, books: 1000 }] },
    ],
  },
  {
    name: 'Baldur', class_name: 'Negotiator', affinity_bonus: 'Troops Attack +10%, Defense +10%',
    skills: [
      { name: 'Blazing Sunrise', max_level: 10, description: '+20% Alliance Mobilization Points',
        costs: [{ level: 2, exp: 25800, books: 300 }, { level: 3, exp: 51600, books: 600 }, { level: 4, exp: 77400, books: 900 }, { level: 5, exp: 103200, books: 1200 }, { level: 6, exp: 129600, books: 1500 }, { level: 7, exp: 155400, books: 1800 }, { level: 8, exp: 181200, books: 2100 }, { level: 9, exp: 207000, books: 2400 }, { level: 10, exp: 232800, books: 2700 }] },
      { name: 'Honored Conquest', max_level: 10, description: '+50% Championship Badges, +3 shop items',
        costs: [{ level: 2, exp: 25800, books: 300 }, { level: 3, exp: 51600, books: 600 }, { level: 4, exp: 77400, books: 900 }, { level: 5, exp: 103200, books: 1200 }, { level: 6, exp: 129600, books: 1500 }, { level: 7, exp: 155400, books: 1800 }, { level: 8, exp: 181200, books: 2100 }, { level: 9, exp: 207000, books: 2400 }, { level: 10, exp: 232800, books: 2700 }] },
      { name: 'Bounty Hunter', max_level: 10, description: '+50% Crazy Joe points, bonus chests',
        costs: [{ level: 2, exp: 25800, books: 300 }, { level: 3, exp: 51600, books: 600 }, { level: 4, exp: 77400, books: 900 }, { level: 5, exp: 103200, books: 1200 }, { level: 6, exp: 129600, books: 1500 }, { level: 7, exp: 155400, books: 1800 }, { level: 8, exp: 181200, books: 2100 }, { level: 9, exp: 207000, books: 2400 }, { level: 10, exp: 232800, books: 2700 }] },
      { name: 'Dawn Hymn', max_level: 10, description: '+50% Alliance Showdown points',
        costs: [{ level: 2, exp: 51600, books: 500 }, { level: 3, exp: 103200, books: 1000 }, { level: 4, exp: 155400, books: 1500 }, { level: 5, exp: 207000, books: 2000 }, { level: 6, exp: 259200, books: 2500 }, { level: 7, exp: 310800, books: 3000 }, { level: 8, exp: 362400, books: 3500 }, { level: 9, exp: 414600, books: 4000 }, { level: 10, exp: 466200, books: 4500 }] },
    ],
  },
  {
    name: 'Romulus', class_name: 'Military Advisor', affinity_bonus: 'Troops Lethality +20%, Health +20%',
    skills: [
      { name: 'Call of War', max_level: 10, description: '+600 free troops/day, +10 Loyalty Tags',
        costs: [{ level: 2, exp: 30600, books: 300 }, { level: 3, exp: 61800, books: 600 }, { level: 4, exp: 93000, books: 900 }, { level: 5, exp: 124200, books: 1200 }, { level: 6, exp: 155400, books: 1500 }, { level: 7, exp: 186600, books: 1800 }, { level: 8, exp: 217200, books: 2100 }, { level: 9, exp: 248400, books: 2400 }, { level: 10, exp: 279600, books: 2700 }] },
      { name: 'Last Line', max_level: 20, description: '+10% Troops Attack & Defense',
        costs: [{ level: 2, exp: 86400, books: 500 }, { level: 3, exp: 86400, books: 500 }, { level: 4, exp: 86400, books: 500 }, { level: 5, exp: 86400, books: 500 }, { level: 6, exp: 86400, books: 500 }, { level: 7, exp: 86400, books: 500 }, { level: 8, exp: 86400, books: 500 }, { level: 9, exp: 86400, books: 500 }, { level: 10, exp: 86400, books: 500 }, { level: 11, exp: 86400, books: 500 }, { level: 12, exp: 86400, books: 500 }, { level: 13, exp: 86400, books: 500 }, { level: 14, exp: 86400, books: 500 }, { level: 15, exp: 86400, books: 500 }, { level: 16, exp: 86400, books: 500 }, { level: 17, exp: 86400, books: 500 }, { level: 18, exp: 86400, books: 500 }, { level: 19, exp: 86400, books: 500 }, { level: 20, exp: 86400, books: 500 }] },
      { name: 'Spirit of Aeetis', max_level: 20, description: '+10% Troops Lethality & Health',
        costs: [{ level: 2, exp: 159000, books: 800 }, { level: 3, exp: 159000, books: 800 }, { level: 4, exp: 159000, books: 800 }, { level: 5, exp: 159000, books: 800 }, { level: 6, exp: 159000, books: 800 }, { level: 7, exp: 159000, books: 800 }, { level: 8, exp: 159000, books: 800 }, { level: 9, exp: 159000, books: 800 }, { level: 10, exp: 159000, books: 800 }, { level: 11, exp: 159000, books: 800 }, { level: 12, exp: 159000, books: 800 }, { level: 13, exp: 159000, books: 800 }, { level: 14, exp: 159000, books: 800 }, { level: 15, exp: 159000, books: 800 }, { level: 16, exp: 159000, books: 800 }, { level: 17, exp: 159000, books: 800 }, { level: 18, exp: 159000, books: 800 }, { level: 19, exp: 159000, books: 800 }, { level: 20, exp: 159000, books: 800 }] },
      { name: 'One Heart', max_level: 20, description: '+100K Rally Capacity',
        costs: [{ level: 2, exp: 179400, books: 800 }, { level: 3, exp: 179400, books: 800 }, { level: 4, exp: 179400, books: 800 }, { level: 5, exp: 179400, books: 800 }, { level: 6, exp: 179400, books: 800 }, { level: 7, exp: 179400, books: 800 }, { level: 8, exp: 179400, books: 800 }, { level: 9, exp: 179400, books: 800 }, { level: 10, exp: 179400, books: 800 }, { level: 11, exp: 179400, books: 800 }, { level: 12, exp: 179400, books: 800 }, { level: 13, exp: 179400, books: 800 }, { level: 14, exp: 179400, books: 800 }, { level: 15, exp: 179400, books: 800 }, { level: 16, exp: 179400, books: 800 }, { level: 17, exp: 179400, books: 800 }, { level: 18, exp: 179400, books: 800 }, { level: 19, exp: 179400, books: 800 }, { level: 20, exp: 179400, books: 800 }] },
    ],
  },
  {
    name: 'Holger', class_name: 'Arena Legend', affinity_bonus: 'Troops Attack +15%, Defense +15%',
    skills: [
      { name: 'Arena Elite', max_level: 10, description: '+20% Arena heroes Attack & Health',
        costs: [{ level: 2, exp: 82800, books: 600 }, { level: 3, exp: 165600, books: 1200 }, { level: 4, exp: 248400, books: 1800 }, { level: 5, exp: 331800, books: 2400 }, { level: 6, exp: 414600, books: 3000 }, { level: 7, exp: 497400, books: 3600 }, { level: 8, exp: 580200, books: 4200 }, { level: 9, exp: 663600, books: 4800 }, { level: 10, exp: 746400, books: 5400 }] },
      { name: 'Crowd Pleaser', max_level: 10, description: '+50% daily/weekly Arena Tokens',
        costs: [{ level: 2, exp: 30600, books: 300 }, { level: 3, exp: 61800, books: 600 }, { level: 4, exp: 93000, books: 900 }, { level: 5, exp: 124200, books: 1200 }, { level: 6, exp: 155400, books: 1500 }, { level: 7, exp: 186600, books: 1800 }, { level: 8, exp: 217200, books: 2100 }, { level: 9, exp: 248400, books: 2400 }, { level: 10, exp: 279600, books: 2700 }] },
      { name: 'Arena Star', max_level: 10, description: '+3 Arena Shop items at 50% off',
        costs: [{ level: 2, exp: 30600, books: 300 }, { level: 3, exp: 61800, books: 600 }, { level: 4, exp: 93000, books: 900 }, { level: 5, exp: 124200, books: 1200 }, { level: 6, exp: 155400, books: 1500 }, { level: 7, exp: 186600, books: 1800 }, { level: 8, exp: 217200, books: 2100 }, { level: 9, exp: 248400, books: 2400 }, { level: 10, exp: 279600, books: 2700 }] },
      { name: 'Legacy', max_level: 10, description: '+20% Arena heroes Attack & Health',
        costs: [{ level: 2, exp: 82800, books: 600 }, { level: 3, exp: 165600, books: 1200 }, { level: 4, exp: 248400, books: 1800 }, { level: 5, exp: 331800, books: 2400 }, { level: 6, exp: 414600, books: 3000 }, { level: 7, exp: 497400, books: 3600 }, { level: 8, exp: 580200, books: 4200 }, { level: 9, exp: 663600, books: 4800 }, { level: 10, exp: 746400, books: 5400 }] },
    ],
  },
  {
    name: 'Cyrille', class_name: 'Bear Huntress', affinity_bonus: 'Troops Attack +15%',
    skills: [
      { name: 'Entrapment', max_level: 10, description: '+300K Bear Hunt Rally Capacity',
        costs: [{ level: 2, exp: 3600, books: 70 }, { level: 3, exp: 7200, books: 140 }, { level: 4, exp: 10800, books: 210 }, { level: 5, exp: 14400, books: 280 }, { level: 6, exp: 18000, books: 350 }, { level: 7, exp: 21600, books: 420 }, { level: 8, exp: 25200, books: 490 }, { level: 9, exp: 28800, books: 560 }, { level: 10, exp: 32400, books: 630 }] },
      { name: 'Scavenging', max_level: 5, description: '+5 x100 Enhancement XP per Bear Hunt',
        costs: [{ level: 2, exp: 27600, books: 400 }, { level: 3, exp: 55200, books: 800 }, { level: 4, exp: 110400, books: 1600 }, { level: 5, exp: 220800, books: 3200 }] },
      { name: 'Weapon Master', max_level: 5, description: '+5 Essence Stones per Bear Hunt',
        costs: [{ level: 2, exp: 43200, books: 500 }, { level: 3, exp: 86400, books: 1000 }, { level: 4, exp: 172800, books: 2000 }, { level: 5, exp: 345600, books: 4000 }] },
      { name: 'Ursa\'s Bane', max_level: 10, description: '+30K Bear Hunt troop deployment',
        costs: [{ level: 2, exp: 10200, books: 100 }, { level: 3, exp: 20400, books: 200 }, { level: 4, exp: 30600, books: 300 }, { level: 5, exp: 41400, books: 400 }, { level: 6, exp: 51600, books: 500 }, { level: 7, exp: 61800, books: 600 }, { level: 8, exp: 72600, books: 700 }, { level: 9, exp: 82800, books: 800 }, { level: 10, exp: 93000, books: 900 }] },
    ],
  },
  {
    name: 'Fabian', class_name: 'Master of Arms', affinity_bonus: 'Troops Lethality +15%, Health +15%',
    skills: [
      { name: 'Salvager', max_level: 10, description: '+100% Arsenal Tokens',
        costs: [{ level: 2, exp: 25800, books: 300 }, { level: 3, exp: 51600, books: 600 }, { level: 4, exp: 77400, books: 900 }, { level: 5, exp: 103200, books: 1200 }, { level: 6, exp: 129600, books: 1500 }, { level: 7, exp: 155400, books: 1800 }, { level: 8, exp: 181200, books: 2100 }, { level: 9, exp: 207000, books: 2400 }, { level: 10, exp: 232800, books: 2700 }] },
      { name: 'Crisis Rescue', max_level: 10, description: '+1M troop recovery in Foundry/Tundra Hellfire',
        costs: [{ level: 2, exp: 33053, books: 500 }, { level: 3, exp: 107400, books: 1000 }, { level: 4, exp: 160800, books: 1500 }, { level: 5, exp: 214800, books: 2000 }, { level: 6, exp: 268800, books: 2500 }, { level: 7, exp: 322200, books: 3000 }, { level: 8, exp: 376200, books: 3500 }, { level: 9, exp: 429600, books: 4000 }, { level: 10, exp: 483600, books: 4500 }] },
      { name: 'Heightened Firepower', max_level: 20, description: '+30% Lethality & Health in Foundry/Hellfire',
        costs: [{ level: 2, exp: 27600, books: 200 }, { level: 3, exp: 27600, books: 200 }, { level: 4, exp: 27600, books: 200 }, { level: 5, exp: 27600, books: 200 }, { level: 6, exp: 27600, books: 200 }, { level: 7, exp: 27600, books: 200 }, { level: 8, exp: 27600, books: 200 }, { level: 9, exp: 27600, books: 200 }, { level: 10, exp: 318000, books: 2300 }, { level: 11, exp: 345600, books: 2500 }, { level: 12, exp: 345600, books: 2500 }, { level: 13, exp: 345600, books: 2500 }, { level: 14, exp: 345600, books: 2500 }, { level: 15, exp: 345600, books: 2500 }, { level: 16, exp: 345600, books: 2500 }, { level: 17, exp: 345600, books: 2500 }, { level: 18, exp: 345600, books: 2500 }, { level: 19, exp: 705000, books: 5100 }, { level: 20, exp: 705000, books: 5100 }] },
      { name: 'Battle Bulwark', max_level: 20, description: '+150K Foundry/Hellfire Rally Capacity',
        costs: [{ level: 2, exp: 46200, books: 300 }, { level: 3, exp: 46200, books: 300 }, { level: 4, exp: 46200, books: 300 }, { level: 5, exp: 46200, books: 300 }, { level: 6, exp: 46200, books: 300 }, { level: 7, exp: 46200, books: 300 }, { level: 8, exp: 46200, books: 300 }, { level: 9, exp: 46200, books: 300 }, { level: 10, exp: 497400, books: 3200 }, { level: 11, exp: 544200, books: 3500 }, { level: 12, exp: 544200, books: 3500 }, { level: 13, exp: 544200, books: 3500 }, { level: 14, exp: 544200, books: 3500 }, { level: 15, exp: 544200, books: 3500 }, { level: 16, exp: 544200, books: 3500 }, { level: 17, exp: 544200, books: 3500 }, { level: 18, exp: 544200, books: 3500 }, { level: 19, exp: 1104000, books: 7100 }, { level: 20, exp: 1104000, books: 7100 }] },
    ],
  },
];

// Expert Affinity: milestones every 10 levels, sigils required at each milestone
// Bonus scales linearly between milestones. Data from wiki (Confidence: A).
interface AffinityMilestone {
  level: number;
  sigils: number;        // cumulative sigils needed to reach this milestone
  bonus_pct: number;     // cumulative bonus % at this level
  advancement: number;   // advancement points needed for THIS milestone level
}

interface ExpertAffinityDef {
  name: string;
  stats: string[];       // which stats get buffed
  max_bonus_pct: number; // per stat at level 100
  milestones: AffinityMilestone[];
}

const EXPERT_AFFINITY: ExpertAffinityDef[] = [
  {
    name: 'Agnes', stats: ['Defense'], max_bonus_pct: 15,
    milestones: [
      { level: 0, sigils: 0, bonus_pct: 0, advancement: 0 },
      { level: 10, sigils: 5, bonus_pct: 2.85, advancement: 640 },
      { level: 20, sigils: 10, bonus_pct: 4.20, advancement: 1040 },
      { level: 30, sigils: 15, bonus_pct: 5.55, advancement: 1460 },
      { level: 40, sigils: 20, bonus_pct: 6.90, advancement: 2080 },
      { level: 50, sigils: 25, bonus_pct: 8.25, advancement: 2900 },
      { level: 60, sigils: 30, bonus_pct: 9.60, advancement: 3900 },
      { level: 70, sigils: 35, bonus_pct: 10.95, advancement: 4900 },
      { level: 80, sigils: 40, bonus_pct: 12.30, advancement: 5900 },
      { level: 90, sigils: 45, bonus_pct: 13.65, advancement: 6900 },
      { level: 100, sigils: 50, bonus_pct: 15.00, advancement: 7900 },
    ],
  },
  {
    name: 'Valeria', stats: ['Lethality', 'Health'], max_bonus_pct: 20,
    milestones: [
      { level: 0, sigils: 0, bonus_pct: 0, advancement: 0 },
      { level: 10, sigils: 20, bonus_pct: 3.80, advancement: 1760 },
      { level: 20, sigils: 40, bonus_pct: 5.60, advancement: 2860 },
      { level: 30, sigils: 80, bonus_pct: 7.40, advancement: 4020 },
      { level: 40, sigils: 120, bonus_pct: 9.20, advancement: 5720 },
      { level: 50, sigils: 160, bonus_pct: 11.00, advancement: 7980 },
      { level: 60, sigils: 200, bonus_pct: 12.80, advancement: 10730 },
      { level: 70, sigils: 240, bonus_pct: 14.60, advancement: 13480 },
      { level: 80, sigils: 280, bonus_pct: 16.40, advancement: 16230 },
      { level: 90, sigils: 320, bonus_pct: 18.20, advancement: 18980 },
      { level: 100, sigils: 360, bonus_pct: 20.00, advancement: 21730 },
    ],
  },
  {
    name: 'Baldur', stats: ['Attack', 'Defense'], max_bonus_pct: 10,
    milestones: [
      { level: 0, sigils: 0, bonus_pct: 0, advancement: 0 },
      { level: 10, sigils: 6, bonus_pct: 1.90, advancement: 640 },
      { level: 20, sigils: 12, bonus_pct: 2.80, advancement: 1040 },
      { level: 30, sigils: 18, bonus_pct: 3.70, advancement: 1460 },
      { level: 40, sigils: 24, bonus_pct: 4.60, advancement: 2080 },
      { level: 50, sigils: 30, bonus_pct: 5.50, advancement: 2900 },
      { level: 60, sigils: 36, bonus_pct: 6.40, advancement: 3900 },
      { level: 70, sigils: 42, bonus_pct: 7.30, advancement: 4900 },
      { level: 80, sigils: 48, bonus_pct: 8.20, advancement: 5900 },
      { level: 90, sigils: 54, bonus_pct: 9.10, advancement: 6900 },
      { level: 100, sigils: 60, bonus_pct: 10.00, advancement: 7900 },
    ],
  },
  {
    name: 'Romulus', stats: ['Lethality', 'Health'], max_bonus_pct: 20,
    milestones: [
      { level: 0, sigils: 0, bonus_pct: 0, advancement: 0 },
      { level: 10, sigils: 20, bonus_pct: 3.80, advancement: 1760 },
      { level: 20, sigils: 40, bonus_pct: 5.60, advancement: 2860 },
      { level: 30, sigils: 80, bonus_pct: 7.40, advancement: 4020 },
      { level: 40, sigils: 120, bonus_pct: 9.20, advancement: 5720 },
      { level: 50, sigils: 160, bonus_pct: 11.00, advancement: 7980 },
      { level: 60, sigils: 200, bonus_pct: 12.80, advancement: 10730 },
      { level: 70, sigils: 240, bonus_pct: 14.60, advancement: 13480 },
      { level: 80, sigils: 280, bonus_pct: 16.40, advancement: 16230 },
      { level: 90, sigils: 320, bonus_pct: 18.20, advancement: 18980 },
      { level: 100, sigils: 360, bonus_pct: 20.00, advancement: 21730 },
    ],
  },
  {
    name: 'Holger', stats: ['Attack', 'Defense'], max_bonus_pct: 15,
    milestones: [
      { level: 0, sigils: 0, bonus_pct: 0, advancement: 0 },
      { level: 10, sigils: 8, bonus_pct: 2.85, advancement: 960 },
      { level: 20, sigils: 16, bonus_pct: 4.20, advancement: 1560 },
      { level: 30, sigils: 24, bonus_pct: 5.55, advancement: 2190 },
      { level: 40, sigils: 32, bonus_pct: 6.90, advancement: 3120 },
      { level: 50, sigils: 40, bonus_pct: 8.25, advancement: 4350 },
      { level: 60, sigils: 48, bonus_pct: 9.60, advancement: 5850 },
      { level: 70, sigils: 56, bonus_pct: 10.95, advancement: 7350 },
      { level: 80, sigils: 64, bonus_pct: 12.30, advancement: 8850 },
      { level: 90, sigils: 72, bonus_pct: 13.65, advancement: 10350 },
      { level: 100, sigils: 80, bonus_pct: 15.00, advancement: 11850 },
    ],
  },
  {
    name: 'Cyrille', stats: ['Attack'], max_bonus_pct: 15,
    milestones: [
      { level: 0, sigils: 0, bonus_pct: 0, advancement: 0 },
      { level: 10, sigils: 5, bonus_pct: 2.85, advancement: 320 },
      { level: 20, sigils: 10, bonus_pct: 4.20, advancement: 520 },
      { level: 30, sigils: 15, bonus_pct: 5.55, advancement: 730 },
      { level: 40, sigils: 20, bonus_pct: 6.90, advancement: 1040 },
      { level: 50, sigils: 25, bonus_pct: 8.25, advancement: 1450 },
      { level: 60, sigils: 30, bonus_pct: 9.60, advancement: 1950 },
      { level: 70, sigils: 35, bonus_pct: 10.95, advancement: 2450 },
      { level: 80, sigils: 40, bonus_pct: 12.30, advancement: 2950 },
      { level: 90, sigils: 45, bonus_pct: 13.65, advancement: 3450 },
      { level: 100, sigils: 50, bonus_pct: 15.00, advancement: 3950 },
    ],
  },
  {
    name: 'Fabian', stats: ['Lethality', 'Health'], max_bonus_pct: 15,
    milestones: [
      { level: 0, sigils: 0, bonus_pct: 0, advancement: 0 },
      { level: 10, sigils: 12, bonus_pct: 2.85, advancement: 960 },
      { level: 20, sigils: 24, bonus_pct: 4.20, advancement: 1560 },
      { level: 30, sigils: 36, bonus_pct: 5.55, advancement: 2190 },
      { level: 40, sigils: 48, bonus_pct: 6.90, advancement: 3120 },
      { level: 50, sigils: 60, bonus_pct: 8.25, advancement: 4350 },
      { level: 60, sigils: 72, bonus_pct: 9.60, advancement: 5850 },
      { level: 70, sigils: 84, bonus_pct: 10.95, advancement: 7350 },
      { level: 80, sigils: 96, bonus_pct: 12.30, advancement: 8850 },
      { level: 90, sigils: 108, bonus_pct: 13.65, advancement: 10350 },
      { level: 100, sigils: 120, bonus_pct: 15.00, advancement: 11850 },
    ],
  },
];

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
        <div className="flex flex-wrap gap-1.5 mb-6 border-b border-surface-border pb-4 lg:flex-nowrap lg:gap-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors whitespace-nowrap lg:flex-1 lg:text-center ${
                activeTab === tab.id
                  ? 'bg-ice text-background'
                  : 'bg-surface text-frost-muted hover:text-frost hover:bg-surface-hover'
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

// Crystal Laboratory: daily refinement costs and expected FC output
const CRYSTAL_LAB_REFINEMENT_COSTS = [5000, 10000, 20000, 30000, 40000, 50000, 50000, 50000];
const CRYSTAL_LAB_DROP_RATES = [
  { crystals: 1, chance: 0.40 },
  { crystals: 2, chance: 0.30 },
  { crystals: 3, chance: 0.15 },
  { crystals: 4, chance: 0.10 },
  { crystals: 5, chance: 0.05 },
];
const CRYSTAL_LAB_DAILY_LIMITS: { label: string; count: number }[] = [
  { label: 'FC5', count: 5 },
  { label: 'War Academy', count: 6 },
  { label: 'FC8', count: 7 },
  { label: 'FC10', count: 8 },
];
// Expected value per refinement: 1*0.4 + 2*0.3 + 3*0.15 + 4*0.1 + 5*0.05 = 2.10
const CRYSTAL_LAB_EV = CRYSTAL_LAB_DROP_RATES.reduce((sum, r) => sum + r.crystals * r.chance, 0);

// Super Refinement: FC → Refined Fire Crystals (100/week, 5 tiers of 20)
const SUPER_REFINEMENT_TIERS = [
  { tier: 1, fc_cost: 20, ev: 1 * 0.65 + 2 * 0.25 + 3 * 0.10 },
  { tier: 2, fc_cost: 50, ev: 2 * 0.85 + 3 * 0.15 },
  { tier: 3, fc_cost: 100, ev: 3 * 0.85 + 4 * 0.125 + 5 * 0.02 + 6 * 0.005 },
  { tier: 4, fc_cost: 130, ev: 3 * 0.75 + 4 * 0.15 + 5 * 0.05 + 6 * 0.03 + 7 * 0.01 + 8 * 0.005 + 9 * 0.005 },
  { tier: 5, fc_cost: 160, ev: 3 * 0.70 + 4 * 0.12 + 5 * 0.09 + 6 * 0.04 + 7 * 0.015 + 8 * 0.01 + 9 * 0.01 + 10 * 0.005 + 11 * 0.005 + 12 * 0.005 },
];

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
  { id: 'pet_leveling', label: 'Pet Leveling', category: 'Pets', color: 'text-amber-400', activeColor: 'border-amber-500/50 bg-amber-500/10 text-amber-400' },
  { id: 'expert_skills', label: 'Expert Skills', category: 'Experts', color: 'text-cyan-400', activeColor: 'border-cyan-500/50 bg-cyan-500/10 text-cyan-400' },
  { id: 'expert_affinity', label: 'Affinity', category: 'Experts', color: 'text-teal-400', activeColor: 'border-teal-500/50 bg-teal-500/10 text-teal-400' },
  { id: 'crystal_lab', label: 'Crystal Lab', category: 'Buildings', color: 'text-red-400', activeColor: 'border-red-500/50 bg-red-500/10 text-red-400' },
];

function UpgradeCalculatorsTab() {
  const [calc, setCalc] = useState<CalcType>('enhancement');

  // Group calculators by category for the sub-tab selector
  const categories = ['Hero Gear', 'Chief', 'Buildings', 'Pets', 'Experts'];

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
      {calc === 'pet_leveling' && <PetLevelingCalc />}
      {calc === 'expert_skills' && <ExpertSkillsCalc />}
      {calc === 'expert_affinity' && <ExpertAffinityCalc />}
      {calc === 'crystal_lab' && <CrystalLabCalc />}
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

// ── Pet Leveling Calculator ──────────────────────────────────────────

type PetRarity = 'Common' | 'N' | 'R' | 'SR' | 'SSR';

// Pet Food costs per level (index = level - 1, so index 0 = cost for level 1→2)
// All pets of the same rarity share identical costs (verified from whiteoutsurvival.app)
const PET_FOOD: Record<PetRarity, number[]> = {
  Common: [
    100,110,120,130,140,150,160,170,185,200,
    220,240,260,280,300,320,340,360,380,400,
    420,440,460,480,500,520,540,560,580,600,
    630,660,690,720,750,780,810,840,870,900,
    940,980,1020,1060,1100,1140,1180,1220,1260,1320,
  ],
  N: [
    200,220,240,260,280,300,320,340,370,400,
    430,460,490,520,550,580,610,640,680,720,
    760,800,840,880,920,960,1000,1040,1100,1160,
    1220,1280,1340,1400,1460,1520,1580,1640,1720,1800,
    1880,1960,2040,2120,2200,2280,2360,2440,2540,2640,
    2740,2840,2940,3040,3140,3240,3340,3440,3560,
  ],
  R: [
    300,330,360,390,420,450,480,510,555,600,
    645,690,735,780,825,870,915,960,1020,1080,
    1140,1200,1260,1320,1380,1440,1500,1560,1650,1740,
    1830,1920,2010,2100,2190,2280,2370,2460,2580,2700,
    2820,2940,3060,3180,3300,3420,3540,3660,3810,3960,
    4110,4260,4410,4560,4710,4860,5010,5160,5340,5520,
    5700,5880,6060,6240,6420,6600,6780,6960,7140,
  ],
  SR: [
    400,440,480,520,560,600,640,680,740,800,
    860,920,980,1040,1100,1160,1220,1280,1360,1440,
    1520,1600,1680,1760,1840,1920,2000,2080,2200,2320,
    2440,2560,2680,2800,2920,3040,3160,3280,3440,3600,
    3760,3920,4080,4240,4400,4560,4720,4880,5080,5280,
    5480,5680,5880,6080,6280,6480,6680,6880,7120,7360,
    7600,7840,8080,8320,8560,8800,9040,9280,9520,9760,
    10000,10240,10480,10720,10960,11200,11440,11680,12000,
  ],
  SSR: [
    500,550,600,650,700,750,800,850,925,1000,
    1075,1150,1225,1300,1375,1450,1525,1600,1700,1800,
    1900,2000,2100,2200,2300,2400,2500,2600,2750,2900,
    3050,3200,3350,3500,3650,3800,3950,4100,4300,4500,
    4700,4900,5100,5300,5500,5700,5900,6100,6350,6600,
    6850,7100,7350,7600,7850,8100,8350,8600,8900,9200,
    9500,9800,10100,10400,10700,11000,11300,11600,11900,12200,
    12500,12800,13100,13400,13700,14000,14300,14600,15000,15400,
    15800,16200,16600,17000,17400,17800,18200,18600,19000,19400,
    19800,20200,20600,21000,21400,21800,22200,22600,23100,
  ],
};

// Advancement milestone costs (materials needed at every 10th level)
// Format: { level, taming, energizing, strengthening }
const PET_ADVANCEMENT: Record<PetRarity, { level: number; taming: number; energizing: number; strengthening: number }[]> = {
  Common: [
    { level: 10, taming: 15, energizing: 0, strengthening: 0 },
    { level: 20, taming: 30, energizing: 0, strengthening: 0 },
    { level: 30, taming: 45, energizing: 10, strengthening: 0 },
    { level: 40, taming: 60, energizing: 20, strengthening: 0 },
    { level: 50, taming: 90, energizing: 30, strengthening: 10 },
  ],
  N: [
    { level: 10, taming: 20, energizing: 0, strengthening: 0 },
    { level: 20, taming: 40, energizing: 0, strengthening: 0 },
    { level: 30, taming: 60, energizing: 10, strengthening: 0 },
    { level: 40, taming: 90, energizing: 20, strengthening: 0 },
    { level: 50, taming: 130, energizing: 30, strengthening: 10 },
    { level: 60, taming: 175, energizing: 50, strengthening: 20 },
  ],
  R: [
    { level: 10, taming: 25, energizing: 0, strengthening: 0 },
    { level: 20, taming: 50, energizing: 0, strengthening: 0 },
    { level: 30, taming: 75, energizing: 10, strengthening: 0 },
    { level: 40, taming: 100, energizing: 20, strengthening: 0 },
    { level: 50, taming: 155, energizing: 30, strengthening: 10 },
    { level: 60, taming: 200, energizing: 50, strengthening: 20 },
    { level: 70, taming: 255, energizing: 80, strengthening: 40 },
  ],
  SR: [
    { level: 10, taming: 30, energizing: 0, strengthening: 0 },
    { level: 20, taming: 60, energizing: 0, strengthening: 0 },
    { level: 30, taming: 95, energizing: 10, strengthening: 0 },
    { level: 40, taming: 125, energizing: 20, strengthening: 0 },
    { level: 50, taming: 190, energizing: 30, strengthening: 10 },
    { level: 60, taming: 250, energizing: 50, strengthening: 20 },
    { level: 70, taming: 310, energizing: 80, strengthening: 40 },
    { level: 80, taming: 380, energizing: 100, strengthening: 60 },
  ],
  SSR: [
    { level: 10, taming: 35, energizing: 0, strengthening: 0 },
    { level: 20, taming: 70, energizing: 0, strengthening: 0 },
    { level: 30, taming: 110, energizing: 15, strengthening: 0 },
    { level: 40, taming: 145, energizing: 35, strengthening: 0 },
    { level: 50, taming: 220, energizing: 50, strengthening: 10 },
    { level: 60, taming: 290, energizing: 65, strengthening: 20 },
    { level: 70, taming: 365, energizing: 85, strengthening: 40 },
    { level: 80, taming: 440, energizing: 100, strengthening: 60 },
    { level: 90, taming: 585, energizing: 115, strengthening: 80 },
    { level: 100, taming: 730, energizing: 135, strengthening: 100 },
  ],
};

const PET_MAX_LEVEL: Record<PetRarity, number> = { Common: 50, N: 60, R: 70, SR: 80, SSR: 100 };

const PET_RARITY_OPTIONS: { value: PetRarity; label: string; pets: string }[] = [
  { value: 'Common', label: 'Common', pets: 'Cave Hyena' },
  { value: 'N', label: 'N (Uncommon)', pets: 'Arctic Wolf, Musk Ox' },
  { value: 'R', label: 'R (Rare)', pets: 'Giant Tapir, Titan Roc' },
  { value: 'SR', label: 'SR (Epic)', pets: 'Giant Elk, Snow Leopard, Frostscale Chameleon' },
  { value: 'SSR', label: 'SSR (Legendary)', pets: 'Cave Lion, Snow Ape, Iron Rhino, Saber-tooth Tiger, Mammoth, Frost Gorilla' },
];

function PetLevelingCalc() {
  const [rarity, setRarity] = useState<PetRarity>('SSR');
  const [fromLevel, setFromLevel] = useState(1);
  const [toLevel, setToLevel] = useState(100);

  const maxLevel = PET_MAX_LEVEL[rarity];
  const foodArr = PET_FOOD[rarity];
  const advArr = PET_ADVANCEMENT[rarity];

  // Clamp levels when rarity changes
  useEffect(() => {
    const max = PET_MAX_LEVEL[rarity];
    if (fromLevel > max) setFromLevel(1);
    if (toLevel > max) setToLevel(max);
  }, [rarity, fromLevel, toLevel]);

  const costs = useMemo(() => {
    if (fromLevel >= toLevel) return null;

    // Pet food: sum costs from fromLevel to toLevel-1
    // foodArr[i] = cost from level (i+1) to (i+2), so for level L the cost is foodArr[L-1]
    let totalFood = 0;
    for (let lvl = fromLevel; lvl < toLevel; lvl++) {
      totalFood += foodArr[lvl - 1] || 0;
    }

    // Advancement materials: sum milestones in range
    let totalTaming = 0, totalEnergizing = 0, totalStrengthening = 0;
    const milestonesInRange: typeof advArr = [];
    for (const m of advArr) {
      if (m.level > fromLevel && m.level <= toLevel) {
        totalTaming += m.taming;
        totalEnergizing += m.energizing;
        totalStrengthening += m.strengthening;
        milestonesInRange.push(m);
      }
    }

    return { totalFood, totalTaming, totalEnergizing, totalStrengthening, milestonesInRange };
  }, [fromLevel, toLevel, foodArr, advArr]);

  return (
    <div className="space-y-4">
      {/* Info Banner */}
      <div className="card border border-amber-500/30 bg-amber-500/5">
        <p className="text-sm text-frost">
          Calculate <strong className="text-amber-400">Pet Leveling</strong> costs. All pets of the same rarity share identical costs.
          Skills upgrade automatically at advancement milestones (every 10 levels).
        </p>
      </div>

      {/* Inputs */}
      <div className="card">
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="text-xs text-frost-muted block mb-1">Pet Rarity</label>
            <select
              value={rarity}
              onChange={(e) => setRarity(e.target.value as PetRarity)}
              className="input w-full text-sm"
            >
              {PET_RARITY_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            <p className="text-[10px] text-frost-muted mt-1">{PET_RARITY_OPTIONS.find(o => o.value === rarity)?.pets}</p>
          </div>
          <div>
            <label className="text-xs text-frost-muted block mb-1">From Level</label>
            <input
              type="number"
              min={1}
              max={maxLevel - 1}
              value={fromLevel}
              onChange={(e) => setFromLevel(Math.max(1, Math.min(maxLevel - 1, Number(e.target.value))))}
              className="input w-full text-center text-lg"
            />
          </div>
          <div>
            <label className="text-xs text-frost-muted block mb-1">To Level</label>
            <input
              type="number"
              min={2}
              max={maxLevel}
              value={toLevel}
              onChange={(e) => setToLevel(Math.max(2, Math.min(maxLevel, Number(e.target.value))))}
              className="input w-full text-center text-lg"
            />
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
          <h3 className="section-header mb-4">Cost: Level {fromLevel} → {toLevel} ({rarity})</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border">
                <th className="text-left py-2 px-3 text-frost-muted font-medium">Resource</th>
                <th className="text-right py-2 px-3 text-frost-muted font-medium">Total</th>
              </tr>
            </thead>
            <tbody>
              <CostRow label="Pet Food" perSlot={costs.totalFood} color="text-amber-400" />
              {costs.totalTaming > 0 && <CostRow label="Taming Manuals" perSlot={costs.totalTaming} color="text-blue-400" />}
              {costs.totalEnergizing > 0 && <CostRow label="Energizing Potions" perSlot={costs.totalEnergizing} color="text-green-400" />}
              {costs.totalStrengthening > 0 && <CostRow label="Strengthening Serums" perSlot={costs.totalStrengthening} color="text-purple-400" />}
            </tbody>
          </table>

          {/* Milestone Breakdown */}
          {costs.milestonesInRange.length > 0 && (
            <div className="mt-4 pt-4 border-t border-surface-border">
              <h4 className="text-xs font-semibold text-frost-muted mb-2 uppercase tracking-wider">Advancement Milestones</h4>
              <div className="space-y-1">
                {costs.milestonesInRange.map((m) => (
                  <div key={m.level} className="flex items-center justify-between text-xs bg-surface/50 rounded px-3 py-2">
                    <span className="text-frost font-medium">Level {m.level}</span>
                    <span className="text-frost-muted">
                      {m.taming} Taming
                      {m.energizing > 0 && ` + ${m.energizing} Energizing`}
                      {m.strengthening > 0 && ` + ${m.strengthening} Strengthening`}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Expert Skills Calculator ────────────────────────────────────────

function ExpertSkillsCalc() {
  const [expertIdx, setExpertIdx] = useState(0);
  const [skillIdx, setSkillIdx] = useState(0);
  const [fromLevel, setFromLevel] = useState(1);
  const [toLevel, setToLevel] = useState(5);
  const [calcAll, setCalcAll] = useState(false);

  const expert = EXPERTS[expertIdx];
  const skill = expert.skills[skillIdx];

  // Reset skill selection and levels when expert changes
  useEffect(() => {
    setSkillIdx(0);
    setFromLevel(1);
    setToLevel(EXPERTS[expertIdx].skills[0].max_level);
  }, [expertIdx]);

  // Reset levels when skill changes
  useEffect(() => {
    const s = EXPERTS[expertIdx].skills[skillIdx];
    setFromLevel(1);
    setToLevel(s.max_level);
  }, [expertIdx, skillIdx]);

  // Calculate costs for a single skill
  const singleCosts = useMemo(() => {
    if (fromLevel >= toLevel) return null;
    let totalExp = 0, totalBooks = 0;
    for (const c of skill.costs) {
      if (c.level > fromLevel && c.level <= toLevel) {
        totalExp += c.exp;
        totalBooks += c.books;
      }
    }
    return { exp: totalExp, books: totalBooks };
  }, [skill, fromLevel, toLevel]);

  // Calculate costs for ALL skills of the selected expert
  const allSkillsCosts = useMemo(() => {
    if (!calcAll) return null;
    const breakdown: { name: string; exp: number; books: number; levels: string }[] = [];
    let grandExp = 0, grandBooks = 0;
    for (const s of expert.skills) {
      let exp = 0, books = 0;
      for (const c of s.costs) {
        exp += c.exp;
        books += c.books;
      }
      breakdown.push({ name: s.name, exp, books, levels: `1 → ${s.max_level}` });
      grandExp += exp;
      grandBooks += books;
    }
    return { breakdown, totalExp: grandExp, totalBooks: grandBooks };
  }, [expert, calcAll]);

  return (
    <div className="space-y-4">
      {/* Info Banner */}
      <div className="card border border-cyan-500/30 bg-cyan-500/5">
        <p className="text-sm text-frost">
          Calculate <strong className="text-cyan-400">Books of Knowledge</strong> and{' '}
          <strong className="text-cyan-400">EXP</strong> needed to upgrade Expert skills.
          Experts unlock at FC4-FC5 via the Dawn Academy. Each expert has 4 skills with varying max levels (5, 10, or 20).
        </p>
      </div>

      {/* Inputs */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Expert selector */}
          <div>
            <label className="text-xs text-frost-muted block mb-1">Expert</label>
            <select
              value={expertIdx}
              onChange={(e) => setExpertIdx(Number(e.target.value))}
              className="input w-full text-sm"
            >
              {EXPERTS.map((ex, i) => (
                <option key={ex.name} value={i}>{ex.name} — {ex.class_name}</option>
              ))}
            </select>
          </div>

          {/* Skill selector */}
          <div>
            <label className="text-xs text-frost-muted block mb-1">Skill</label>
            <select
              value={skillIdx}
              onChange={(e) => setSkillIdx(Number(e.target.value))}
              className="input w-full text-sm"
            >
              {expert.skills.map((s, i) => (
                <option key={i} value={i}>{s.name} (max Lv.{s.max_level})</option>
              ))}
            </select>
          </div>

          {/* From Level */}
          <div>
            <label className="text-xs text-frost-muted block mb-1">From Level</label>
            <input
              type="number"
              min={1}
              max={skill.max_level - 1}
              value={fromLevel}
              onChange={(e) => setFromLevel(Math.max(1, Math.min(skill.max_level - 1, Number(e.target.value))))}
              className="input w-full text-center text-lg"
            />
          </div>

          {/* To Level */}
          <div>
            <label className="text-xs text-frost-muted block mb-1">To Level</label>
            <input
              type="number"
              min={2}
              max={skill.max_level}
              value={toLevel}
              onChange={(e) => setToLevel(Math.max(2, Math.min(skill.max_level, Number(e.target.value))))}
              className="input w-full text-center text-lg"
            />
          </div>
        </div>

        {/* Toggle: show all skills total */}
        <div className="mt-4 flex items-center gap-2">
          <button
            onClick={() => setCalcAll(!calcAll)}
            aria-pressed={calcAll}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors border ${
              calcAll
                ? 'border-cyan-500/50 bg-cyan-500/10 text-cyan-400'
                : 'border-surface-border bg-surface text-frost-muted hover:text-frost'
            }`}
          >
            Show all skills total for {expert.name}
          </button>
        </div>
      </div>

      {/* Skill Description */}
      <div className="card border border-cyan-500/20">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-frost font-medium">{skill.name}</span>
            <span className="text-frost-muted text-sm ml-2">— {skill.description}</span>
          </div>
          <span className="text-xs px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400">
            Max Lv.{skill.max_level}
          </span>
        </div>
        <div className="text-xs text-frost-muted mt-1">
          {expert.name}&apos;s affinity bonus: <span className="text-cyan-400">{expert.affinity_bonus}</span>
        </div>
      </div>

      {/* Single Skill Results */}
      {fromLevel >= toLevel ? (
        <div className="card text-center py-8">
          <p className="text-frost-muted">Set &quot;From Level&quot; lower than &quot;To Level&quot; to see costs</p>
        </div>
      ) : singleCosts && (
        <div className="card">
          <h3 className="section-header mb-4">{skill.name}: Level {fromLevel} → {toLevel}</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border">
                <th className="text-left py-2 px-3 text-frost-muted font-medium">Resource</th>
                <th className="text-right py-2 px-3 text-frost-muted font-medium">Total Needed</th>
              </tr>
            </thead>
            <tbody>
              <CostRow label="Books of Knowledge" perSlot={singleCosts.books} color="text-cyan-400" />
              {singleCosts.exp > 0 && (
                <CostRow label="EXP" perSlot={singleCosts.exp} color="text-purple-400" />
              )}
            </tbody>
          </table>

          {/* Per-level breakdown */}
          <div className="mt-4">
            <h4 className="text-xs text-frost-muted mb-2">Per-Level Breakdown</h4>
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-surface-border">
                  <th className="text-left py-1.5 px-3 text-frost-muted">Level</th>
                  <th className="text-right py-1.5 px-3 text-frost-muted">Books</th>
                  <th className="text-right py-1.5 px-3 text-frost-muted">EXP</th>
                </tr>
              </thead>
              <tbody>
                {skill.costs.filter(c => c.level > fromLevel && c.level <= toLevel).map((c) => (
                  <tr key={c.level} className="border-b border-surface-border/30">
                    <td className="py-1.5 px-3 text-frost">Lv.{c.level - 1} → {c.level}</td>
                    <td className="py-1.5 px-3 text-right text-cyan-400">{c.books.toLocaleString()}</td>
                    <td className="py-1.5 px-3 text-right text-purple-400">{c.exp > 0 ? c.exp.toLocaleString() : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* All Skills Total */}
      {calcAll && allSkillsCosts && (
        <div className="card border border-cyan-500/20">
          <h3 className="section-header mb-4">All Skills Total — {expert.name}</h3>
          <p className="text-xs text-frost-muted mb-3">
            Total cost to fully max all 4 skills from Lv.1 to their maximum level.
          </p>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border">
                <th className="text-left py-2 px-3 text-frost-muted font-medium">Skill</th>
                <th className="text-center py-2 px-3 text-frost-muted font-medium">Levels</th>
                <th className="text-right py-2 px-3 text-frost-muted font-medium">Books</th>
                <th className="text-right py-2 px-3 text-frost-muted font-medium">EXP</th>
              </tr>
            </thead>
            <tbody>
              {allSkillsCosts.breakdown.map((s) => (
                <tr key={s.name} className="border-b border-surface-border/30">
                  <td className="py-2 px-3 text-frost">{s.name}</td>
                  <td className="py-2 px-3 text-center text-frost-muted">{s.levels}</td>
                  <td className="py-2 px-3 text-right text-cyan-400">{s.books.toLocaleString()}</td>
                  <td className="py-2 px-3 text-right text-purple-400">{s.exp > 0 ? s.exp.toLocaleString() : '—'}</td>
                </tr>
              ))}
              <tr className="border-t-2 border-cyan-500/30 font-bold">
                <td className="py-3 px-3 text-frost" colSpan={2}>Grand Total</td>
                <td className="py-3 px-3 text-right text-cyan-400 text-lg">{allSkillsCosts.totalBooks.toLocaleString()}</td>
                <td className="py-3 px-3 text-right text-purple-400 text-lg">{allSkillsCosts.totalExp > 0 ? allSkillsCosts.totalExp.toLocaleString() : '—'}</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ── Expert Affinity Calculator ──────────────────────────────────────

function ExpertAffinityCalc() {
  const [expertIdx, setExpertIdx] = useState(0);
  const [fromMilestone, setFromMilestone] = useState(0);
  const [toMilestone, setToMilestone] = useState(10);

  const aff = EXPERT_AFFINITY[expertIdx];
  const milestoneOptions = aff.milestones.map(m => m.level);

  // Reset milestones when expert changes
  useEffect(() => {
    setFromMilestone(0);
    setToMilestone(10);
  }, [expertIdx]);

  const costs = useMemo(() => {
    const fromIdx = milestoneOptions.indexOf(fromMilestone);
    const toIdx = milestoneOptions.indexOf(toMilestone);
    if (fromIdx < 0 || toIdx < 0 || fromIdx >= toIdx) return null;

    const fromM = aff.milestones[fromIdx];
    const toM = aff.milestones[toIdx];

    // Sigils needed = difference in cumulative sigils
    const sigils = toM.sigils - fromM.sigils;

    // Sum advancement points for all milestones in range
    let totalAdvancement = 0;
    for (let i = fromIdx + 1; i <= toIdx; i++) {
      totalAdvancement += aff.milestones[i].advancement;
    }

    // Bonus gain
    const bonusFrom = fromM.bonus_pct;
    const bonusTo = toM.bonus_pct;

    return {
      sigils,
      advancement: totalAdvancement,
      bonus_from: bonusFrom,
      bonus_to: bonusTo,
      bonus_gain: bonusTo - bonusFrom,
      // Milestone breakdown
      breakdown: aff.milestones.slice(fromIdx + 1, toIdx + 1),
    };
  }, [aff, fromMilestone, toMilestone, milestoneOptions]);

  return (
    <div className="space-y-4">
      {/* Info Banner */}
      <div className="card border border-teal-500/30 bg-teal-500/5">
        <p className="text-sm text-frost">
          Calculate <strong className="text-teal-400">Sigils</strong> and{' '}
          <strong className="text-teal-400">Advancement Points</strong> needed to increase Expert affinity.
          Affinity provides passive troop stat bonuses. Gift items (Compass, Fiery Heart, Sail of Conquest) provide advancement points.
          Sigils are required at every 10-level milestone.
        </p>
      </div>

      {/* Inputs */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Expert */}
          <div>
            <label className="text-xs text-frost-muted block mb-1">Expert</label>
            <select
              value={expertIdx}
              onChange={(e) => setExpertIdx(Number(e.target.value))}
              className="input w-full text-sm"
            >
              {EXPERT_AFFINITY.map((ex, i) => (
                <option key={ex.name} value={i}>
                  {ex.name} — {ex.stats.join(' & ')} +{ex.max_bonus_pct}%
                </option>
              ))}
            </select>
          </div>

          {/* From Milestone */}
          <div>
            <label className="text-xs text-frost-muted block mb-1">From Level</label>
            <select
              value={fromMilestone}
              onChange={(e) => setFromMilestone(Number(e.target.value))}
              className="input w-full text-sm"
            >
              {milestoneOptions.slice(0, -1).map((lvl) => (
                <option key={lvl} value={lvl}>
                  Level {lvl}{lvl === 0 ? ' (start)' : ''}
                </option>
              ))}
            </select>
          </div>

          {/* To Milestone */}
          <div>
            <label className="text-xs text-frost-muted block mb-1">To Level</label>
            <select
              value={toMilestone}
              onChange={(e) => setToMilestone(Number(e.target.value))}
              className="input w-full text-sm"
            >
              {milestoneOptions.filter(lvl => lvl > fromMilestone).map((lvl) => (
                <option key={lvl} value={lvl}>Level {lvl}{lvl === 100 ? ' (max)' : ''}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Bonus Display */}
      {costs && (
        <div className="card border border-teal-500/20">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="text-sm text-frost-muted">
              {aff.stats.join(' & ')} Bonus
            </div>
            <div className="flex items-center gap-3">
              <span className="text-frost">+{costs.bonus_from.toFixed(1)}%</span>
              <span className="text-frost-muted">&rarr;</span>
              <span className="font-bold text-lg text-teal-400">+{costs.bonus_to.toFixed(1)}%</span>
              <span className="text-xs px-2 py-0.5 rounded bg-green-500/10 text-green-400">
                +{costs.bonus_gain.toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {!costs ? (
        <div className="card text-center py-8">
          <p className="text-frost-muted">Select a valid level range to see costs</p>
        </div>
      ) : (
        <div className="card">
          <h3 className="section-header mb-4">
            {aff.name}: Level {fromMilestone} &rarr; {toMilestone}
          </h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border">
                <th className="text-left py-2 px-3 text-frost-muted font-medium">Resource</th>
                <th className="text-right py-2 px-3 text-frost-muted font-medium">Total Needed</th>
              </tr>
            </thead>
            <tbody>
              <CostRow label="Common Expert Sigils" perSlot={costs.sigils} color="text-teal-400" />
              <CostRow label="Advancement Points (from gifts)" perSlot={costs.advancement} color="text-purple-400" />
            </tbody>
          </table>

          {/* Milestone Breakdown */}
          <div className="mt-4">
            <h4 className="text-xs text-frost-muted mb-2">Milestone Breakdown</h4>
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-surface-border">
                  <th className="text-left py-1.5 px-3 text-frost-muted">Milestone</th>
                  <th className="text-right py-1.5 px-3 text-frost-muted">Sigils (total)</th>
                  <th className="text-right py-1.5 px-3 text-frost-muted">Advancement</th>
                  <th className="text-right py-1.5 px-3 text-frost-muted">Bonus</th>
                </tr>
              </thead>
              <tbody>
                {costs.breakdown.map((m) => (
                  <tr key={m.level} className="border-b border-surface-border/30">
                    <td className="py-1.5 px-3 text-frost font-medium">Level {m.level}</td>
                    <td className="py-1.5 px-3 text-right text-teal-400">{m.sigils.toLocaleString()}</td>
                    <td className="py-1.5 px-3 text-right text-purple-400">{m.advancement.toLocaleString()}</td>
                    <td className="py-1.5 px-3 text-right text-green-400">+{m.bonus_pct.toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Crystal Laboratory Calculator ───────────────────────────────────

function CrystalLabCalc() {
  const [fcLevel, setFcLevel] = useState(0);
  const [days, setDays] = useState(7);

  const dailyLimit = CRYSTAL_LAB_DAILY_LIMITS[fcLevel].count;

  const results = useMemo(() => {
    // Daily resource costs
    let dailyMeat = 0, dailyWood = 0, dailyCoal = 0, dailyIron = 0;
    for (let i = 0; i < dailyLimit; i++) {
      const cost = CRYSTAL_LAB_REFINEMENT_COSTS[i];
      dailyMeat += cost;
      dailyWood += cost;
      dailyCoal += cost;
      dailyIron += cost;
    }

    const dailyExpectedFC = +(dailyLimit * CRYSTAL_LAB_EV).toFixed(1);
    const periodMeat = dailyMeat * days;
    const periodExpectedFC = +(dailyExpectedFC * days).toFixed(1);

    // Super refinement (weekly): 100 total = 5 tiers × 20 each
    let weeklyFCCost = 0;
    let weeklyExpectedRefined = 0;
    for (const t of SUPER_REFINEMENT_TIERS) {
      // 20 refinements per tier, first each day gets 50% discount
      // For simplicity, compute full-price expected values (discount is minor)
      weeklyFCCost += t.fc_cost * 20;
      weeklyExpectedRefined += t.ev * 20;
    }
    // Apply daily discount: 7 days × 50% off 1 refinement at current tier
    // Average tier cost ≈ (20+50+100+130+160)/5 = 92. Discount saves ~46/day × 7 = ~322 FC/week
    const avgTierCost = SUPER_REFINEMENT_TIERS.reduce((s, t) => s + t.fc_cost, 0) / SUPER_REFINEMENT_TIERS.length;
    const weeklyDiscount = Math.round(avgTierCost * 0.5 * 7);
    weeklyFCCost -= weeklyDiscount;

    return {
      dailyLimit,
      dailyMeat,
      dailyExpectedFC,
      periodDays: days,
      periodMeat: periodMeat,
      periodExpectedFC,
      weeklyFCCost,
      weeklyExpectedRefined: +weeklyExpectedRefined.toFixed(1),
      weeklyDiscount,
    };
  }, [dailyLimit, days]);

  return (
    <div className="space-y-4">
      {/* Info Banner */}
      <div className="card border border-red-500/30 bg-red-500/5">
        <p className="text-sm text-frost">
          Calculate <strong className="text-red-400">Fire Crystal</strong> output from the Crystal Laboratory.
          Normal refinement exchanges resources for Fire Crystals daily.
          Super Refinement converts Fire Crystals to <strong className="text-red-400">Refined Fire Crystals</strong> (100/week).
        </p>
      </div>

      {/* Inputs */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-xs text-frost-muted block mb-1">FC Level (determines daily limit)</label>
            <select
              value={fcLevel}
              onChange={(e) => setFcLevel(Number(e.target.value))}
              className="input w-full text-sm"
            >
              {CRYSTAL_LAB_DAILY_LIMITS.map((d, i) => (
                <option key={d.label} value={i}>{d.label} — {d.count} refinements/day</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-frost-muted block mb-1">Time Period (days)</label>
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="input w-full text-sm"
            >
              <option value={1}>1 day</option>
              <option value={7}>7 days (1 week)</option>
              <option value={14}>14 days (2 weeks)</option>
              <option value={30}>30 days (1 month)</option>
              <option value={90}>90 days (3 months)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Normal Refinement Results */}
      <div className="card">
        <h3 className="section-header mb-4">Normal Refinement — {results.periodDays} day{results.periodDays > 1 ? 's' : ''}</h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-surface-border">
              <th className="text-left py-2 px-3 text-frost-muted font-medium">Resource</th>
              <th className="text-right py-2 px-3 text-frost-muted font-medium">Per Day</th>
              {results.periodDays > 1 && (
                <th className="text-right py-2 px-3 text-frost-muted font-medium">Total ({results.periodDays}d)</th>
              )}
            </tr>
          </thead>
          <tbody>
            <CostRow label="Meat" perSlot={results.dailyMeat} total={results.periodDays > 1 ? results.periodMeat : undefined} color="text-orange-400" />
            <CostRow label="Wood" perSlot={results.dailyMeat} total={results.periodDays > 1 ? results.periodMeat : undefined} color="text-orange-400" />
            <CostRow label="Coal" perSlot={results.dailyMeat} total={results.periodDays > 1 ? results.periodMeat : undefined} color="text-orange-400" />
            <CostRow label="Iron" perSlot={results.dailyMeat} total={results.periodDays > 1 ? results.periodMeat : undefined} color="text-orange-400" />
            <tr className="border-t-2 border-red-500/30">
              <td className="py-3 px-3 text-frost font-bold">Expected Fire Crystals</td>
              <td className="py-3 px-3 text-right font-bold text-red-400 text-lg">~{results.dailyExpectedFC}</td>
              {results.periodDays > 1 && (
                <td className="py-3 px-3 text-right font-bold text-red-400 text-lg">~{results.periodExpectedFC}</td>
              )}
            </tr>
          </tbody>
        </table>
      </div>

      {/* Drop Rates Reference */}
      <div className="card border border-red-500/20">
        <h4 className="text-xs text-frost-muted mb-2">Fire Crystal Drop Rates (per refinement)</h4>
        <div className="flex flex-wrap gap-3">
          {CRYSTAL_LAB_DROP_RATES.map((r) => (
            <div key={r.crystals} className="text-xs">
              <span className="text-red-400 font-medium">{r.crystals} FC</span>
              <span className="text-frost-muted ml-1">({(r.chance * 100).toFixed(0)}%)</span>
            </div>
          ))}
          <div className="text-xs">
            <span className="text-frost font-medium">EV: {CRYSTAL_LAB_EV.toFixed(2)} FC</span>
            <span className="text-frost-muted ml-1">(per refine)</span>
          </div>
        </div>
      </div>

      {/* Super Refinement Summary */}
      <div className="card">
        <h3 className="section-header mb-4">Super Refinement (Weekly)</h3>
        <p className="text-xs text-frost-muted mb-3">
          100 super refinements per week across 5 tiers of 20. First daily refinement is 50% off.
        </p>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-surface-border">
              <th className="text-left py-2 px-3 text-frost-muted font-medium">Tier</th>
              <th className="text-right py-2 px-3 text-frost-muted font-medium">FC Cost</th>
              <th className="text-right py-2 px-3 text-frost-muted font-medium">Refined FC (EV)</th>
              <th className="text-right py-2 px-3 text-frost-muted font-medium">× 20</th>
            </tr>
          </thead>
          <tbody>
            {SUPER_REFINEMENT_TIERS.map((t) => (
              <tr key={t.tier} className="border-b border-surface-border/30">
                <td className="py-2 px-3 text-frost">Tier {t.tier}</td>
                <td className="py-2 px-3 text-right text-red-400">{t.fc_cost} FC</td>
                <td className="py-2 px-3 text-right text-purple-400">~{t.ev.toFixed(2)}</td>
                <td className="py-2 px-3 text-right text-purple-400">~{(t.ev * 20).toFixed(1)}</td>
              </tr>
            ))}
            <tr className="border-t-2 border-red-500/30 font-bold">
              <td className="py-3 px-3 text-frost" colSpan={2}>Weekly Total (with discount)</td>
              <td className="py-3 px-3 text-right text-red-400">~{results.weeklyFCCost.toLocaleString()} FC</td>
              <td className="py-3 px-3 text-right text-purple-400 text-lg">~{results.weeklyExpectedRefined} Refined</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Per-refinement cost breakdown */}
      <div className="card border border-red-500/20">
        <h4 className="text-xs text-frost-muted mb-2">Daily Refinement Cost Breakdown ({dailyLimit} refines)</h4>
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-surface-border">
              <th className="text-left py-1.5 px-3 text-frost-muted">#</th>
              <th className="text-right py-1.5 px-3 text-frost-muted">Cost (each resource)</th>
            </tr>
          </thead>
          <tbody>
            {CRYSTAL_LAB_REFINEMENT_COSTS.slice(0, dailyLimit).map((cost, i) => (
              <tr key={i} className="border-b border-surface-border/30">
                <td className="py-1.5 px-3 text-frost">Refinement {i + 1}</td>
                <td className="py-1.5 px-3 text-right text-orange-400">{cost.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
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
