import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Switch,
  FormControlLabel,
  Chip,
  Alert,
  Tabs,
  Tab,
  Container,
  useTheme,
  alpha,
  Fade,
  Grow,
  Slide
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Assessment,
  Psychology,
  Analytics,
  Warning,
  AutoFixHigh,
  Business,
  MonitorHeart,
  BugReport,
  Cloud,
  AttachMoney,
  Speed,
  Notifications
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
  ComposedChart
} from 'recharts';

// Import AI components
import PredictiveAnalytics from './AI/PredictiveAnalytics';
import AnomalyDetection from './AI/AnomalyDetection';
import AutoMLIntegration from './AI/AutoMLIntegration';
import NaturalLanguageInterface from './AI/NaturalLanguageInterface';
import ExecutiveReporting from './ExecutiveReporting';
import SystemMetrics from './SystemMetrics';

const ModernAtharmanDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [darkMode, setDarkMode] = useState(true);
  const [animationsEnabled, setAnimationsEnabled] = useState(true);
  const [liveData, setLiveData] = useState({});
  const theme = useTheme();

  // Real-time pricing data (simulated)
  const [pricingData, setPricingData] = useState([]);
  const [providerComparison, setProviderComparison] = useState([]);
  const [metrics, setMetrics] = useState({
    totalCost: 145.07,
    potentialSavings: 21.76,
    activeResources: 8,
    activeAlerts: 0,
    trends: {
      cost: -0.32,
      savings: 17.5,
      resources: -2.2,
      alerts: 12.5
    }
  });

  // Generate realistic pricing data
  useEffect(() => {
    const generatePricingData = () => {
      const hours = Array.from({ length: 24 }, (_, i) => {
        const hour = i.toString().padStart(2, '0') + ':0';
        return {
          time: hour,
          AWS: Math.random() * 0.4 + 0.1,
          Azure: Math.random() * 0.4 + 0.1,
          GCP: Math.random() * 0.4 + 0.1,
          Oracle: Math.random() * 0.4 + 0.1
        };
      });
      setPricingData(hours);
    };

    const generateProviderComparison = () => {
      setProviderComparison([
        { provider: 'AWS', cost: 45.2, instances: 12, efficiency: 85 },
        { provider: 'Azure', cost: 38.7, instances: 8, efficiency: 92 },
        { provider: 'GCP', cost: 29.1, instances: 6, efficiency: 88 },
        { provider: 'Oracle', cost: 32.0, instances: 4, efficiency: 78 }
      ]);
    };

    generatePricingData();
    generateProviderComparison();

    // Update data every 30 seconds
    const interval = setInterval(() => {
      generatePricingData();
      setMetrics(prev => ({
        ...prev,
        totalCost: prev.totalCost + (Math.random() - 0.5) * 2,
        potentialSavings: prev.potentialSavings + (Math.random() - 0.5) * 1
      }));
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const darkTheme = {
    background: darkMode ? '#0a0e1a' : '#f8fafc',
    surface: darkMode ? '#1a1f2e' : '#ffffff',
    primary: darkMode ? '#3b82f6' : '#2563eb',
    secondary: darkMode ? '#8b5cf6' : '#7c3aed',
    text: darkMode ? '#f1f5f9' : '#1e293b',
    textSecondary: darkMode ? '#94a3b8' : '#64748b',
    accent: darkMode ? '#06d6a0' : '#059669',
    warning: darkMode ? '#f59e0b' : '#d97706',
    error: darkMode ? '#ef4444' : '#dc2626'
  };

  const MetricCard = ({ title, value, trend, icon, color, prefix = '', suffix = '' }) => (
    <Grow in={true} timeout={800}>
      <Card sx={{
        background: darkMode 
          ? `linear-gradient(135deg, ${darkTheme.surface} 0%, ${alpha(color, 0.1)} 100%)`
          : `linear-gradient(135deg, ${darkTheme.surface} 0%, ${alpha(color, 0.05)} 100%)`,
        border: `1px solid ${alpha(color, 0.2)}`,
        borderRadius: 3,
        transition: 'all 0.3s ease-in-out',
        '&:hover': {
          transform: animationsEnabled ? 'translateY(-4px)' : 'none',
          boxShadow: `0 12px 40px ${alpha(color, 0.3)}`,
          border: `1px solid ${alpha(color, 0.4)}`
        }
      }}>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box sx={{
              p: 1.5,
              borderRadius: 2,
              background: `linear-gradient(135deg, ${color} 0%, ${alpha(color, 0.8)} 100%)`,
              color: 'white',
              boxShadow: `0 4px 20px ${alpha(color, 0.4)}`
            }}>
              {icon}
            </Box>
            <Chip
              label={`${trend > 0 ? '↗' : '↘'} ${Math.abs(trend)}%`}
              size="small"
              sx={{
                backgroundColor: trend > 0 ? alpha(darkTheme.accent, 0.2) : alpha(darkTheme.error, 0.2),
                color: trend > 0 ? darkTheme.accent : darkTheme.error,
                fontWeight: 600,
                fontSize: '0.75rem'
              }}
            />
          </Box>
          <Typography variant="body2" sx={{ color: darkTheme.textSecondary, mb: 1, fontWeight: 500 }}>
            {title}
          </Typography>
          <Typography variant="h4" sx={{ 
            fontWeight: 700, 
            color: darkTheme.text,
            fontSize: '2rem',
            background: `linear-gradient(135deg, ${color} 0%, ${alpha(color, 0.7)} 100%)`,
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            {prefix}{typeof value === 'number' ? value.toLocaleString() : value}{suffix}
          </Typography>
        </CardContent>
      </Card>
    </Grow>
  );

  const tabs = [
    { label: '📊 Dashboard Overview', icon: <Assessment /> },
    { label: '🤖 AI Predictions', icon: <Psychology /> },
    { label: '💬 AI Assistant', icon: <Analytics /> },
    { label: '⚠️ Anomaly Detection', icon: <Warning /> },
    { label: '🎛️ AutoML Engine', icon: <AutoFixHigh /> },
    { label: '📈 Executive Reports', icon: <Business /> },
    { label: '🔧 System Metrics', icon: <MonitorHeart /> },
    { label: '🧪 Integration Test', icon: <BugReport /> }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 0:
        return (
          <Fade in={true} timeout={600}>
            <Box>
              {/* Metrics Cards */}
              <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={6} md={3}>
                  <MetricCard
                    title="Total Monthly Cost"
                    value={metrics.totalCost}
                    trend={metrics.trends.cost}
                    icon={<AttachMoney />}
                    color={darkTheme.primary}
                    prefix="$"
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <MetricCard
                    title="Potential Savings"
                    value={metrics.potentialSavings}
                    trend={metrics.trends.savings}
                    icon={<TrendingUp />}
                    color={darkTheme.accent}
                    prefix="$"
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <MetricCard
                    title="Active Resources"
                    value={metrics.activeResources}
                    trend={metrics.trends.resources}
                    icon={<Cloud />}
                    color={darkTheme.secondary}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <MetricCard
                    title="Active Alerts"
                    value={metrics.activeAlerts}
                    trend={metrics.trends.alerts}
                    icon={<Notifications />}
                    color={darkTheme.warning}
                  />
                </Grid>
              </Grid>

              {/* Charts Section */}
              <Grid container spacing={3}>
                <Grid item xs={12} lg={8}>
                  <Slide direction="up" in={true} timeout={800}>
                    <Card sx={{
                      background: darkTheme.surface,
                      border: `1px solid ${alpha(darkTheme.primary, 0.2)}`,
                      borderRadius: 3,
                      overflow: 'hidden'
                    }}>
                      <CardContent sx={{ p: 3 }}>
                        <Typography variant="h6" sx={{ 
                          color: darkTheme.text, 
                          mb: 3, 
                          fontWeight: 600,
                          display: 'flex',
                          alignItems: 'center',
                          gap: 1
                        }}>
                          📈 Real-Time Pricing Trends - Live Data
                        </Typography>
                        <ResponsiveContainer width="100%" height={300}>
                          <LineChart data={pricingData}>
                            <CartesianGrid strokeDasharray="3 3" stroke={alpha(darkTheme.text, 0.1)} />
                            <XAxis 
                              dataKey="time" 
                              stroke={darkTheme.textSecondary}
                              fontSize={12}
                            />
                            <YAxis 
                              stroke={darkTheme.textSecondary}
                              fontSize={12}
                            />
                            <Tooltip 
                              contentStyle={{
                                backgroundColor: darkTheme.surface,
                                border: `1px solid ${alpha(darkTheme.primary, 0.3)}`,
                                borderRadius: 8,
                                color: darkTheme.text
                              }}
                            />
                            <Legend />
                            <Line 
                              type="monotone" 
                              dataKey="AWS" 
                              stroke="#ff6b35" 
                              strokeWidth={3}
                              dot={{ fill: '#ff6b35', strokeWidth: 2, r: 4 }}
                            />
                            <Line 
                              type="monotone" 
                              dataKey="Azure" 
                              stroke="#0078d4" 
                              strokeWidth={3}
                              dot={{ fill: '#0078d4', strokeWidth: 2, r: 4 }}
                            />
                            <Line 
                              type="monotone" 
                              dataKey="GCP" 
                              stroke="#4285f4" 
                              strokeWidth={3}
                              dot={{ fill: '#4285f4', strokeWidth: 2, r: 4 }}
                            />
                            <Line 
                              type="monotone" 
                              dataKey="Oracle" 
                              stroke="#f80000" 
                              strokeWidth={3}
                              dot={{ fill: '#f80000', strokeWidth: 2, r: 4 }}
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </CardContent>
                    </Card>
                  </Slide>
                </Grid>

                <Grid item xs={12} lg={4}>
                  <Slide direction="left" in={true} timeout={1000}>
                    <Card sx={{
                      background: darkTheme.surface,
                      border: `1px solid ${alpha(darkTheme.secondary, 0.2)}`,
                      borderRadius: 3,
                      height: '100%'
                    }}>
                      <CardContent sx={{ p: 3 }}>
                        <Typography variant="h6" sx={{ 
                          color: darkTheme.text, 
                          mb: 3, 
                          fontWeight: 600,
                          display: 'flex',
                          alignItems: 'center',
                          gap: 1
                        }}>
                          ☁️ Multi-Cloud Provider Comparison
                        </Typography>
                        <ResponsiveContainer width="100%" height={250}>
                          <BarChart data={providerComparison}>
                            <CartesianGrid strokeDasharray="3 3" stroke={alpha(darkTheme.text, 0.1)} />
                            <XAxis 
                              dataKey="provider" 
                              stroke={darkTheme.textSecondary}
                              fontSize={12}
                            />
                            <YAxis 
                              stroke={darkTheme.textSecondary}
                              fontSize={12}
                            />
                            <Tooltip 
                              contentStyle={{
                                backgroundColor: darkTheme.surface,
                                border: `1px solid ${alpha(darkTheme.secondary, 0.3)}`,
                                borderRadius: 8,
                                color: darkTheme.text
                              }}
                            />
                            <Bar 
                              dataKey="cost" 
                              fill={darkTheme.secondary}
                              radius={[4, 4, 0, 0]}
                            />
                          </BarChart>
                        </ResponsiveContainer>
                      </CardContent>
                    </Card>
                  </Slide>
                </Grid>
              </Grid>
            </Box>
          </Fade>
        );
      case 1:
        return <PredictiveAnalytics pricingData={pricingData} />;
      case 2:
        return <NaturalLanguageInterface />;
      case 3:
        return <AnomalyDetection pricingData={pricingData} />;
      case 4:
        return <AutoMLIntegration pricingData={pricingData} />;
      case 5:
        return <ExecutiveReporting />;
      case 6:
        return <SystemMetrics expanded={true} />;
      case 7:
        return (
          <Card sx={{ background: darkTheme.surface, border: `1px solid ${alpha(darkTheme.primary, 0.2)}` }}>
            <CardContent>
              <Typography variant="h5" sx={{ color: darkTheme.text, mb: 2 }}>
                🧪 Integration Test Suite
              </Typography>
              <Typography variant="body1" sx={{ color: darkTheme.textSecondary }}>
                Integration testing interface coming soon...
              </Typography>
            </CardContent>
          </Card>
        );
      default:
        return null;
    }
  };

  return (
    <Box sx={{ 
      minHeight: '100vh', 
      background: darkMode 
        ? `linear-gradient(135deg, ${darkTheme.background} 0%, #0f172a 100%)`
        : `linear-gradient(135deg, ${darkTheme.background} 0%, #f1f5f9 100%)`,
      transition: 'all 0.3s ease-in-out'
    }}>
      {/* Header */}
      <Box sx={{
        background: darkMode 
          ? `linear-gradient(135deg, ${darkTheme.primary} 0%, ${darkTheme.secondary} 100%)`
          : `linear-gradient(135deg, ${darkTheme.primary} 0%, ${darkTheme.secondary} 100%)`,
        color: 'white',
        py: 2,
        px: 3,
        boxShadow: `0 4px 20px ${alpha(darkTheme.primary, 0.3)}`
      }}>
        <Container maxWidth="xl">
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>
                🚀 Atharman Enterprise Intelligence Dashboard
              </Typography>
              <Typography variant="subtitle1" sx={{ opacity: 0.9 }}>
                Real-time cloud intelligence and AI-powered cost optimization insights
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={darkMode}
                    onChange={(e) => setDarkMode(e.target.checked)}
                    sx={{
                      '& .MuiSwitch-switchBase.Mui-checked': {
                        color: '#fff',
                      },
                      '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                        backgroundColor: alpha('#fff', 0.3),
                      },
                    }}
                  />
                }
                label="Dark Mode"
                sx={{ color: 'white', m: 0 }}
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={animationsEnabled}
                    onChange={(e) => setAnimationsEnabled(e.target.checked)}
                    sx={{
                      '& .MuiSwitch-switchBase.Mui-checked': {
                        color: '#fff',
                      },
                      '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                        backgroundColor: alpha('#fff', 0.3),
                      },
                    }}
                  />
                }
                label="Animations"
                sx={{ color: 'white', m: 0 }}
              />
            </Box>
          </Box>
        </Container>
      </Box>

      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Tab Navigation */}
        <Fade in={true} timeout={400}>
          <Card sx={{
            background: darkTheme.surface,
            border: `1px solid ${alpha(darkTheme.primary, 0.2)}`,
            borderRadius: 3,
            mb: 4,
            overflow: 'hidden'
          }}>
            <Tabs
              value={activeTab}
              onChange={(e, newValue) => setActiveTab(newValue)}
              variant="scrollable"
              scrollButtons="auto"
              sx={{
                '& .MuiTab-root': {
                  minHeight: 64,
                  textTransform: 'none',
                  fontWeight: 500,
                  fontSize: '0.95rem',
                  color: darkTheme.textSecondary,
                  transition: 'all 0.3s ease-in-out',
                  '&.Mui-selected': {
                    color: darkTheme.primary,
                    fontWeight: 600,
                    background: alpha(darkTheme.primary, 0.1),
                  },
                  '&:hover': {
                    background: alpha(darkTheme.primary, 0.05),
                    transform: animationsEnabled ? 'translateY(-2px)' : 'none',
                  },
                },
                '& .MuiTabs-indicator': {
                  height: 3,
                  background: `linear-gradient(135deg, ${darkTheme.primary} 0%, ${darkTheme.secondary} 100%)`,
                }
              }}
            >
              {tabs.map((tab, index) => (
                <Tab key={index} label={tab.label} icon={tab.icon} />
              ))}
            </Tabs>
          </Card>
        </Fade>

        {/* Tab Content */}
        {renderTabContent()}
      </Container>
    </Box>
  );
};

export default ModernAtharmanDashboard;