'use client';

import { useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';

interface InventoryItem {
  name: string;
  quantity: number;
  category: string;
}

const categories = ['All', 'Speedups', 'Resources', 'Hero Items', 'Gear', 'Other'];

export default function BackpackPage() {
  const { token } = useAuth();
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [ocrEnabled, setOcrEnabled] = useState(false);

  const filteredItems = selectedCategory === 'All'
    ? items
    : items.filter((i) => i.category === selectedCategory);

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-frost">Backpack</h1>
            <p className="text-frost-muted mt-2">Track your inventory items</p>
          </div>
        </div>

        {/* OCR Upload */}
        <div className="card mb-6">
          <h2 className="section-header">Screenshot Import (OCR)</h2>
          <div className="p-6 border-2 border-dashed border-surface-border rounded-lg text-center">
            <div className="text-4xl mb-4">📷</div>
            <p className="text-frost mb-2">Upload a screenshot of your backpack</p>
            <p className="text-sm text-frost-muted mb-4">
              Our OCR system will automatically detect and count items
            </p>
            <label className="btn-primary cursor-pointer">
              <input
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => {
                  // TODO: Handle OCR upload
                  console.log('File selected:', e.target.files?.[0]);
                }}
              />
              Upload Screenshot
            </label>
          </div>
          <p className="text-xs text-frost-muted mt-4 text-center">
            Note: OCR feature requires the inventory_ocr feature flag to be enabled
          </p>
        </div>

        {/* Category Filter */}
        <div className="card mb-6">
          <div className="flex flex-wrap gap-2">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedCategory === cat
                    ? 'bg-ice text-background'
                    : 'bg-surface text-frost-muted hover:text-frost hover:bg-surface-hover'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Inventory Grid */}
        {items.length === 0 ? (
          <div className="card text-center py-12">
            <div className="text-4xl mb-4">🎒</div>
            <h3 className="text-lg font-medium text-frost mb-2">No items tracked</h3>
            <p className="text-frost-muted mb-4">
              Upload a screenshot or manually add items to track your inventory
            </p>
            <button className="btn-secondary">Add Items Manually</button>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {filteredItems.map((item, i) => (
              <div key={i} className="card text-center">
                <div className="w-12 h-12 bg-surface-hover rounded-lg mx-auto mb-2 flex items-center justify-center">
                  <span className="text-2xl">📦</span>
                </div>
                <p className="font-medium text-frost text-sm truncate">{item.name}</p>
                <p className="text-lg font-bold text-ice">{item.quantity.toLocaleString()}</p>
              </div>
            ))}
          </div>
        )}

        {/* Common Items Reference */}
        <div className="card mt-6">
          <h2 className="section-header">Common Items to Track</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <h3 className="font-medium text-frost mb-2">Speedups</h3>
              <ul className="text-sm text-frost-muted space-y-1">
                <li>• Construction Speedups (1m, 5m, 15m, 1h, 3h, 8h, 24h)</li>
                <li>• Research Speedups</li>
                <li>• Training Speedups</li>
                <li>• Healing Speedups</li>
              </ul>
            </div>
            <div>
              <h3 className="font-medium text-frost mb-2">Hero Items</h3>
              <ul className="text-sm text-frost-muted space-y-1">
                <li>• Exploration Manuals</li>
                <li>• Expedition Manuals</li>
                <li>• Hero Shards</li>
                <li>• Universal Hero Fragments</li>
              </ul>
            </div>
            <div>
              <h3 className="font-medium text-frost mb-2">Resources</h3>
              <ul className="text-sm text-frost-muted space-y-1">
                <li>• Food</li>
                <li>• Wood</li>
                <li>• Steel</li>
                <li>• Gas</li>
              </ul>
            </div>
            <div>
              <h3 className="font-medium text-frost mb-2">Premium Items</h3>
              <ul className="text-sm text-frost-muted space-y-1">
                <li>• Fire Crystals</li>
                <li>• Mithril</li>
                <li>• Frost Stars</li>
                <li>• VIP Points</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Tips */}
        <div className="card mt-6 border-ice/30 bg-ice/5">
          <h2 className="section-header">Inventory Tips</h2>
          <ul className="space-y-2 text-sm text-frost-muted">
            <li className="flex items-start gap-2">
              <span className="text-ice">💡</span>
              <span>Keep track of speedups to plan your SvS contribution</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-ice">💡</span>
              <span>Note your Fire Crystal and Mithril counts before SvS events</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-ice">💡</span>
              <span>Track hero shards to plan upgrade paths efficiently</span>
            </li>
          </ul>
        </div>
      </div>
    </PageLayout>
  );
}
