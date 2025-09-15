import React, { useState, useEffect } from 'react';
import { 
  Card, CardContent, Typography, Box, Alert, Chip, 
  List, ListItem, ListItemText, ListItemIcon, 
  LinearProgress, Skeleton, Accordion, AccordionSummary, AccordionDetails
} from '@mui/material';
import {
  TrendingUp, TrendingDown, Warning, CheckCircle,
  ExpandMore, Psychology, AutoAwesome, Speed
} from '@mui/icons-material';
import axios from 'axios';

const AIInsightsSummary = ({ data, loading }) => {
  const [aiInsights, setAiInsights] = useState(null);
  const [apiLoading, setApiLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAIInsights = async () => {
      try {
        setApiLoading(true);
        setError(null);
        
        const response = await axios.post('/api/ai/optimization-recommendations', {
          timeframe: '30d',
          budget_limit: 1000,
          services: ['compute', 'storage', 'database'],
          optimization_goals: ['cost', 'performance', 'efficiency']
        }, {
          timeout: 12000,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer your-token-here'
          }
        });
        
        if (response.data && response.data.success) {
          setAiInsights(response.data);
        } else {
          throw new Error('Invalid AI response format');
        }
      } catch (err) {
        console.error('AI API Error:', err);
        setError('Failed to fetch AI insights - Using demo analysis');
        // Fallback to demo AI insights
        setAiInsights(generateDemoAIInsights());
      } finally {
        setApiLoading(false);
      }
    };

    fetchAIInsights();
    
    // Refresh AI insights every 5 minutes
    const interval = setInterval(fetchAIInsights, 300000);
    return () => clearInterval(interval);
  }, []);

  const generateDemoAIInsights = () => {
    return {
      success: true,
      optimization_score: 76,
      potential_savings: 234.56,
      recommendations: [
        {
          id: 1,
          type: 'cost_optimization',
          title: 'Right-size EC2 Instances',
          description: 'Switch to t3.medium instances for 23% cost reduction',
          impact: 'high',
          savings: 89.45,
          effort: 'low',
          provider: 'AWS',
          confidence: 94
        },
        {
          id: 2,
          type: 'performance',
          title: 'Enable Auto Scaling',
          description: 'Implement auto-scaling to handle traffic spikes efficiently',
          impact: 'medium',
          savings: 67.23,
          effort: 'medium',
          provider: 'Azure',
          confidence: 87
        },
        {
          id: 3,
          type: 'efficiency',
          title: 'Storage Class Optimization',
          description: 'Move infrequently accessed data to cold storage',
          impact: 'high',
          savings: 77.88,
          effort: 'low',
          provider: 'GCP',
          confidence: 91
        }
      ],
      predictions: {
        next_month_cost: 876.45,
        trend: 'decreasing',
        confidence: 89,
        factors: ['seasonal_decrease', 'optimization_impact', 'workload_efficiency']
      },
      alerts: [
        { type: 'warning', message: 'Database costs increased 15% this week' },
        { type: 'info', message: 'New cost optimization opportunities detected' }
      ]
    };
  };

  const getSeverityColor = (impact) => {
    switch (impact) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getSeverityIcon = (impact) => {
    switch (impact) {
      case 'high': return <TrendingUp color="error" />;
      case 'medium': return <Warning color="warning" />;
      case 'low': return <TrendingDown color="info" />;
      default: return <CheckCircle />;
    }
  };

  const isLoading = loading || apiLoading;

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" fontWeight="600" gutterBottom>
            🤖 AI Insights & Recommendations
          </Typography>
          <Box sx={{ height: 300 }}>
            <Skeleton variant="text" height={40} />
            <Skeleton variant="rectangular" height={80} sx={{ mt: 1 }} />
            <Skeleton variant="text" height={30} sx={{ mt: 1 }} />
            <Skeleton variant="rectangular" height={60} sx={{ mt: 1 }} />
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error && !aiInsights) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" fontWeight="600" gutterBottom>
            🤖 AI Insights & Recommendations
          </Typography>
          <Alert severity="error">
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" fontWeight="600" gutterBottom>
          🤖 AI Insights & Recommendations - Live Analysis
        </Typography>
        
        {error && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* AI Score and Savings */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
            <Psychology color="primary" />
            <Typography variant="body2">
              Optimization Score: {aiInsights?.optimization_score || 0}/100
            </Typography>
            <AutoAwesome color="secondary" />
            <Typography variant="body2" color="success.main">
              Potential Savings: ${aiInsights?.potential_savings?.toFixed(2) || '0.00'}
            </Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={aiInsights?.optimization_score || 0} 
            color="primary"
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>

        {/* Predictions */}
        {aiInsights?.predictions && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              📈 Next Month Prediction: ${aiInsights.predictions.next_month_cost}
            </Typography>
            <Chip 
              label={`${aiInsights.predictions.trend} (${aiInsights.predictions.confidence}% confidence)`}
              color={aiInsights.predictions.trend === 'decreasing' ? 'success' : 'warning'}
              size="small"
            />
          </Box>
        )}

        {/* Top Recommendations */}
        <Typography variant="subtitle2" gutterBottom>
          💡 Top AI Recommendations:
        </Typography>
        
        <List dense>
          {aiInsights?.recommendations?.slice(0, 3).map((rec) => (
            <Accordion key={rec.id} sx={{ boxShadow: 'none', border: '1px solid #e0e0e0' }}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <ListItemIcon sx={{ minWidth: 32 }}>
                  {getSeverityIcon(rec.impact)}
                </ListItemIcon>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    {rec.title}
                  </Typography>
                  <Chip 
                    label={rec.provider} 
                    size="small" 
                    color="primary" 
                    variant="outlined"
                  />
                  <Chip 
                    label={`$${rec.savings} savings`} 
                    size="small" 
                    color="success"
                  />
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2" color="text.secondary">
                  {rec.description}
                </Typography>
                <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                  <Chip label={`${rec.confidence}% confidence`} size="small" />
                  <Chip label={`${rec.effort} effort`} size="small" variant="outlined" />
                </Box>
              </AccordionDetails>
            </Accordion>
          ))}
        </List>

        {/* Alerts */}
        {aiInsights?.alerts && aiInsights.alerts.length > 0 && (
          <Box sx={{ mt: 2 }}>
            {aiInsights.alerts.map((alert, idx) => (
              <Alert 
                key={idx} 
                severity={alert.type} 
                sx={{ mt: 1 }}
                icon={<Speed />}
              >
                {alert.message}
              </Alert>
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default AIInsightsSummary;
