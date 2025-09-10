import axios from 'axios';

class ApiService {
  constructor() {
    this.baseURL = process.env.NODE_ENV === 'production' 
      ? process.env.REACT_APP_API_URL || '/api'
      : '/api';
      
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    this.sessionInfo = null;
    this.isInitialized = false;
    
    // Setup interceptors
    this.setupInterceptors();
  }

  setupInterceptors() {
    // Request interceptor for auth
    this.client.interceptors.request.use(
      (config) => {
        if (this.sessionInfo?.api_key) {
          config.headers.Authorization = `Bearer ${this.sessionInfo.api_key}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        
        if (error.response?.status === 401) {
          // Handle authentication error
          this.handleAuthError();
        }
        
        return Promise.reject({
          message: error.response?.data?.error || error.message,
          status: error.response?.status,
          details: error.response?.data?.details
        });
      }
    );
  }

  async initialize() {
    try {
      const sessionResponse = await axios.get(`${this.baseURL}/session-info`);
      
      if (sessionResponse.data.success) {
        this.sessionInfo = sessionResponse.data;
        this.isInitialized = true;
        console.log('✅ API Service initialized successfully');
      } else {
        throw new Error('Failed to initialize session');
      }
    } catch (error) {
      console.error('❌ API Service initialization failed:', error);
      throw error;
    }
  }

  handleAuthError() {
    console.warn('Authentication error - reinitializing session...');
    this.sessionInfo = null;
    this.isInitialized = false;
    
    // Attempt to reinitialize
    this.initialize().catch(error => {
      console.error('Failed to reinitialize API service:', error);
    });
  }

  // Dashboard & Analytics
  async getRealTimePricing() {
    const response = await this.client.get('/ai/real-time-pricing');
    return response.data;
  }

  async getCostPrediction(workloadConfig) {
    const response = await this.client.post('/ai/cost-prediction', workloadConfig);
    return response.data;
  }

  async getComprehensiveAnalysis(analysisConfig) {
    const response = await this.client.post('/ai/comprehensive-analysis', analysisConfig);
    return response.data;
  }

  async getOptimizationRecommendations(optimizationConfig) {
    const response = await this.client.post('/ai/optimization-recommendations', optimizationConfig);
    return response.data;
  }

  async getTrendAnalysis() {
    const response = await this.client.get('/ai/trend-analysis');
    return response.data;
  }

  // FISO Core APIs
  async orchestrate(payload) {
    const response = await this.client.post('/orchestrate', payload);
    return response.data;
  }

  async getAnalysis(region = 'us-east-1') {
    const response = await this.client.get('/analysis', { params: { region } });
    return response.data;
  }

  async getComparison(providers = ['aws', 'azure', 'gcp']) {
    const response = await this.client.get('/comparison', { 
      params: { providers: providers.join(',') } 
    });
    return response.data;
  }

  // Utility methods
  async healthCheck() {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      return { status: 'error', error: error.message };
    }
  }

  async getSystemStatus() {
    const response = await this.client.get('/status');
    return response.data;
  }

  // Session management
  getSessionInfo() {
    return this.sessionInfo;
  }

  isReady() {
    return this.isInitialized && this.sessionInfo;
  }

  // Error handling utilities
  formatError(error) {
    if (typeof error === 'string') {
      return error;
    }
    
    return error.message || error.details || 'An unexpected error occurred';
  }
}

// Create singleton instance
export const apiService = new ApiService();

// Export class for testing
export { ApiService };
