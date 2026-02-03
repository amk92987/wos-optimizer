'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';
import { adminApi, Hero, AdminItem, DataFile } from '@/lib/api';

type TabType = 'heroes' | 'items' | 'json';

export default function AdminGameDataPage() {
  const { token, user } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('heroes');

  // Stats
  const [heroCount, setHeroCount] = useState(0);
  const [itemCount, setItemCount] = useState(0);
  const [fileCount, setFileCount] = useState(0);

  useEffect(() => {
    if (token) {
      fetchStats();
    }
  }, [token]);

  const fetchStats = async () => {
    try {
      const [heroData, itemData, fileData] = await Promise.all([
        adminApi.listAdminHeroes(token!).catch(() => ({ heroes: [] })),
        adminApi.listAdminItems(token!).catch(() => ({ items: [] })),
        adminApi.getGameDataFiles(token!).catch(() => ({ files: [] })),
      ]);
      setHeroCount(heroData.heroes?.length || 0);
      setItemCount(itemData.items?.length || 0);
      const files = Array.isArray(fileData.files) ? fileData.files : Array.isArray(fileData) ? fileData : [];
      setFileCount(files.length);
    } catch {
      // Fallback
    }
  };

  // Redirect non-admins
  if (user && user.role !== 'admin') {
    return (
      <PageLayout>
        <div className="max-w-2xl mx-auto text-center py-16">
          <div className="text-6xl mb-6">&#x1F512;</div>
          <h1 className="text-2xl font-bold text-frost mb-4">Access Denied</h1>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="max-w-6xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Game Data</h1>
          <p className="text-frost-muted mt-1">Manage heroes, items, and game data files</p>
        </div>

        {/* Stat Cards */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="card text-center">
            <p className="text-2xl font-bold text-ice">{heroCount}</p>
            <p className="text-xs text-frost-muted">Heroes</p>
          </div>
          <div className="card text-center">
            <p className="text-2xl font-bold text-success">{itemCount || '--'}</p>
            <p className="text-xs text-frost-muted">Items</p>
          </div>
          <div className="card text-center">
            <p className="text-2xl font-bold text-warning">{fileCount}</p>
            <p className="text-xs text-frost-muted">Data Files</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-surface-border pb-2">
          {[
            { id: 'heroes' as const, label: 'Heroes' },
            { id: 'items' as const, label: 'Items' },
            { id: 'json' as const, label: 'JSON Files' },
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
        {activeTab === 'heroes' && (
          <HeroesTab token={token!} onStatsChange={(count) => setHeroCount(count)} />
        )}
        {activeTab === 'items' && (
          <ItemsTab token={token!} onStatsChange={(count) => setItemCount(count)} />
        )}
        {activeTab === 'json' && <JsonFilesTab token={token!} />}

        {/* Data Sources */}
        <div className="card mt-6">
          <h2 className="section-header">Data Sources</h2>
          <div className="grid md:grid-cols-4 gap-4 text-sm">
            <a href="https://www.whiteoutsurvival.wiki/" target="_blank" rel="noopener noreferrer" className="p-3 rounded-lg bg-surface hover:bg-surface-hover transition-colors">
              <p className="font-medium text-frost">WoS Wiki</p>
              <p className="text-xs text-frost-muted">Hero data, images</p>
            </a>
            <a href="https://whiteoutdata.com/" target="_blank" rel="noopener noreferrer" className="p-3 rounded-lg bg-surface hover:bg-surface-hover transition-colors">
              <p className="font-medium text-frost">WhiteoutData</p>
              <p className="text-xs text-frost-muted">Game mechanics</p>
            </a>
            <a href="https://whiteoutsurvival.app/" target="_blank" rel="noopener noreferrer" className="p-3 rounded-lg bg-surface hover:bg-surface-hover transition-colors">
              <p className="font-medium text-frost">WoS App</p>
              <p className="text-xs text-frost-muted">FC building data</p>
            </a>
            <a href="https://www.quackulator.com/" target="_blank" rel="noopener noreferrer" className="p-3 rounded-lg bg-surface hover:bg-surface-hover transition-colors">
              <p className="font-medium text-frost">Quackulator</p>
              <p className="text-xs text-frost-muted">Cost calculators</p>
            </a>
          </div>
        </div>
      </div>
    </PageLayout>
  );
}

// ============================================================
// Heroes Tab
// ============================================================

function HeroesTab({ token, onStatsChange }: { token: string; onStatsChange: (count: number) => void }) {
  const [heroes, setHeroes] = useState<Hero[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingHero, setEditingHero] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Add form state
  const [newName, setNewName] = useState('');
  const [newClass, setNewClass] = useState('Infantry');
  const [newRarity, setNewRarity] = useState('Epic');
  const [newGen, setNewGen] = useState(1);
  const [newTier, setNewTier] = useState('A');

  // Edit form state
  const [editName, setEditName] = useState('');
  const [editClass, setEditClass] = useState('Infantry');
  const [editRarity, setEditRarity] = useState('Epic');
  const [editGen, setEditGen] = useState(1);
  const [editTier, setEditTier] = useState('A');

  useEffect(() => {
    fetchHeroes();
  }, [token]);

  const fetchHeroes = async () => {
    try {
      const data = await adminApi.listAdminHeroes(token);
      const list = data.heroes || [];
      setHeroes(list);
      onStatsChange(list.length);
    } catch {
      setHeroes([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!newName.trim()) {
      setMessage({ type: 'error', text: 'Name is required' });
      return;
    }
    try {
      await adminApi.createAdminHero(token, {
        name: newName.trim(),
        hero_class: newClass,
        rarity: newRarity,
        generation: newGen,
        tier_overall: newTier,
      });
      setMessage({ type: 'success', text: `Hero "${newName}" created` });
      setShowAddForm(false);
      setNewName('');
      setNewGen(1);
      setNewTier('A');
      fetchHeroes();
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to create hero' });
    }
  };

  const handleEdit = (hero: Hero) => {
    setEditingHero(hero.name);
    setEditName(hero.name);
    setEditClass(hero.hero_class || 'Infantry');
    setEditRarity(hero.rarity || 'Epic');
    setEditGen(hero.generation || 1);
    setEditTier(hero.tier_overall || 'A');
  };

  const handleSaveEdit = async (originalName: string) => {
    try {
      await adminApi.updateAdminHero(token, originalName, {
        name: editName,
        hero_class: editClass as any,
        rarity: editRarity as any,
        generation: editGen,
        tier_overall: editTier,
      });
      setMessage({ type: 'success', text: `Hero "${editName}" updated` });
      setEditingHero(null);
      fetchHeroes();
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to update hero' });
    }
  };

  const handleDelete = async (heroName: string) => {
    try {
      await adminApi.deleteAdminHero(token, heroName);
      setMessage({ type: 'success', text: `Hero "${heroName}" deleted` });
      setConfirmDelete(null);
      fetchHeroes();
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to delete hero' });
    }
  };

  const classIcons: Record<string, string> = { Infantry: 'INF', Marksman: 'MRK', Lancer: 'LAN' };
  const tierColors: Record<string, string> = {
    'S+': 'text-yellow-400', S: 'text-gray-300', A: 'text-amber-600',
    B: 'text-green-400', C: 'text-yellow-500', D: 'text-red-400',
  };

  // Filter and sort
  const filtered = heroes
    .filter((h) => {
      if (!search) return true;
      const s = search.toLowerCase();
      return (
        h.name.toLowerCase().includes(s) ||
        (h.hero_class || '').toLowerCase().includes(s) ||
        (h.rarity || '').toLowerCase().includes(s)
      );
    })
    .sort((a, b) => (a.generation || 0) - (b.generation || 0) || a.name.localeCompare(b.name));

  return (
    <div className="space-y-4">
      {message && (
        <div className={`p-3 rounded-lg text-sm ${
          message.type === 'success'
            ? 'bg-success/10 text-success border border-success/30'
            : 'bg-error/10 text-error border border-error/30'
        }`}>
          {message.text}
        </div>
      )}

      {/* Search and Add */}
      <div className="card">
        <div className="flex items-center gap-4 mb-4">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name, class, or rarity..."
            className="input flex-1"
          />
          <button onClick={() => setShowAddForm(!showAddForm)} className="btn-primary whitespace-nowrap">
            {showAddForm ? 'Cancel' : 'Add New Hero'}
          </button>
        </div>
        <p className="text-xs text-frost-muted">Showing {filtered.length} heroes</p>
      </div>

      {/* Add Form */}
      {showAddForm && (
        <div className="card border-ice/30">
          <h3 className="font-medium text-frost mb-4">New Hero</h3>
          <div className="grid md:grid-cols-5 gap-4 mb-4">
            <div>
              <label className="text-xs text-frost-muted">Name *</label>
              <input value={newName} onChange={(e) => setNewName(e.target.value)} className="input mt-1" placeholder="Hero name" />
            </div>
            <div>
              <label className="text-xs text-frost-muted">Class</label>
              <select value={newClass} onChange={(e) => setNewClass(e.target.value)} className="input mt-1">
                <option>Infantry</option>
                <option>Marksman</option>
                <option>Lancer</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-frost-muted">Rarity</label>
              <select value={newRarity} onChange={(e) => setNewRarity(e.target.value)} className="input mt-1">
                <option>Epic</option>
                <option>Legendary</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-frost-muted">Generation</label>
              <input type="number" min={1} max={20} value={newGen} onChange={(e) => setNewGen(Number(e.target.value))} className="input mt-1" />
            </div>
            <div>
              <label className="text-xs text-frost-muted">Tier</label>
              <select value={newTier} onChange={(e) => setNewTier(e.target.value)} className="input mt-1">
                <option>S+</option>
                <option>S</option>
                <option>A</option>
                <option>B</option>
                <option>C</option>
                <option>D</option>
              </select>
            </div>
          </div>
          <button onClick={handleCreate} className="btn-primary">Create Hero</button>
        </div>
      )}

      {/* Hero List */}
      <div className="card">
        {isLoading ? (
          <div className="space-y-2">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-12 bg-surface-hover rounded animate-pulse" />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <p className="text-frost-muted text-center py-8">No heroes found</p>
        ) : (
          <div className="space-y-1">
            {filtered.map((hero) => (
              <div key={hero.name}>
                {/* Hero Row */}
                <div className="flex items-center gap-3 p-3 rounded-lg hover:bg-surface/50">
                  <span className="text-xs font-mono bg-surface px-2 py-0.5 rounded w-10 text-center text-frost-muted">
                    {classIcons[hero.hero_class] || '?'}
                  </span>
                  <span className="font-medium text-frost flex-1">{hero.name}</span>
                  <span className="text-xs text-frost-muted w-32">Gen {hero.generation} - {hero.hero_class}</span>
                  <span className={`text-sm font-bold w-8 text-center ${tierColors[hero.tier_overall || ''] || 'text-frost-muted'}`}>
                    {hero.tier_overall || '?'}
                  </span>
                  <button
                    onClick={() => handleEdit(hero)}
                    className="text-xs text-ice hover:underline px-2"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => setConfirmDelete(hero.name)}
                    className="text-xs text-error hover:underline px-2"
                  >
                    Delete
                  </button>
                </div>

                {/* Edit Form */}
                {editingHero === hero.name && (
                  <div className="p-4 ml-4 rounded-lg bg-surface border border-surface-border mb-2">
                    <div className="grid md:grid-cols-5 gap-3 mb-3">
                      <div>
                        <label className="text-xs text-frost-muted">Name</label>
                        <input value={editName} onChange={(e) => setEditName(e.target.value)} className="input mt-1" />
                      </div>
                      <div>
                        <label className="text-xs text-frost-muted">Class</label>
                        <select value={editClass} onChange={(e) => setEditClass(e.target.value)} className="input mt-1">
                          <option>Infantry</option>
                          <option>Marksman</option>
                          <option>Lancer</option>
                        </select>
                      </div>
                      <div>
                        <label className="text-xs text-frost-muted">Rarity</label>
                        <select value={editRarity} onChange={(e) => setEditRarity(e.target.value)} className="input mt-1">
                          <option>Epic</option>
                          <option>Legendary</option>
                        </select>
                      </div>
                      <div>
                        <label className="text-xs text-frost-muted">Generation</label>
                        <input type="number" min={1} max={20} value={editGen} onChange={(e) => setEditGen(Number(e.target.value))} className="input mt-1" />
                      </div>
                      <div>
                        <label className="text-xs text-frost-muted">Tier</label>
                        <select value={editTier} onChange={(e) => setEditTier(e.target.value)} className="input mt-1">
                          <option>S+</option>
                          <option>S</option>
                          <option>A</option>
                          <option>B</option>
                          <option>C</option>
                          <option>D</option>
                        </select>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button onClick={() => handleSaveEdit(hero.name)} className="btn-primary text-sm">Save</button>
                      <button onClick={() => setEditingHero(null)} className="btn-secondary text-sm">Cancel</button>
                    </div>
                  </div>
                )}

                {/* Delete Confirmation */}
                {confirmDelete === hero.name && (
                  <div className="p-4 ml-4 rounded-lg bg-error/10 border border-error/30 mb-2">
                    <p className="text-sm text-warning mb-3">Delete {hero.name}? This will also delete user hero data!</p>
                    <div className="flex gap-2">
                      <button onClick={() => handleDelete(hero.name)} className="btn-primary bg-error hover:bg-error/80 text-sm">
                        Yes, Delete
                      </button>
                      <button onClick={() => setConfirmDelete(null)} className="btn-secondary text-sm">Cancel</button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================
// Items Tab
// ============================================================

function ItemsTab({ token, onStatsChange }: { token: string; onStatsChange: (count: number) => void }) {
  const [items, setItems] = useState<AdminItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingItem, setEditingItem] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Add form state
  const [newName, setNewName] = useState('');
  const [newCategory, setNewCategory] = useState('');
  const [newSubcategory, setNewSubcategory] = useState('');
  const [newRarity, setNewRarity] = useState('Common');

  // Edit form state
  const [editName, setEditName] = useState('');
  const [editCategory, setEditCategory] = useState('');
  const [editRarity, setEditRarity] = useState('Common');

  useEffect(() => {
    fetchItems();
  }, [token]);

  const fetchItems = async () => {
    try {
      const data = await adminApi.listAdminItems(token);
      const list = data.items || [];
      setItems(list);
      onStatsChange(list.length);
    } catch {
      setItems([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!newName.trim()) {
      setMessage({ type: 'error', text: 'Name is required' });
      return;
    }
    try {
      await adminApi.createAdminItem(token, {
        name: newName.trim(),
        category: newCategory.trim(),
        subcategory: newSubcategory.trim() || undefined,
        rarity: newRarity,
      });
      setMessage({ type: 'success', text: `Item "${newName}" created` });
      setShowAddForm(false);
      setNewName('');
      setNewCategory('');
      setNewSubcategory('');
      fetchItems();
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to create item' });
    }
  };

  const handleEdit = (item: AdminItem) => {
    setEditingItem(item.name);
    setEditName(item.name);
    setEditCategory(item.category || '');
    setEditRarity(item.rarity || 'Common');
  };

  const handleSaveEdit = async (originalName: string) => {
    try {
      await adminApi.updateAdminItem(token, originalName, {
        name: editName,
        category: editCategory,
        rarity: editRarity,
      });
      setMessage({ type: 'success', text: `Item "${editName}" updated` });
      setEditingItem(null);
      fetchItems();
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to update item' });
    }
  };

  const handleDelete = async (itemName: string) => {
    try {
      await adminApi.deleteAdminItem(token, itemName);
      setMessage({ type: 'success', text: `Item "${itemName}" deleted` });
      fetchItems();
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to delete item' });
    }
  };

  const rarityColors: Record<string, string> = {
    Common: 'text-frost-muted',
    Rare: 'text-blue-400',
    Epic: 'text-purple-400',
    Legendary: 'text-yellow-400',
  };

  // Filter
  const filtered = items.filter((item) => {
    if (!search) return true;
    const s = search.toLowerCase();
    return (
      item.name.toLowerCase().includes(s) ||
      (item.category || '').toLowerCase().includes(s)
    );
  });

  // Group by category
  const grouped: Record<string, AdminItem[]> = {};
  for (const item of filtered) {
    const cat = item.category || 'Uncategorized';
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push(item);
  }
  const sortedCategories = Object.keys(grouped).sort();

  return (
    <div className="space-y-4">
      <div className="card border-ice/20 bg-ice/5">
        <p className="text-sm text-frost-muted">
          Items are used for backpack/inventory tracking (OCR feature). Add items here to enable inventory scanning.
        </p>
      </div>

      {message && (
        <div className={`p-3 rounded-lg text-sm ${
          message.type === 'success'
            ? 'bg-success/10 text-success border border-success/30'
            : 'bg-error/10 text-error border border-error/30'
        }`}>
          {message.text}
        </div>
      )}

      {/* Search and Add */}
      <div className="card">
        <div className="flex items-center gap-4 mb-4">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name or category..."
            className="input flex-1"
          />
          <button onClick={() => setShowAddForm(!showAddForm)} className="btn-primary whitespace-nowrap">
            {showAddForm ? 'Cancel' : 'Add New Item'}
          </button>
        </div>
        <p className="text-xs text-frost-muted">Showing {filtered.length} items</p>
      </div>

      {/* Add Form */}
      {showAddForm && (
        <div className="card border-ice/30">
          <h3 className="font-medium text-frost mb-4">New Item</h3>
          <div className="grid md:grid-cols-4 gap-4 mb-4">
            <div>
              <label className="text-xs text-frost-muted">Name *</label>
              <input value={newName} onChange={(e) => setNewName(e.target.value)} className="input mt-1" placeholder="Item name" />
            </div>
            <div>
              <label className="text-xs text-frost-muted">Category</label>
              <input value={newCategory} onChange={(e) => setNewCategory(e.target.value)} className="input mt-1" placeholder="e.g., Shard, XP, Material" />
            </div>
            <div>
              <label className="text-xs text-frost-muted">Subcategory</label>
              <input value={newSubcategory} onChange={(e) => setNewSubcategory(e.target.value)} className="input mt-1" placeholder="Optional" />
            </div>
            <div>
              <label className="text-xs text-frost-muted">Rarity</label>
              <select value={newRarity} onChange={(e) => setNewRarity(e.target.value)} className="input mt-1">
                <option>Common</option>
                <option>Rare</option>
                <option>Epic</option>
                <option>Legendary</option>
              </select>
            </div>
          </div>
          <button onClick={handleCreate} className="btn-primary">Create Item</button>
        </div>
      )}

      {/* Items grouped by category */}
      {isLoading ? (
        <div className="card">
          <div className="space-y-2">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-12 bg-surface-hover rounded animate-pulse" />
            ))}
          </div>
        </div>
      ) : sortedCategories.length === 0 ? (
        <div className="card text-center py-8">
          <p className="text-frost-muted">No items found</p>
        </div>
      ) : (
        sortedCategories.map((category) => (
          <div key={category} className="card">
            <h3 className="font-medium text-frost mb-3">
              {category} <span className="text-frost-muted text-sm font-normal">({grouped[category].length} items)</span>
            </h3>
            <div className="space-y-1">
              {grouped[category].map((item) => (
                <div key={item.name}>
                  <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-surface/50">
                    <span className="font-medium text-frost flex-1">{item.name}</span>
                    <span className={`text-xs ${rarityColors[item.rarity || ''] || 'text-frost-muted'}`}>
                      {item.rarity || 'Unknown'}
                    </span>
                    <button onClick={() => handleEdit(item)} className="text-xs text-ice hover:underline px-2">
                      Edit
                    </button>
                    <button onClick={() => handleDelete(item.name)} className="text-xs text-error hover:underline px-2">
                      Delete
                    </button>
                  </div>

                  {/* Edit Form */}
                  {editingItem === item.name && (
                    <div className="p-4 ml-4 rounded-lg bg-surface border border-surface-border mb-2">
                      <div className="grid md:grid-cols-3 gap-3 mb-3">
                        <div>
                          <label className="text-xs text-frost-muted">Name</label>
                          <input value={editName} onChange={(e) => setEditName(e.target.value)} className="input mt-1" />
                        </div>
                        <div>
                          <label className="text-xs text-frost-muted">Category</label>
                          <input value={editCategory} onChange={(e) => setEditCategory(e.target.value)} className="input mt-1" />
                        </div>
                        <div>
                          <label className="text-xs text-frost-muted">Rarity</label>
                          <select value={editRarity} onChange={(e) => setEditRarity(e.target.value)} className="input mt-1">
                            <option>Common</option>
                            <option>Rare</option>
                            <option>Epic</option>
                            <option>Legendary</option>
                          </select>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button onClick={() => handleSaveEdit(item.name)} className="btn-primary text-sm">Save</button>
                        <button onClick={() => setEditingItem(null)} className="btn-secondary text-sm">Cancel</button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  );
}

// ============================================================
// JSON Files Tab (existing functionality)
// ============================================================

function JsonFilesTab({ token }: { token: string }) {
  const [files, setFiles] = useState<DataFile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedFile, setSelectedFile] = useState<DataFile | null>(null);
  const [fileContent, setFileContent] = useState<any>(null);
  const [isLoadingContent, setIsLoadingContent] = useState(false);
  const [filterCategory, setFilterCategory] = useState('');

  // Edit mode state
  const [editMode, setEditMode] = useState(false);
  const [editContent, setEditContent] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    fetchFiles();
  }, [token]);

  const fetchFiles = async () => {
    try {
      const data = await adminApi.getGameDataFiles(token);
      setFiles(Array.isArray(data.files) ? data.files : Array.isArray(data) ? data : []);
    } catch {
      setFiles([]);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchFileContent = async (file: DataFile) => {
    setIsLoadingContent(true);
    setSelectedFile(file);
    setEditMode(false);
    setSaveMessage(null);
    try {
      const data = await adminApi.getGameDataFile(token, file.path);
      setFileContent(data.content || data);
    } catch {
      setFileContent({ error: 'Failed to load file content' });
    } finally {
      setIsLoadingContent(false);
    }
  };

  const handleToggleEdit = () => {
    if (!editMode && fileContent) {
      setEditContent(JSON.stringify(fileContent, null, 2));
    }
    setEditMode(!editMode);
    setSaveMessage(null);
  };

  const handleSaveFile = async () => {
    if (!selectedFile) return;
    setIsSaving(true);
    setSaveMessage(null);
    try {
      JSON.parse(editContent);
      await adminApi.saveGameDataFile(token, selectedFile.path, editContent);
      setFileContent(JSON.parse(editContent));
      setEditMode(false);
      setSaveMessage({ type: 'success', text: 'File saved successfully' });
    } catch (error: any) {
      if (error instanceof SyntaxError) {
        setSaveMessage({ type: 'error', text: 'Invalid JSON syntax' });
      } else {
        setSaveMessage({ type: 'error', text: 'Failed to save file' });
      }
    } finally {
      setIsSaving(false);
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const categories = Array.from(new Set(files.map((f) => f.category))).sort();
  const filteredFiles = filterCategory ? files.filter((f) => f.category === filterCategory) : files;

  const categoryColors: Record<string, string> = {
    core: 'text-ice',
    guides: 'text-success',
    upgrades: 'text-warning',
    optimizer: 'text-purple-400',
    ai: 'text-fire',
    conversions: 'text-frost',
  };

  return (
    <div className="grid md:grid-cols-3 gap-6">
      {/* Files List */}
      <div className="card md:col-span-1">
        <div className="mb-4">
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="input"
          >
            <option value="">All Categories</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        {isLoading ? (
          <div className="space-y-2">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-12 bg-surface-hover rounded animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="space-y-1 max-h-[60vh] overflow-y-auto">
            {filteredFiles.map((file) => (
              <button
                key={file.path}
                onClick={() => fetchFileContent(file)}
                className={`w-full p-3 rounded-lg text-left transition-colors ${
                  selectedFile?.path === file.path
                    ? 'bg-ice/20 text-ice'
                    : 'hover:bg-surface text-frost-muted hover:text-frost'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium truncate">{file.name}</span>
                  <span className={`text-xs ${categoryColors[file.category] || 'text-frost-muted'}`}>
                    {file.category}
                  </span>
                </div>
                <div className="text-xs text-frost-muted mt-1 flex items-center justify-between">
                  <span>{formatDate(file.modified_at)}</span>
                  <span className="font-mono">{formatSize(file.size_bytes)}</span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* File Content */}
      <div className="card md:col-span-2">
        {!selectedFile ? (
          <div className="text-center py-16">
            <div className="text-4xl mb-4">&#x1F4C1;</div>
            <p className="text-frost-muted">Select a file to view its contents</p>
          </div>
        ) : isLoadingContent ? (
          <div className="animate-pulse">
            <div className="h-6 bg-surface-hover rounded w-48 mb-4" />
            <div className="h-96 bg-surface-hover rounded" />
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-bold text-frost">{selectedFile.name}</h2>
                <p className="text-xs text-frost-muted">
                  {selectedFile.path} &middot; {formatSize(selectedFile.size_bytes)}
                </p>
              </div>
              <button onClick={handleToggleEdit} className="text-sm btn-secondary">
                {editMode ? 'Cancel Edit' : 'Edit Mode'}
              </button>
            </div>

            {saveMessage && (
              <div className={`mb-4 p-3 rounded-lg text-sm ${
                saveMessage.type === 'success'
                  ? 'bg-success/10 text-success border border-success/30'
                  : 'bg-error/10 text-error border border-error/30'
              }`}>
                {saveMessage.text}
              </div>
            )}

            {editMode ? (
              <div>
                <textarea
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  className="w-full p-4 rounded-lg bg-background text-sm text-frost font-mono border border-surface-border focus:outline-none focus:border-ice/50"
                  style={{ minHeight: '60vh' }}
                  spellCheck={false}
                />
                <div className="flex justify-end mt-4">
                  <button onClick={handleSaveFile} disabled={isSaving} className="btn-primary">
                    {isSaving ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              </div>
            ) : (
              <pre className="p-4 rounded-lg bg-background text-sm text-frost-muted overflow-auto max-h-[60vh] font-mono">
                {JSON.stringify(fileContent, null, 2)}
              </pre>
            )}
          </>
        )}
      </div>
    </div>
  );
}
