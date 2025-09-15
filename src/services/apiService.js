import axios from 'axios';

const BASE_URL = 'http://localhost:5000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to: ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('Response error:', error);
    if (error.response) {
      console.error('Error status:', error.response.status);
      console.error('Error data:', error.response.data);
    }
    return Promise.reject(error);
  }
);

export const apiService = {
  // Core pricing data endpoints
  async getPricingData() {
    try {
      const response = await api.get('/api/pricing-data');
      return response.data;
    } catch (error) {
      console.warn('Failed to fetch pricing data, using fallback:', error.message);
      return this.getFallbackPricingData();
    }
  },

  async getRecommendations() {
    try {
      const response = await api.get('/api/recommendations');
      return response.data;
    } catch (error) {
      console.warn('Failed to fetch recommendations, using fallback:', error.message);
      return this.getFallbackRecommendations();
    }
  },

  // AI/ML endpoints
  async predictCosts(data) {
    try {
      const response = await api.post('/api/ai/predict-costs', data);
      return response.data;
    } catch (error) {
      console.warn('Failed to get AI predictions:', error.message);
      throw error;
    }
  },

  async detectAnomalies(provider, serviceType) {
    try {
      const response = await api.get(`/api/ai/detect-anomalies?provider=${provider}&service_type=${serviceType}`);
      return response.data;
    } catch (error) {
      console.warn('Failed to detect anomalies:', error.message);
      throw error;
    }
  },

  async processNaturalQuery(query) {
    try {
      const response = await api.post('/api/ai/natural-query', { query });
      return response.data;
    } catch (error) {
      console.warn('Failed to process natural language query:', error.message);
      throw error;
    }
  },

  async getModelPerformance() {
    try {
      const response = await api.get('/api/ai/model-performance');
      return response.data;
    } catch (error) {
      console.warn('Failed to get model performance:', error.message);
      throw error;
    }
  },

  async trainModels() {
    try {
      const response = await api.post('/api/ai/train-models');
      return response.data;
    } catch (error) {
      console.warn('Failed to train models:', error.message);
      throw error;
    }
  },

  // Fallback data for when backend is not available
  getFallbackPricingData() {
    return {
      status: 'success',
      pricing_data: {
        aws: {
          ec2: {
            't3.micro': {
              price: 0.0104,
              confidence: 0.95,
              trend: 'stable',
              last_updated: new Date().toISOString()
            },
            't3.small': {
              price: 0.0208,
              confidence: 0.93,
              trend: 'increasing',
              last_updated: new Date().toISOString()
            },
            't3.medium': {
              price: 0.0416,
              confidence: 0.94,
              trend: 'stable',
              last_updated: new Date().toISOString()
            }
          },
          lambda: {
            'requests': {
              price: 0.0000002,
              confidence: 0.98,
              trend: 'stable',
              last_updated: new Date().toISOString()
            }
          },
          rds: {
            'db.t3.micro': {
              price: 0.017,
              confidence: 0.92,
              trend: 'stable',
              last_updated: new Date().toISOString()
            }
          }
        },
        azure: {
          vm: {
            'B1s': {
              price: 0.0125,
              confidence: 0.91,
              trend: 'decreasing',
              last_updated: new Date().toISOString()
            },
            'B2s': {
              price: 0.0502,
              confidence: 0.89,
              trend: 'stable',
              last_updated: new Date().toISOString()
            }
          },
          functions: {
            'consumption': {
              price: 0.000016,
              confidence: 0.95,
              trend: 'stable',
              last_updated: new Date().toISOString()
            }
          },
          sql: {
            'Basic': {
              price: 0.0067,
              confidence: 0.93,
              trend: 'stable',
              last_updated: new Date().toISOString()
            }
          }
        },
        gcp: {
          compute: {
            'e2.micro': {
              price: 0.008467,
              confidence: 0.96,
              trend: 'stable',
              last_updated: new Date().toISOString()
            },
            'e2.small': {
              price: 0.01693,
              confidence: 0.94,
              trend: 'stable',
              last_updated: new Date().toISOString()
            }
          }
        }
      },
      last_updated: new Date().toISOString(),
      total_services: 12
    };
  },

  getFallbackRecommendations() {
    return {
      status: 'success',
      recommendations: [
        {
          type: 'cost_optimization',
          priority: 'high',
          service: 'AWS EC2',
          description: 'Consider switching from t3.small to t3.micro for development workloads',
          potential_savings: 120.50,
          confidence: 0.87
        },
        {
          type: 'right_sizing',
          priority: 'medium',
          service: 'Azure VM',
          description: 'B2s instances show low utilization - consider B1s for cost savings',
          potential_savings: 89.30,
          confidence: 0.82
        },
        {
          type: 'reserved_instances',
          priority: 'high',
          service: 'AWS RDS',
          description: 'Reserve db.t3.micro instances for 1-year term to save 30%',
          potential_savings: 156.20,
          confidence: 0.95
        }
      ]
    };
  }
};

export default apiService;