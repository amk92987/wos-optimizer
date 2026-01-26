/**
 * API client for Bear's Den backend
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Debug: log API base on load
if (typeof window !== 'undefined') {
  console.log('[API] Base URL:', API_BASE);
}

interface ApiOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  body?: any;
  token?: string;
}

export async function api<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
  const { method = 'GET', body, token } = options;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
}

// Auth API
export const authApi = {
  login: (email: string, password: string) =>
    api<{ access_token: string; user: User }>('/api/auth/login', {
      method: 'POST',
      body: { email, password },
    }),

  register: (email: string, password: string) =>
    api<{ access_token: string; user: User }>('/api/auth/register', {
      method: 'POST',
      body: { email, password },
    }),

  me: (token: string) =>
    api<User>('/api/auth/me', { token }),
};

// Heroes API
export const heroesApi = {
  getAll: (token: string, includeImages = false) =>
    api<Hero[]>(`/api/heroes/all?include_images=${includeImages}`, { token }),

  getOwned: (token: string) =>
    api<UserHero[]>('/api/heroes/owned?include_images=true', { token }),

  addHero: (token: string, heroId: number) =>
    api('/api/heroes/own/' + heroId, { method: 'POST', token }),

  updateHero: (token: string, heroId: number, data: Partial<UserHero>) =>
    api('/api/heroes/update/' + heroId, { method: 'PUT', body: data, token }),

  removeHero: (token: string, heroId: number) =>
    api('/api/heroes/remove/' + heroId, { method: 'DELETE', token }),
};

// Profile API
export const profileApi = {
  getCurrent: (token: string) =>
    api<Profile>('/api/profiles/current', { token }),

  update: (token: string, data: Partial<Profile>) =>
    api<Profile>('/api/profiles/update', { method: 'PUT', body: data, token }),
};

// Dashboard API
export const dashboardApi = {
  getStats: (token: string) =>
    api<DashboardStats>('/api/dashboard/stats', { token }),
};

// Chief Gear & Charms API
export const chiefApi = {
  getGear: (token: string) =>
    api<ChiefGear>('/api/chief/gear', { token }),

  updateGear: (token: string, data: Partial<ChiefGear>) =>
    api<ChiefGear>('/api/chief/gear', { method: 'PUT', body: data, token }),

  getCharms: (token: string) =>
    api<ChiefCharms>('/api/chief/charms', { token }),

  updateCharms: (token: string, data: Partial<ChiefCharms>) =>
    api<ChiefCharms>('/api/chief/charms', { method: 'PUT', body: data, token }),
};

// Recommendations API
export const recommendationsApi = {
  get: (token: string, limit = 10, includePower = true) =>
    api<Recommendation[]>(`/api/recommendations/?limit=${limit}&include_power=${includePower}`, { token }),

  getInvestments: (token: string, limit = 10) =>
    api<Investment[]>(`/api/recommendations/investments?limit=${limit}`, { token }),

  getPhase: (token: string) =>
    api<PhaseInfo>('/api/recommendations/phase', { token }),

  getGearPriority: (token: string) =>
    api<GearPriority>('/api/recommendations/gear-priority', { token }),
};

// AI Advisor API
export const advisorApi = {
  ask: (token: string, question: string, forceAi = false) =>
    api<AdvisorResponse>('/api/advisor/ask', {
      method: 'POST',
      body: { question, force_ai: forceAi },
      token,
    }),

  getHistory: (token: string, limit = 10) =>
    api<Conversation[]>(`/api/advisor/history?limit=${limit}`, { token }),

  rate: (token: string, conversationId: number, rating?: number, isHelpful?: boolean) =>
    api('/api/advisor/rate', {
      method: 'POST',
      body: { conversation_id: conversationId, rating, is_helpful: isHelpful },
      token,
    }),

  getStatus: (token: string) =>
    api<AdvisorStatus>('/api/advisor/status', { token }),
};

// Lineups API
export const lineupsApi = {
  getTemplates: () =>
    api<Record<string, LineupTemplate>>('/api/lineups/templates'),

  build: (token: string, gameMode: string) =>
    api<LineupResponse>(`/api/lineups/build/${gameMode}`, { token }),

  buildAll: (token: string) =>
    api<Record<string, LineupResponse>>('/api/lineups/build-all', { token }),

  getGeneral: (gameMode: string, maxGeneration = 8) =>
    api<LineupResponse>(`/api/lineups/general/${gameMode}?max_generation=${maxGeneration}`),

  getJoinerRecommendation: (token: string, attackType: string) =>
    api<JoinerRecommendation>(`/api/lineups/joiner/${attackType}`, { token }),

  getTemplateDetails: (gameMode: string) =>
    api<LineupTemplateDetails>(`/api/lineups/template/${gameMode}`),
};

// Admin API
export const adminApi = {
  // Users
  listUsers: (token: string, skip = 0, limit = 50, testOnly = false) =>
    api<AdminUser[]>(`/api/admin/users?skip=${skip}&limit=${limit}&test_only=${testOnly}`, { token }),

  createUser: (token: string, data: CreateUserRequest) =>
    api<AdminUser>('/api/admin/users', { method: 'POST', body: data, token }),

  updateUser: (token: string, userId: number, data: UpdateUserRequest) =>
    api<AdminUser>(`/api/admin/users/${userId}`, { method: 'PUT', body: data, token }),

  deleteUser: (token: string, userId: number) =>
    api(`/api/admin/users/${userId}`, { method: 'DELETE', token }),

  // Announcements
  listAnnouncements: (token: string, activeOnly = false) =>
    api<Announcement[]>(`/api/admin/announcements?active_only=${activeOnly}`, { token }),

  createAnnouncement: (token: string, data: CreateAnnouncementRequest) =>
    api<Announcement>('/api/admin/announcements', { method: 'POST', body: data, token }),

  toggleAnnouncement: (token: string, id: number, isActive: boolean) =>
    api(`/api/admin/announcements/${id}?is_active=${isActive}`, { method: 'PUT', token }),

  // Feature Flags
  listFeatureFlags: (token: string) =>
    api<FeatureFlag[]>('/api/admin/feature-flags', { token }),

  toggleFeatureFlag: (token: string, name: string, isEnabled: boolean) =>
    api(`/api/admin/feature-flags/${name}?is_enabled=${isEnabled}`, { method: 'PUT', token }),

  // AI Settings
  getAISettings: (token: string) =>
    api<AISettings>('/api/admin/ai-settings', { token }),

  updateAISettings: (token: string, data: Partial<AISettings>) =>
    api('/api/admin/ai-settings', { method: 'PUT', body: data, token }),

  // Stats
  getStats: (token: string) =>
    api<AdminStats>('/api/admin/stats', { token }),

  // Feedback
  listFeedback: (token: string, status?: string, feedbackType?: string) => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (feedbackType) params.append('feedback_type', feedbackType);
    return api<FeedbackItem[]>(`/api/admin/feedback?${params}`, { token });
  },

  updateFeedbackStatus: (token: string, id: number, status: string) =>
    api(`/api/admin/feedback/${id}?status=${status}`, { method: 'PUT', token }),

  // Impersonation
  impersonateUser: (token: string, userId: number) =>
    api<{ access_token: string; user: User }>(`/api/admin/users/${userId}/impersonate`, { method: 'POST', token }),

  switchBack: (token: string) =>
    api<{ access_token: string; user: User }>('/api/admin/users/switch-back', { method: 'POST', token }),
};

// Types
export interface User {
  id: number;
  email: string;
  username: string;
  role: string;
  impersonating?: boolean;
  original_admin_id?: number;
}

export interface Hero {
  id: number;
  name: string;
  generation: number;
  hero_class: string;
  tier_overall: string | null;
  tier_expedition: string | null;
  tier_exploration: string | null;
  image_filename: string | null;
  image_base64: string | null;
}

export interface UserHero {
  hero_id: number;
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
  // Image
  image_base64: string | null;
}

export interface Profile {
  id: number;
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
}

export interface DashboardStats {
  total_heroes: number;
  owned_heroes: number;
  furnace_level: number;
  furnace_display: string;
  server_age_days: number;
  generation: number;
  state_number: number | null;
  spending_profile: string;
  alliance_role: string;
  priority_focus: string;
}

// Chief Gear & Charms Types
export interface ChiefGear {
  id: number;
  profile_id: number;
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
  id: number;
  profile_id: number;
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

export interface PhaseInfo {
  phase_id: string;
  phase_name: string;
  focus_areas: string[];
  common_mistakes: string[];
  bottlenecks: string[];
  next_milestone: Record<string, any> | null;
}

export interface GearPriority {
  spending_profile: string;
  priority: Record<string, any>[];
}

// AI Advisor Types
export interface AdvisorResponse {
  answer: string;
  source: string;
  category: string | null;
  recommendations: Record<string, any>[];
  lineup: Record<string, any> | null;
  conversation_id: number | null;
}

export interface Conversation {
  id: number;
  question: string;
  answer: string;
  source: string;
  created_at: string;
  rating: number | null;
  is_helpful: boolean | null;
}

export interface AdvisorStatus {
  ai_enabled: boolean;
  mode: string;
  daily_limit: number;
  requests_today: number;
  requests_remaining: number;
  primary_provider?: string;
}

// Lineups Types
export interface LineupHero {
  hero: string;
  hero_class: string;
  slot: string;
  role: string;
  is_lead: boolean;
  status: string;
  power?: number;
}

export interface LineupResponse {
  game_mode: string;
  heroes: LineupHero[];
  troop_ratio: Record<string, number>;
  notes: string;
  confidence: string;
  recommended_to_get: Record<string, any>[];
}

export interface LineupTemplate {
  name: string;
  troop_ratio: Record<string, number>;
  notes: string;
  key_heroes: string[];
  ratio_explanation: string;
}

export interface LineupTemplateDetails extends LineupTemplate {
  slots: Record<string, any>[];
  hero_explanations: Record<string, string>;
  sustain_heroes?: Record<string, string>;
  joiner_warning?: string;
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

// Admin Types
export interface AdminUser {
  id: number;
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
  id: number;
  title: string;
  message: string;
  type: string;
  is_active: boolean;
  display_type: string;
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
  id: number;
  name: string;
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
  id: number;
  user_id: number;
  type: string;
  message: string;
  status: string;
  created_at: string;
}
