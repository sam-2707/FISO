import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Alert,
  Tabs,
  Tab,
  Container,
  IconButton,
  Tooltip,
  Collapse
} from '@mui/material';
import {
  TrendingUp,
  Speed,
  AttachMoney,
  Assessment,
  Psychology,
  Analytics,
  Warning,
  AutoFixHigh,
  Business,
  MonitorHeart,
  ToggleOn,
  ToggleOff,
  BugReport
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import NaturalLanguageInterface from './AI/NaturalLanguageInterface';
import PredictiveAnalytics from './AI/PredictiveAnalytics';
import AnomalyDetection from './AI/AnomalyDetection';
import AutoMLIntegration from './AI/AutoMLIntegration';
import RealTimeStatus from './RealTimeStatus';
import ExecutiveReporting from './ExecutiveReporting';
import ConnectionStatus from './ConnectionStatus';
import LoadingComponent from './LoadingComponent';
import ErrorBoundary from './ErrorBoundary';
import SystemMetrics from './SystemMetrics';
import IntegrationTest from './IntegrationTest';
import { useNotification } from './NotificationProvider';

import apiService from '../services/apiService';
import webSocketService from '../services/webSocketService';

/**
 * CloudDashboard Component
 * 
 * Main dashboard component that provides comprehensive cloud pricing analytics,
 * AI-powered insights, and real-time monitoring capabilities.
 * 
 * Features:
 * - Multi-cloud pricing data visualization
 * - Real-time data streaming via WebSocket
 * - AI predictions and anomaly detection
 * - System metrics monitoring
 * - Executive reporting
 * - Integration testing interface
 * 
 * @returns {JSX.Element} The main dashboard interface
 */
const CloudDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [pricingData, setPricingData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [realTimeEnabled, setRealTimeEnabled] = useState(false);
  const [realTimeData, setRealTimeData] = useState({});
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [showMetrics, setShowMetrics] = useState(false);
  
  // Notification system
  const { showSuccess, showError, showWarning, showInfo } = useNotification();

  // Demo data generation
  const generateDemoData = () => {
    return {
      aws: {
        ec2: {
          't3.micro': { price: 0.0104, confidence: 0.95, trend: 'stable', last_updated: new Date().toISOString() },
          't3.small': { price: 0.0208, confidence: 0.95, trend: 'decreasing', last_updated: new Date().toISOString() },
          'm5.large': { price: 0.096, confidence: 0.95, trend: 'increasing', last_updated: new Date().toISOString() }
        },
        rds: {
          'db.t3.micro': { price: 0.017, confidence: 0.92, trend: 'stable', last_updated: new Date().toISOString() }
        }
      },
      azure: {
        'virtual_machines': {
          'B1s': { price: 0.0104, confidence: 0.93, trend: 'stable', last_updated: new Date().toISOString() },
          'D2s_v3': { price: 0.096, confidence: 0.91, trend: 'decreasing', last_updated: new Date().toISOString() }
        }
      },
      gcp: {
        'compute_engine': {
          'f1-micro': { price: 0.0076, confidence: 0.89, trend: 'increasing', last_updated: new Date().toISOString() },
          'n1-standard-1': { price: 0.0475, confidence: 0.94, trend: 'stable', last_updated: new Date().toISOString() }
        }
      }
    };
  };

  // Calculate metrics from pricing data
  const calculateMetrics = useCallback(() => {
    if (!pricingData) {
      return {
        totalCost: 8420.45,
        potentialSavings: 1247.32,
        activeResources: 234,
        activeAlerts: 7
      };
    }

    let totalCost = 0;
    let resourceCount = 0;

    Object.values(pricingData.pricing_data || {}).forEach(provider => {
      Object.values(provider).forEach(serviceGroup => {
        Object.values(serviceGroup).forEach(resource => {
          if (resource.price) {
            totalCost += resource.price * 730; // Monthly estimate
            resourceCount++;
          }
        });
      });
    });

    return {
      totalCost: totalCost * 10 || 8420.45, // Scale up for demo
      potentialSavings: totalCost * 1.5 || 1247.32,
      activeResources: resourceCount * 10 || 234,
      activeAlerts: Math.floor(Math.random() * 10) + 5
    };
  }, [pricingData]);

  // Format data for charts
  const formatChartData = useCallback(() => {
    return [
      { name: 'AWS', value: 3420, color: '#FF9500' },
      { name: 'Azure', value: 2890, color: '#0078D4' },
      { name: 'GCP', value: 1850, color: '#4285F4' },
      { name: 'Oracle', value: 260, color: '#F80000' }
    ];
  }, []);

  // Generate time series data
  const generateTimeSeriesData = useCallback(() => {
    const now = new Date();
    const data = [];
    
    for (let i = 23; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 60 * 60 * 1000);
      data.push({
        time: time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        AWS: 140 + Math.random() * 40,
        Azure: 120 + Math.random() * 30,
        GCP: 90 + Math.random() * 25,
        Oracle: 35 + Math.random() * 15
      });
    }
    
    return data;
  }, []); // Remove timeSeriesKey dependency as it's not used in the function

  // Fetch data from API
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const pricingResponse = await apiService.getPricingData();
        
        setPricingData(pricingResponse);
        
        // Show success notification on successful load
        showSuccess('Dashboard data loaded successfully', {
          title: 'Connected to Production API'
        });
        
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        
        if (err.code === 'NETWORK_ERROR') {
          setError('Network connection failed - Check if servers are running');
          showError('Unable to connect to backend servers', {
            title: 'Connection Failed',
            autoHideDuration: 8000
          });
        } else {
          setError(`Data fetch error: ${err.message} - Using demo data`);
          showWarning(err.userMessage || 'Using cached data due to server issue', {
            title: 'API Warning'
          });
        }
        
        // Set demo data as fallback
        setPricingData({
          timestamp: new Date().toISOString(),
          pricing_data: generateDemoData(),
          total_data_points: 42
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    
    if (realTimeEnabled) {
      const interval = setInterval(() => {
        fetchData();
      }, 30000);
      return () => clearInterval(interval);
    }
  }, [realTimeEnabled, showError, showSuccess, showWarning]); // Removed pricingData to prevent infinite re-render

  // WebSocket connection
  useEffect(() => {
    const initializeWebSocket = async () => {
      try {
        showInfo('Connecting to real-time data stream...', {
          title: 'Real-time Connection',
          autoHideDuration: 3000
        });
        
        await webSocketService.connect();
        setConnectionStatus(webSocketService.getConnectionStatus());

        webSocketService.subscribeToPricingUpdates((data) => {
          setRealTimeData(prev => ({
            ...prev,
            pricing: data,
            lastUpdate: new Date().toISOString()
          }));
        });

        showSuccess('Real-time data connection established', {
          title: 'Connected'
        });

      } catch (error) {
        console.warn('WebSocket connection failed:', error);
        setConnectionStatus('disconnected');
        showWarning('Real-time connection failed - using polling fallback', {
          title: 'Connection Issue'
        });
      }
    };

    if (realTimeEnabled) {
      initializeWebSocket();
    } else {
      // Disconnect when real-time is disabled
      webSocketService.disconnect();
      setConnectionStatus('disconnected');
      showInfo('Real-time updates disabled', {
        title: 'Real-time Mode',
        autoHideDuration: 2000
      });
    }

    return () => {
      if (realTimeEnabled) {
        webSocketService.disconnect();
      }
    };
  }, [realTimeEnabled, showInfo, showSuccess, showWarning]); // Added missing dependencies

  const refreshData = async () => {
    try {
      setLoading(true);
      showInfo('Refreshing dashboard data...', { 
        title: 'Data Refresh', 
        autoHideDuration: 2000 
      });
      
      const pricingResponse = await apiService.getPricingData();
      
      setPricingData(pricingResponse);
      setError(null);
      
      showSuccess('Dashboard data refreshed successfully', {
        title: 'Refresh Complete'
      });
    } catch (err) {
      console.error('Manual refresh failed:', err);
      setError(`Refresh failed: ${err.message} - Using cached data`);
      showError(err.userMessage || 'Failed to refresh data - using cached version', {
        title: 'Refresh Failed',
        autoHideDuration: 6000
      });
    } finally {
      setLoading(false);
    }
  };

  // Memoize expensive calculations to prevent unnecessary re-computation
  const metrics = useMemo(() => calculateMetrics(), [calculateMetrics]);
  const chartData = useMemo(() => formatChartData(), [formatChartData]);
  const timeSeriesData = useMemo(() => generateTimeSeriesData(), [generateTimeSeriesData]);

  if (loading) {
    return (
      <LoadingComponent 
        type="analytics"
        message="Loading cloud analytics dashboard..."
        showDetails={true}
        fullScreen={false}
      />
    );
  }

  return (
    <ErrorBoundary>
      <Box sx={{ 
        minHeight: '100vh',
        backgroundColor: '#f7fafc',
      }}>
      {/* Hero Section */}
      <Box
        sx={{
          backgroundColor: '#ffffff',
          py: { xs: 4, md: 6 },
          textAlign: 'center',
          borderBottom: '1px solid rgba(226, 232, 240, 0.8)',
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            gap: 3, 
            mb: 3,
            flexDirection: { xs: 'column', sm: 'row' }
          }}>
            <img 
              src="/atharman_logo.svg" 
              alt="Atharman Logo" 
              style={{ 
                height: '60px', 
                width: 'auto'
              }}
              onError={(e) => {
                console.log('Logo failed to load, using fallback');
                e.target.style.display = 'none';
              }}
            />
          </Box>
          <Typography 
            variant="h1" 
            component="h1" 
            sx={{ 
              fontWeight: 700,
              fontSize: { xs: '2rem', md: '2.5rem' },
              color: '#2d3748',
              mb: 2
            }}
          >
            Atharman
          </Typography>
          <Typography 
            variant="h5" 
            sx={{ 
              maxWidth: 600, 
              mx: 'auto',
              fontWeight: 400,
              fontSize: { xs: '1.125rem', md: '1.25rem' },
              lineHeight: 1.5,
              color: '#4a5568',
              mb: 3
            }}
          >
            AI-Powered Financial Intelligence & Operations Platform
          </Typography>
          <Box sx={{ 
            display: 'flex', 
            gap: 1.5, 
            justifyContent: 'center',
            flexWrap: 'wrap'
          }}>
            <Chip 
              label="Real-Time Analytics" 
              variant="outlined"
              sx={{ 
                borderColor: '#3182ce',
                color: '#3182ce',
                fontWeight: 500
              }} 
            />
            <Chip 
              label="AI Predictions" 
              variant="outlined"
              sx={{ 
                borderColor: '#38a169',
                color: '#38a169',
                fontWeight: 500
              }} 
            />
            <Chip 
              label="Smart Optimization" 
              variant="outlined"
              sx={{ 
                borderColor: '#ed8936',
                color: '#ed8936',
                fontWeight: 500
              }} 
            />
          </Box>
        </Container>
      </Box>

      {/* Main Content */}
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Connection Status */}
        <Box sx={{ mb: 3 }}>
          <ConnectionStatus />
        </Box>
        
        {/* Tab Navigation */}
        <Box sx={{ 
          backgroundColor: '#ffffff',
          borderRadius: 2,
          p: 1,
          mb: 4,
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          border: '1px solid rgba(226, 232, 240, 0.8)'
        }}>
          <Tabs 
            value={activeTab} 
            onChange={(e, newValue) => setActiveTab(newValue)}
            variant="scrollable"
            scrollButtons="auto"
            sx={{
              '& .MuiTab-root': {
                minHeight: 48,
                textTransform: 'none',
                fontWeight: 500,
                fontSize: '0.875rem',
                color: '#718096',
                borderRadius: 1,
                margin: '4px',
                '&.Mui-selected': {
                  color: '#2d3748',
                  backgroundColor: '#f7fafc',
                  fontWeight: 600,
                },
              },
              '& .MuiTabs-indicator': {
                display: 'none',
              }
            }}
          >
            <Tab icon={<Assessment />} label="Dashboard Overview" />
            <Tab icon={<Psychology />} label="AI Predictions" />
            <Tab icon={<Analytics />} label="Natural Language" />
            <Tab icon={<Warning />} label="Anomaly Detection" />
            <Tab icon={<AutoFixHigh />} label="AutoML" />
            <Tab icon={<Business />} label="Executive Reports" />
            <Tab icon={<MonitorHeart />} label="System Metrics" />
            <Tab icon={<BugReport />} label="Integration Test" />
          </Tabs>
        </Box>
        
        {/* System Metrics Toggle */}
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          mb: 2 
        }}>
          <Box>
            {error && (
              <Alert 
                severity="warning" 
                sx={{ 
                  borderRadius: 2,
                }}
              >
                {error}
              </Alert>
            )}
          </Box>
          <Tooltip title={showMetrics ? "Hide System Metrics" : "Show System Metrics"}>
            <IconButton
              onClick={() => setShowMetrics(!showMetrics)}
              sx={{
                color: showMetrics ? 'primary.main' : 'text.secondary',
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  transform: 'scale(1.1)',
                  backgroundColor: 'rgba(25, 118, 210, 0.04)'
                }
              }}
            >
              {showMetrics ? <ToggleOn /> : <ToggleOff />}
            </IconButton>
          </Tooltip>
        </Box>

        {/* System Metrics Panel */}
        <Collapse in={showMetrics}>
          <Box sx={{ mb: 3 }}>
            <SystemMetrics />
          </Box>
        </Collapse>

        {/* Real-Time Status */}
        <RealTimeStatus
          connectionStatus={connectionStatus}
          realTimeData={realTimeData}
          realTimeEnabled={realTimeEnabled}
          onToggleRealTime={() => setRealTimeEnabled(prev => !prev)}
          onRefresh={refreshData}
        />
        
        {/* Tab Content */}
        {activeTab === 0 && (
          <>
            {/* Metrics Cards */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 2 }}>
                      <Box sx={{
                        p: 1.5,
                        borderRadius: 2,
                        backgroundColor: '#e6f3ff',
                        color: '#3182ce'
                      }}>
                        <Speed sx={{ fontSize: 24 }} />
                      </Box>
                      <Chip 
                        label="↗ 0.2%" 
                        size="small"
                        color="error"
                        variant="outlined"
                      />
                    </Box>
                    <Typography color="textSecondary" variant="body2" gutterBottom>
                      Total Monthly Cost
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 600, color: '#2d3748' }}>
                      ${metrics.totalCost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 2 }}>
                      <Box sx={{
                        p: 1.5,
                        borderRadius: 2,
                        backgroundColor: '#f0fff4',
                        color: '#38a169'
                      }}>
                        <AttachMoney sx={{ fontSize: 24 }} />
                      </Box>
                      <Chip 
                        label="↗ 17.5%" 
                        size="small"
                        color="success"
                        variant="outlined"
                      />
                    </Box>
                    <Typography color="textSecondary" variant="body2" gutterBottom>
                      Potential Savings
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 600, color: '#2d3748' }}>
                      ${metrics.potentialSavings.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 2 }}>
                      <Box sx={{
                        p: 1.5,
                        borderRadius: 2,
                        backgroundColor: '#f0f9ff',
                        color: '#3182ce'
                      }}>
                        <Assessment sx={{ fontSize: 24 }} />
                      </Box>
                      <Chip 
                        label="↘ 2.2%" 
                        size="small"
                        color="error"
                        variant="outlined"
                      />
                    </Box>
                    <Typography color="textSecondary" variant="body2" gutterBottom>
                      Active Resources
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 600, color: '#2d3748' }}>
                      {metrics.activeResources}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 2 }}>
                      <Box sx={{
                        p: 1.5,
                        borderRadius: 2,
                        backgroundColor: '#fffbeb',
                        color: '#ed8936'
                      }}>
                        <TrendingUp sx={{ fontSize: 24 }} />
                      </Box>
                      <Chip 
                        label="↗ 12.5%" 
                        size="small"
                        color="warning"
                        variant="outlined"
                      />
                    </Box>
                    <Typography color="textSecondary" variant="body2" gutterBottom>
                      Active Alerts
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 600, color: '#2d3748' }}>
                      {metrics.activeAlerts}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Charts Section */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
              {/* Real-time Pricing Trends */}
              <Grid item xs={12} lg={8}>
                <Card sx={{ minHeight: 400 }}>
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                      <Typography variant="h6" sx={{ fontWeight: 600, color: '#2d3748' }}>
                        📊 Real-Time Pricing Trends
                      </Typography>
                      <Chip 
                        label="Live Data" 
                        size="small"
                        color="success"
                        variant="outlined"
                      />
                    </Box>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={timeSeriesData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                        <XAxis dataKey="time" tick={{ fontSize: 12 }} />
                        <YAxis tick={{ fontSize: 12 }} />
                        <RechartsTooltip />
                        <Legend />
                        <Line type="monotone" dataKey="AWS" stroke="#FF9500" strokeWidth={2} />
                        <Line type="monotone" dataKey="Azure" stroke="#0078D4" strokeWidth={2} />
                        <Line type="monotone" dataKey="GCP" stroke="#4285F4" strokeWidth={2} />
                        <Line type="monotone" dataKey="Oracle" stroke="#F80000" strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </Grid>

              {/* Provider Comparison */}
              <Grid item xs={12} lg={4}>
                <Card sx={{ minHeight: 400 }}>
                  <CardContent sx={{ p: 3 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600, color: '#2d3748', mb: 3 }}>
                      🏢 Provider Cost Breakdown
                    </Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={chartData}
                          cx="50%"
                          cy="50%"
                          innerRadius={40}
                          outerRadius={80}
                          paddingAngle={5}
                          dataKey="value"
                        >
                          {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <RechartsTooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </>
        )}

        {activeTab === 1 && <PredictiveAnalytics />}
        {activeTab === 2 && <NaturalLanguageInterface />}
        {activeTab === 3 && <AnomalyDetection />}
        {activeTab === 4 && <AutoMLIntegration />}
        {activeTab === 5 && <ExecutiveReporting />}
        {activeTab === 6 && (
          <Box sx={{ mt: 2 }}>
            <SystemMetrics expanded={true} />
          </Box>
        )}
        {activeTab === 7 && <IntegrationTest />}
      </Container>
    </Box>
    </ErrorBoundary>
  );
};

export default CloudDashboard;