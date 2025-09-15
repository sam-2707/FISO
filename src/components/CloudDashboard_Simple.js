import React, { useState } from 'react';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
  Alert,
  Button,
} from '@mui/material';
import {
  TrendingUp,
  CloudQueue,
  Speed,
  Savings,
  Refresh,
  Settings,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

// Hooks
import useRealTimePricing from '../hooks/useRealTimePricing';

// Components
import MetricsCard from './Dashboard/MetricsCard';
import PricingChart from './Dashboard/PricingChart';
import ProviderComparison from './Dashboard/ProviderComparison';
import AIInsightsSummary from './Dashboard/AIInsightsSummary';

const CloudDashboard = () => {
  const { data: pricingData, loading: pricingLoading, error: pricingError } = useRealTimePricing();
  const [refreshKey, setRefreshKey] = useState(0);
  const navigate = useNavigate();

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  const handleOperationsClick = () => {
    navigate('/operations');
  };

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" fontWeight="700" gutterBottom>
            🚀 FISO Enterprise Intelligence Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Real-time cloud intelligence and cost optimization insights
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {pricingError && (
            <Alert severity="warning" sx={{ mr: 2 }}>
              Using demo data - Backend connection issues
            </Alert>
          )}
          
          <Button
            variant="outlined"
            onClick={handleOperationsClick}
            startIcon={<Settings />}
            color="primary"
          >
            Operations Dashboard
          </Button>
          
          <Tooltip title="Refresh Data">
            <IconButton 
              onClick={handleRefresh} 
              disabled={pricingLoading}
              color="primary"
            >
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Main Metrics Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricsCard
            title="Total Monthly Cost"
            value={`$${pricingData.currentCost.toFixed(2)}`}
            change={pricingData.costChange}
            icon={<CloudQueue />}
            loading={pricingLoading}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <MetricsCard
            title="Potential Savings"
            value={`$${pricingData.monthlySavings.toFixed(2)}`}
            change={pricingData.savingsChange}
            icon={<Savings />}
            loading={pricingLoading}
            color="success"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <MetricsCard
            title="Active Resources"
            value={pricingData.activeResources.toString()}
            change={pricingData.resourcesChange}
            icon={<Speed />}
            loading={pricingLoading}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <MetricsCard
            title="Optimization Score"
            value={`${pricingData.optimizationScore}%`}
            change={pricingData.scoreChange}
            icon={<TrendingUp />}
            loading={pricingLoading}
            color="info"
          />
        </Grid>
      </Grid>

      {/* Charts and Analysis */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} lg={8}>
          <PricingChart 
            data={pricingData.chartData} 
            loading={pricingLoading}
            refreshKey={refreshKey}
          />
        </Grid>
        
        <Grid item xs={12} lg={4}>
          <ProviderComparison 
            data={pricingData.providerData} 
            loading={pricingLoading}
          />
        </Grid>
      </Grid>

      {/* AI Insights */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <AIInsightsSummary 
            insights={pricingData.aiInsights}
            loading={pricingLoading}
          />
        </Grid>
      </Grid>
    </Container>
  );
};

export default CloudDashboard;