/**
 * API client for Bear's Den backend
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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

// Types
export interface User {
  id: number;
  email: string;
  username: string;
  role: string;
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
  exploration_skill_1: number;
  exploration_skill_2: number;
  exploration_skill_3: number;
  expedition_skill_1: number;
  expedition_skill_2: number;
  expedition_skill_3: number;
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
