import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

interface AuthContextType {
  token: string | null;
  isAuthenticated: boolean;
  login: (jwtToken: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('jwt_token'));
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(!!token);

  useEffect(() => {
    setIsAuthenticated(!!token);
  }, [token]);

  const login = useCallback((jwtToken: string) => {
    localStorage.setItem('jwt_token', jwtToken);
    setToken(jwtToken);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('jwt_token');
    setToken(null);
  }, []);

  return (
    <AuthContext.Provider value={{ token, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};