import { ReactNode, createContext, useContext, useEffect, useMemo, useState } from "react";
import { getCurrentUser, login as loginRequest } from "../services/authService";
import { clearAccessToken, getAccessToken, setAccessToken } from "../utils/auth";
import { LoginResponse, User } from "../types";

type AuthContextValue = {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<LoginResponse>;
  logout: () => void;
  refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = async () => {
    if (!getAccessToken()) {
      setUser(null);
      return;
    }
    try {
      const profile = await getCurrentUser();
      setUser(profile);
    } catch {
      clearAccessToken();
      setUser(null);
    }
  };

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      await refreshUser();
      setLoading(false);
    };
    void load();
  }, []);

  const login = async (email: string, password: string) => {
    const token = await loginRequest(email, password);
    setAccessToken(token.access_token);
    await refreshUser();
    return token;
  };

  const logout = () => {
    clearAccessToken();
    setUser(null);
  };

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      isAuthenticated: Boolean(user),
      login,
      logout,
      refreshUser,
    }),
    [user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
