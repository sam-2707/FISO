import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Container, 
  Grid, 
  Card, 
  CardContent,
  CircularProgress,
  Alert,
  Chip,
  LinearProgress
} from '@mui/material';
import { 
  TrendingUp, 
  CloudSync, 
  Analytics, 
  Speed 
} from '@mui/icons-material';
import { apiService } from '../../services/apiService';

const AIInsights = () => {
  const [realTimeData, setRealTimeData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchRealTimeData = async () => {
    try {
      setError(null);
      const data = await apiService.getRealTimePricing();
      setRealTimeData(data);
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (err) {
      setError(`Failed to fetch real-time data: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initialize API service and fetch data
    const initialize = async () => {
      try {
        if (!apiService.isInitialized) {
          await apiService.initialize();
        }
        await fetchRealTimeData();
      } catch (err) {
        setError(`Initialization failed: ${err.message}`);
        setLoading(false);
      }
    };

    initialize();

    // Set up real-time updates every 30 seconds
    const interval = setInterval(fetchRealTimeData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 3 }}>
        <Typography variant="h4" fontWeight="700" gutterBottom>
          AI Insights
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
          <CircularProgress size={60} />
          <Typography sx={{ ml: 2 }}>Loading real-time data...</Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ py: 3 }}>
        <Typography variant="h4" fontWeight="700" gutterBottom>
          AI Insights
        </Typography>
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      </Container>
    );
  }

  const { market_analysis, data_quality, ai_insights } = realTimeData || {};

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight="700">
          AI Insights - Live Data
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Chip 
            icon={<CloudSync />} 
            label={`Updated: ${lastUpdate}`} 
            color="primary" 
            variant="outlined" 
          />
          <Chip 
            label={`${data_quality?.total_data_points || 0} Live Data Points`} 
            color="success" 
          />
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Data Quality Metrics */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Speed color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6" fontWeight="600">
                  Data Quality
                </Typography>
              </Box>
              <Typography variant="h3" color="primary" gutterBottom>
                {data_quality?.accuracy_score || 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Real-time accuracy from {data_quality?.data_sources?.length || 0} sources
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={parseFloat(data_quality?.accuracy_score?.replace('%', '') || 0)} 
                sx={{ mt: 2 }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Market Analysis */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUp color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6" fontWeight="600">
                  Best Value Provider
                </Typography>
              </Box>
              <Typography variant="h4" color="success.main" gutterBottom>
                {market_analysis?.best_value_provider || 'Analyzing...'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Potential savings: {market_analysis?.cost_savings_potential || 'Calculating...'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* AI Insights */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Analytics color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6" fontWeight="600">
                  AI Confidence
                </Typography>
              </Box>
              <Typography variant="h3" color="info.main" gutterBottom>
                {ai_insights?.confidence_score || 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Model accuracy: {ai_insights?.model_accuracy || 'Processing...'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Real-time Pricing Trends */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight="600" gutterBottom>
                Live Market Trends
              </Typography>
              <Grid container spacing={2}>
                {market_analysis?.price_trends && Object.entries(market_analysis.price_trends).map(([provider, trend]) => (
                  <Grid item xs={12} sm={4} key={provider}>
                    <Box sx={{ 
                      p: 2, 
                      border: 1, 
                      borderColor: 'divider', 
                      borderRadius: 1,
                      backgroundColor: trend?.direction === 'increasing' ? 'error.50' : 'success.50'
                    }}>
                      <Typography variant="subtitle1" fontWeight="600">
                        {provider.toUpperCase()}
                      </Typography>
                      <Typography variant="h5" color={trend?.direction === 'increasing' ? 'error.main' : 'success.main'}>
                        {trend?.direction === 'increasing' ? '↗️' : '↘️'} {trend?.change || 'Stable'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {trend?.description || 'Real-time analysis'}
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* AI Recommendations */}
        {ai_insights?.recommendations && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="600" gutterBottom>
                  AI Recommendations
                </Typography>
                <Grid container spacing={1}>
                  {ai_insights.recommendations.map((recommendation, index) => (
                    <Grid item xs={12} sm={6} md={4} key={index}>
                      <Alert severity="info" sx={{ mb: 1 }}>
                        {recommendation}
                      </Alert>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Container>
  );
};

export default AIInsights;
