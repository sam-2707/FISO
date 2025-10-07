import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  LinearProgress,
  Avatar,
  alpha,
  useTheme
} from '@mui/material';
import {
  TrendingUpOutlined,
  PsychologyOutlined,
  SmartToyOutlined,
  InsightsOutlined,
  AutoGraphOutlined
} from '@mui/icons-material';
import {
  LineChart,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { keyframes, styled } from '@mui/material/styles';

const pulse = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
`;

const AICard = styled(Card)(({ theme }) => ({
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

const PulsingAvatar = styled(Avatar)(({ theme }) => ({
  animation: `${pulse} 2s ease-in-out infinite`,
  background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
}));

function EnhancedAIInsights() {
  const theme = useTheme();
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAIInsights = async () => {
      try {
        const response = await fetch('http://localhost:8000/ai/insights');
        if (response.ok) {
          const data = await response.json();
          setInsights(data);
        } else {
          setInsights(generateDemoInsights());
        }
      } catch (error) {
        console.warn('Using demo AI insights:', error);
        setInsights(generateDemoInsights());
      } finally {
        setLoading(false);
      }
    };

    fetchAIInsights();
    const interval = setInterval(fetchAIInsights, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const generateDemoInsights = () => ({
    predictions: [
      { metric: 'Cost Optimization', current: 87, predicted: 92, confidence: 94 },
      { metric: 'Performance', current: 89, predicted: 91, confidence: 88 },
      { metric: 'Resource Usage', current: 76, predicted: 82, confidence: 91 },
      { metric: 'Security Score', current: 95, predicted: 97, confidence: 96 }
    ],
    trends: Array.from({ length: 12 }, (_, i) => ({
      month: new Date(2024, i).toLocaleDateString('en-US', { month: 'short' }),
      savings: Math.random() * 20 + 10,
      efficiency: Math.random() * 15 + 80,
      prediction: Math.random() * 25 + 15
    })),
    recommendations: [
      {
        title: 'Optimize Compute Resources',
        impact: 'High',
        savings: '$2,400/month',
        confidence: 92,
        description: 'AI detected 23% over-provisioned compute instances'
      },
      {
        title: 'Storage Tier Optimization',
        impact: 'Medium',
        savings: '$800/month',
        confidence: 87,
        description: 'Move infrequently accessed data to cheaper storage tiers'
      },
      {
        title: 'Auto-scaling Configuration',
        impact: 'High',
        savings: '$1,600/month',
        confidence: 95,
        description: 'Implement intelligent auto-scaling based on usage patterns'
      }
    ],
    anomalies: {
      detected: 7,
      resolved: 5,
      critical: 1,
      trend: Array.from({ length: 24 }, (_, i) => ({
        hour: i,
        anomalies: Math.floor(Math.random() * 5),
        severity: Math.random() * 100
      }))
    }
  });

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  const impactColors = {
    'High': theme.palette.error.main,
    'Medium': theme.palette.warning.main,
    'Low': theme.palette.success.main
  };

  return (
    <Box>
      {/* AI Predictions Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {insights.predictions.map((pred, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <AICard>
              <CardContent sx={{ p: 2.5 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box>
                    <Typography color="text.secondary" variant="body2" gutterBottom>
                      {pred.metric}
                    </Typography>
                    <Typography variant="h5" fontWeight="bold">
                      {pred.current}%
                    </Typography>
                  </Box>
                  <PulsingAvatar sx={{ width: 48, height: 48 }}>
                    <PsychologyOutlined />
                  </PulsingAvatar>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    AI Prediction: {pred.predicted}%
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={pred.predicted} 
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                </Box>
                <Chip 
                  label={`${pred.confidence}% confidence`} 
                  size="small" 
                  color="primary" 
                  variant="outlined"
                />
              </CardContent>
            </AICard>
          </Grid>
        ))}
      </Grid>

      {/* AI Trends and Recommendations */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Trends Chart */}
        <Grid item xs={12} lg={8}>
          <AICard sx={{ height: 400 }}>
            <CardContent sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AutoGraphOutlined sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6" fontWeight="bold">
                  AI-Powered Trends & Predictions
                </Typography>
                <Chip 
                  label="Real-time" 
                  size="small" 
                  color="success" 
                  sx={{ ml: 2 }}
                />
              </Box>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={insights.trends}>
                  <defs>
                    <linearGradient id="savingsGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={theme.palette.primary.main} stopOpacity={0.3}/>
                      <stop offset="95%" stopColor={theme.palette.primary.main} stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="predictionGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={theme.palette.secondary.main} stopOpacity={0.3}/>
                      <stop offset="95%" stopColor={theme.palette.secondary.main} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.divider, 0.3)} />
                  <XAxis dataKey="month" stroke={theme.palette.text.secondary} />
                  <YAxis stroke={theme.palette.text.secondary} />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: alpha(theme.palette.background.paper, 0.9),
                      border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
                      borderRadius: 8,
                      backdropFilter: 'blur(10px)'
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="savings"
                    stroke={theme.palette.primary.main}
                    fillOpacity={1}
                    fill="url(#savingsGradient)"
                    strokeWidth={2}
                    name="Current Savings %"
                  />
                  <Area
                    type="monotone"
                    dataKey="prediction"
                    stroke={theme.palette.secondary.main}
                    fill="url(#predictionGradient)"
                    strokeWidth={3}
                    strokeDasharray="5 5"
                    name="AI Prediction %"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </AICard>
        </Grid>

        {/* Recommendations */}
        <Grid item xs={12} lg={4}>
          <AICard sx={{ height: 400 }}>
            <CardContent sx={{ p: 3, height: '100%', overflow: 'auto' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <SmartToyOutlined sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6" fontWeight="bold">
                  AI Recommendations
                </Typography>
              </Box>
              {insights.recommendations.map((rec, index) => (
                <Box key={index} sx={{ mb: 3, p: 2, bgcolor: alpha(theme.palette.background.paper, 0.5), borderRadius: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                    <Typography variant="subtitle2" fontWeight="bold">
                      {rec.title}
                    </Typography>
                    <Chip 
                      label={rec.impact} 
                      size="small" 
                      sx={{ 
                        bgcolor: alpha(impactColors[rec.impact], 0.1),
                        color: impactColors[rec.impact],
                        fontWeight: 'bold'
                      }}
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {rec.description}
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                    <Typography variant="body2" fontWeight="bold" color="success.main">
                      {rec.savings}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {rec.confidence}% confidence
                    </Typography>
                  </Box>
                </Box>
              ))}
            </CardContent>
          </AICard>
        </Grid>
      </Grid>

      {/* Anomaly Detection */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <AICard>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <InsightsOutlined sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6" fontWeight="bold">
                    Anomaly Detection Dashboard
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <Chip 
                    label={`${insights.anomalies.detected} detected`} 
                    color="warning" 
                    variant="outlined"
                  />
                  <Chip 
                    label={`${insights.anomalies.resolved} resolved`} 
                    color="success" 
                    variant="outlined"
                  />
                  <Chip 
                    label={`${insights.anomalies.critical} critical`} 
                    color="error" 
                    variant="outlined"
                  />
                </Box>
              </Box>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={insights.anomalies.trend}>
                  <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.divider, 0.3)} />
                  <XAxis 
                    dataKey="hour" 
                    stroke={theme.palette.text.secondary}
                    tickFormatter={(value) => `${value}:00`}
                  />
                  <YAxis stroke={theme.palette.text.secondary} />
                  <Tooltip 
                    formatter={(value, name) => [value, name === 'anomalies' ? 'Anomalies' : 'Severity']}
                    contentStyle={{
                      backgroundColor: alpha(theme.palette.background.paper, 0.9),
                      border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
                      borderRadius: 8,
                      backdropFilter: 'blur(10px)'
                    }}
                  />
                  <Bar 
                    dataKey="anomalies" 
                    fill={theme.palette.warning.main}
                    radius={[4, 4, 0, 0]}
                    name="Anomalies"
                  />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </AICard>
        </Grid>
      </Grid>
    </Box>
  );
}

export default EnhancedAIInsights;