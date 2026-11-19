import React, { useState, useEffect, useCallback, type ReactNode } from 'react';
import { authService, type UserResponse } from '../services/auth.service';
import { AuthContext } from './auth-context';

function readStoredUser(): UserResponse | null {
  const storedUser = localStorage.getItem('user');
  if (!storedUser) return null;
  try {
    return JSON.parse(storedUser);
  } catch {
    return null;
  }
}

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserResponse | null>(readStoredUser);
  const [isLoading, setIsLoading] = useState(() => !localStorage.getItem('token'));

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  }, []);

  const refreshUser = useCallback(async () => {
    try {
      const userData = await authService.getMe();
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
    } catch (error) {
      console.error('Falha ao obter dados do usuário:', error);
      logout();
    }
  }, [logout]);

  useEffect(() => {
    if (localStorage.getItem('token')) {
      refreshUser().finally(() => setIsLoading(false));
    }
  }, [refreshUser]);

  const login = async (username: string, password: string) => {
    const tokenData = await authService.login(username, password);
    localStorage.setItem('token', tokenData.access_token);
    const userData = await authService.getMe();
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};