import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Switch,
  FormControlLabel,
  Button,
  TextField,
  Slider,
  Paper
} from '@mui/material';
import {
  TrendingUp,
  Speed,
  Security,
  LocationOn,
  AttachMoney,
  Assessment
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter
} from 'recharts';

import { apiService } from '../services/apiService';

const OperationsDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pricingData, setPricingData] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [tabValue, setTabValue] = useState(0);
  const [selectionCriteria, setSelectionCriteria] = useState({
    costWeight: 40,
    performanceWeight: 30,
    reliabilityWeight: 20,
    complianceWeight: 10,
    maxBudget: 1000,
    region: 'us-east-1'
  });
  const [realTimeEnabled, setRealTimeEnabled] = useState(true);

  // Real-time data refresh
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [pricingResponse, recommendationsResponse] = await Promise.all([
          apiService.getRealTimePricing(),
          apiService.getRecommendations()
        ]);
        setPricingData(pricingResponse);
        setRecommendations(recommendationsResponse);
        generateAlerts(pricingResponse, recommendationsResponse);
        setError(null);
      } catch (err) {
        setError('Failed to fetch data: ' + err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    
    if (realTimeEnabled) {
      const interval = setInterval(fetchData, 30000); // 30-second refresh
      return () => clearInterval(interval);
    }
  }, [realTimeEnabled]);

  const generateAlerts = useCallback((pricing, recs) => {
    const newAlerts = [];
    
    // Cost spike alerts
    if (pricing?.pricing_data) {
      // pricing_data has nested structure: provider -> serviceType -> instanceType -> details
      Object.entries(pricing.pricing_data).forEach(([provider, providerData]) => {
        Object.entries(providerData).forEach(([serviceType, services]) => {
          Object.entries(services).forEach(([instanceType, details]) => {
            if (details && details.trend === 'increasing' && details.price > 0.1) {
              newAlerts.push({
                type: 'warning',
                title: 'Price Increase Detected',
                message: `${provider.toUpperCase()} ${serviceType} ${instanceType} prices increased`,
                timestamp: new Date().toISOString(),
                actionable: true,
                action: 'Consider switching to alternative provider'
              });
            }
          });
        });
      });
    }

    // Budget threshold alerts
    const totalCost = calculateTotalCost();
    if (totalCost > selectionCriteria.maxBudget * 0.8) {
      newAlerts.push({
        type: 'error',
        title: 'Budget Threshold Alert',
        message: `Current costs (${totalCost.toFixed(2)}) approaching budget limit (${selectionCriteria.maxBudget})`,
        timestamp: new Date().toISOString(),
        actionable: true,
        action: 'Review cost optimization recommendations'
      });
    }

    setAlerts(newAlerts);
  }, [selectionCriteria.maxBudget]);

  const calculateTotalCost = () => {
    if (!pricingData?.pricing_data) return 0;
    
    let total = 0;
    Object.entries(pricingData.pricing_data).forEach(([provider, providerData]) => {
      Object.entries(providerData).forEach(([serviceType, services]) => {
        Object.entries(services).forEach(([instanceType, details]) => {
          total += details.price || 0;
        });
      });
    });
    return total;
  };

  const getOptimalProvider = () => {
    if (!pricingData?.pricing_data) return null;

    const providers = ['aws', 'azure', 'gcp'];
    const scores = providers.map(provider => {
      const providerData = pricingData.pricing_data[provider];
      
      // Check if provider data exists and has services
      if (!providerData || typeof providerData !== 'object') {
        return { provider, score: 0 };
      }

      // Calculate average cost across all services for this provider
      let totalCost = 0;
      let serviceCount = 0;
      
      Object.entries(providerData).forEach(([serviceType, services]) => {
        Object.entries(services).forEach(([instanceType, details]) => {
          totalCost += details.price || 0;
          serviceCount++;
        });
      });
      
      if (serviceCount === 0) return { provider, score: 0 };
      
      const avgCost = totalCost / serviceCount;
      
      // Get all services across all providers for comparison
      const allCosts = [];
      Object.values(pricingData.pricing_data).forEach(providerData => {
        Object.values(providerData).forEach(services => {
          Object.values(services).forEach(details => {
            allCosts.push(details.price || 0);
          });
        });
      });
      
      const maxCost = Math.max(...allCosts);
      
      // Calculate weighted score based on user criteria
      const costScore = maxCost > 0 ? (1 - (avgCost / maxCost)) * 100 : 0;
      const performanceScore = 85; // Mock baseline score
      const reliabilityScore = (provider === 'aws' ? 95 : provider === 'azure' ? 92 : 90); // Mock scores
      const complianceScore = (provider === 'aws' ? 98 : provider === 'azure' ? 95 : 88); // Mock scores

      const totalScore = (
        (costScore * selectionCriteria.costWeight) +
        (performanceScore * selectionCriteria.performanceWeight) +
        (reliabilityScore * selectionCriteria.reliabilityWeight) +
        (complianceScore * selectionCriteria.complianceWeight)
      ) / 100;

      return { provider, score: totalScore, costScore, performanceScore, reliabilityScore, complianceScore };
    });

    return scores.sort((a, b) => b.score - a.score);
  };

  const formatChartData = () => {
    if (!pricingData?.pricing_data) return [];
    
    const chartItems = [];
    Object.entries(pricingData.pricing_data).forEach(([provider, providerData]) => {
      Object.entries(providerData).forEach(([serviceType, services]) => {
        Object.entries(services).forEach(([instanceType, details]) => {
          chartItems.push({
            name: `${provider.toUpperCase()} ${serviceType} ${instanceType}`,
            cost: details.price || 0,
            confidence: (details.confidence * 100) || 85,
            provider: provider.toUpperCase(),
            performance: Math.random() * 100, // Mock performance data
            reliability: (details.confidence * 100) || 85,
            trend: details.trend || 'stable'
          });
        });
      });
    });
    
    return chartItems;
  };

  const providerColors = {
    AWS: '#FF9500',
    AZURE: '#0078D4',
    GCP: '#4285F4',
    aws: '#FF9500',
    azure: '#0078D4',
    gcp: '#4285F4'
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        {error}
      </Alert>
    );
  }

  const optimalProviders = getOptimalProvider();
  const chartData = formatChartData();
  const totalCost = calculateTotalCost();

  return (
    <Box sx={{ p: 3, pt: 1, bgcolor: '#f5f5f5', minHeight: '100vh' }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ color: '#1976d2', fontWeight: 'bold' }}>
          🚀 FISO Operations Intelligence Dashboard
        </Typography>
        <Typography variant="h6" color="textSecondary" gutterBottom>
          Real-time Cloud Operations & Cost Optimization Platform
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={realTimeEnabled}
                onChange={(e) => setRealTimeEnabled(e.target.checked)}
                color="primary"
              />
            }
            label="Real-time Updates"
          />
          
          <Chip 
            label={`Total Cost: $${totalCost.toFixed(2)}`}
            color="primary"
            variant="outlined"
            icon={<AttachMoney />}
          />
          
          <Chip 
            label={`Last Updated: ${new Date().toLocaleTimeString()}`}
            color="secondary"
            variant="outlined"
          />
        </Box>
      </Box>

      {/* Alerts Section */}
      {alerts.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            🚨 Active Alerts
          </Typography>
          {alerts.map((alert, index) => (
            <Alert 
              key={index} 
              severity={alert.type} 
              sx={{ mb: 1 }}
              action={
                alert.actionable && (
                  <Button color="inherit" size="small">
                    {alert.action}
                  </Button>
                )
              }
            >
              <strong>{alert.title}</strong>: {alert.message}
            </Alert>
          ))}
        </Box>
      )}

      {/* Tabs for Different Views */}
      <Box sx={{ width: '100%' }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)} sx={{ mb: 3 }}>
          <Tab label="Cost Analysis" icon={<AttachMoney />} />
          <Tab label="Performance Metrics" icon={<Speed />} />
          <Tab label="Provider Comparison" icon={<Assessment />} />
          <Tab label="Optimization" icon={<TrendingUp />} />
        </Tabs>

        {/* Tab Panel 0: Cost Analysis */}
        {tabValue === 0 && (
          <Grid container spacing={3}>
            {/* Real-time Cost Chart */}
            <Grid item xs={12} lg={8}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Real-time Cost Analysis
                  </Typography>
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="cost" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>

            {/* Cost Breakdown Pie Chart */}
            <Grid item xs={12} lg={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Cost Distribution
                  </Typography>
                  <ResponsiveContainer width="100%" height={400}>
                    <PieChart>
                      <Pie
                        data={chartData.slice(0, 6)}
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="cost"
                        label
                      >
                        {chartData.slice(0, 6).map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={providerColors[entry.provider] || '#8884d8'} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Tab Panel 1: Performance Metrics */}
        {tabValue === 1 && (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Performance vs Cost Analysis
                  </Typography>
                  <ResponsiveContainer width="100%" height={400}>
                    <ScatterChart data={chartData}>
                      <CartesianGrid />
                      <XAxis dataKey="cost" name="Cost" />
                      <YAxis dataKey="performance" name="Performance" />
                      <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                      <Scatter dataKey="cost" fill="#8884d8" />
                    </ScatterChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Tab Panel 2: Provider Comparison */}
        {tabValue === 2 && optimalProviders && (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                🏆 Optimal Provider Rankings
              </Typography>
              {optimalProviders.slice(0, 3).map((provider, index) => (
                <Card key={provider.provider} sx={{ mb: 2, border: index === 0 ? '2px solid #4CAF50' : 'none' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box>
                        <Typography variant="h6" sx={{ color: providerColors[provider.provider.toUpperCase()] }}>
                          #{index + 1} {provider.provider.toUpperCase()}
                          {index === 0 && <Chip label="RECOMMENDED" color="success" size="small" sx={{ ml: 1 }} />}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          Overall Score: {provider.score.toFixed(1)}/100
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Chip label={`Cost: ${provider.costScore.toFixed(0)}`} size="small" />
                        <Chip label={`Performance: ${provider.performanceScore.toFixed(0)}`} size="small" />
                        <Chip label={`Reliability: ${provider.reliabilityScore.toFixed(0)}`} size="small" />
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </Grid>
          </Grid>
        )}

        {/* Tab Panel 3: Optimization */}
        {tabValue === 3 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Cost Optimization Criteria
                  </Typography>
                  
                  <Box sx={{ mt: 2 }}>
                    <Typography gutterBottom>Cost Weight: {selectionCriteria.costWeight}%</Typography>
                    <Slider
                      value={selectionCriteria.costWeight}
                      onChange={(e, newValue) => setSelectionCriteria(prev => ({ ...prev, costWeight: newValue }))}
                      valueLabelDisplay="auto"
                      min={0}
                      max={100}
                    />
                  </Box>

                  <Box sx={{ mt: 2 }}>
                    <Typography gutterBottom>Performance Weight: {selectionCriteria.performanceWeight}%</Typography>
                    <Slider
                      value={selectionCriteria.performanceWeight}
                      onChange={(e, newValue) => setSelectionCriteria(prev => ({ ...prev, performanceWeight: newValue }))}
                      valueLabelDisplay="auto"
                      min={0}
                      max={100}
                    />
                  </Box>

                  <Box sx={{ mt: 2 }}>
                    <Typography gutterBottom>Reliability Weight: {selectionCriteria.reliabilityWeight}%</Typography>
                    <Slider
                      value={selectionCriteria.reliabilityWeight}
                      onChange={(e, newValue) => setSelectionCriteria(prev => ({ ...prev, reliabilityWeight: newValue }))}
                      valueLabelDisplay="auto"
                      min={0}
                      max={100}
                    />
                  </Box>

                  <TextField
                    fullWidth
                    label="Max Budget ($)"
                    type="number"
                    value={selectionCriteria.maxBudget}
                    onChange={(e) => setSelectionCriteria(prev => ({ ...prev, maxBudget: parseInt(e.target.value) }))}
                    sx={{ mt: 2 }}
                  />
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    💡 AI Recommendations
                  </Typography>
                  
                  {recommendations?.recommendations?.slice(0, 5).map((rec, index) => (
                    <Alert key={index} severity="info" sx={{ mb: 1 }}>
                      <Typography variant="body2">
                        <strong>{rec.type}:</strong> {rec.description}
                      </Typography>
                      {rec.potential_savings && (
                        <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                          Potential savings: ${rec.potential_savings}
                        </Typography>
                      )}
                    </Alert>
                  )) || (
                    <Typography color="textSecondary">
                      Loading AI recommendations...
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </Box>
    </Box>
  );
};

export default OperationsDashboard;