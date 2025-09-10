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
} from '@mui/material';
import {
  TrendingUp,
  CloudQueue,
  Speed,
  Savings,
  Refresh,
} from '@mui/icons-material';

// Hooks
import useRealTimePricing from '../../hooks/useRealTimePricing';

// Components
import MetricsCard from './MetricsCard';
import PricingChart from './PricingChart';
import ProviderComparison from './ProviderComparison';
import AIInsightsSummary from './AIInsightsSummary';

const Dashboard = () => {
  const { data: pricingData, loading: pricingLoading, error: pricingError } = useRealTimePricing();
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
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
            title="Active Alerts"
            value={pricingData.alerts.toString()}
            change={pricingData.alertsChange}
            icon={<TrendingUp />}
            loading={pricingLoading}
            color="warning"
          />
        </Grid>
      </Grid>

      {/* Charts and Analysis Grid */}
      <Grid container spacing={3}>
        {/* Real-time Pricing Chart */}
        <Grid item xs={12} lg={8}>
          <PricingChart data={pricingData} loading={pricingLoading} key={refreshKey} />
        </Grid>

        {/* Provider Comparison */}
        <Grid item xs={12} lg={4}>
          <ProviderComparison data={pricingData} loading={pricingLoading} key={refreshKey} />
        </Grid>

        {/* AI Insights Summary */}
        <Grid item xs={12}>
          <AIInsightsSummary data={pricingData} loading={pricingLoading} key={refreshKey} />
        </Grid>
      </Grid>

      {/* Status Footer */}
      <Box sx={{ mt: 3, textAlign: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          🤖 FISO Enterprise AI Intelligence • Real-time Cloud Cost Optimization • Backend Status: {pricingError ? '⚠️ Demo Mode' : '✅ Live'}
        </Typography>
      </Box>
    </Container>
  );
};

export default Dashboard;
