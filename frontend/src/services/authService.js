class AuthService {
  constructor() {
    this.user = null;
    this.isAuthenticated = false;
    this.loading = false;
    this.listeners = [];
  }

  async initialize() {
    this.loading = true;
    this.notifyListeners();
    
    try {
      // For now, we'll use session-based auth from the API
      // In the future, this could integrate with OAuth, JWT, etc.
      const response = await fetch('/api/session-info');
      const sessionInfo = await response.json();
      
      if (sessionInfo.success) {
        this.user = {
          id: sessionInfo.session_id,
          name: 'Enterprise User',
          email: 'user@enterprise.com',
          permissions: sessionInfo.permissions || [],
          mode: sessionInfo.mode,
        };
        this.isAuthenticated = true;
      } else {
        throw new Error('Session initialization failed');
      }
    } catch (error) {
      console.error('Auth initialization error:', error);
      this.user = null;
      this.isAuthenticated = false;
    } finally {
      this.loading = false;
      this.notifyListeners();
    }
  }

  async login(credentials) {
    this.loading = true;
    this.notifyListeners();
    
    try {
      // Placeholder for future authentication implementation
      // For now, we rely on the session-info endpoint
      await this.initialize();
    } catch (error) {
      this.loading = false;
      this.notifyListeners();
      throw error;
    }
  }

  logout() {
    this.user = null;
    this.isAuthenticated = false;
    this.notifyListeners();
  }

  getCurrentUser() {
    return this.user;
  }

  isUserAuthenticated() {
    return this.isAuthenticated;
  }

  isLoading() {
    return this.loading;
  }

  hasPermission(permission) {
    if (!this.user || !this.user.permissions) {
      return false;
    }
    return this.user.permissions.includes(permission);
  }

  // Observer pattern for state changes
  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  notifyListeners() {
    this.listeners.forEach(listener => listener({
      user: this.user,
      isAuthenticated: this.isAuthenticated,
      loading: this.loading,
    }));
  }
}

// Create singleton instance
export const authService = new AuthService();

// Export class for testing
export { AuthService };
