'use client';

import { useState } from 'react';
import PageLayout from '@/components/PageLayout';

interface Tip {
  category: string;
  tips: string[];
}

const quickTips: Tip[] = [
  {
    category: 'Speedups & Events',
    tips: [
      'NEVER use speedups outside of SvS or specific events',
      'Speedups give points only on Day 1, 2, and 5 of SvS',
      'Fire Crystals are worth 2,000 points each on Day 1',
      'Lucky Wheel spins give 8,000 points each',
      'Mithril is worth 40,000 points each on Day 4',
    ],
  },
  {
    category: 'Hero Priorities',
    tips: [
      'F2P: Focus on 3-4 heroes max',
      'Jessie is the most important hero for rally joining (Stand of Arms)',
      'Sergey is essential for garrison defense (Defenders Edge)',
      'Level expedition skills for PvP, exploration skills for PvE',
      'Hero gear becomes important at FC30+',
    ],
  },
  {
    category: 'Rally Mechanics',
    tips: [
      'Only the FIRST hero\'s top-right skill applies when joining',
      'Top 4 highest LEVEL expedition skills apply to rally',
      'Always put Jessie first for attack rallies',
      'Always put Sergey first for garrison defense',
      'Rally leader\'s troop composition matters most',
    ],
  },
  {
    category: 'Troop Management',
    tips: [
      'Infantry > Lancer > Marksman > Infantry (type advantage)',
      'Higher tier troops are always better',
      'Bear Trap: 0/10/90 (Infantry/Lancer/Marksman)',
      'Crazy Joe: 90/10/0 (Infantry/Lancer/Marksman)',
      'Garrison: 60/25/15 (Infantry/Lancer/Marksman)',
    ],
  },
  {
    category: 'Resource Protection',
    tips: [
      'Resources above warehouse capacity can be stolen',
      'Spend resources or shield before going offline',
      'Farm accounts should stay shielded during SvS',
      'Never have more troops than your hospital can heal',
      'Use peace shields during preparation phases',
    ],
  },
  {
    category: 'Chief Gear',
    tips: [
      'Focus on one troop type\'s gear first',
      'Gold quality unlocks mastery (huge boost)',
      'Charms unlock at Furnace 25',
      'Mythic gear provides biggest stat increase',
      'Don\'t neglect gear - it\'s a major power source',
    ],
  },
  {
    category: 'Alliance Tips',
    tips: [
      'Join the most active alliance you can',
      'Alliance tech provides permanent buffs',
      'Participate in all alliance events',
      'Help alliance members with their builds',
      'Coordinate during SvS for better results',
    ],
  },
  {
    category: 'Daybreak Island',
    tips: [
      'Unlocks at Furnace 19',
      'Battle Enhancer decorations give combat stats',
      'Tree of Life gives universal buffs',
      'Mythic decorations: 10 levels × 1% = 10% max',
      'Epic decorations: 5 levels × 0.5% = 2.5% max',
    ],
  },
];

export default function QuickTipsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const categories = [...new Set(quickTips.map((t) => t.category))];

  const filteredTips = quickTips
    .filter((t) => !selectedCategory || t.category === selectedCategory)
    .map((t) => ({
      ...t,
      tips: t.tips.filter(
        (tip) =>
          !searchQuery || tip.toLowerCase().includes(searchQuery.toLowerCase())
      ),
    }))
    .filter((t) => t.tips.length > 0);

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Quick Tips</h1>
          <p className="text-frost-muted mt-2">
            Fast reference for key game mechanics and strategies
          </p>
        </div>

        {/* Search & Filter */}
        <div className="card mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <input
              type="text"
              placeholder="Search tips..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input flex-1"
            />
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setSelectedCategory(null)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  !selectedCategory
                    ? 'bg-ice text-background'
                    : 'bg-surface text-frost-muted hover:text-frost'
                }`}
              >
                All
              </button>
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    selectedCategory === cat
                      ? 'bg-ice text-background'
                      : 'bg-surface text-frost-muted hover:text-frost'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Tips Grid */}
        {filteredTips.length === 0 ? (
          <div className="card text-center py-12">
            <div className="text-4xl mb-4">🔍</div>
            <p className="text-frost-muted">No tips match your search</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-4">
            {filteredTips.map((section) => (
              <div key={section.category} className="card">
                <h2 className="text-lg font-bold text-frost mb-4">
                  {section.category}
                </h2>
                <ul className="space-y-2">
                  {section.tips.map((tip, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2 text-sm text-frost-muted"
                    >
                      <span className="text-ice mt-0.5">•</span>
                      <span
                        dangerouslySetInnerHTML={{
                          __html: searchQuery
                            ? tip.replace(
                                new RegExp(`(${searchQuery})`, 'gi'),
                                '<mark class="bg-ice/30 text-frost px-0.5 rounded">$1</mark>'
                              )
                            : tip,
                        }}
                      />
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}

        {/* Important Formulas */}
        <div className="card mt-6">
          <h2 className="section-header">Key Formulas</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-surface">
              <h3 className="font-medium text-frost mb-2">Generation Calculation</h3>
              <code className="text-sm text-ice">Gen = floor(server_age / 80) + 1</code>
              <p className="text-xs text-frost-muted mt-2">
                New gen every ~80 days. Gen 14 caps at day 1000+.
              </p>
            </div>
            <div className="p-4 rounded-lg bg-surface">
              <h3 className="font-medium text-frost mb-2">Type Advantage</h3>
              <code className="text-sm text-ice">Damage × 1.25 vs weak type</code>
              <p className="text-xs text-frost-muted mt-2">
                Infantry → Lancer → Marksman → Infantry
              </p>
            </div>
          </div>
        </div>

        {/* Print Button */}
        <div className="text-center mt-6">
          <button
            onClick={() => window.print()}
            className="btn-secondary"
          >
            Print Cheat Sheet
          </button>
        </div>
      </div>
    </PageLayout>
  );
}
