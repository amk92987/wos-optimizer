'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, authApi, adminApi, getStoredToken, storeTokens, clearTokens } from './api';

interface ImpersonateUserResponse {
  id?: string;
  user_id?: string;
  email?: string;
  username?: string;
  role?: string;
  is_active?: boolean;
  is_test_account?: boolean;
  created_at?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isImpersonating: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  impersonate: (userId: string) => Promise<void>;
  switchBack: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isImpersonating, setIsImpersonating] = useState(false);

  // Check for existing Cognito tokens on mount
  useEffect(() => {
    async function initAuth() {
      const storedToken = getStoredToken();
      if (storedToken) {
        setToken(storedToken);
        try {
          const userData = await authApi.me(storedToken);
          setUser(userData);
        } catch {
          // Token expired - try refresh
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            try {
              const response = await authApi.refresh(refreshToken);
              storeTokens({
                id_token: response.id_token,
                access_token: response.access_token,
                refresh_token: response.refresh_token || refreshToken,
              });
              setToken(response.id_token);
              setUser(response.user);
            } catch {
              // Refresh also failed - clear everything
              clearTokens();
              setToken(null);
            }
          } else {
            // No refresh token - clear everything
            clearTokens();
            setToken(null);
          }
        }
      }
      // Restore impersonation state and impersonated user data
      if (localStorage.getItem('impersonating') === 'true') {
        setIsImpersonating(true);
        const savedImpersonateUser = localStorage.getItem('impersonate_user');
        if (savedImpersonateUser) {
          try {
            setUser(JSON.parse(savedImpersonateUser));
          } catch {
            // If parsing fails, fall through with admin user
          }
        }
      }
      setIsLoading(false);
    }

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authApi.login(email, password);
    storeTokens({
      id_token: response.id_token,
      access_token: response.access_token,
      refresh_token: response.refresh_token,
    });
    setToken(response.id_token);
    setUser(response.user);
  };

  const register = async (email: string, password: string) => {
    const response = await authApi.register(email, password);
    storeTokens({
      id_token: response.id_token,
      access_token: response.access_token,
      refresh_token: response.refresh_token,
    });
    setToken(response.id_token);
    setUser(response.user);
  };

  const logout = () => {
    clearTokens();
    setToken(null);
    setUser(null);
    setIsImpersonating(false);
    localStorage.removeItem('impersonating');
    localStorage.removeItem('impersonate_user_id');
    localStorage.removeItem('impersonate_user');
    localStorage.removeItem('admin_user');
  };

  const impersonate = async (userId: string) => {
    if (!token) throw new Error('Not authenticated');
    // Save original admin user before impersonating
    if (user) {
      localStorage.setItem('admin_user', JSON.stringify(user));
    }
    const response = await adminApi.impersonateUser(token, userId);
    // Impersonation doesn't change auth tokens (admin stays authenticated).
    // We swap the displayed user and store the target ID so API calls
    // include the X-Impersonate-User header for backend routing.
    // The backend returns the raw DynamoDB user item which may have
    // 'user_id' instead of 'id', so we normalize to the User interface.
    const raw = response.user as ImpersonateUserResponse;
    const impersonatedUser: User = {
      id: raw.id || raw.user_id || userId,
      email: raw.email || raw.username || userId,
      username: raw.username || raw.email || userId,
      role: raw.role || 'user',
      is_active: raw.is_active !== false,
      is_test_account: raw.is_test_account || false,
      created_at: raw.created_at || '',
    };
    setUser(impersonatedUser);
    setIsImpersonating(true);
    localStorage.setItem('impersonating', 'true');
    localStorage.setItem('impersonate_user_id', userId);
    localStorage.setItem('impersonate_user', JSON.stringify(impersonatedUser));
  };

  const switchBack = () => {
    const savedAdmin = localStorage.getItem('admin_user');
    if (savedAdmin) {
      setUser(JSON.parse(savedAdmin));
      localStorage.removeItem('admin_user');
    }
    setIsImpersonating(false);
    localStorage.removeItem('impersonating');
    localStorage.removeItem('impersonate_user_id');
    localStorage.removeItem('impersonate_user');
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, isImpersonating, login, register, logout, impersonate, switchBack }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
