import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Switch,
  FormGroup,
  FormControlLabel,
  Tabs,
  Tab,
  Chip,
  Avatar,
  LinearProgress,
  Fade,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Badge,
  CircularProgress,
  useTheme,
  alpha
} from '@mui/material';
import { useThemeMode } from '../contexts/ThemeContext';
import {
  Area,
  AreaChart,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  RadialBarChart,
  RadialBar,
  ScatterChart,
  Scatter
} from 'recharts';
import {
  CloudOutlined,
  MonetizationOnOutlined,
  SpeedOutlined,
  NetworkCheckOutlined,
  AutoGraphOutlined,
  DarkModeOutlined,
  LightModeOutlined,
  DashboardOutlined,
  InsightsOutlined,
  TimelineOutlined,
  BugReportOutlined,
  BuildOutlined,
  AssessmentOutlined,
  IntegrationInstructionsOutlined,
  SmartToyOutlined,
  TrendingUpOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  ErrorOutlined,
  InfoOutlined,
  SettingsOutlined,
  ApiOutlined,
  StorageOutlined,
  CloudSyncOutlined,
  SecurityOutlined,

  DataUsageOutlined
} from '@mui/icons-material';
import { keyframes, styled } from '@mui/material/styles';
import EnhancedAIInsights from './AI/EnhancedAIInsights';
import EnhancedChatbot from './AI/EnhancedChatbot';

// Animations
const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
`;





// Styled Components
const AnimatedCard = styled(Card)(({ theme }) => ({
  animation: `${fadeIn} 0.6s ease-out`,
  background: theme.palette.mode === 'dark' 
    ? `linear-gradient(135deg, ${alpha(theme.palette.primary.dark, 0.1)} 0%, ${alpha(theme.palette.secondary.dark, 0.1)} 100%)`
    : `linear-gradient(135deg, ${alpha(theme.palette.primary.light, 0.1)} 0%, ${alpha(theme.palette.secondary.light, 0.1)} 100%)`,
  backdropFilter: 'blur(10px)',
  border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`,
  borderRadius: 16,
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: theme.palette.mode === 'dark' 
      ? `0 12px 40px ${alpha(theme.palette.primary.main, 0.3)}`
      : `0 12px 40px ${alpha(theme.palette.primary.main, 0.15)}`,
    borderColor: alpha(theme.palette.primary.main, 0.3),
  }
}));

const GlassCard = styled(Paper)(({ theme }) => ({
  background: theme.palette.mode === 'dark'
    ? alpha(theme.palette.background.paper, 0.8)
    : alpha(theme.palette.background.paper, 0.9),
  backdropFilter: 'blur(20px)',
  borderRadius: 20,
  border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  boxShadow: theme.palette.mode === 'dark'
    ? `0 8px 32px ${alpha('#000', 0.3)}`
    : `0 8px 32px ${alpha('#000', 0.1)}`,
}));

const MetricCard = styled(AnimatedCard)(({ theme }) => ({
  height: '140px',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'space-between',
  position: 'relative',
  overflow: 'hidden',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '4px',
    background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
  }
}));

const SimpleIcon = styled(Avatar)(({ theme }) => ({
  background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
  width: 44,
  height: 44,
  transition: 'transform 0.2s ease',
  '&:hover': {
    transform: 'scale(1.05)'
  }
}));

function ModernDashboard() {
  const theme = useTheme();
  const { mode, toggleMode } = useThemeMode();
  const [activeTab, setActiveTab] = useState(0);
  const [metrics, setMetrics] = useState({});
  const [realTimeData, setRealTimeData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [animated, setAnimated] = useState(false);

  // Animation trigger
  useEffect(() => {
    const timer = setTimeout(() => setAnimated(true), 100);
    return () => clearTimeout(timer);
  }, []);

  // Fetch real-time data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        const responses = await Promise.allSettled([
          fetch('http://localhost:8000/metrics/system'),
          fetch('http://localhost:8000/pricing/real-time'),
          fetch('http://localhost:8000/providers/comparison'),
          fetch('http://localhost:8000/ai/predictions')
        ]);

        const [systemRes, pricingRes, providersRes, aiRes] = responses;
        
        // Process system metrics
        if (systemRes.status === 'fulfilled' && systemRes.value.ok) {
          const systemData = await systemRes.value.json();
          setMetrics(prev => ({ ...prev, system: systemData }));
        }

        // Process pricing data  
        if (pricingRes.status === 'fulfilled' && pricingRes.value.ok) {
          const pricingData = await pricingRes.value.json();
          setRealTimeData(pricingData.historical || generateRealisticData());
        } else {
          setRealTimeData(generateRealisticData());
        }

        // Process provider comparison
        if (providersRes.status === 'fulfilled' && providersRes.value.ok) {
          const providersData = await providersRes.value.json();
          setMetrics(prev => ({ ...prev, providers: providersData }));
        }

        // Process AI predictions
        if (aiRes.status === 'fulfilled' && aiRes.value.ok) {
          const aiData = await aiRes.value.json();
          setMetrics(prev => ({ ...prev, ai: aiData }));
        }

      } catch (error) {
        console.warn('Using realistic demo data due to API error:', error);
        setRealTimeData(generateRealisticData());
        setMetrics(generateRealisticMetrics());
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  // Generate realistic cloud pricing data
  const generateRealisticData = () => {
    const now = new Date();
    return Array.from({ length: 24 }, (_, i) => {
      const time = new Date(now.getTime() - (23 - i) * 60 * 60 * 1000);
      const hour = time.getHours();
      
      // Realistic pricing patterns based on actual cloud usage
      const businessHourMultiplier = hour >= 9 && hour <= 17 ? 1.2 : 0.85;
      const weekendMultiplier = time.getDay() === 0 || time.getDay() === 6 ? 0.7 : 1.0;
      
      return {
        timestamp: time.toLocaleTimeString('en-US', { 
          hour: '2-digit', 
          minute: '2-digit' 
        }),
        aws_cost: Number(((0.12 + (hour % 12) * 0.008) * businessHourMultiplier * weekendMultiplier).toFixed(3)),
        azure_cost: Number(((0.14 + (hour % 10) * 0.007) * businessHourMultiplier * weekendMultiplier).toFixed(3)),
        gcp_cost: Number(((0.10 + (hour % 8) * 0.006) * businessHourMultiplier * weekendMultiplier).toFixed(3)),
        cost_savings: Number((12 + (hour % 6) * 2).toFixed(1))
      };
    });
  };

  const generateRealisticMetrics = () => ({
    system: {
      cost_optimization: 87.2,
      performance: 92.4,
      uptime: 99.97,
      active_resources: 156
    },
    providers: [
      { name: 'AWS', market_share: 32, cost_efficiency: 87, performance: 94 },
      { name: 'Azure', market_share: 21, cost_efficiency: 89, performance: 91 },
      { name: 'GCP', market_share: 8, cost_efficiency: 92, performance: 88 },
      { name: 'Others', market_share: 39, cost_efficiency: 76, performance: 83 }
    ]
  });

  const providerColors = {
    aws: '#FF9900',
    azure: '#0078D4', 
    gcp: '#4285F4',
    cost_savings: '#4CAF50',
    performance: '#9C27B0'
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <GlassCard sx={{ p: 2, minWidth: 200 }}>
          <Typography variant="subtitle2" color="primary" gutterBottom>
            {label}
          </Typography>
          {payload.map((entry, index) => (
            <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  bgcolor: entry.color,
                  mr: 1
                }}
              />
              <Typography variant="body2">
                {entry.name}: <strong>${entry.value?.toFixed(3)}</strong>
              </Typography>
            </Box>
          ))}
        </GlassCard>
      );
    }
    return null;
  };

  const tabData = [
    { label: 'Overview', icon: <DashboardOutlined /> },
    { label: 'AI Insights', icon: <InsightsOutlined /> },
    { label: 'AI Chatbot', icon: <SmartToyOutlined /> },
    { label: 'Predictions', icon: <TimelineOutlined /> },
    { label: 'Anomalies', icon: <BugReportOutlined /> },
    { label: 'AutoML', icon: <BuildOutlined /> },
    { label: 'Reports', icon: <AssessmentOutlined /> },
    { label: 'Metrics', icon: <SpeedOutlined /> },
    { label: 'Integration', icon: <IntegrationInstructionsOutlined /> }
  ];

  const renderOverviewTab = () => (
    <Box>
      {/* Key Metrics Row */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {[
          { 
            title: 'Cost Optimization', 
            value: `${metrics.system?.cost_optimization || '87.2'}%`, 
            icon: <MonetizationOnOutlined />,
            color: 'success.main',
            trend: '+5.2%'
          },
          { 
            title: 'Performance Score', 
            value: `${metrics.system?.performance || '92.4'}%`, 
            icon: <SpeedOutlined />,
            color: 'primary.main',
            trend: '+2.1%'
          },
          { 
            title: 'Active Resources', 
            value: metrics.system?.active_resources || '156', 
            icon: <CloudOutlined />,
            color: 'info.main',
            trend: '+12'
          },
          { 
            title: 'System Uptime', 
            value: `${metrics.system?.uptime || '99.97'}%`, 
            icon: <NetworkCheckOutlined />,
            color: 'success.main',
            trend: '0.0%'
          }
        ].map((metric, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Fade in={animated} timeout={600 + index * 200}>
              <MetricCard>
                <CardContent sx={{ p: 2.5 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box>
                      <Typography color="text.secondary" variant="body2" gutterBottom>
                        {metric.title}
                      </Typography>
                      <Typography variant="h4" component="div" fontWeight="bold">
                        {metric.value}
                      </Typography>
                      <Chip 
                        label={metric.trend} 
                        size="small" 
                        color={metric.trend.startsWith('+') ? 'success' : 'default'}
                        sx={{ mt: 1, fontSize: '0.75rem' }}
                      />
                    </Box>
                    <SimpleIcon sx={{ bgcolor: metric.color }}>
                      {metric.icon}
                    </SimpleIcon>
                  </Box>
                </CardContent>
              </MetricCard>
            </Fade>
          </Grid>
        ))}
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3}>
        {/* Real-time Pricing Chart */}
        <Grid item xs={12} lg={8}>
          <Fade in={animated} timeout={800}>
            <GlassCard sx={{ p: 3, height: 400 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" fontWeight="bold">
                  Real-time Cloud Pricing
                </Typography>
                <Chip 
                  icon={<AutoGraphOutlined />} 
                  label="Live Data" 
                  color="success" 
                  variant="outlined" 
                />
              </Box>
              <ResponsiveContainer width="100%" height={320}>
                <ComposedChart data={realTimeData}>
                  <defs>
                    <linearGradient id="awsGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={providerColors.aws} stopOpacity={0.3}/>
                      <stop offset="95%" stopColor={providerColors.aws} stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="azureGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={providerColors.azure} stopOpacity={0.3}/>
                      <stop offset="95%" stopColor={providerColors.azure} stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="gcpGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={providerColors.gcp} stopOpacity={0.3}/>
                      <stop offset="95%" stopColor={providerColors.gcp} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.divider, 0.3)} />
                  <XAxis 
                    dataKey="time" 
                    stroke={theme.palette.text.secondary}
                    fontSize={12}
                  />
                  <YAxis 
                    stroke={theme.palette.text.secondary}
                    fontSize={12}
                    tickFormatter={(value) => `$${value}`}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="aws_cost"
                    stackId="1"
                    stroke={providerColors.aws}
                    fill="url(#awsGradient)"
                    strokeWidth={2}
                    name="AWS"
                  />
                  <Area
                    type="monotone"
                    dataKey="azure_cost"
                    stackId="1"
                    stroke={providerColors.azure}
                    fill="url(#azureGradient)"
                    strokeWidth={2}
                    name="Azure"
                  />
                  <Area
                    type="monotone"
                    dataKey="gcp_cost"
                    stackId="1"
                    stroke={providerColors.gcp}
                    fill="url(#gcpGradient)"
                    strokeWidth={2}
                    name="GCP"
                  />
                  <Line
                    type="monotone"
                    dataKey="cost_savings"
                    stroke={providerColors.cost_savings}
                    strokeWidth={3}
                    strokeDasharray="5 5"
                    name="Savings %"
                    yAxisId="right"
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </GlassCard>
          </Fade>
        </Grid>

        {/* Provider Distribution */}
        <Grid item xs={12} lg={4}>
          <Fade in={animated} timeout={1000}>
            <GlassCard sx={{ p: 3, height: 400 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Provider Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={metrics.providers || generateRealisticMetrics().providers}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="market_share"
                  >
                    {(metrics.providers || generateRealisticMetrics().providers).map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={Object.values(providerColors)[index]} 
                      />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value) => [`${value}%`, 'Market Share']}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
              <Box sx={{ mt: 2 }}>
                {(metrics.providers || generateRealisticMetrics().providers).map((provider, index) => (
                  <Box key={provider.name} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">{provider.name}</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <LinearProgress 
                        variant="determinate" 
                        value={provider.performance} 
                        sx={{ width: 60, height: 4, borderRadius: 2 }}
                      />
                      <Typography variant="caption">{provider.performance}%</Typography>
                    </Box>
                  </Box>
                ))}
              </Box>
            </GlassCard>
          </Fade>
        </Grid>
      </Grid>
    </Box>
  );

  // Predictions Tab
  const renderPredictionsTab = () => (
    <Fade in={animated} timeout={500}>
      <Box>
        <Grid container spacing={3}>
          {/* Prediction Summary Cards */}
          <Grid item xs={12} md={4}>
            <GlassCard sx={{ p: 3, textAlign: 'center' }}>
              <TrendingUpOutlined sx={{ fontSize: 48, color: 'success.main', mb: 2 }} />
              <Typography variant="h4" fontWeight="bold">94.5%</Typography>
              <Typography color="text.secondary">Prediction Accuracy</Typography>
              <LinearProgress variant="determinate" value={94.5} sx={{ mt: 2, height: 8, borderRadius: 4 }} />
            </GlassCard>
          </Grid>
          <Grid item xs={12} md={4}>
            <GlassCard sx={{ p: 3, textAlign: 'center' }}>
              <TimelineOutlined sx={{ fontSize: 48, color: 'info.main', mb: 2 }} />
              <Typography variant="h4" fontWeight="bold">7 Days</Typography>
              <Typography color="text.secondary">Forecast Horizon</Typography>
              <Chip label="Real-time Updates" color="info" sx={{ mt: 2 }} />
            </GlassCard>
          </Grid>
          <Grid item xs={12} md={4}>
            <GlassCard sx={{ p: 3, textAlign: 'center' }}>
              <DataUsageOutlined sx={{ fontSize: 48, color: 'warning.main', mb: 2 }} />
              <Typography variant="h4" fontWeight="bold">2.4M</Typography>
              <Typography color="text.secondary">Data Points</Typography>
              <Chip label="High Confidence" color="success" sx={{ mt: 2 }} />
            </GlassCard>
          </Grid>

          {/* Prediction Chart */}
          <Grid item xs={12} lg={8}>
            <GlassCard sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Cost Prediction Trends
              </Typography>
              <ResponsiveContainer width="100%" height={350}>
                <ComposedChart data={realTimeData.slice(-30)}>
                  <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.text.primary, 0.1)} />
                  <XAxis dataKey="timestamp" stroke={theme.palette.text.secondary} />
                  <YAxis stroke={theme.palette.text.secondary} />
                  <Tooltip content={CustomTooltip} />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="aws_cost"
                    stackId="1"
                    stroke={theme.palette.primary.main}
                    fill={`url(#colorAWS)`}
                    name="AWS Forecast"
                  />
                  <Area
                    type="monotone"
                    dataKey="azure_cost"
                    stackId="1"
                    stroke={theme.palette.secondary.main}
                    fill={`url(#colorAzure)`}
                    name="Azure Forecast"
                  />
                  <Line
                    type="monotone"
                    dataKey="gcp_cost"
                    stroke={theme.palette.warning.main}
                    strokeWidth={3}
                    name="GCP Trend"
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </GlassCard>
          </Grid>

          {/* Prediction Alerts */}
          <Grid item xs={12} lg={4}>
            <GlassCard sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Prediction Alerts
              </Typography>
              <List>
                <ListItem>
                  <ListItemIcon>
                    <WarningOutlined color="warning" />
                  </ListItemIcon>
                  <ListItemText
                    primary="High Usage Predicted"
                    secondary="AWS costs may increase 23% next week"
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemIcon>
                    <InfoOutlined color="info" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Optimization Opportunity"
                    secondary="Switch to Azure for 15% savings"
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleOutlined color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Budget On Track"
                    secondary="GCP spending within limits"
                  />
                </ListItem>
              </List>
            </GlassCard>
          </Grid>
        </Grid>
      </Box>
    </Fade>
  );

  // Anomalies Tab
  const renderAnomaliesTab = () => (
    <Fade in={animated} timeout={500}>
      <Box>
        <Grid container spacing={3}>
          {/* Anomaly Overview */}
          <Grid item xs={12} md={3}>
            <GlassCard sx={{ p: 3, textAlign: 'center' }}>
              <Badge badgeContent={3} color="error">
                <ErrorOutlined sx={{ fontSize: 48, color: 'error.main' }} />
              </Badge>
              <Typography variant="h6" sx={{ mt: 2 }}>Critical Anomalies</Typography>
              <Typography variant="h4" fontWeight="bold" color="error.main">3</Typography>
            </GlassCard>
          </Grid>
          <Grid item xs={12} md={3}>
            <GlassCard sx={{ p: 3, textAlign: 'center' }}>
              <Badge badgeContent={7} color="warning">
                <WarningOutlined sx={{ fontSize: 48, color: 'warning.main' }} />
              </Badge>
              <Typography variant="h6" sx={{ mt: 2 }}>Warnings</Typography>
              <Typography variant="h4" fontWeight="bold" color="warning.main">7</Typography>
            </GlassCard>
          </Grid>
          <Grid item xs={12} md={3}>
            <GlassCard sx={{ p: 3, textAlign: 'center' }}>
              <CheckCircleOutlined sx={{ fontSize: 48, color: 'success.main' }} />
              <Typography variant="h6" sx={{ mt: 2 }}>Resolved</Typography>
              <Typography variant="h4" fontWeight="bold" color="success.main">24</Typography>
            </GlassCard>
          </Grid>
          <Grid item xs={12} md={3}>
            <GlassCard sx={{ p: 3, textAlign: 'center' }}>
              <TrendingUpOutlined sx={{ fontSize: 48, color: 'info.main' }} />
              <Typography variant="h6" sx={{ mt: 2 }}>Detection Rate</Typography>
              <Typography variant="h4" fontWeight="bold" color="info.main">96.2%</Typography>
            </GlassCard>
          </Grid>

          {/* Anomaly Timeline */}
          <Grid item xs={12} lg={8}>
            <GlassCard sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Anomaly Detection Timeline
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <ScatterChart data={realTimeData.slice(-20).map((item, index) => ({
                  ...item,
                  anomaly_score: Math.random() * 100,
                  severity: Math.random() > 0.7 ? 'high' : Math.random() > 0.4 ? 'medium' : 'low'
                }))}>
                  <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.text.primary, 0.1)} />
                  <XAxis dataKey="timestamp" stroke={theme.palette.text.secondary} />
                  <YAxis dataKey="anomaly_score" stroke={theme.palette.text.secondary} />
                  <Tooltip />
                  <Scatter 
                    name="Anomalies" 
                    data={realTimeData.slice(-20)} 
                    fill={theme.palette.error.main} 
                  />
                </ScatterChart>
              </ResponsiveContainer>
            </GlassCard>
          </Grid>

          {/* Recent Anomalies */}
          <Grid item xs={12} lg={4}>
            <GlassCard sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Recent Anomalies
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Time</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <TableRow>
                      <TableCell>14:32</TableCell>
                      <TableCell>CPU Spike</TableCell>
                      <TableCell><Chip label="Critical" color="error" size="small" /></TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>14:15</TableCell>
                      <TableCell>Memory Leak</TableCell>
                      <TableCell><Chip label="Warning" color="warning" size="small" /></TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>13:58</TableCell>
                      <TableCell>Network Latency</TableCell>
                      <TableCell><Chip label="Resolved" color="success" size="small" /></TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>13:45</TableCell>
                      <TableCell>Disk Usage</TableCell>
                      <TableCell><Chip label="Warning" color="warning" size="small" /></TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </GlassCard>
          </Grid>
        </Grid>
      </Box>
    </Fade>
  );

  // AutoML Tab
  const renderAutoMLTab = () => (
    <Fade in={animated} timeout={500}>
      <Box>
        <Grid container spacing={3}>
          {/* AutoML Pipeline Status */}
          <Grid item xs={12} md={6}>
            <GlassCard sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Active ML Pipelines
              </Typography>
              <List>
                <ListItem>
                  <ListItemIcon>
                    <CircularProgress size={24} color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Cost Optimization Model"
                    secondary="Training: 87% complete"
                  />
                  <Chip label="Running" color="success" size="small" />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleOutlined color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Anomaly Detection"
                    secondary="Deployed: v2.1.3"
                  />
                  <Chip label="Active" color="info" size="small" />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemIcon>
                    <SettingsOutlined color="action" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Resource Predictor"
                    secondary="Queued for training"
                  />
                  <Chip label="Pending" color="warning" size="small" />
                </ListItem>
              </List>
            </GlassCard>
          </Grid>

          {/* Model Performance */}
          <Grid item xs={12} md={6}>
            <GlassCard sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Model Performance Metrics
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <RadialBarChart cx="50%" cy="50%" innerRadius="20%" outerRadius="90%" data={[
                  { name: 'Accuracy', value: 94.5, fill: theme.palette.success.main },
                  { name: 'Precision', value: 91.2, fill: theme.palette.info.main },
                  { name: 'Recall', value: 88.7, fill: theme.palette.warning.main },
                  { name: 'F1-Score', value: 89.9, fill: theme.palette.secondary.main }
                ]}>
                  <RadialBar dataKey="value" cornerRadius={10} fill="#8884d8" />
                  <Tooltip />
                  <Legend />
                </RadialBarChart>
              </ResponsiveContainer>
            </GlassCard>
          </Grid>

          {/* Training History */}
          <Grid item xs={12}>
            <GlassCard sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Training History & Results
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={Array.from({length: 20}, (_, i) => ({
                  epoch: i + 1,
                  accuracy: 60 + Math.random() * 35,
                  loss: 1.2 - (i * 0.05) + Math.random() * 0.1,
                  val_accuracy: 58 + Math.random() * 32,
                  val_loss: 1.3 - (i * 0.04) + Math.random() * 0.12
                }))}>
                  <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.text.primary, 0.1)} />
                  <XAxis dataKey="epoch" stroke={theme.palette.text.secondary} />
                  <YAxis stroke={theme.palette.text.secondary} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="accuracy" stroke={theme.palette.success.main} strokeWidth={2} name="Training Accuracy" />
                  <Line type="monotone" dataKey="val_accuracy" stroke={theme.palette.info.main} strokeWidth={2} name="Validation Accuracy" />
                  <Line type="monotone" dataKey="loss" stroke={theme.palette.error.main} strokeWidth={2} name="Training Loss" />
                  <Line type="monotone" dataKey="val_loss" stroke={theme.palette.warning.main} strokeWidth={2} name="Validation Loss" />
                </LineChart>
              </ResponsiveContainer>
            </GlassCard>
          </Grid>
        </Grid>
      </Box>
    </Fade>
  );

  // Reports Tab
  const renderReportsTab = () => (
    <Fade in={animated} timeout={500}>
      <Box>
        <Grid container spacing={3}>
          {/* Report Generation */}
          <Grid item xs={12} md={4}>
            <GlassCard sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Generate Reports
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button variant="contained" startIcon={<AssessmentOutlined />}>
                  Cost Analysis Report
                </Button>
                <Button variant="outlined" startIcon={<TrendingUpOutlined />}>
                  Performance Summary
                </Button>
                <Button variant="outlined" startIcon={<SecurityOutlined />}>
                  Security Audit
                </Button>
                <Button variant="outlined" startIcon={<ApiOutlined />}>
                  API Usage Report
                </Button>
              </Box>
            </GlassCard>
          </Grid>

          {/* Recent Reports */}
          <Grid item xs={12} md={8}>
            <GlassCard sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Recent Reports
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Report Name</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Generated</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <TableRow>
                      <TableCell>Monthly Cost Analysis</TableCell>
                      <TableCell>Cost</TableCell>
                      <TableCell>2 hours ago</TableCell>
                      <TableCell><Chip label="Ready" color="success" size="small" /></TableCell>
                      <TableCell>
                        <Button size="small" variant="text">Download</Button>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Security Assessment</TableCell>
                      <TableCell>Security</TableCell>
                      <TableCell>1 day ago</TableCell>
                      <TableCell><Chip label="Ready" color="success" size="small" /></TableCell>
                      <TableCell>
                        <Button size="small" variant="text">Download</Button>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Performance Report</TableCell>
                      <TableCell>Performance</TableCell>
                      <TableCell>3 days ago</TableCell>
                      <TableCell><Chip label="Generating" color="warning" size="small" /></TableCell>
                      <TableCell>
                        <CircularProgress size={16} />
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </GlassCard>
          </Grid>

          {/* Report Analytics */}
          <Grid item xs={12}>
            <GlassCard sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Report Usage Analytics
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={[
                  { name: 'Cost Reports', count: 45, downloads: 38 },
                  { name: 'Performance', count: 32, downloads: 28 },
                  { name: 'Security', count: 28, downloads: 25 },
                  { name: 'API Usage', count: 22, downloads: 18 },
                  { name: 'Custom', count: 15, downloads: 12 }
                ]}>
                  <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.text.primary, 0.1)} />
                  <XAxis dataKey="name" stroke={theme.palette.text.secondary} />
                  <YAxis stroke={theme.palette.text.secondary} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="count" fill={theme.palette.primary.main} name="Generated" />
                  <Bar dataKey="downloads" fill={theme.palette.secondary.main} name="Downloaded" />
                </BarChart>
              </ResponsiveContainer>
            </GlassCard>
          </Grid>
        </Grid>
      </Box>
    </Fade>
  );

  // Metrics Tab
  const renderMetricsTab = () => (
    <Fade in={animated} timeout={500}>
      <Box>
        <Grid container spacing={3}>
          {/* System Metrics */}
          <Grid item xs={12} md={3}>
            <GlassCard sx={{ p: 3, textAlign: 'center' }}>
              <SpeedOutlined sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h4" fontWeight="bold">73%</Typography>
              <Typography color="text.secondary">CPU Usage</Typography>
              <LinearProgress variant="determinate" value={73} sx={{ mt: 2 }} />
            </GlassCard>
          </Grid>
          <Grid item xs={12} md={3}>
            <GlassCard sx={{ p: 3, textAlign: 'center' }}>
              <StorageOutlined sx={{ fontSize: 48, color: 'secondary.main', mb: 2 }} />
              <Typography variant="h4" fontWeight="bold">8.2GB</Typography>
              <Typography color="text.secondary">Memory Usage</Typography>
              <LinearProgress variant="determinate" value={68} sx={{ mt: 2 }} />
            </GlassCard>
          </Grid>
          <Grid item xs={12} md={3}>
            <GlassCard sx={{ p: 3, textAlign: 'center' }}>
              <StorageOutlined sx={{ fontSize: 48, color: 'success.main', mb: 2 }} />
              <Typography variant="h4" fontWeight="bold">456GB</Typography>
              <Typography color="text.secondary">Storage Used</Typography>
              <LinearProgress variant="determinate" value={85} sx={{ mt: 2 }} />
            </GlassCard>
          </Grid>
          <Grid item xs={12} md={3}>
            <GlassCard sx={{ p: 3, textAlign: 'center' }}>
              <NetworkCheckOutlined sx={{ fontSize: 48, color: 'info.main', mb: 2 }} />
              <Typography variant="h4" fontWeight="bold">12ms</Typography>
              <Typography color="text.secondary">Network Latency</Typography>
              <Chip label="Excellent" color="success" sx={{ mt: 2 }} />
            </GlassCard>
          </Grid>

          {/* Performance Chart */}
          <Grid item xs={12} lg={8}>
            <GlassCard sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                System Performance Over Time
              </Typography>
              <ResponsiveContainer width="100%" height={350}>
                <AreaChart data={realTimeData.slice(-24)}>
                  <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.text.primary, 0.1)} />
                  <XAxis dataKey="timestamp" stroke={theme.palette.text.secondary} />
                  <YAxis stroke={theme.palette.text.secondary} />
                  <Tooltip />
                  <Legend />
                  <Area type="monotone" dataKey="aws_cost" stackId="1" stroke={theme.palette.primary.main} fill={theme.palette.primary.main} fillOpacity={0.3} name="CPU %" />
                  <Area type="monotone" dataKey="azure_cost" stackId="2" stroke={theme.palette.secondary.main} fill={theme.palette.secondary.main} fillOpacity={0.3} name="Memory %" />
                  <Area type="monotone" dataKey="gcp_cost" stackId="3" stroke={theme.palette.success.main} fill={theme.palette.success.main} fillOpacity={0.3} name="Network I/O" />
                </AreaChart>
              </ResponsiveContainer>
            </GlassCard>
          </Grid>

          {/* Key Performance Indicators */}
          <Grid item xs={12} lg={4}>
            <GlassCard sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Key Performance Indicators
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">Uptime</Typography>
                  <Typography variant="h6" fontWeight="bold">99.98%</Typography>
                  <LinearProgress variant="determinate" value={99.98} color="success" sx={{ height: 6, borderRadius: 3 }} />
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Response Time</Typography>
                  <Typography variant="h6" fontWeight="bold">143ms</Typography>
                  <LinearProgress variant="determinate" value={85} color="info" sx={{ height: 6, borderRadius: 3 }} />
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Throughput</Typography>
                  <Typography variant="h6" fontWeight="bold">2.4K req/s</Typography>
                  <LinearProgress variant="determinate" value={78} color="warning" sx={{ height: 6, borderRadius: 3 }} />
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Error Rate</Typography>
                  <Typography variant="h6" fontWeight="bold">0.02%</Typography>
                  <LinearProgress variant="determinate" value={2} color="error" sx={{ height: 6, borderRadius: 3 }} />
                </Box>
              </Box>
            </GlassCard>
          </Grid>
        </Grid>
      </Box>
    </Fade>
  );

  // Integration Tab
  const renderIntegrationTab = () => (
    <Fade in={animated} timeout={500}>
      <Box>
        <Grid container spacing={3}>
          {/* Integration Status */}
          <Grid item xs={12} md={6}>
            <GlassCard sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Active Integrations
              </Typography>
              <List>
                <ListItem>
                  <ListItemIcon>
                    <CloudOutlined color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="AWS Integration"
                    secondary="Connected • Last sync: 2 min ago"
                  />
                  <Chip label="Active" color="success" size="small" />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemIcon>
                    <CloudSyncOutlined color="info" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Azure Integration"
                    secondary="Connected • Last sync: 5 min ago"
                  />
                  <Chip label="Active" color="success" size="small" />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemIcon>
                    <ApiOutlined color="secondary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Google Cloud"
                    secondary="Connected • Last sync: 1 min ago"
                  />
                  <Chip label="Active" color="success" size="small" />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemIcon>
                    <SecurityOutlined color="warning" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Security Scanner"
                    secondary="Checking connection..."
                  />
                  <CircularProgress size={20} />
                </ListItem>
              </List>
            </GlassCard>
          </Grid>

          {/* API Usage Stats */}
          <Grid item xs={12} md={6}>
            <GlassCard sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                API Usage Statistics
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'AWS API', value: 45, fill: theme.palette.primary.main },
                      { name: 'Azure API', value: 30, fill: theme.palette.secondary.main },
                      { name: 'GCP API', value: 20, fill: theme.palette.success.main },
                      { name: 'Others', value: 5, fill: theme.palette.warning.main }
                    ]}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    dataKey="value"
                  >
                  </Pie>
                  <Tooltip formatter={(value) => [`${value}%`, 'Usage']} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </GlassCard>
          </Grid>

          {/* Integration Health */}
          <Grid item xs={12}>
            <GlassCard sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Integration Health Monitor
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={Array.from({length: 24}, (_, i) => ({
                  hour: `${i}:00`,
                  aws_health: 95 + Math.random() * 5,
                  azure_health: 92 + Math.random() * 8,
                  gcp_health: 97 + Math.random() * 3,
                  api_calls: Math.floor(Math.random() * 1000) + 500
                }))}>
                  <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.text.primary, 0.1)} />
                  <XAxis dataKey="hour" stroke={theme.palette.text.secondary} />
                  <YAxis stroke={theme.palette.text.secondary} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="aws_health" stroke={theme.palette.primary.main} strokeWidth={2} name="AWS Health %" />
                  <Line type="monotone" dataKey="azure_health" stroke={theme.palette.secondary.main} strokeWidth={2} name="Azure Health %" />
                  <Line type="monotone" dataKey="gcp_health" stroke={theme.palette.success.main} strokeWidth={2} name="GCP Health %" />
                </LineChart>
              </ResponsiveContainer>
            </GlassCard>
          </Grid>

          {/* Quick Actions */}
          <Grid item xs={12}>
            <GlassCard sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button variant="contained" startIcon={<ApiOutlined />}>
                  Test All Connections
                </Button>
                <Button variant="outlined" startIcon={<CloudSyncOutlined />}>
                  Force Sync
                </Button>
                <Button variant="outlined" startIcon={<SettingsOutlined />}>
                  Configure Webhooks
                </Button>
                <Button variant="outlined" startIcon={<SecurityOutlined />}>
                  Refresh Tokens
                </Button>
              </Box>
            </GlassCard>
          </Grid>
        </Grid>
      </Box>
    </Fade>
  );

  return (
    <Box sx={{ 
      minHeight: '100vh',
      background: theme.palette.mode === 'dark'
        ? 'linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 50%, #0c0c0c 100%)'
        : 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 50%, #f5f7fa 100%)',
      py: 3
    }}>
      <Container maxWidth="xl">
        {/* Header */}
        <Fade in={animated} timeout={500}>
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            mb: 4,
            background: alpha(theme.palette.background.paper, 0.8),
            backdropFilter: 'blur(20px)',
            borderRadius: 3,
            p: 3,
            border: `1px solid ${alpha(theme.palette.divider, 0.1)}`
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <img 
                src="/atharman_logo.svg" 
                alt="Atharman Logo" 
                style={{ 
                  height: '48px', 
                  width: 'auto',
                  filter: theme.palette.mode === 'dark' ? 'brightness(0) invert(1)' : 'none'
                }} 
              />
              <Box>
                <Typography variant="h3" fontWeight="bold" gutterBottom>
                  Atharman
                </Typography>
                <Typography variant="subtitle1" color="text.secondary">
                  Cloud Intelligence Platform
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <FormGroup>
                <FormControlLabel
                  control={
                    <Switch
                      checked={mode === 'dark'}
                      onChange={toggleMode}
                      icon={<LightModeOutlined />}
                      checkedIcon={<DarkModeOutlined />}
                    />
                  }
                  label={mode === 'dark' ? "Dark Mode" : "Light Mode"}
                />
              </FormGroup>
            </Box>
          </Box>
        </Fade>

        {/* Navigation Tabs */}
        <Fade in={animated} timeout={700}>
          <GlassCard sx={{ mb: 3 }}>
            <Tabs
              value={activeTab}
              onChange={(e, newValue) => setActiveTab(newValue)}
              variant="scrollable"
              scrollButtons="auto"
              sx={{
                '& .MuiTab-root': {
                  textTransform: 'none',
                  fontWeight: 600,
                  minHeight: 64,
                  '&:hover': {
                    backgroundColor: alpha(theme.palette.primary.main, 0.1),
                  }
                },
                '& .Mui-selected': {
                  color: theme.palette.primary.main,
                }
              }}
            >
              {tabData.map((tab, index) => (
                <Tab
                  key={index}
                  icon={tab.icon}
                  label={tab.label}
                  iconPosition="start"
                />
              ))}
            </Tabs>
          </GlassCard>
        </Fade>

        {/* Tab Content */}
        <Box sx={{ position: 'relative' }}>
          {loading && (
            <Box sx={{ position: 'absolute', top: 0, left: 0, right: 0, zIndex: 1 }}>
              <LinearProgress sx={{ borderRadius: 2 }} />
            </Box>
          )}
          
          {activeTab === 0 && renderOverviewTab()}
          
          {activeTab === 1 && <EnhancedAIInsights />}
          {activeTab === 2 && <EnhancedChatbot />}
          
          {activeTab === 3 && renderPredictionsTab()}
          {activeTab === 4 && renderAnomaliesTab()}
          {activeTab === 5 && renderAutoMLTab()}
          {activeTab === 6 && renderReportsTab()}
          {activeTab === 7 && renderMetricsTab()}
          {activeTab === 8 && renderIntegrationTab()}
        </Box>
      </Container>
    </Box>
  );
}

export default ModernDashboard;
