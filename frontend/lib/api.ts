/**
 * API client for Bear's Den backend
 * Connects to API Gateway (Lambda) with Cognito token auth
 */

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Debug: log API base on load
if (typeof window !== 'undefined') {
  console.log('[API] Base URL:', API_BASE);
}

interface ApiOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  body?: any;
  token?: string;
}

/**
 * Get the current Cognito ID token from localStorage.
 * Falls back to legacy 'token' key for backwards compatibility.
 */
export function getStoredToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('id_token') || localStorage.getItem('token') || null;
}

/**
 * Store Cognito tokens in localStorage.
 */
export function storeTokens(tokens: { id_token: string; access_token: string; refresh_token?: string }) {
  localStorage.setItem('id_token', tokens.id_token);
  localStorage.setItem('access_token', tokens.access_token);
  if (tokens.refresh_token) {
    localStorage.setItem('refresh_token', tokens.refresh_token);
  }
  // Also store as legacy 'token' for any code that still reads it
  localStorage.setItem('token', tokens.id_token);
}

/**
 * Clear all auth tokens from localStorage.
 */
export function clearTokens() {
  localStorage.removeItem('id_token');
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('token');
}

export async function api<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
  const { method = 'GET', body, token } = options;

  // Use provided token, or fall back to stored Cognito ID token
  const authToken = token || getStoredToken();

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    // On 401, try to refresh token using Cognito refresh_token and retry once
    if (response.status === 401 && authToken) {
      const newToken = await tryRefreshToken();
      if (newToken) {
        const retryHeaders: HeadersInit = {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${newToken}`,
        };
        const retryResponse = await fetch(`${API_BASE}${endpoint}`, {
          method,
          headers: retryHeaders,
          body: body ? JSON.stringify(body) : undefined,
        });
        if (retryResponse.ok) {
          return retryResponse.json();
        }
      }
    }
    const error = await response.json().catch(() => ({ message: 'Request failed' }));
    throw new Error(error.message || error.error || error.detail || 'Request failed');
  }

  return response.json();
}

async function tryRefreshToken(): Promise<string | null> {
  try {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) return null;

    // Call the backend refresh endpoint with the Cognito refresh token
    const res = await fetch(`${API_BASE}/api/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (res.ok) {
      const data = await res.json();
      storeTokens({
        id_token: data.id_token,
        access_token: data.access_token,
        refresh_token: data.refresh_token || refreshToken,
      });
      return data.id_token;
    }
  } catch {
    // Refresh failed
  }
  return null;
}

// Auth API - Cognito token-based authentication
export interface AuthResponse {
  id_token: string;
  access_token: string;
  refresh_token?: string;
  user: User;
}

export const authApi = {
  login: (email: string, password: string) =>
    api<AuthResponse>('/api/auth/login', {
      method: 'POST',
      body: { email, password },
    }),

  register: (email: string, password: string) =>
    api<AuthResponse>('/api/auth/register', {
      method: 'POST',
      body: { email, password },
    }),

  me: (token: string) =>
    api<User>('/api/auth/me', { token }),

  refresh: (refreshToken: string) =>
    api<AuthResponse>('/api/auth/refresh', {
      method: 'POST',
      body: { refresh_token: refreshToken },
    }),
};

// Heroes API
export const heroesApi = {
  getAll: (token: string, includeImages = false) =>
    api<{ heroes: Hero[] }>(`/api/heroes/all?include_images=${includeImages}`, { token }),

  getOwned: (token: string) =>
    api<{ heroes: UserHero[] }>('/api/heroes/owned?include_images=true', { token }),

  addHero: (token: string, heroName: string, data: Partial<UserHero> = {}) =>
    api<{ hero: UserHero }>(`/api/heroes/${encodeURIComponent(heroName)}`, { method: 'PUT', body: data, token }),

  updateHero: (token: string, heroName: string, data: Partial<UserHero>) =>
    api<{ hero: UserHero }>(`/api/heroes/${encodeURIComponent(heroName)}`, { method: 'PUT', body: data, token }),

  batchUpdate: (token: string, heroes: Partial<UserHero>[]) =>
    api<{ updated: number; heroes: UserHero[] }>('/api/heroes/batch', { method: 'PUT', body: { heroes }, token }),

  removeHero: (token: string, heroName: string) =>
    api<{ deleted: string }>(`/api/heroes/${encodeURIComponent(heroName)}`, { method: 'DELETE', token }),
};

// Profile API
export const profileApi = {
  list: (token: string) =>
    api<{ profiles: Profile[] }>('/api/profiles', { token }),

  get: (token: string, profileId: string) =>
    api<{ profile: Profile }>(`/api/profiles/${profileId}`, { token }),

  getCurrent: (token: string) =>
    api<{ profile: Profile }>('/api/profiles/current', { token }),

  getDeleted: (token: string) =>
    api<{ profiles: Profile[] }>('/api/profiles/deleted', { token }),

  create: (token: string, data: { name?: string; state_number?: number; is_farm_account?: boolean }) =>
    api<{ profile: Profile }>('/api/profiles', { method: 'POST', body: data, token }),

  update: (token: string, profileId: string, data: Partial<Profile>) =>
    api<{ profile: Profile }>(`/api/profiles/${profileId}`, { method: 'PUT', body: data, token }),

  delete: (token: string, profileId: string, hard = false) =>
    api(`/api/profiles/${profileId}?hard=${hard}`, { method: 'DELETE', token }),

  switch: (token: string, profileId: string) =>
    api(`/api/profiles/${profileId}/switch`, { method: 'POST', token }),

  duplicate: (token: string, profileId: string, name: string) =>
    api<{ profile: Profile }>(`/api/profiles/${profileId}/duplicate`, { method: 'POST', body: { name }, token }),

  restore: (token: string, profileId: string) =>
    api(`/api/profiles/${profileId}/restore`, { method: 'POST', token }),

  preview: (token: string, profileId: string) =>
    api<ProfilePreview>(`/api/profiles/${profileId}/preview`, { token }),
};

// Dashboard API
export const dashboardApi = {
  getStats: (token: string) =>
    api<DashboardStats>('/api/dashboard', { token }),
};

// Chief Gear & Charms API
export const chiefApi = {
  getGear: (token: string) =>
    api<{ gear: ChiefGear }>('/api/chief/gear', { token }),

  updateGear: (token: string, data: Partial<ChiefGear>) =>
    api<{ gear: ChiefGear }>('/api/chief/gear', { method: 'PUT', body: data, token }),

  getCharms: (token: string) =>
    api<{ charms: ChiefCharms }>('/api/chief/charms', { token }),

  updateCharms: (token: string, data: Partial<ChiefCharms>) =>
    api<{ charms: ChiefCharms }>('/api/chief/charms', { method: 'PUT', body: data, token }),
};

// Recommendations API
export const recommendationsApi = {
  get: (token: string) =>
    api<{ recommendations: Recommendation[] }>('/api/recommendations', { token }),

  getInvestments: (token: string) =>
    api<{ investments: Investment[] }>('/api/recommendations/investments', { token }),

  getPhase: (token: string) =>
    api<{ phase: PhaseInfo }>('/api/recommendations/phase', { token }),

  getGearPriority: (token: string) =>
    api<{ gear_priority: GearPriority[] }>('/api/recommendations/gear-priority', { token }),
};

// AI Advisor API
export const advisorApi = {
  ask: (token: string, question: string, threadId?: string) =>
    api<AdvisorResponse>('/api/advisor/ask', {
      method: 'POST',
      body: { question, thread_id: threadId },
      token,
    }),

  getHistory: (token: string, limit = 10) =>
    api<{ conversations: Conversation[] }>(`/api/advisor/history?limit=${limit}`, { token }),

  rate: (token: string, conversationSk: string, data: { rating?: number; is_helpful?: boolean; user_feedback?: string; is_favorite?: boolean }) =>
    api<{ conversation: Conversation }>('/api/advisor/rate', {
      method: 'POST',
      body: { conversation_sk: conversationSk, ...data },
      token,
    }),

  getThreads: (token: string, limit = 10) =>
    api<{ threads: any[] }>(`/api/advisor/threads?limit=${limit}`, { token }),

  getThreadMessages: (token: string, threadId: string) =>
    api<{ thread_id: string; messages: Conversation[] }>(`/api/advisor/threads/${threadId}`, { token }),

  getFavorites: (token: string, limit = 20) =>
    api<{ favorites: Conversation[] }>(`/api/advisor/favorites?limit=${limit}`, { token }),

  toggleFavorite: (token: string, convSk: string) =>
    api<{ is_favorite: boolean }>(`/api/advisor/favorite/${convSk}`, { method: 'POST', token }),

  getStatus: (token: string) =>
    api<AdvisorStatus>('/api/advisor/status', { token }),
};

// Lineups API
export const lineupsApi = {
  getAll: (token: string) =>
    api<{ lineups: Record<string, any>; owned_heroes: number; hero_count: number }>('/api/lineups', { token }),

  getForEvent: (token: string, eventType: string) =>
    api<{ event_type: string; lineup: any; owned_heroes: string[] }>(`/api/lineups/${eventType}`, { token }),

  getTemplates: () =>
    api<Record<string, LineupTemplate>>('/api/lineups/templates'),

  getTemplate: (gameMode: string) =>
    api<LineupTemplate>(`/api/lineups/template/${gameMode}`),

  buildForMode: (token: string, gameMode: string) =>
    api<LineupResponse>(`/api/lineups/build/${gameMode}`, { token }),

  buildAll: (token: string) =>
    api<{ lineups: Record<string, LineupResponse> }>('/api/lineups/build-all', { token }),

  getGeneral: (gameMode: string, maxGeneration = 14) =>
    api<LineupResponse>(`/api/lineups/general/${gameMode}?max_generation=${maxGeneration}`),

  getJoiner: (token: string, attackType: string) =>
    api<JoinerRecommendation>(`/api/lineups/joiner/${attackType}`, { token }),
};

// Admin API
export const adminApi = {
  // Users
  listUsers: (token: string, limit = 50, testOnly = false) =>
    api<{ users: AdminUser[] }>(`/api/admin/users?limit=${limit}&test_only=${testOnly}`, { token }),

  getUser: (token: string, userId: string) =>
    api<{ user: AdminUser; profiles: Profile[] }>(`/api/admin/users/${userId}`, { token }),

  createUser: (token: string, data: CreateUserRequest) =>
    api<{ user: AdminUser }>('/api/admin/users', { method: 'POST', body: data, token }),

  updateUser: (token: string, userId: string, data: UpdateUserRequest) =>
    api<{ user: AdminUser }>(`/api/admin/users/${userId}`, { method: 'PUT', body: data, token }),

  deleteUser: (token: string, userId: string) =>
    api(`/api/admin/users/${userId}`, { method: 'DELETE', token }),

  // Announcements
  listAnnouncements: (token: string) =>
    api<{ announcements: Announcement[] }>('/api/admin/announcements', { token }),

  createAnnouncement: (token: string, data: CreateAnnouncementRequest) =>
    api<{ announcement: Announcement }>('/api/admin/announcements', { method: 'POST', body: data, token }),

  updateAnnouncement: (token: string, id: string, data: Partial<Announcement>) =>
    api<{ announcement: Announcement }>(`/api/admin/announcements/${id}`, { method: 'PUT', body: data, token }),

  deleteAnnouncement: (token: string, id: string) =>
    api(`/api/admin/announcements/${id}`, { method: 'DELETE', token }),

  // Feature Flags
  listFeatureFlags: (token: string) =>
    api<{ flags: FeatureFlag[] }>('/api/admin/flags', { token }),

  updateFeatureFlag: (token: string, name: string, data: { is_enabled?: boolean; description?: string }) =>
    api<{ flag: FeatureFlag }>(`/api/admin/flags/${name}`, { method: 'PUT', body: data, token }),

  // AI Settings
  getAISettings: (token: string) =>
    api<{ settings: AISettings }>('/api/admin/ai-settings', { token }),

  updateAISettings: (token: string, data: Partial<AISettings>) =>
    api<{ settings: AISettings }>('/api/admin/ai-settings', { method: 'PUT', body: data, token }),

  // Metrics
  getMetrics: (token: string) =>
    api<AdminStats>('/api/admin/metrics', { token }),

  // Audit Log
  getAuditLog: (token: string, month?: string, limit = 100) => {
    const params = new URLSearchParams();
    if (month) params.append('month', month);
    params.append('limit', String(limit));
    return api<{ logs: any[] }>(`/api/admin/audit-log?${params}`, { token });
  },

  // Feedback
  listFeedback: (token: string, status?: string, category?: string) => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (category) params.append('category', category);
    return api<{ feedback: FeedbackItem[] }>(`/api/admin/feedback?${params}`, { token });
  },

  updateFeedback: (token: string, feedbackId: string, data: { status?: string; admin_notes?: string }) =>
    api<{ feedback: FeedbackItem }>(`/api/admin/feedback/${feedbackId}`, { method: 'PUT', body: data, token }),

  // AI Conversations (admin view)
  listAIConversations: (token: string, limit = 50) =>
    api<{ conversations: Conversation[] }>(`/api/admin/ai-conversations?limit=${limit}`, { token }),

  // Database Browser
  listTables: (token: string) =>
    api<{ tables: { name: string; alias: string }[] }>('/api/admin/database/tables', { token }),

  scanTable: (token: string, tableName: string, limit = 25) =>
    api<{ table: string; items: any[]; count: number }>(`/api/admin/database/tables/${tableName}?limit=${limit}`, { token }),

  // Export
  exportData: (token: string, format: 'json' | 'csv', table = 'main') =>
    api<any>(`/api/admin/export/${format}?table=${table}`, { token }),

  // Impersonation
  impersonateUser: (token: string, userId: string) =>
    api<{ user: User; profiles: Profile[]; impersonating: boolean }>(`/api/admin/impersonate/${userId}`, { method: 'POST', token }),

  // Stats (richer than metrics)
  getStats: (token: string) =>
    api<any>('/api/admin/stats', { token }),

  // Usage Reports
  getUsageStats: (token: string, range = '7d') =>
    api<any>(`/api/admin/usage/stats?range=${range}`, { token }),

  // Feature Flags (additional)
  createFeatureFlag: (token: string, data: { name: string; description?: string; is_enabled?: boolean }) =>
    api<{ flag: FeatureFlag }>('/api/admin/flags', { method: 'POST', body: data, token }),

  deleteFeatureFlag: (token: string, name: string) =>
    api('/api/admin/flags/' + name, { method: 'DELETE', token }),

  bulkFlagAction: (token: string, action: string) =>
    api('/api/admin/flags/bulk', { method: 'POST', body: { action }, token }),

  // Errors
  getErrors: (token: string) =>
    api<{ errors: any[] }>('/api/admin/errors', { token }),

  resolveError: (token: string, errorId: string) =>
    api('/api/admin/errors/' + errorId + '/resolve', { method: 'POST', token }),

  // Admin Conversations
  getConversations: (token: string, params: Record<string, string> = {}) => {
    const qs = new URLSearchParams(params);
    return api<{ conversations: Conversation[] }>(`/api/admin/conversations?${qs}`, { token });
  },

  curateConversation: (token: string, id: string, data: { is_good_example?: boolean; is_bad_example?: boolean; admin_notes?: string }) =>
    api(`/api/admin/conversations/${id}/curate`, { method: 'PUT', body: data, token }),

  getConversationStats: (token: string) =>
    api<ConversationStats>('/api/admin/conversations/stats', { token }),

  exportConversations: (token: string, format = 'jsonl', filter?: string) => {
    const params = new URLSearchParams({ format });
    if (filter) params.append('filter', filter);
    return api<any>(`/api/admin/conversations/export?${params}`, { token });
  },

  // Data Integrity
  checkDataIntegrity: (token: string) =>
    api<IntegrityCheck>('/api/admin/data-integrity/check', { token }),

  // Game Data
  getGameDataFiles: (token: string) =>
    api<{ files: DataFile[] }>('/api/admin/game-data/files', { token }),

  getGameDataFile: (token: string, path: string) =>
    api<{ path: string; content: any }>(`/api/admin/game-data/file?path=${encodeURIComponent(path)}`, { token }),

  // Database (additional)
  getBackups: (token: string) =>
    api<{ backups: any[] }>('/api/admin/database/backups', { token }),

  createBackup: (token: string) =>
    api('/api/admin/database/backup', { method: 'POST', token }),

  databaseCleanup: (token: string, action: string) =>
    api(`/api/admin/database/cleanup/${action}`, { method: 'POST', token }),

  databaseQuery: (token: string, query: string) =>
    api('/api/admin/database/query', { method: 'POST', body: { query }, token }),
};

// Inbox API
export const inboxApi = {
  getNotifications: (token: string) =>
    api<{ notifications: any[] }>('/api/inbox/notifications', { token }),

  markRead: (token: string, notificationId: string) =>
    api('/api/inbox/notifications/' + notificationId + '/read', { method: 'POST', token }),

  getUnreadCount: (token: string) =>
    api<{ unread_notifications: number; total_unread: number }>('/api/inbox/unread-count', { token }),

  getThreads: (token: string) =>
    api<{ threads: any[] }>('/api/inbox/threads', { token }),

  getThreadMessages: (token: string, threadId: string) =>
    api<{ messages: any[] }>(`/api/inbox/threads/${threadId}/messages`, { token }),

  replyToThread: (token: string, threadId: string, content: string) =>
    api(`/api/inbox/threads/${threadId}/reply`, { method: 'POST', body: { content }, token }),
};

// Feedback API
export const feedbackApi = {
  submit: (token: string, data: { category: string; description: string; page?: string }) =>
    api('/api/feedback', { method: 'POST', body: data, token }),
};

export const eventsApi = {
  getGuide: () =>
    api<any>('/api/events/guide'),
};

// Types
export interface User {
  id: string;
  email: string;
  username: string;
  role: string;
  is_active: boolean;
  is_test_account: boolean;
  created_at: string;
}

export interface Hero {
  name: string;
  generation: number;
  hero_class: string;
  rarity: string | null;
  tier_overall: string | null;
  tier_expedition: string | null;
  tier_exploration: string | null;
  image_filename: string | null;
  image_base64: string | null;
  // Additional info
  how_to_obtain: string | null;
  notes: string | null;
  best_use: string | null;
  // Skill names
  exploration_skill_1: string | null;
  exploration_skill_2: string | null;
  exploration_skill_3: string | null;
  expedition_skill_1: string | null;
  expedition_skill_2: string | null;
  expedition_skill_3: string | null;
  // Skill descriptions
  exploration_skill_1_desc: string | null;
  exploration_skill_2_desc: string | null;
  exploration_skill_3_desc: string | null;
  expedition_skill_1_desc: string | null;
  expedition_skill_2_desc: string | null;
  expedition_skill_3_desc: string | null;
  // Mythic gear
  mythic_gear: string | null;
}

export interface UserHero {
  hero_name: string;
  name: string;
  generation: number;
  hero_class: string;
  tier_overall: string | null;
  level: number;
  stars: number;
  ascension: number;
  // Skill levels
  exploration_skill_1: number;
  exploration_skill_2: number;
  exploration_skill_3: number;
  expedition_skill_1: number;
  expedition_skill_2: number;
  expedition_skill_3: number;
  // Skill names
  exploration_skill_1_name: string | null;
  exploration_skill_2_name: string | null;
  exploration_skill_3_name: string | null;
  expedition_skill_1_name: string | null;
  expedition_skill_2_name: string | null;
  expedition_skill_3_name: string | null;
  // Skill descriptions
  exploration_skill_1_desc: string | null;
  exploration_skill_2_desc: string | null;
  exploration_skill_3_desc: string | null;
  expedition_skill_1_desc: string | null;
  expedition_skill_2_desc: string | null;
  expedition_skill_3_desc: string | null;
  // Gear slots (4 slots)
  gear_slot1_quality: number;
  gear_slot1_level: number;
  gear_slot1_mastery: number;
  gear_slot2_quality: number;
  gear_slot2_level: number;
  gear_slot2_mastery: number;
  gear_slot3_quality: number;
  gear_slot3_level: number;
  gear_slot3_mastery: number;
  gear_slot4_quality: number;
  gear_slot4_level: number;
  gear_slot4_mastery: number;
  // Mythic gear
  mythic_gear_name: string | null;
  mythic_gear_unlocked: boolean;
  mythic_gear_quality: number;
  mythic_gear_level: number;
  mythic_gear_mastery: number;
  exclusive_gear_skill_level: number;
  // Image
  image_base64: string | null;
}

export interface Profile {
  profile_id: string;
  user_id: string;
  name: string | null;
  state_number: number | null;
  server_age_days: number;
  furnace_level: number;
  furnace_fc_level: string | null;
  spending_profile: string;
  priority_focus: string;
  alliance_role: string;
  priority_svs: number;
  priority_rally: number;
  priority_castle_battle: number;
  priority_exploration: number;
  priority_gathering: number;
  is_farm_account: boolean;
  is_active: boolean;
  created_at: string;
}

export interface DashboardStats {
  generation: number;
  server_age_days: number;
  furnace_display: string;
  owned_heroes: number;
  total_heroes: number;
  username: string;
  profile: Profile;
  hero_count: number;
  profile_count: number;
  furnace_level: number;
  spending_profile: string;
  announcements: Announcement[];
}

// Chief Gear & Charms Types
export interface ChiefGear {
  helmet_quality: number;
  helmet_level: number;
  armor_quality: number;
  armor_level: number;
  gloves_quality: number;
  gloves_level: number;
  boots_quality: number;
  boots_level: number;
  ring_quality: number;
  ring_level: number;
  amulet_quality: number;
  amulet_level: number;
}

export interface ChiefCharms {
  cap_slot_1: string;
  cap_slot_2: string;
  cap_slot_3: string;
  watch_slot_1: string;
  watch_slot_2: string;
  watch_slot_3: string;
  coat_slot_1: string;
  coat_slot_2: string;
  coat_slot_3: string;
  pants_slot_1: string;
  pants_slot_2: string;
  pants_slot_3: string;
  belt_slot_1: string;
  belt_slot_2: string;
  belt_slot_3: string;
  weapon_slot_1: string;
  weapon_slot_2: string;
  weapon_slot_3: string;
}

// Recommendations Types
export interface Recommendation {
  priority: number;
  action: string;
  category: string;
  hero: string | null;
  reason: string;
  resources: string;
  relevance_tags: string[];
  source: string;
}

export interface Investment {
  hero: string;
  hero_class: string;
  tier: string;
  generation: number;
  current_level: number;
  target_level: number;
  current_stars: number;
  target_stars: number;
  reason: string;
  priority: number;
}

// AI Advisor Types
export interface AdvisorResponse {
  answer: string;
  source: string;
  conversation_id: string | null;
  thread_id: string | null;
  remaining_requests: number;
}

export interface Conversation {
  conversation_id: string;
  question: string;
  answer: string;
  source: string;
  provider: string | null;
  model: string | null;
  created_at: string;
  rating: number | null;
  is_helpful: boolean | null;
  user_feedback: string | null;
  is_favorite: boolean;
  thread_id: string | null;
}

// Admin Types
export interface AdminUser {
  user_id: string;
  email: string;
  username: string;
  role: string;
  is_active: boolean;
  is_test_account: boolean;
  created_at: string;
  last_login: string | null;
}

export interface CreateUserRequest {
  email: string;
  password: string;
  role?: string;
  is_test_account?: boolean;
}

export interface UpdateUserRequest {
  email?: string;
  role?: string;
  is_active?: boolean;
  is_test_account?: boolean;
}

export interface Announcement {
  announcement_id: string;
  title: string;
  message: string;
  type: string;
  is_active: boolean;
  display_type: string;
  inbox_content: string | null;
  show_from: string | null;
  show_until: string | null;
  created_at: string;
}

export interface CreateAnnouncementRequest {
  title: string;
  message: string;
  type?: string;
  display_type?: string;
  inbox_content?: string;
  show_from?: string;
  show_until?: string;
}

export interface FeatureFlag {
  flag_name: string;
  is_enabled: boolean;
  description: string | null;
}

export interface AISettings {
  mode: string;
  daily_limit_free: number;
  daily_limit_admin: number;
  cooldown_seconds: number;
  primary_provider: string;
  primary_model: string;
}

export interface AdminStats {
  users: {
    total: number;
    active: number;
    test: number;
  };
  profiles: number;
  conversations: {
    total: number;
    ai: number;
    rules: number;
    ai_percentage: number;
  };
  feedback_pending: number;
}

export interface FeedbackItem {
  feedback_id: string;
  user_id: string;
  category: string;
  description: string;
  page: string | null;
  status: string;
  admin_notes: string | null;
  created_at: string;
}

// Profile Preview
export interface ProfilePreview {
  profile: Profile;
  heroes: Array<{
    name: string;
    level: number;
    stars: number;
    generation: number;
    hero_class: string;
  }>;
}

// Phase & Gear
export interface PhaseInfo {
  name: string;
  furnace_level: number;
}

export interface GearPriority {
  gear: string;
  priority: number;
  reason: string;
}

// Advisor Status
export interface AdvisorStatus {
  ai_enabled: boolean;
  mode: string;
  daily_limit: number;
  requests_today: number;
  requests_remaining: number;
  primary_provider: string;
}

// Lineup Types
export interface LineupHero {
  hero: string;
  hero_class: string;
  slot: string;
  role: string;
  is_lead: boolean;
  status: string;
  power: number;
}

export interface LineupResponse {
  game_mode: string;
  heroes: LineupHero[];
  troop_ratio: { infantry: number; lancer: number; marksman: number };
  notes: string;
  confidence: string;
  recommended_to_get: Array<{ hero: string; reason: string }>;
}

export interface LineupTemplate {
  name: string;
  troop_ratio: { infantry: number; lancer: number; marksman: number };
  notes: string;
  key_heroes: string[];
  ratio_explanation: string;
  hero_explanations?: Record<string, string>;
}

export interface JoinerRecommendation {
  hero: string | null;
  status: string;
  skill_level: number | null;
  max_skill: number;
  recommendation: string;
  action: string;
  critical_note: string;
}

// Admin Types (additional)
export interface ConversationStats {
  total: number;
  ai: number;
  rules: number;
  ai_percentage: number;
  rated: number;
  helpful: number;
  good_examples: number;
  bad_examples: number;
}

export interface DataFile {
  path: string;
  name: string;
  size_bytes: number;
}

export interface IntegrityCheck {
  checks: Array<{
    file: string;
    exists: boolean;
    valid_json: boolean;
    size_bytes: number;
  }>;
  total: number;
  passing: number;
}
