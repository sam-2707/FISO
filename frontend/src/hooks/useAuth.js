import { useState, useEffect } from 'react';
import { authService } from '../services/authService';

export const useAuth = () => {
  const [authState, setAuthState] = useState({
    user: authService.getCurrentUser(),
    isAuthenticated: authService.isUserAuthenticated(),
    loading: authService.isLoading(),
  });

  useEffect(() => {
    // Subscribe to auth state changes
    const unsubscribe = authService.subscribe(setAuthState);
    
    return unsubscribe;
  }, []);

  useEffect(() => {
    // Initialize if not already done
    if (!authState.isAuthenticated && !authState.loading) {
      authService.initialize();
    }
  }, [authState.isAuthenticated, authState.loading]);

  const login = async (credentials) => {
    try {
      await authService.login(credentials);
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const logout = () => {
    authService.logout();
  };

  const hasPermission = (permission) => {
    return authService.hasPermission(permission);
  };

  return {
    user: authState.user,
    isAuthenticated: authState.isAuthenticated,
    loading: authState.loading,
    login,
    logout,
    hasPermission,
  };
};
