/**
 * FISO API Utilities
 * Shared utilities for API authentication and common functions
 */

/**
 * Get API token for production authentication
 * @returns {Promise<string>} API token
 */
export const getApiToken = async () => {
  try {
    // In production, this would get a JWT token from your auth service
    const authResponse = await fetch(`${process.env.REACT_APP_AUTH_URL || 'http://localhost:8000'}/api/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include'
    });
    const authData = await authResponse.json();
    return authData.token || 'default-demo-token';
  } catch (error) {
    console.warn('Using demo token for development:', error);
    return 'demo-production-token';
  }
};

/**
 * Get base API URL
 * @returns {string} Base API URL
 */
export const getApiBaseUrl = () => {
  return process.env.REACT_APP_API_URL || 'http://localhost:8000';
};

/**
 * Create headers with authentication
 * @returns {Promise<object>} Headers object with auth token
 */
export const createAuthHeaders = async () => {
  const token = await getApiToken();
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    'X-API-Version': '2.0'
  };
};

/**
 * Handle API errors consistently
 * @param {Error} error - The error object
 * @param {string} context - Context where error occurred
 */
export const handleApiError = (error, context = 'API call') => {
  console.error(`${context} failed:`, error);
  
  if (error.response) {
    // Server responded with error status
    const message = error.response.data?.message || error.response.statusText;
    throw new Error(`${context} failed: ${message}`);
  } else if (error.request) {
    // Network error
    throw new Error(`${context} failed: Network error. Please check your connection.`);
  } else {
    // Other error
    throw new Error(`${context} failed: ${error.message}`);
  }
};

/**
 * Format currency values
 * @param {number} amount - Amount to format
 * @param {string} currency - Currency code (default: USD)
 * @returns {string} Formatted currency string
 */
export const formatCurrency = (amount, currency = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount);
};

/**
 * Format date for display
 * @param {Date|string} date - Date to format
 * @returns {string} Formatted date string
 */
export const formatDate = (date) => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return dateObj.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

/**
 * Debounce function to limit API calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Cache API responses for better performance
 */
class ApiCache {
  constructor() {
    this.cache = new Map();
    this.defaultTTL = 5 * 60 * 1000; // 5 minutes
  }

  get(key) {
    const item = this.cache.get(key);
    if (!item) return null;
    
    if (Date.now() > item.expiry) {
      this.cache.delete(key);
      return null;
    }
    
    return item.data;
  }

  set(key, data, ttl = this.defaultTTL) {
    this.cache.set(key, {
      data,
      expiry: Date.now() + ttl
    });
  }

  clear() {
    this.cache.clear();
  }
}

export const apiCache = new ApiCache();