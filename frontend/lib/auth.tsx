'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, authApi, adminApi, getStoredToken, storeTokens, clearTokens } from './api';

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
      // Restore impersonation state
      if (localStorage.getItem('impersonating') === 'true') {
        setIsImpersonating(true);
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
  };

  const impersonate = async (userId: string) => {
    if (!token) throw new Error('Not authenticated');
    // Save original admin user before impersonating
    if (user) {
      localStorage.setItem('admin_user', JSON.stringify(user));
    }
    const response = await adminApi.impersonateUser(token, userId);
    // Impersonation doesn't change auth tokens (admin stays authenticated).
    // We just swap the displayed user to the target user.
    setUser(response.user);
    setIsImpersonating(true);
    localStorage.setItem('impersonating', 'true');
  };

  const switchBack = () => {
    const savedAdmin = localStorage.getItem('admin_user');
    if (savedAdmin) {
      setUser(JSON.parse(savedAdmin));
      localStorage.removeItem('admin_user');
    }
    setIsImpersonating(false);
    localStorage.removeItem('impersonating');
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
