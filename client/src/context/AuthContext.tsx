import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { DEMO_MODE, fetchCurrentUser, logout as apiLogout } from '../api/api';
import type { User } from '../api/api';

// ── Types ──────────────────────────────────────────────────────────────────

interface AuthContextValue {
  user: User | null;
  repos: any[];
  isLoading: boolean;
  isAuthenticated: boolean;
  refetch: () => Promise<void>;
  logout: () => Promise<void>;
}


// ── Context ────────────────────────────────────────────────────────────────

const AuthContext = createContext<AuthContextValue | null>(null);

// ── Provider ───────────────────────────────────────────────────────────────

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [repos, setRepos] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const refetch = useCallback(async (): Promise<void> => {
    if (DEMO_MODE) {
      setUser({
        id: 'demo-user',
        login: 'interviewer-demo',
        name: 'EasyOps Demo',
        email: '',
        avatar_url: '',
      });
      setRepos([
        {
          id: 1,
          full_name: 'acme/payments-api',
          name: 'payments-api',
          owner: 'acme',
          private: false,
          description: 'FastAPI service with GitHub Actions CI',
          updated_at: new Date().toISOString(),
        },
        {
          id: 2,
          full_name: 'acme/web-dashboard',
          name: 'web-dashboard',
          owner: 'acme',
          private: false,
          description: 'React dashboard with Vite build checks',
          updated_at: new Date().toISOString(),
        },
      ]);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    try {
      const data = await fetchCurrentUser();
      setUser(data.user);
      setRepos(data.repos || []);
    } catch {
      setUser(null);
      setRepos([]);
    } finally {
      setIsLoading(false);
    }
  }, []);


  const logout = useCallback(async (): Promise<void> => {
    if (DEMO_MODE) {
      window.location.href = '/';
      return;
    }

    try {
      await apiLogout();
    } catch (err) {
      console.error(err);
    } finally {
      setUser(null);
      setRepos([]);
      window.location.href = '/';
    }
  }, []);

  // Check session on mount
  useEffect(() => {
    void refetch();
  }, [refetch]);

  return (
    <AuthContext.Provider
      value={{
        user,
        repos,
        isLoading,
        isAuthenticated: user !== null,
        refetch,
        logout,

      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// ── Hook ───────────────────────────────────────────────────────────────────

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = (): AuthContextValue => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
};
