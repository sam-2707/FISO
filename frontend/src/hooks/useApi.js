import { useState, useEffect, useCallback, useRef } from 'react';
import { apiService } from '../services/apiService';

export const useApi = (endpoint, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const {
    immediate = true,
    dependencies = [],
    transform = (data) => data,
  } = options;
  
  const abortControllerRef = useRef(null);

  const execute = useCallback(async (params = {}) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();
    
    setLoading(true);
    setError(null);

    try {
      let response;
      
      // Handle different types of API calls
      if (endpoint === 'realTimePricing') {
        response = await apiService.getRealTimePricing();
      } else if (endpoint === 'costPrediction') {
        response = await apiService.getCostPrediction(params);
      } else if (endpoint === 'comprehensiveAnalysis') {
        response = await apiService.getComprehensiveAnalysis(params);
      } else if (endpoint === 'optimizationRecommendations') {
        response = await apiService.getOptimizationRecommendations(params);
      } else if (endpoint === 'trendAnalysis') {
        response = await apiService.getTrendAnalysis();
      } else if (endpoint === 'orchestrate') {
        response = await apiService.orchestrate(params);
      } else if (endpoint === 'analysis') {
        response = await apiService.getAnalysis(params.region);
      } else if (endpoint === 'comparison') {
        response = await apiService.getComparison(params.providers);
      } else if (endpoint === 'healthCheck') {
        response = await apiService.healthCheck();
      } else if (endpoint === 'systemStatus') {
        response = await apiService.getSystemStatus();
      } else {
        throw new Error(`Unknown endpoint: ${endpoint}`);
      }

      const transformedData = transform(response);
      setData(transformedData);
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(apiService.formatError(err));
      }
    } finally {
      if (abortControllerRef.current && !abortControllerRef.current.signal.aborted) {
        setLoading(false);
      }
    }
  }, [endpoint, transform]);

  useEffect(() => {
    if (immediate && apiService.isReady()) {
      execute();
    }
    
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [execute, immediate]);

  const refetch = useCallback((params) => {
    return execute(params);
  }, [execute]);

  return {
    data,
    loading,
    error,
    execute,
    refetch,
  };
};

// Specialized hooks for common API calls
export const useRealTimePricing = (options = {}) => {
  return useApi('realTimePricing', {
    ...options,
    transform: (data) => {
      // Transform the real-time pricing data for easier use in components
      return {
        timestamp: data.timestamp,
        providers: data.providers || {},
        insights: data.insights || {},
        recommendations: data.recommendations || [],
      };
    },
  });
};

export const useCostPrediction = (options = {}) => {
  return useApi('costPrediction', {
    ...options,
    immediate: false, // Don't auto-execute, wait for user input
  });
};

export const useSystemStatus = (options = {}) => {
  return useApi('systemStatus', {
    ...options,
    transform: (data) => ({
      status: data.status || 'unknown',
      uptime: data.uptime || 0,
      version: data.version || '1.0.0',
      features: data.features || {},
    }),
  });
};
