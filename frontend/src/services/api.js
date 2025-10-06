/**
 * Atharman API Service
 * Handles all API communications between frontend and backend
 */

import axios from 'axios';

// Configure axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

// Health check
export const checkHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error(`Health check failed: ${error.message}`);
  }
};

// Pricing data
export const getPricingData = async () => {
  try {
    const response = await api.get('/api/pricing-data');
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch pricing data: ${error.message}`);
  }
};

// Optimization recommendations
export const getOptimizationRecommendations = async () => {
  try {
    const response = await api.get('/api/optimization-recommendations');
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch recommendations: ${error.message}`);
  }
};

// AI Prediction Services
export const predictCosts = async (provider = 'aws', serviceType = 'ec2', horizonHours = 24) => {
  try {
    const response = await api.post('/api/ai/predict-costs', {
      provider,
      service_type: serviceType,
      horizon_hours: horizonHours,
    });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to predict costs: ${error.message}`);
  }
};

// Anomaly detection
export const detectAnomalies = async (provider = 'aws', serviceType = 'ec2') => {
  try {
    const response = await api.get('/api/ai/detect-anomalies', {
      params: { provider, service_type: serviceType }
    });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to detect anomalies: ${error.message}`);
  }
};

// Natural language processing
export const processNaturalQuery = async (query, context = {}) => {
  try {
    const response = await api.post('/api/ai/natural-query', {
      query,
      context,
    });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to process query: ${error.message}`);
  }
};

// Model performance
export const getModelPerformance = async () => {
  try {
    const response = await api.get('/api/ai/model-performance');
    return response.data;
  } catch (error) {
    throw new Error(`Failed to get model performance: ${error.message}`);
  }
};

// Real-time pricing (from secure server)
export const getRealTimePricing = async () => {
  try {
    const response = await api.get('/api/ai/real-time-pricing');
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch real-time pricing: ${error.message}`);
  }
};

// Comprehensive AI analysis
export const getComprehensiveAnalysis = async (usageScenario = {}) => {
  try {
    const response = await api.post('/api/ai/comprehensive-analysis', usageScenario);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to get comprehensive analysis: ${error.message}`);
  }
};

// Live recommendations
export const getLiveRecommendations = async () => {
  try {
    const response = await api.get('/api/ai/live-recommendations');
    return response.data;
  } catch (error) {
    throw new Error(`Failed to get live recommendations: ${error.message}`);
  }
};

// Store cost data for ML training
export const storeCostData = async (costData) => {
  try {
    const response = await api.post('/api/ai/store-cost-data', costData);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to store cost data: ${error.message}`);
  }
};

// Train models
export const trainModels = async () => {
  try {
    const response = await api.post('/api/ai/train-models');
    return response.data;
  } catch (error) {
    throw new Error(`Failed to train models: ${error.message}`);
  }
};

// Operational endpoints
export const getOperationalDashboard = async () => {
  try {
    const response = await api.get('/api/operational/dashboard-data');
    return response.data;
  } catch (error) {
    throw new Error(`Failed to get operational dashboard: ${error.message}`);
  }
};

export const getIntelligentRecommendations = async (criteria = {}) => {
  try {
    const response = await api.post('/api/operational/recommendations', criteria);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to get intelligent recommendations: ${error.message}`);
  }
};

export const getRealTimeCosts = async () => {
  try {
    const response = await api.get('/api/operational/real-time-costs');
    return response.data;
  } catch (error) {
    throw new Error(`Failed to get real-time costs: ${error.message}`);
  }
};

export const getCurrentTimePricing = async (region = 'us-east-1') => {
  try {
    const response = await api.get('/api/operational/current-time-pricing', {
      params: { region }
    });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to get current time pricing: ${error.message}`);
  }
};

// Connection test
export const testConnection = async () => {
  try {
    const health = await checkHealth();
    const pricing = await getPricingData();
    
    return {
      status: 'connected',
      health,
      sampleData: pricing,
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    return {
      status: 'disconnected',
      error: error.message,
      timestamp: new Date().toISOString(),
    };
  }
};

export default api;