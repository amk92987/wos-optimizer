'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, authApi, adminApi } from './api';

// Dev mode auto-login credentials (only used in development)
// Set enabled: true to always auto-login, or use NODE_ENV check for safety
const DEV_AUTO_LOGIN = {
  enabled: true, // Always enabled for local dev - change to false for production builds
  email: 'dev@local',
  password: 'dev123',
};

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  impersonate: (userId: number) => Promise<void>;
  switchBack: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing token on mount, or auto-login in dev mode
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      authApi.me(storedToken)
        .then(user => setUser(user))
        .catch(() => {
          localStorage.removeItem('token');
          setToken(null);
          // Try auto-login in dev mode if token expired
          if (DEV_AUTO_LOGIN.enabled) {
            autoLoginDev();
          } else {
            setIsLoading(false);
          }
        })
        .finally(() => {
          if (storedToken) setIsLoading(false);
        });
    } else if (DEV_AUTO_LOGIN.enabled) {
      // No token, auto-login in dev mode
      autoLoginDev();
    } else {
      setIsLoading(false);
    }

    async function autoLoginDev() {
      try {
        console.log('[Dev] Auto-logging in as', DEV_AUTO_LOGIN.email);
        const response = await authApi.login(DEV_AUTO_LOGIN.email, DEV_AUTO_LOGIN.password);
        localStorage.setItem('token', response.access_token);
        setToken(response.access_token);
        setUser(response.user);
      } catch (error) {
        console.error('[Dev] Auto-login failed:', error);
      } finally {
        setIsLoading(false);
      }
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authApi.login(email, password);
    localStorage.setItem('token', response.access_token);
    setToken(response.access_token);
    setUser(response.user);
  };

  const register = async (email: string, password: string) => {
    const response = await authApi.register(email, password);
    localStorage.setItem('token', response.access_token);
    setToken(response.access_token);
    setUser(response.user);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const impersonate = async (userId: number) => {
    if (!token) throw new Error('Not authenticated');
    const response = await adminApi.impersonateUser(token, userId);
    localStorage.setItem('token', response.access_token);
    setToken(response.access_token);
    setUser(response.user);
  };

  const switchBack = async () => {
    if (!token) throw new Error('Not authenticated');
    const response = await adminApi.switchBack(token);
    localStorage.setItem('token', response.access_token);
    setToken(response.access_token);
    setUser(response.user);
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, register, logout, impersonate, switchBack }}>
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
