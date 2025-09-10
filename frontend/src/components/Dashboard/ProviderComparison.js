import React, { useState, useEffect } from 'react';
import { 
  Card, CardContent, Typography, Grid, Box, Chip, 
  Paper, CircularProgress, Alert, Divider 
} from '@mui/material';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, PieChart, Pie, Cell, RadarChart,
  PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar
} from 'recharts';
import axios from 'axios';

const COLORS = ['#FF9900', '#0078D4', '#4285F4', '#F80000'];

const ProviderComparison = ({ data }) => {
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchComparisonData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await axios.post('/api/ai/comprehensive-analysis', {
          providers: ['aws', 'azure', 'gcp', 'oracle'],
          services: ['compute', 'storage', 'database', 'networking'],
          region: 'us-east-1'
        }, {
          timeout: 15000,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer your-token-here'
          }
        });
        
        if (response.data && response.data.success) {
          setComparisonData(response.data);
        } else {
          throw new Error('Invalid response format');
        }
      } catch (err) {
        console.error('API Error:', err);
        setError('Failed to fetch comparison data - Using demo data');
        // Fallback to demo data
        setComparisonData(generateDemoData());
      } finally {
        setLoading(false);
      }
    };

    fetchComparisonData();
  }, []);

  const generateDemoData = () => {
    return {
      success: true,
      comparison: {
        cost_analysis: {
          aws: { total_cost: 245.67, compute: 156.20, storage: 45.30, database: 28.17, networking: 16.00 },
          azure: { total_cost: 278.45, compute: 178.90, storage: 52.10, database: 31.25, networking: 16.20 },
          gcp: { total_cost: 232.18, compute: 148.75, storage: 41.80, database: 25.63, networking: 16.00 },
          oracle: { total_cost: 298.34, compute: 189.60, storage: 58.74, database: 33.00, networking: 17.00 }
        },
        performance_scores: {
          aws: { compute: 92, storage: 89, database: 94, networking: 91 },
          azure: { compute: 88, storage: 91, database: 89, networking: 87 },
          gcp: { compute: 95, storage: 88, database: 92, networking: 93 },
          oracle: { compute: 85, storage: 87, database: 96, networking: 84 }
        },
        recommendations: [
          { provider: 'GCP', reason: 'Best cost-performance ratio for compute workloads', savings: '$13.49' },
          { provider: 'AWS', reason: 'Superior database performance and reliability', savings: '$8.21' },
          { provider: 'Azure', reason: 'Best integration for enterprise Windows environments', savings: '$5.67' }
        ]
      }
    };
  };

  if (loading) {
    return (
      <Card sx={{ height: 500, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Box sx={{ textAlign: 'center' }}>
          <CircularProgress />
          <Typography variant="body2" sx={{ mt: 2 }}>
            Analyzing multi-cloud providers...
          </Typography>
        </Box>
      </Card>
    );
  }

  if (error && !comparisonData) {
    return (
      <Card sx={{ height: 500 }}>
        <CardContent>
          <Alert severity="error">
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const costData = comparisonData?.comparison?.cost_analysis ? 
    Object.entries(comparisonData.comparison.cost_analysis).map(([provider, costs]) => ({
      provider: provider.toUpperCase(),
      compute: costs.compute,
      storage: costs.storage,
      database: costs.database,
      networking: costs.networking,
      total: costs.total_cost
    })) : [];

  const pieData = costData.map((item, index) => ({
    name: item.provider,
    value: item.total,
    color: COLORS[index]
  }));

  const performanceData = comparisonData?.comparison?.performance_scores ?
    Object.entries(comparisonData.comparison.performance_scores).map(([provider, scores]) => ({
      provider: provider.toUpperCase(),
      compute: scores.compute,
      storage: scores.storage,
      database: scores.database,
      networking: scores.networking
    })) : [];

  return (
    <Card sx={{ height: 500 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          🔍 Multi-Cloud Provider Comparison - Live Analysis
        </Typography>
        
        {error && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={2} sx={{ height: 420 }}>
          {/* Cost Comparison Bar Chart */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, height: '100%' }}>
              <Typography variant="subtitle2" gutterBottom>
                Cost Analysis (Monthly $)
              </Typography>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={costData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="provider" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`$${value}`, 'Cost']} />
                  <Bar dataKey="total" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
              
              {/* Recommendations */}
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  💡 Top Recommendations:
                </Typography>
                {comparisonData?.comparison?.recommendations?.slice(0, 2).map((rec, idx) => (
                  <Chip
                    key={idx}
                    label={`${rec.provider}: ${rec.savings} savings`}
                    size="small"
                    color="primary"
                    variant="outlined"
                    sx={{ mr: 1, mb: 1 }}
                  />
                ))}
              </Box>
            </Paper>
          </Grid>

          {/* Performance Radar Chart */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, height: '100%' }}>
              <Typography variant="subtitle2" gutterBottom>
                Performance Scores (0-100)
              </Typography>
              <ResponsiveContainer width="100%" height={200}>
                <RadarChart data={performanceData[0] ? [performanceData[0]] : []}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="provider" />
                  <PolarRadiusAxis angle={90} domain={[0, 100]} />
                  <Radar 
                    name="AWS" 
                    dataKey="compute" 
                    stroke="#FF9900" 
                    fill="#FF9900" 
                    fillOpacity={0.3} 
                  />
                  <Radar 
                    name="Storage" 
                    dataKey="storage" 
                    stroke="#0078D4" 
                    fill="#0078D4" 
                    fillOpacity={0.3} 
                  />
                </RadarChart>
              </ResponsiveContainer>

              {/* Cost Breakdown Pie */}
              <ResponsiveContainer width="100%" height={150}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={30}
                    outerRadius={60}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`$${value}`, 'Monthly Cost']} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default ProviderComparison;
