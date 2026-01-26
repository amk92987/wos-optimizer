'use client';

import { useState } from 'react';
import PageLayout from '@/components/PageLayout';

interface PackCategory {
  name: string;
  description: string;
  recommendation: 'good' | 'ok' | 'bad';
  notes: string;
}

const packCategories: PackCategory[] = [
  {
    name: 'Monthly Card',
    description: '30-day daily rewards subscription',
    recommendation: 'good',
    notes: 'Best value for light spenders. Daily gems add up significantly over time.',
  },
  {
    name: 'Weekly Growth Fund',
    description: 'Weekly progression bonuses',
    recommendation: 'good',
    notes: 'Good value if you play daily. Returns more than initial cost over time.',
  },
  {
    name: 'Hero Pack (On Sale)',
    description: 'Discounted hero shards',
    recommendation: 'ok',
    notes: 'Only buy for S-tier heroes you\'re actively building. Check if hero is worth investment.',
  },
  {
    name: 'Speedup Packs',
    description: 'Construction/Research speedups',
    recommendation: 'ok',
    notes: 'Only valuable during SvS or specific events. Never buy at full price.',
  },
  {
    name: 'Resource Packs',
    description: 'Food, Wood, Steel bundles',
    recommendation: 'bad',
    notes: 'Terrible value. Resources are farmable. Only whales should consider.',
  },
  {
    name: 'Random Chest Packs',
    description: 'RNG-based reward chests',
    recommendation: 'bad',
    notes: 'Gambling mechanics. Odds are usually terrible. Avoid unless whale.',
  },
  {
    name: 'Event Packs (Limited)',
    description: 'Event-specific bundles',
    recommendation: 'ok',
    notes: 'Varies widely. Calculate gem value before buying. Some are traps.',
  },
  {
    name: 'VIP Packs',
    description: 'VIP level progression',
    recommendation: 'ok',
    notes: 'VIP buffs are permanent. Good long-term investment for medium spenders.',
  },
];

export default function PacksPage() {
  const [showCalculator, setShowCalculator] = useState(false);
  const [packPrice, setPackPrice] = useState('');
  const [packGems, setPackGems] = useState('');

  const gemValue = packPrice && packGems
    ? (parseFloat(packPrice) / parseFloat(packGems) * 1000).toFixed(2)
    : null;

  const getRecommendationBadge = (rec: string) => {
    switch (rec) {
      case 'good':
        return 'badge-success';
      case 'ok':
        return 'badge-warning';
      case 'bad':
        return 'badge-error';
      default:
        return 'badge-secondary';
    }
  };

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Pack Analyzer</h1>
          <p className="text-frost-muted mt-2">Evaluate pack value before buying</p>
        </div>

        {/* Quick Calculator */}
        <div className="card mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="section-header mb-0">Gem Value Calculator</h2>
            <button
              onClick={() => setShowCalculator(!showCalculator)}
              className="text-sm text-ice hover:text-ice-light"
            >
              {showCalculator ? 'Hide' : 'Show'}
            </button>
          </div>

          {showCalculator && (
            <div className="grid md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm text-frost-muted mb-1">Pack Price ($)</label>
                <input
                  type="number"
                  value={packPrice}
                  onChange={(e) => setPackPrice(e.target.value)}
                  className="input"
                  placeholder="4.99"
                />
              </div>
              <div>
                <label className="block text-sm text-frost-muted mb-1">Gems Included</label>
                <input
                  type="number"
                  value={packGems}
                  onChange={(e) => setPackGems(e.target.value)}
                  className="input"
                  placeholder="1000"
                />
              </div>
              <div>
                <label className="block text-sm text-frost-muted mb-1">Cost per 1000 Gems</label>
                <div className={`input flex items-center ${gemValue ? '' : 'text-frost-muted'}`}>
                  {gemValue ? `$${gemValue}` : 'Enter values'}
                </div>
              </div>
            </div>
          )}

          {showCalculator && (
            <div className="mt-4 p-3 rounded-lg bg-surface">
              <p className="text-sm text-frost-muted">
                <strong className="text-frost">Benchmark:</strong> A "good" deal is generally under $3 per 1000 gems.
                Monthly card gives ~$1.50/1000 gems equivalent value.
              </p>
            </div>
          )}
        </div>

        {/* Pack Guide */}
        <div className="card mb-6">
          <h2 className="section-header">General Guidelines</h2>
          <ul className="space-y-2 text-sm text-frost-muted">
            <li className="flex items-start gap-2">
              <span className="text-success">✓</span>
              <span>Monthly Card and Weekly Growth Fund are best value for light spenders</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-success">✓</span>
              <span>Only buy speedup packs during SvS or specific events</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-warning">△</span>
              <span>Hero packs only for S-tier heroes you're committed to building</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-error">✗</span>
              <span>Avoid resource packs - resources are easily farmable</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-error">✗</span>
              <span>Avoid random chest/gambling packs - odds are terrible</span>
            </li>
          </ul>
        </div>

        {/* Pack Categories */}
        <div className="space-y-4">
          {packCategories.map((pack) => (
            <div key={pack.name} className="card">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-medium text-frost">{pack.name}</h3>
                    <span className={`badge text-xs ${getRecommendationBadge(pack.recommendation)}`}>
                      {pack.recommendation === 'good' ? 'Recommended' :
                       pack.recommendation === 'ok' ? 'Situational' : 'Avoid'}
                    </span>
                  </div>
                  <p className="text-sm text-frost-muted">{pack.description}</p>
                  <p className="text-sm text-frost mt-2">{pack.notes}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Spending Profile Tips */}
        <div className="card mt-6">
          <h2 className="section-header">Spending Profile Tips</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-surface">
              <h3 className="font-medium text-frost mb-2">F2P / Minnow ($0-30)</h3>
              <ul className="text-sm text-frost-muted space-y-1">
                <li>• Monthly Card only (best value)</li>
                <li>• Save free gems for key events</li>
                <li>• Never buy resource packs</li>
              </ul>
            </div>
            <div className="p-4 rounded-lg bg-surface">
              <h3 className="font-medium text-frost mb-2">Dolphin / Orca ($30-500)</h3>
              <ul className="text-sm text-frost-muted space-y-1">
                <li>• Monthly Card + Growth Fund</li>
                <li>• Select hero packs (S-tier only)</li>
                <li>• Event packs during SvS</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Farm Account Warning */}
        <div className="card mt-6 border-warning/30 bg-warning/5">
          <div className="flex gap-3">
            <span className="text-2xl">⚠️</span>
            <div>
              <h3 className="font-medium text-frost">Farm Accounts</h3>
              <p className="text-sm text-frost-muted mt-1">
                Never spend money on farm accounts. They should be pure resource generators
                to support your main account.
              </p>
            </div>
          </div>
        </div>
      </div>
    </PageLayout>
  );
}
