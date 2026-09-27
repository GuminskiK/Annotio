import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import { api } from '../api/axiosClient';
import { loginApi, loginMfaApi, logoutApi } from '@/api/auth/auth';
import type { User } from '../api/auth/types'


interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string, mfaCode?: string) => Promise<any>;
  loginMfa: (mfaCode: string, mfaToken: string) => Promise<any>;
  logout: () => Promise<boolean>;
  updateUser: (updatedData: User) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchUserProfile = useCallback(async () => {
    try {
      const response = await api.get<User>('/api/users/me'); 
      setUser(response.data);
      return response.data;
    } catch (error) {
      setUser(null);
      return null;
    }
  }, []);

  useEffect(() => {
    const checkSession = async () => {
      await fetchUserProfile();
      setIsLoading(false);
    };
    checkSession();
  }, [fetchUserProfile]);

  useEffect(() => {
    const handleUnauthorized = () => {
      setUser(null); 
    };

    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => {
      window.removeEventListener('auth:unauthorized', handleUnauthorized);
    };
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const response = await loginApi(username, password);

    if ( response.status === 200) {
      await fetchUserProfile();
    }
    return response;
  }, [fetchUserProfile]);


  const loginMfa = useCallback(async (mfaCode: string, mfaToken: string) => {
    const response = await loginMfaApi(mfaCode, mfaToken);
    await fetchUserProfile();
    return response;
  }, []);

  const logout = useCallback(async () => {
    try {
      const response = await logoutApi();
      if (response.status === 200) {
        setUser(null);
        return true;
      }
      return false;
    } catch (error) {
      console.error("Błąd podczas wylogowywania:", error);
      return false;
    }
  }, []);

  const updateUser = useCallback((updatedData: User) => {
    setUser(updatedData);
  }, []);

  const contextValue = useMemo(() => ({
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    loginMfa,
    logout,
    updateUser
  }), [user, isLoading, login, loginMfa, logout, updateUser]);

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};