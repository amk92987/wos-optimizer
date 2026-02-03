'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';
import { adminApi } from '@/lib/api';

interface DataFile {
  name: string;
  path: string;
  size_bytes: number;
  modified_at: string;
  category: string;
}

export default function AdminGameDataPage() {
  const { token, user } = useAuth();
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

  // Stats
  const [heroCount, setHeroCount] = useState(0);
  const [itemCount, setItemCount] = useState(0);

  useEffect(() => {
    if (token) {
      fetchFiles();
    }
  }, [token]);

  const fetchFiles = async () => {
    try {
      const data = await adminApi.getGameDataFiles(token!);
      const fileList = Array.isArray(data.files) ? data.files : Array.isArray(data) ? data : [];
      setFiles(fileList);

      // Calculate stats from file data
      const heroFile = fileList.find((f: DataFile) => f.name === 'heroes.json');
      const itemFile = fileList.find((f: DataFile) => f.name === 'items.json');

      // Try to get hero count from the heroes.json content
      if (heroFile) {
        try {
          const heroData = await adminApi.getGameDataFile(token!, heroFile.path);
          const content = heroData.content || heroData;
          if (content?.heroes) {
            setHeroCount(content.heroes.length);
          }
        } catch {
          setHeroCount(56); // fallback
        }
      }

      if (itemFile) {
        try {
          const itemData = await adminApi.getGameDataFile(token!, itemFile.path);
          const content = itemData.content || itemData;
          if (Array.isArray(content)) {
            setItemCount(content.length);
          } else if (content?.items) {
            setItemCount(content.items.length);
          }
        } catch {
          setItemCount(0);
        }
      }
    } catch (error) {
      console.error('Failed to fetch files:', error);
      setFiles([
        { name: 'heroes.json', path: 'data/heroes.json', size_bytes: 43000, modified_at: new Date().toISOString(), category: 'core' },
        { name: 'chief_gear.json', path: 'data/chief_gear.json', size_bytes: 15000, modified_at: new Date().toISOString(), category: 'core' },
        { name: 'events.json', path: 'data/events.json', size_bytes: 8000, modified_at: new Date().toISOString(), category: 'core' },
        { name: 'quick_tips.json', path: 'data/guides/quick_tips.json', size_bytes: 12000, modified_at: new Date().toISOString(), category: 'guides' },
        { name: 'combat_formulas.json', path: 'data/guides/combat_formulas.json', size_bytes: 5000, modified_at: new Date().toISOString(), category: 'guides' },
        { name: 'buildings.edges.json', path: 'data/upgrades/buildings.edges.json', size_bytes: 25000, modified_at: new Date().toISOString(), category: 'upgrades' },
        { name: 'war_academy.steps.json', path: 'data/upgrades/war_academy.steps.json', size_bytes: 8000, modified_at: new Date().toISOString(), category: 'upgrades' },
      ]);
      setHeroCount(56);
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
      const data = await adminApi.getGameDataFile(token!, file.path);
      setFileContent(data.content || data);
    } catch (error) {
      console.error('Failed to fetch file content:', error);
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
      // Validate JSON
      JSON.parse(editContent);
      await adminApi.saveGameDataFile(token!, selectedFile.path, editContent);
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

  // Extract unique categories
  const categories = Array.from(new Set(files.map((f) => f.category))).sort();

  // Filter files
  const filteredFiles = filterCategory
    ? files.filter((f) => f.category === filterCategory)
    : files;

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

  const categoryColors: Record<string, string> = {
    core: 'text-ice',
    guides: 'text-success',
    upgrades: 'text-warning',
    optimizer: 'text-purple-400',
    ai: 'text-fire',
    conversions: 'text-frost',
  };

  return (
    <PageLayout>
      <div className="max-w-6xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Game Data</h1>
          <p className="text-frost-muted mt-1">View and manage game data files</p>
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
            <p className="text-2xl font-bold text-warning">{files.length}</p>
            <p className="text-xs text-frost-muted">Data Files</p>
          </div>
        </div>

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
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
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
                  <button
                    onClick={handleToggleEdit}
                    className={`text-sm ${editMode ? 'btn-secondary' : 'btn-secondary'}`}
                  >
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
                      <button
                        onClick={handleSaveFile}
                        disabled={isSaving}
                        className="btn-primary"
                      >
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
