import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('error_rate');
const responseTime = new Trend('response_time');
const apiCalls = new Counter('api_calls');

// Load test configuration
export const options = {
  stages: [
    { duration: '2m', target: 10 },   // Warm-up
    { duration: '5m', target: 50 },   // Ramp-up
    { duration: '10m', target: 100 }, // Stay at 100 users
    { duration: '5m', target: 200 },  // Peak load
    { duration: '10m', target: 200 }, // Sustain peak
    { duration: '5m', target: 0 },    // Ramp-down
  ],
  thresholds: {
    'error_rate': ['rate<0.1'],        // Error rate should be less than 10%
    'response_time': ['p(95)<2000'],   // 95% of requests should be below 2s
    'http_req_duration': ['p(99)<5000'], // 99% of requests should be below 5s
  },
};

const BASE_URL = __ENV.STAGING_URL || 'http://localhost:5000';
const REALTIME_URL = __ENV.REALTIME_URL || 'http://localhost:5001';

// Test data
const testScenarios = [
  {
    name: 'Health Check',
    endpoint: '/health',
    weight: 10,
  },
  {
    name: 'Pricing Data',
    endpoint: '/api/pricing-data',
    weight: 20,
  },
  {
    name: 'Optimization Recommendations',
    endpoint: '/api/optimization-recommendations',
    weight: 15,
  },
  {
    name: 'AI Predictions',
    endpoint: '/api/ai/predict-costs',
    method: 'POST',
    payload: {
      provider: 'aws',
      service: 'ec2',
      days: 30
    },
    weight: 10,
  },
  {
    name: 'Natural Language Query',
    endpoint: '/api/ai/natural-query',
    method: 'POST',
    payload: {
      query: 'What are my highest costs this month?'
    },
    weight: 8,
  },
  {
    name: 'Anomaly Detection',
    endpoint: '/api/ai/detect-anomalies',
    method: 'POST',
    payload: {
      provider: 'azure',
      threshold: 0.8
    },
    weight: 7,
  },
  {
    name: 'Executive Report Generation',
    endpoint: '/api/reports/executive-summary',
    method: 'POST',
    payload: {
      include_charts: true,
      include_recommendations: true
    },
    weight: 3,
  },
  {
    name: 'Reports List',
    endpoint: '/api/reports/list',
    weight: 5,
  },
];

// Weighted random scenario selection
function selectScenario() {
  const totalWeight = testScenarios.reduce((sum, scenario) => sum + scenario.weight, 0);
  let random = Math.random() * totalWeight;
  
  for (const scenario of testScenarios) {
    random -= scenario.weight;
    if (random <= 0) {
      return scenario;
    }
  }
  
  return testScenarios[0]; // Fallback
}

export default function () {
  const scenario = selectScenario();
  
  let response;
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'k6-load-test/1.0',
    },
    timeout: '30s',
  };

  const startTime = new Date();

  if (scenario.method === 'POST') {
    response = http.post(
      `${BASE_URL}${scenario.endpoint}`,
      JSON.stringify(scenario.payload),
      params
    );
  } else {
    response = http.get(`${BASE_URL}${scenario.endpoint}`, params);
  }

  const endTime = new Date();
  const duration = endTime - startTime;

  // Record metrics
  apiCalls.add(1, { scenario: scenario.name });
  responseTime.add(duration, { scenario: scenario.name });
  
  const isError = response.status >= 400;
  errorRate.add(isError, { scenario: scenario.name });

  // Checks
  const checks = {
    'status is 200-299': response.status >= 200 && response.status < 300,
    'response time < 5000ms': duration < 5000,
  };

  // Scenario-specific checks
  if (scenario.name === 'Health Check') {
    checks['health status is healthy'] = response.json() && response.json().status === 'healthy';
  }

  if (scenario.name === 'Pricing Data') {
    checks['has pricing data'] = response.json() && response.json().pricing_data;
  }

  if (scenario.name === 'AI Predictions') {
    checks['has predictions'] = response.json() && (response.json().predictions || response.json().forecast);
  }

  if (scenario.name === 'Executive Report Generation') {
    checks['report generated'] = response.json() && response.json().status === 'success';
  }

  check(response, checks);

  // Random sleep between 1-3 seconds
  sleep(Math.random() * 2 + 1);
}

// Real-time WebSocket connection test
export function websocketTest() {
  const wsUrl = REALTIME_URL.replace('http', 'ws') + '/socket.io/?transport=websocket';
  
  const response = http.get(REALTIME_URL + '/health');
  check(response, {
    'real-time server is healthy': (r) => r.status === 200,
  });
}

// Stress test for specific endpoints
export function stressTest() {
  const endpoints = [
    '/api/pricing-data',
    '/api/optimization-recommendations',
    '/health'
  ];

  endpoints.forEach(endpoint => {
    const response = http.get(`${BASE_URL}${endpoint}`);
    check(response, {
      [`${endpoint} responds successfully`]: (r) => r.status === 200,
      [`${endpoint} response time OK`]: (r) => r.timings.duration < 2000,
    });
  });
}

// Data integrity test
export function dataIntegrityTest() {
  // Test pricing data consistency
  const pricingResponse = http.get(`${BASE_URL}/api/pricing-data`);
  const pricingData = pricingResponse.json();

  check(pricingData, {
    'pricing data has timestamp': (data) => data.timestamp !== undefined,
    'pricing data has providers': (data) => data.pricing_data && Object.keys(data.pricing_data).length > 0,
    'pricing data has valid format': (data) => {
      if (!data.pricing_data) return false;
      
      for (const provider of Object.values(data.pricing_data)) {
        for (const service of Object.values(provider)) {
          for (const instance of Object.values(service)) {
            if (typeof instance.price !== 'number' || instance.price < 0) {
              return false;
            }
          }
        }
      }
      return true;
    },
  });

  // Test AI endpoint data quality
  const aiResponse = http.post(
    `${BASE_URL}/api/ai/predict-costs`,
    JSON.stringify({
      provider: 'aws',
      service: 'ec2',
      days: 7
    }),
    {
      headers: { 'Content-Type': 'application/json' }
    }
  );

  check(aiResponse, {
    'AI prediction has valid structure': (r) => {
      const data = r.json();
      return data && (data.predictions || data.forecast || data.error);
    }
  });
}

// Security test
export function securityTest() {
  // Test for SQL injection
  const maliciousPayload = {
    query: "'; DROP TABLE users; --"
  };

  const response = http.post(
    `${BASE_URL}/api/ai/natural-query`,
    JSON.stringify(maliciousPayload),
    {
      headers: { 'Content-Type': 'application/json' }
    }
  );

  check(response, {
    'SQL injection attempt blocked': (r) => r.status !== 500,
    'No database error exposed': (r) => !r.body.includes('SQL') && !r.body.includes('database'),
  });

  // Test for XSS
  const xssPayload = {
    query: "<script>alert('xss')</script>"
  };

  const xssResponse = http.post(
    `${BASE_URL}/api/ai/natural-query`,
    JSON.stringify(xssPayload),
    {
      headers: { 'Content-Type': 'application/json' }
    }
  );

  check(xssResponse, {
    'XSS attempt handled': (r) => !r.body.includes('<script>'),
  });
}

// Export additional test scenarios
export { websocketTest, stressTest, dataIntegrityTest, securityTest };