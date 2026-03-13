import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from 'react';
import type { User } from '../types';
import * as api from '../services/api';

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: {
    email: string;
    password: string;
    full_name: string;
    role?: string;
    institution?: string;
    npi_number?: string;
  }) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch current user if token exists on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setLoading(false);
      return;
    }

    api
      .getMe()
      .then((userData) => {
        setUser(userData);
      })
      .catch(() => {
        // Token is invalid or expired
        localStorage.removeItem('access_token');
        setUser(null);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setError(null);
    try {
      const response = await api.login(email, password);
      localStorage.setItem('access_token', response.access_token);
      setUser(response.user);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Login failed. Please check your credentials.';
      setError(message);
      throw new Error(message);
    }
  }, []);

  const register = useCallback(
    async (payload: {
      email: string;
      password: string;
      full_name: string;
      role?: string;
      institution?: string;
      npi_number?: string;
    }) => {
      setError(null);
      try {
        await api.register(payload);
        // Auto-login after registration
        await login(payload.email, payload.password);
      } catch (err: unknown) {
        const message =
          (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
          'Registration failed. Please try again.';
        setError(message);
        throw new Error(message);
      }
    },
    [login]
  );

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    setUser(null);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, loading, error, login, register, logout, clearError }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default useAuth;
