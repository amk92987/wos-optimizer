'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';
import { adminApi, API_BASE } from '@/lib/api';

interface AISettings {
  mode: 'off' | 'on' | 'unlimited';
  primary_provider: string;
  fallback_provider: string;
  primary_model: string;
  fallback_model: string;
  daily_limit_free: number;
  daily_limit_admin: number;
  cooldown_seconds: number;
}

interface AIStats {
  total_requests: number;
  total_tokens: number;
  total_conversations: number;
  avg_rating: number | null;
  good_examples: number;
  bad_examples: number;
  helpful_count: number;
  not_helpful_count: number;
}

interface AIConversation {
  id: string;
  user_email: string;
  question: string;
  answer: string;
  provider: string;
  model: string;
  tokens_used: number;
  response_time_ms: number;
  rating: number | null;
  is_helpful: boolean | null;
  user_feedback: string | null;
  is_good_example: boolean;
  is_bad_example: boolean;
  admin_notes: string | null;
  created_at: string;
}

type TabType = 'settings' | 'conversations' | 'training' | 'export';

export default function AdminAIPage() {
  const { token, user } = useAuth();
  const [settings, setSettings] = useState<AISettings | null>(null);
  const [stats, setStats] = useState<AIStats | null>(null);
  const [conversations, setConversations] = useState<AIConversation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabType>('settings');

  // Conversation filters
  const [ratingFilter, setRatingFilter] = useState<'all' | 'rated' | 'unrated'>('all');
  const [curationFilter, setCurationFilter] = useState<'all' | 'good' | 'bad'>('all');
  const [resultLimit, setResultLimit] = useState<number>(50);

  useEffect(() => {
    if (token) {
      fetchData();
    }
  }, [token]);

  useEffect(() => {
    if (token && activeTab === 'conversations') {
      fetchConversations();
    }
  }, [token, ratingFilter, curationFilter, resultLimit, activeTab]);

  const fetchData = async () => {
    try {
      const result = await adminApi.getAISettings(token!);
      const data = result.settings || result;
      setSettings({
        mode: (data.mode || 'on') as 'off' | 'on' | 'unlimited',
        primary_provider: data.primary_provider || 'openai',
        fallback_provider: (data as any).fallback_provider || 'anthropic',
        primary_model: data.primary_model || 'gpt-4o-mini',
        fallback_model: (data as any).fallback_model || 'claude-3-haiku',
        daily_limit_free: data.daily_limit_free || 10,
        daily_limit_admin: data.daily_limit_admin || 1000,
        cooldown_seconds: data.cooldown_seconds || 30,
      });

      // Fetch conversation stats
      try {
        const statsData = await adminApi.getConversationStats(token!);
        setStats({
          total_requests: statsData.total || 0,
          total_tokens: (statsData as any).total_tokens || 0,
          total_conversations: statsData.total || 0,
          avg_rating: (statsData as any).avg_rating || null,
          good_examples: statsData.good_examples || 0,
          bad_examples: statsData.bad_examples || 0,
          helpful_count: statsData.helpful || 0,
          not_helpful_count: (statsData as any).not_helpful || 0,
        });
      } catch {
        setStats({
          total_requests: 0,
          total_tokens: 0,
          total_conversations: 0,
          avg_rating: null,
          good_examples: 0,
          bad_examples: 0,
          helpful_count: 0,
          not_helpful_count: 0,
        });
      }

      await fetchConversations();
    } catch (error) {
      console.error('Failed to fetch AI data:', error);
      setSettings({
        mode: 'on',
        primary_provider: 'openai',
        fallback_provider: 'anthropic',
        primary_model: 'gpt-4o-mini',
        fallback_model: 'claude-3-haiku',
        daily_limit_free: 10,
        daily_limit_admin: 1000,
        cooldown_seconds: 30,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const fetchConversations = async () => {
    try {
      const params: Record<string, string> = { limit: String(resultLimit) };
      if (ratingFilter !== 'all') params.rating = ratingFilter;
      if (curationFilter !== 'all') params.curation = curationFilter;
      const data = await adminApi.getConversations(token!, params);
      const convs = data.conversations || [];
      setConversations(convs.map((c: any) => ({
        id: c.conversation_id || c.id,
        user_email: c.user_email || '',
        question: c.question || '',
        answer: c.answer || '',
        provider: c.provider || '',
        model: c.model || '',
        tokens_used: c.tokens_used || 0,
        response_time_ms: c.response_time_ms || 0,
        rating: c.rating,
        is_helpful: c.is_helpful,
        user_feedback: c.user_feedback || null,
        is_good_example: c.is_good_example || false,
        is_bad_example: c.is_bad_example || false,
        admin_notes: c.admin_notes || null,
        created_at: c.created_at || '',
      })));
    } catch {
      setConversations([]);
    }
  };

  const handleUpdateSettings = async (updates: Partial<AISettings>) => {
    try {
      await adminApi.updateAISettings(token!, updates);
      setSettings(prev => prev ? { ...prev, ...updates } : null);
    } catch (error) {
      console.error('Failed to update settings:', error);
    }
  };

  const handleMarkExample = async (id: string, field: 'is_good_example' | 'is_bad_example', value: boolean) => {
    try {
      await adminApi.curateConversation(token!, String(id), { [field]: value });
      setConversations((prev) =>
        prev.map((c) => (c.id === id ? { ...c, [field]: value } : c))
      );
    } catch (error) {
      console.error('Failed to update conversation:', error);
    }
  };

  const handleSaveAdminNotes = async (id: string, admin_notes: string) => {
    try {
      await adminApi.curateConversation(token!, String(id), { admin_notes });
      setConversations((prev) =>
        prev.map((c) => (c.id === id ? { ...c, admin_notes } : c))
      );
    } catch (error) {
      console.error('Failed to save admin notes:', error);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  // Redirect non-admins
  if (user && user.role !== 'admin') {
    return (
      <PageLayout>
        <div className="max-w-2xl mx-auto text-center py-16">
          <div className="text-6xl mb-6">🔒</div>
          <h1 className="text-2xl font-bold text-frost mb-4">Access Denied</h1>
        </div>
      </PageLayout>
    );
  }

  const modeColors = {
    off: 'bg-error/20 text-error border-error/30',
    on: 'bg-success/20 text-success border-success/30',
    unlimited: 'bg-warning/20 text-warning border-warning/30',
  };

  const goodExamples = conversations.filter((c) => c.is_good_example);
  const badExamples = conversations.filter((c) => c.is_bad_example);

  return (
    <PageLayout>
      <div className="max-w-5xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">AI Settings</h1>
          <p className="text-frost-muted mt-1">Configure AI behavior, view conversations, and manage training data</p>
        </div>

        {/* Mode Toggle */}
        <div className="card mb-6">
          <h2 className="section-header">AI Mode</h2>
          <div className="flex gap-3">
            {(['off', 'on', 'unlimited'] as const).map((mode) => (
              <button
                key={mode}
                onClick={() => handleUpdateSettings({ mode })}
                className={`flex-1 p-4 rounded-lg border-2 transition-all ${
                  settings?.mode === mode
                    ? modeColors[mode]
                    : 'bg-surface border-surface-border text-frost-muted hover:border-frost-muted/50'
                }`}
              >
                <p className="font-bold text-lg uppercase">{mode}</p>
                <p className="text-xs mt-1 opacity-80">
                  {mode === 'off' && 'AI disabled, rules only'}
                  {mode === 'on' && 'AI enabled with rate limits'}
                  {mode === 'unlimited' && 'No rate limits (testing)'}
                </p>
              </button>
            ))}
          </div>
        </div>

        {/* Stats - 8 metrics */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="card text-center">
              <p className="text-2xl font-bold text-ice">{stats.total_requests}</p>
              <p className="text-xs text-frost-muted">Total Requests</p>
            </div>
            <div className="card text-center">
              <p className="text-2xl font-bold text-frost">{stats.total_tokens.toLocaleString()}</p>
              <p className="text-xs text-frost-muted">Total Tokens</p>
            </div>
            <div className="card text-center">
              <p className="text-2xl font-bold text-purple-400">{stats.total_conversations}</p>
              <p className="text-xs text-frost-muted">Conversations</p>
            </div>
            <div className="card text-center">
              <p className="text-2xl font-bold text-warning">
                {stats.avg_rating !== null ? stats.avg_rating.toFixed(1) : '--'}
              </p>
              <p className="text-xs text-frost-muted">Avg Rating</p>
            </div>
            <div className="card text-center">
              <p className="text-2xl font-bold text-success">{stats.good_examples}</p>
              <p className="text-xs text-frost-muted">Good Examples</p>
            </div>
            <div className="card text-center">
              <p className="text-2xl font-bold text-error">{stats.bad_examples}</p>
              <p className="text-xs text-frost-muted">Bad Examples</p>
            </div>
            <div className="card text-center">
              <p className="text-2xl font-bold text-success">{stats.helpful_count}</p>
              <p className="text-xs text-frost-muted">Helpful</p>
            </div>
            <div className="card text-center">
              <p className="text-2xl font-bold text-error">{stats.not_helpful_count}</p>
              <p className="text-xs text-frost-muted">Not Helpful</p>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-surface-border pb-2">
          {[
            { id: 'settings' as const, label: 'Settings' },
            { id: 'conversations' as const, label: 'Conversations' },
            { id: 'training' as const, label: 'Training Data' },
            { id: 'export' as const, label: 'Export' },
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

        {/* Content */}
        {activeTab === 'settings' && (
          <SettingsTab settings={settings} onUpdate={handleUpdateSettings} isLoading={isLoading} />
        )}
        {activeTab === 'conversations' && (
          <ConversationsTab
            conversations={conversations}
            formatDate={formatDate}
            isLoading={isLoading}
            onMarkExample={handleMarkExample}
            onSaveAdminNotes={handleSaveAdminNotes}
            ratingFilter={ratingFilter}
            setRatingFilter={setRatingFilter}
            curationFilter={curationFilter}
            setCurationFilter={setCurationFilter}
            resultLimit={resultLimit}
            setResultLimit={setResultLimit}
          />
        )}
        {activeTab === 'training' && (
          <TrainingDataTab
            goodExamples={goodExamples}
            badExamples={badExamples}
            allConversations={conversations}
            formatDate={formatDate}
            onMarkExample={handleMarkExample}
          />
        )}
        {activeTab === 'export' && (
          <ExportTab
            token={token!}
            goodExamplesCount={goodExamples.length}
            badExamplesCount={badExamples.length}
            totalCount={conversations.length}
          />
        )}
      </div>
    </PageLayout>
  );
}

function SettingsTab({
  settings,
  onUpdate,
  isLoading,
}: {
  settings: AISettings | null;
  onUpdate: (updates: Partial<AISettings>) => void;
  isLoading: boolean;
}) {
  const [localLimits, setLocalLimits] = useState({
    daily_limit_free: '',
    daily_limit_admin: '',
    cooldown_seconds: '',
    primary_model: '',
    fallback_model: '',
  });
  const [initialized, setInitialized] = useState(false);

  // Sync local state when settings load
  useEffect(() => {
    if (settings && !initialized) {
      setLocalLimits({
        daily_limit_free: String(settings.daily_limit_free),
        daily_limit_admin: String(settings.daily_limit_admin),
        cooldown_seconds: String(settings.cooldown_seconds),
        primary_model: settings.primary_model,
        fallback_model: settings.fallback_model,
      });
      setInitialized(true);
    }
  }, [settings, initialized]);

  const handleBlur = (field: keyof AISettings, value: string) => {
    if (field === 'primary_model' || field === 'fallback_model') {
      if (value !== (settings as any)?.[field]) {
        onUpdate({ [field]: value });
      }
    } else {
      const numValue = parseInt(value) || 0;
      if (numValue !== (settings as any)?.[field]) {
        onUpdate({ [field]: numValue });
      }
    }
  };

  if (isLoading || !settings) {
    return (
      <div className="card animate-pulse">
        <div className="space-y-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-12 bg-surface-hover rounded" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Provider Settings */}
      <div className="card">
        <h3 className="section-header">Provider Configuration</h3>
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-frost-muted mb-2">Primary Provider</label>
            <select
              value={settings.primary_provider}
              onChange={(e) => onUpdate({ primary_provider: e.target.value })}
              className="input"
            >
              <option value="anthropic">Anthropic (Claude)</option>
              <option value="openai">OpenAI (GPT)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-frost-muted mb-2">Primary Model</label>
            <input
              type="text"
              value={localLimits.primary_model}
              onChange={(e) => setLocalLimits(prev => ({ ...prev, primary_model: e.target.value }))}
              onBlur={(e) => handleBlur('primary_model', e.target.value)}
              className="input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-frost-muted mb-2">Fallback Provider</label>
            <select
              value={settings.fallback_provider}
              onChange={(e) => onUpdate({ fallback_provider: e.target.value })}
              className="input"
            >
              <option value="openai">OpenAI (GPT)</option>
              <option value="anthropic">Anthropic (Claude)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-frost-muted mb-2">Fallback Model</label>
            <input
              type="text"
              value={localLimits.fallback_model}
              onChange={(e) => setLocalLimits(prev => ({ ...prev, fallback_model: e.target.value }))}
              onBlur={(e) => handleBlur('fallback_model', e.target.value)}
              className="input"
            />
          </div>
        </div>
      </div>

      {/* Rate Limits */}
      <div className="card">
        <h3 className="section-header">Rate Limits</h3>
        <p className="text-sm text-frost-muted mb-4">
          These limits control how many AI-powered questions users can ask per day.
          Questions handled by the rules engine (92%+) don&apos;t count against limits.
          Per-user limits can be customized in Admin &rarr; Users.
        </p>
        <div className="grid md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-frost-muted mb-2">Daily Limit (Free Users)</label>
            <input
              type="number"
              value={localLimits.daily_limit_free}
              onChange={(e) => setLocalLimits(prev => ({ ...prev, daily_limit_free: e.target.value }))}
              onBlur={(e) => handleBlur('daily_limit_free', e.target.value)}
              className="input"
              min={0}
            />
            <p className="text-xs text-frost-muted mt-1">AI questions per day for regular users</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-frost-muted mb-2">Daily Limit (Admin)</label>
            <input
              type="number"
              value={localLimits.daily_limit_admin}
              onChange={(e) => setLocalLimits(prev => ({ ...prev, daily_limit_admin: e.target.value }))}
              onBlur={(e) => handleBlur('daily_limit_admin', e.target.value)}
              className="input"
              min={0}
            />
            <p className="text-xs text-frost-muted mt-1">AI questions per day for admin users</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-frost-muted mb-2">Cooldown (seconds)</label>
            <input
              type="number"
              value={localLimits.cooldown_seconds}
              onChange={(e) => setLocalLimits(prev => ({ ...prev, cooldown_seconds: e.target.value }))}
              onBlur={(e) => handleBlur('cooldown_seconds', e.target.value)}
              className="input"
              min={0}
            />
            <p className="text-xs text-frost-muted mt-1">Minimum wait between AI requests</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function ConversationsTab({
  conversations,
  formatDate,
  isLoading,
  onMarkExample,
  onSaveAdminNotes,
  ratingFilter,
  setRatingFilter,
  curationFilter,
  setCurationFilter,
  resultLimit,
  setResultLimit,
}: {
  conversations: AIConversation[];
  formatDate: (date: string) => string;
  isLoading: boolean;
  onMarkExample: (id: string, field: 'is_good_example' | 'is_bad_example', value: boolean) => void;
  onSaveAdminNotes: (id: string, notes: string) => void;
  ratingFilter: 'all' | 'rated' | 'unrated';
  setRatingFilter: (v: 'all' | 'rated' | 'unrated') => void;
  curationFilter: 'all' | 'good' | 'bad';
  setCurationFilter: (v: 'all' | 'good' | 'bad') => void;
  resultLimit: number;
  setResultLimit: (v: number) => void;
}) {
  const [selected, setSelected] = useState<AIConversation | null>(null);
  const [notesInput, setNotesInput] = useState('');

  const handleSelectConversation = (conv: AIConversation) => {
    setSelected(conv);
    setNotesInput(conv.admin_notes || '');
  };

  if (isLoading) {
    return (
      <div className="card animate-pulse">
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-surface-hover rounded" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Filters */}
      <div className="card mb-4">
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="block text-xs font-medium text-frost-muted mb-1">Rating</label>
            <select value={ratingFilter} onChange={(e) => setRatingFilter(e.target.value as any)} className="input text-sm py-1.5">
              <option value="all">All</option>
              <option value="rated">Rated</option>
              <option value="unrated">Unrated</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-frost-muted mb-1">Curation</label>
            <select value={curationFilter} onChange={(e) => setCurationFilter(e.target.value as any)} className="input text-sm py-1.5">
              <option value="all">All</option>
              <option value="good">Good Examples</option>
              <option value="bad">Bad Examples</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-frost-muted mb-1">Limit</label>
            <select value={resultLimit} onChange={(e) => setResultLimit(Number(e.target.value))} className="input text-sm py-1.5">
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
              <option value={200}>200</option>
            </select>
          </div>
          <div className="text-sm text-frost-muted pb-1.5">
            Showing {conversations.length} conversation{conversations.length !== 1 ? 's' : ''}
          </div>
        </div>
      </div>

      {conversations.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-4xl mb-4">&#x1F4AC;</div>
          <p className="text-frost-muted">No AI conversations match these filters</p>
        </div>
      ) : (
        <div className="card">
          <div className="space-y-3">
            {conversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => handleSelectConversation(conv)}
                className="w-full p-4 rounded-lg bg-surface hover:bg-surface-hover transition-colors text-left"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="text-frost truncate">{conv.question}</p>
                      {conv.is_good_example && <span className="text-success text-xs font-medium">Good</span>}
                      {conv.is_bad_example && <span className="text-error text-xs font-medium">Bad</span>}
                    </div>
                    <div className="flex items-center gap-3 mt-2 text-xs text-frost-muted">
                      <span>{conv.user_email}</span>
                      <span>&middot;</span>
                      <span>{conv.provider}/{conv.model}</span>
                      <span>&middot;</span>
                      <span>{conv.tokens_used} tokens</span>
                      <span>&middot;</span>
                      <span>{conv.response_time_ms}ms</span>
                      {conv.rating !== null && (
                        <>
                          <span>&middot;</span>
                          <span className="text-warning">{conv.rating}/5</span>
                        </>
                      )}
                      {conv.is_helpful !== null && (
                        <>
                          <span>&middot;</span>
                          <span>{conv.is_helpful ? 'Helpful' : 'Not Helpful'}</span>
                        </>
                      )}
                    </div>
                  </div>
                  <span className="text-xs text-frost-muted">{formatDate(conv.created_at)}</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {selected && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-surface rounded-xl border border-surface-border max-w-2xl w-full p-6 animate-fadeIn max-h-[80vh] overflow-y-auto">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-xl font-bold text-frost">Conversation</h2>
                <p className="text-sm text-frost-muted">{formatDate(selected.created_at)}</p>
              </div>
              <button onClick={() => setSelected(null)} className="text-frost-muted hover:text-frost text-xl">
                &times;
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-xs text-frost-muted uppercase tracking-wide">Question</label>
                <p className="text-frost mt-1 p-3 rounded-lg bg-ice/10">{selected.question}</p>
              </div>

              <div>
                <label className="text-xs text-frost-muted uppercase tracking-wide">Answer</label>
                <p className="text-frost mt-1 p-3 rounded-lg bg-surface-hover whitespace-pre-wrap">
                  {selected.answer}
                </p>
              </div>

              <div className="grid grid-cols-4 gap-4 text-center">
                <div>
                  <p className="text-lg font-bold text-frost">{selected.provider}</p>
                  <p className="text-xs text-frost-muted">Provider</p>
                </div>
                <div>
                  <p className="text-lg font-bold text-frost">{selected.tokens_used}</p>
                  <p className="text-xs text-frost-muted">Tokens</p>
                </div>
                <div>
                  <p className="text-lg font-bold text-frost">{selected.response_time_ms}ms</p>
                  <p className="text-xs text-frost-muted">Response Time</p>
                </div>
                <div>
                  <p className="text-lg font-bold text-frost">
                    {selected.rating !== null ? `${selected.rating}/5` : '--'}
                  </p>
                  <p className="text-xs text-frost-muted">Rating</p>
                </div>
              </div>

              {/* User Feedback */}
              <div className="p-3 rounded-lg bg-surface border border-surface-border">
                <label className="text-xs text-frost-muted uppercase tracking-wide">User Feedback</label>
                <div className="flex items-center gap-3 mt-2">
                  <span className="text-sm text-frost">
                    {selected.is_helpful === true
                      ? 'Marked as helpful'
                      : selected.is_helpful === false
                        ? 'Marked as not helpful'
                        : 'No feedback'}
                  </span>
                  {selected.user_feedback && (
                    <span className="text-sm text-frost-muted italic">&mdash; &quot;{selected.user_feedback}&quot;</span>
                  )}
                </div>
              </div>

              {/* Admin Notes */}
              <div>
                <label className="text-xs text-frost-muted uppercase tracking-wide">Admin Notes</label>
                <div className="flex gap-2 mt-1">
                  <input
                    type="text"
                    value={notesInput}
                    onChange={(e) => setNotesInput(e.target.value)}
                    placeholder="Add admin notes..."
                    className="input flex-1 text-sm"
                  />
                  <button
                    onClick={() => {
                      onSaveAdminNotes(selected.id, notesInput);
                      setSelected({ ...selected, admin_notes: notesInput });
                    }}
                    className="btn-secondary text-sm"
                  >
                    Save
                  </button>
                </div>
              </div>

              {/* Training Data Actions */}
              <div className="flex gap-3 pt-4 border-t border-surface-border">
                <button
                  onClick={() => {
                    onMarkExample(selected.id, 'is_good_example', !selected.is_good_example);
                    setSelected({ ...selected, is_good_example: !selected.is_good_example });
                  }}
                  className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                    selected.is_good_example
                      ? 'bg-success/20 text-success'
                      : 'bg-surface hover:bg-surface-hover text-frost-muted'
                  }`}
                >
                  {selected.is_good_example ? 'Good Example' : 'Mark as Good'}
                </button>
                <button
                  onClick={() => {
                    onMarkExample(selected.id, 'is_bad_example', !selected.is_bad_example);
                    setSelected({ ...selected, is_bad_example: !selected.is_bad_example });
                  }}
                  className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                    selected.is_bad_example
                      ? 'bg-error/20 text-error'
                      : 'bg-surface hover:bg-surface-hover text-frost-muted'
                  }`}
                >
                  {selected.is_bad_example ? 'Bad Example' : 'Mark as Bad'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

function TrainingDataTab({
  goodExamples,
  badExamples,
  allConversations,
  formatDate,
  onMarkExample,
}: {
  goodExamples: AIConversation[];
  badExamples: AIConversation[];
  allConversations: AIConversation[];
  formatDate: (date: string) => string;
  onMarkExample: (id: string, field: 'is_good_example' | 'is_bad_example', value: boolean) => void;
}) {
  const [subTab, setSubTab] = useState<'good' | 'bad' | 'preview'>('good');

  const examples = subTab === 'good' ? goodExamples : subTab === 'bad' ? badExamples : [];
  const previewData = goodExamples.slice(0, 10);

  return (
    <div className="space-y-6">
      <div className="card">
        <h3 className="section-header">Training Data Overview</h3>
        <div className="grid md:grid-cols-3 gap-4">
          <button
            onClick={() => setSubTab('good')}
            className={`p-4 rounded-lg border-2 text-left transition-all ${
              subTab === 'good'
                ? 'bg-success/10 border-success/30'
                : 'bg-surface border-surface-border hover:border-frost-muted/50'
            }`}
          >
            <p className="text-2xl font-bold text-success">{goodExamples.length}</p>
            <p className="text-sm text-frost-muted">Good Examples</p>
            <p className="text-xs text-frost-muted mt-1">High quality Q&amp;A pairs for fine-tuning</p>
          </button>
          <button
            onClick={() => setSubTab('bad')}
            className={`p-4 rounded-lg border-2 text-left transition-all ${
              subTab === 'bad'
                ? 'bg-error/10 border-error/30'
                : 'bg-surface border-surface-border hover:border-frost-muted/50'
            }`}
          >
            <p className="text-2xl font-bold text-error">{badExamples.length}</p>
            <p className="text-sm text-frost-muted">Bad Examples</p>
            <p className="text-xs text-frost-muted mt-1">Examples to avoid in training</p>
          </button>
          <button
            onClick={() => setSubTab('preview')}
            className={`p-4 rounded-lg border-2 text-left transition-all ${
              subTab === 'preview'
                ? 'bg-ice/10 border-ice/30'
                : 'bg-surface border-surface-border hover:border-frost-muted/50'
            }`}
          >
            <p className="text-2xl font-bold text-ice">{previewData.length}</p>
            <p className="text-sm text-frost-muted">Training Preview</p>
            <p className="text-xs text-frost-muted mt-1">Sample Q&amp;A pairs from good examples</p>
          </button>
        </div>
      </div>

      {subTab === 'preview' ? (
        <div className="card">
          <h3 className="section-header">Training Data Preview (Top 10 Good Examples)</h3>
          {previewData.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-frost-muted">No good examples to preview. Mark conversations as good examples first.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {previewData.map((ex, idx) => (
                <div key={ex.id} className="p-4 rounded-lg bg-surface border border-surface-border">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-xs font-mono text-frost-muted bg-surface-hover px-2 py-0.5 rounded">
                      #{idx + 1}
                    </span>
                    <span className="text-xs text-frost-muted">{formatDate(ex.created_at)}</span>
                  </div>
                  <div className="space-y-2">
                    <div>
                      <span className="text-xs font-medium text-ice uppercase">Q:</span>
                      <p className="text-sm text-frost mt-0.5">{ex.question}</p>
                    </div>
                    <div>
                      <span className="text-xs font-medium text-success uppercase">A:</span>
                      <p className="text-sm text-frost-muted mt-0.5 line-clamp-4 whitespace-pre-wrap">{ex.answer}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="card">
          <h3 className="section-header">{subTab === 'good' ? 'Good' : 'Bad'} Examples</h3>
          {examples.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-frost-muted">
                No {subTab} examples marked yet. Browse conversations and mark examples.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {examples.map((ex) => (
                <div key={ex.id} className="p-4 rounded-lg bg-surface">
                  <div className="flex items-start justify-between gap-4 mb-2">
                    <p className="text-frost font-medium">{ex.question}</p>
                    <button
                      onClick={() =>
                        onMarkExample(ex.id, subTab === 'good' ? 'is_good_example' : 'is_bad_example', false)
                      }
                      className="text-xs text-frost-muted hover:text-error"
                    >
                      Remove
                    </button>
                  </div>
                  <p className="text-sm text-frost-muted line-clamp-2">{ex.answer}</p>
                  <div className="flex items-center gap-3 mt-2">
                    <p className="text-xs text-frost-muted">{formatDate(ex.created_at)}</p>
                    {ex.admin_notes && (
                      <p className="text-xs text-ice italic">Note: {ex.admin_notes}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ExportTab({
  token,
  goodExamplesCount,
  badExamplesCount,
  totalCount,
}: {
  token: string;
  goodExamplesCount: number;
  badExamplesCount: number;
  totalCount: number;
}) {
  const [isExporting, setIsExporting] = useState(false);
  const [exportFormat, setExportFormat] = useState<'jsonl' | 'csv'>('jsonl');
  const [exportFilter, setExportFilter] = useState<'all' | 'good' | 'bad'>('good');

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const res = await fetch(
        `${API_BASE}/api/admin/conversations/export?format=${exportFormat}&filter=${exportFilter}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ai_training_data_${exportFilter}.${exportFormat}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <h3 className="section-header">Export Training Data</h3>
        <p className="text-sm text-frost-muted mb-6">
          Export curated conversation data for fine-tuning or analysis.
        </p>

        <div className="grid md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-frost-muted mb-2">Export Format</label>
            <div className="flex gap-2">
              <button
                onClick={() => setExportFormat('jsonl')}
                className={`flex-1 p-3 rounded-lg text-sm font-medium transition-colors ${
                  exportFormat === 'jsonl'
                    ? 'bg-ice/20 text-ice'
                    : 'bg-surface text-frost-muted hover:bg-surface-hover'
                }`}
              >
                JSONL
                <p className="text-xs opacity-70 mt-1">For OpenAI/Claude fine-tuning</p>
              </button>
              <button
                onClick={() => setExportFormat('csv')}
                className={`flex-1 p-3 rounded-lg text-sm font-medium transition-colors ${
                  exportFormat === 'csv'
                    ? 'bg-ice/20 text-ice'
                    : 'bg-surface text-frost-muted hover:bg-surface-hover'
                }`}
              >
                CSV
                <p className="text-xs opacity-70 mt-1">For spreadsheet analysis</p>
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-frost-muted mb-2">Filter</label>
            <div className="flex gap-2">
              <button
                onClick={() => setExportFilter('good')}
                className={`flex-1 p-3 rounded-lg text-sm font-medium transition-colors ${
                  exportFilter === 'good'
                    ? 'bg-success/20 text-success'
                    : 'bg-surface text-frost-muted hover:bg-surface-hover'
                }`}
              >
                Good ({goodExamplesCount})
              </button>
              <button
                onClick={() => setExportFilter('bad')}
                className={`flex-1 p-3 rounded-lg text-sm font-medium transition-colors ${
                  exportFilter === 'bad'
                    ? 'bg-error/20 text-error'
                    : 'bg-surface text-frost-muted hover:bg-surface-hover'
                }`}
              >
                Bad ({badExamplesCount})
              </button>
              <button
                onClick={() => setExportFilter('all')}
                className={`flex-1 p-3 rounded-lg text-sm font-medium transition-colors ${
                  exportFilter === 'all'
                    ? 'bg-ice/20 text-ice'
                    : 'bg-surface text-frost-muted hover:bg-surface-hover'
                }`}
              >
                All ({totalCount})
              </button>
            </div>
          </div>
        </div>

        <button
          onClick={handleExport}
          disabled={isExporting}
          className="btn-primary w-full"
        >
          {isExporting ? 'Exporting...' : `Export ${exportFilter} examples as ${exportFormat.toUpperCase()}`}
        </button>
      </div>

      <div className="card border-ice/30 bg-ice/5">
        <h3 className="section-header">Fine-Tuning Tips</h3>
        <ul className="space-y-2 text-sm text-frost-muted">
          <li className="flex items-start gap-2">
            <span className="text-ice">&bull;</span>
            <span>Use JSONL format for OpenAI and Claude fine-tuning APIs</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-ice">&bull;</span>
            <span>Aim for at least 50 good examples for effective fine-tuning</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-ice">&bull;</span>
            <span>Review bad examples to understand common failure modes</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-ice">&bull;</span>
            <span>Include diverse question types for better generalization</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
