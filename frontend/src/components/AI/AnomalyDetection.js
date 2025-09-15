import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Alert,
  CircularProgress,
  Chip,
  Button,
  ButtonGroup,
  Switch,
  FormControlLabel,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
  LinearProgress,
  Divider
} from '@mui/material';
import {
  Warning,
  Error,
  Info,
  CheckCircle,
  ExpandMore,
  Refresh,
  TrendingUp,
  TrendingDown,
  Analytics,
  Security,
  Speed,
  AttachMoney
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  ScatterPlot,
  Scatter,
  ReferenceLine
} from 'recharts';

const AnomalyDetection = ({ pricingData }) => {
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedSeverity, setSelectedSeverity] = useState('all');
  const [selectedProvider, setSelectedProvider] = useState('all');
  const [detectionSensitivity, setDetectionSensitivity] = useState('medium');

  // Enhanced anomaly detection
  const detectAnomalies = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/ai/detect-anomalies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sensitivity: detectionSensitivity,
          provider: selectedProvider !== 'all' ? selectedProvider : null,
          lookback_hours: 168 // 7 days
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        setAnomalies(data.anomalies);
      }
    } catch (error) {
      console.error('Error detecting anomalies:', error);
      // Fallback to demo anomalies with enhanced data
      setAnomalies(generateEnhancedDemoAnomalies());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    detectAnomalies();
  }, [detectionSensitivity, selectedProvider]);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(detectAnomalies, 30000); // Refresh every 30 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh, detectionSensitivity, selectedProvider]);

  // Generate enhanced demo anomalies
  const generateEnhancedDemoAnomalies = () => {
    const now = new Date();
    return [
      {
        id: 'anom_001',
        timestamp: new Date(now.getTime() - 2 * 60 * 60 * 1000).toISOString(),
        provider: 'AWS',
        service_type: 'ec2',
        resource_id: 'i-0123456789abcdef0',
        actual_cost: 0.245,
        expected_cost: 0.089,
        anomaly_score: 0.92,
        severity: 'high',
        confidence: 0.94,
        type: 'cost_spike',
        description: 'Unusual cost spike detected in EC2 instances - 175% above baseline',
        root_cause: 'Instance type changed from t3.micro to c5.large',
        recommendation: 'Review instance sizing and consider scheduled scaling',
        impact: 'financial',
        duration_minutes: 120,
        cost_impact: 156.78
      },
      {
        id: 'anom_002',
        timestamp: new Date(now.getTime() - 5 * 60 * 60 * 1000).toISOString(),
        provider: 'Azure',
        service_type: 'vm',
        resource_id: 'vm-production-web-01',
        actual_cost: 0.134,
        expected_cost: 0.096,
        anomaly_score: 0.67,
        severity: 'medium',
        confidence: 0.82,
        type: 'performance_degradation',
        description: 'Moderate cost increase with performance degradation pattern',
        root_cause: 'High CPU utilization causing auto-scaling',
        recommendation: 'Optimize application performance or increase instance size',
        impact: 'performance',
        duration_minutes: 300,
        cost_impact: 38.45
      },
      {
        id: 'anom_003',
        timestamp: new Date(now.getTime() - 1 * 60 * 60 * 1000).toISOString(),
        provider: 'GCP',
        service_type: 'compute',
        resource_id: 'instance-analytics-worker',
        actual_cost: 0.067,
        expected_cost: 0.045,
        anomaly_score: 0.58,
        severity: 'low',
        confidence: 0.73,
        type: 'unusual_pattern',
        description: 'Atypical usage pattern detected - increased compute during off-hours',
        root_cause: 'Batch processing job running longer than expected',
        recommendation: 'Review batch job scheduling and resource allocation',
        impact: 'efficiency',
        duration_minutes: 180,
        cost_impact: 22.15
      },
      {
        id: 'anom_004',
        timestamp: new Date(now.getTime() - 30 * 60 * 1000).toISOString(),
        provider: 'AWS',
        service_type: 'lambda',
        resource_id: 'function-data-processor',
        actual_cost: 0.012,
        expected_cost: 0.003,
        anomaly_score: 0.85,
        severity: 'high',
        confidence: 0.91,
        type: 'execution_anomaly',
        description: 'Abnormal Lambda execution count - 300% increase',
        root_cause: 'Possible infinite loop or retry storm',
        recommendation: 'Investigate function logs and implement circuit breaker',
        impact: 'reliability',
        duration_minutes: 45,
        cost_impact: 9.67
      }
    ];
  };

  // Filter anomalies based on selected criteria
  const filteredAnomalies = useMemo(() => {
    return anomalies.filter(anomaly => {
      const severityMatch = selectedSeverity === 'all' || anomaly.severity === selectedSeverity;
      const providerMatch = selectedProvider === 'all' || anomaly.provider.toLowerCase() === selectedProvider;
      return severityMatch && providerMatch;
    });
  }, [anomalies, selectedSeverity, selectedProvider]);

  // Anomaly statistics
  const anomalyStats = useMemo(() => {
    const stats = {
      total: filteredAnomalies.length,
      high: filteredAnomalies.filter(a => a.severity === 'high').length,
      medium: filteredAnomalies.filter(a => a.severity === 'medium').length,
      low: filteredAnomalies.filter(a => a.severity === 'low').length,
      totalCostImpact: filteredAnomalies.reduce((sum, a) => sum + (a.cost_impact || 0), 0),
      avgConfidence: filteredAnomalies.length > 0 
        ? filteredAnomalies.reduce((sum, a) => sum + a.confidence, 0) / filteredAnomalies.length 
        : 0
    };
    return stats;
  }, [filteredAnomalies]);

  // Get severity color and icon
  const getSeverityInfo = (severity) => {
    switch (severity) {
      case 'high':
        return { color: 'error', icon: <Error />, label: 'Critical' };
      case 'medium':
        return { color: 'warning', icon: <Warning />, label: 'Warning' };
      case 'low':
        return { color: 'info', icon: <Info />, label: 'Info' };
      default:
        return { color: 'default', icon: <CheckCircle />, label: 'Normal' };
    }
  };

  // Get type icon
  const getTypeIcon = (type) => {
    switch (type) {
      case 'cost_spike':
        return <AttachMoney />;
      case 'performance_degradation':
        return <Speed />;
      case 'execution_anomaly':
        return <Analytics />;
      case 'security_anomaly':
        return <Security />;
      default:
        return <TrendingUp />;
    }
  };

  // Generate chart data for anomaly visualization
  const chartData = useMemo(() => {
    const now = new Date();
    const data = [];
    
    // Generate baseline data points
    for (let i = 23; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 60 * 60 * 1000);
      const hour = time.getHours();
      
      // Business hours pattern
      const baseValue = hour >= 9 && hour <= 17 ? 0.08 : 0.05;
      const variance = Math.random() * 0.02 - 0.01;
      
      data.push({
        time: time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        baseline: baseValue,
        actual: baseValue + variance,
        anomaly: null
      });
    }
    
    // Add anomaly points
    filteredAnomalies.forEach(anomaly => {
      const anomalyTime = new Date(anomaly.timestamp);
      const hoursDiff = Math.round((now - anomalyTime) / (1000 * 60 * 60));
      
      if (hoursDiff >= 0 && hoursDiff < 24) {
        const index = 23 - hoursDiff;
        if (data[index]) {
          data[index].anomaly = anomaly.actual_cost;
          data[index].actual = anomaly.actual_cost;
        }
      }
    });
    
    return data;
  }, [filteredAnomalies]);

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Warning />
        Intelligent Anomaly Detection
        <Chip label="Real-time" color="primary" variant="outlined" />
      </Typography>

      {/* Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item>
              <FormControlLabel
                control={
                  <Switch
                    checked={autoRefresh}
                    onChange={(e) => setAutoRefresh(e.target.checked)}
                  />
                }
                label="Auto Refresh"
              />
            </Grid>
            
            <Grid item>
              <Typography variant="subtitle2">Severity Filter:</Typography>
              <ButtonGroup size="small">
                {['all', 'high', 'medium', 'low'].map((severity) => (
                  <Button
                    key={severity}
                    variant={selectedSeverity === severity ? 'contained' : 'outlined'}
                    onClick={() => setSelectedSeverity(severity)}
                  >
                    {severity.charAt(0).toUpperCase() + severity.slice(1)}
                  </Button>
                ))}
              </ButtonGroup>
            </Grid>
            
            <Grid item>
              <Typography variant="subtitle2">Provider:</Typography>
              <ButtonGroup size="small">
                {['all', 'aws', 'azure', 'gcp'].map((provider) => (
                  <Button
                    key={provider}
                    variant={selectedProvider === provider ? 'contained' : 'outlined'}
                    onClick={() => setSelectedProvider(provider)}
                  >
                    {provider.toUpperCase()}
                  </Button>
                ))}
              </ButtonGroup>
            </Grid>
            
            <Grid item>
              <Typography variant="subtitle2">Sensitivity:</Typography>
              <ButtonGroup size="small">
                {['low', 'medium', 'high'].map((sensitivity) => (
                  <Button
                    key={sensitivity}
                    variant={detectionSensitivity === sensitivity ? 'contained' : 'outlined'}
                    onClick={() => setDetectionSensitivity(sensitivity)}
                  >
                    {sensitivity.charAt(0).toUpperCase() + sensitivity.slice(1)}
                  </Button>
                ))}
              </ButtonGroup>
            </Grid>
            
            <Grid item>
              <Button
                variant="contained"
                onClick={detectAnomalies}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={16} /> : <Refresh />}
              >
                Scan Now
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Anomalies
              </Typography>
              <Typography variant="h4">
                {anomalyStats.total}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Last 24 hours
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Critical Issues
              </Typography>
              <Typography variant="h4" color="error.main">
                {anomalyStats.high}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Requires immediate attention
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Cost Impact
              </Typography>
              <Typography variant="h4" color="warning.main">
                ${anomalyStats.totalCostImpact.toFixed(2)}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Additional costs identified
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Avg Confidence
              </Typography>
              <Typography variant="h4" color="success.main">
                {Math.round(anomalyStats.avgConfidence * 100)}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Detection accuracy
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Anomaly Timeline Chart */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Anomaly Detection Timeline (24 Hours)
              </Typography>
              
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis tickFormatter={(value) => `$${value.toFixed(3)}`} />
                  <RechartsTooltip formatter={(value, name) => [`$${value?.toFixed(4)}`, name]} />
                  
                  <Area
                    dataKey="baseline"
                    stackId="1"
                    stroke="#4caf50"
                    fill="#e8f5e8"
                    fillOpacity={0.6}
                    name="Expected Baseline"
                  />
                  <Line
                    type="monotone"
                    dataKey="actual"
                    stroke="#2196f3"
                    strokeWidth={2}
                    dot={false}
                    name="Actual Cost"
                  />
                  <Line
                    type="monotone"
                    dataKey="anomaly"
                    stroke="#f44336"
                    strokeWidth={3}
                    dot={{ fill: '#f44336', strokeWidth: 2, r: 5 }}
                    name="Anomaly"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Anomalies List */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Anomalies
              </Typography>
              
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : filteredAnomalies.length === 0 ? (
                <Alert severity="success" icon={<CheckCircle />}>
                  No anomalies detected. Your infrastructure is running normally.
                </Alert>
              ) : (
                <List>
                  {filteredAnomalies.slice(0, 5).map((anomaly) => {
                    const severityInfo = getSeverityInfo(anomaly.severity);
                    return (
                      <ListItem key={anomaly.id} divider>
                        <ListItemIcon>
                          <Tooltip title={anomaly.type}>
                            {getTypeIcon(anomaly.type)}
                          </Tooltip>
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Chip
                                label={severityInfo.label}
                                color={severityInfo.color}
                                size="small"
                              />
                              <Typography variant="body2">
                                {anomaly.provider} {anomaly.service_type.toUpperCase()}
                              </Typography>
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="body2" color="textSecondary">
                                ${anomaly.actual_cost.toFixed(4)} (expected ${anomaly.expected_cost?.toFixed(4)})
                              </Typography>
                              <Typography variant="caption" color="textSecondary">
                                {new Date(anomaly.timestamp).toLocaleString()}
                              </Typography>
                            </Box>
                          }
                        />
                      </ListItem>
                    );
                  })}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Detailed Anomaly List */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Detailed Anomaly Analysis
              </Typography>
              
              {filteredAnomalies.length === 0 ? (
                <Alert severity="info">
                  No anomalies match the current filter criteria.
                </Alert>
              ) : (
                filteredAnomalies.map((anomaly, index) => {
                  const severityInfo = getSeverityInfo(anomaly.severity);
                  return (
                    <Accordion key={anomaly.id}>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                          {getTypeIcon(anomaly.type)}
                          <Chip 
                            label={severityInfo.label}
                            color={severityInfo.color}
                            size="small"
                          />
                          <Typography variant="body1" sx={{ flexGrow: 1 }}>
                            {anomaly.provider} {anomaly.service_type.toUpperCase()} - {anomaly.resource_id}
                          </Typography>
                          <Chip 
                            label={`${Math.round(anomaly.confidence * 100)}% confident`}
                            size="small"
                            variant="outlined"
                          />
                          <Typography variant="caption" color="textSecondary">
                            {new Date(anomaly.timestamp).toLocaleString()}
                          </Typography>
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Grid container spacing={2}>
                          <Grid item xs={12}>
                            <Typography variant="h6" gutterBottom>
                              {anomaly.description}
                            </Typography>
                            <Divider sx={{ my: 2 }} />
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <Typography variant="subtitle2" gutterBottom>
                              <strong>Root Cause Analysis:</strong>
                            </Typography>
                            <Typography variant="body2" gutterBottom>
                              {anomaly.root_cause}
                            </Typography>
                            
                            <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                              <strong>Recommendation:</strong>
                            </Typography>
                            <Typography variant="body2" gutterBottom>
                              {anomaly.recommendation}
                            </Typography>
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <Typography variant="subtitle2" gutterBottom>
                              <strong>Impact Details:</strong>
                            </Typography>
                            <Box sx={{ mb: 2 }}>
                              <Typography variant="body2">
                                <strong>Type:</strong> {anomaly.impact}
                              </Typography>
                              <Typography variant="body2">
                                <strong>Duration:</strong> {anomaly.duration_minutes} minutes
                              </Typography>
                              <Typography variant="body2">
                                <strong>Cost Impact:</strong> ${anomaly.cost_impact?.toFixed(2)}
                              </Typography>
                              <Typography variant="body2">
                                <strong>Anomaly Score:</strong> {Math.round(anomaly.anomaly_score * 100)}%
                              </Typography>
                            </Box>
                            
                            <Typography variant="subtitle2" gutterBottom>
                              <strong>Detection Confidence:</strong>
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <LinearProgress 
                                variant="determinate" 
                                value={anomaly.confidence * 100}
                                sx={{ flexGrow: 1 }}
                                color={anomaly.confidence > 0.8 ? 'success' : 'warning'}
                              />
                              <Typography variant="body2">
                                {Math.round(anomaly.confidence * 100)}%
                              </Typography>
                            </Box>
                          </Grid>
                        </Grid>
                      </AccordionDetails>
                    </Accordion>
                  );
                })
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AnomalyDetection;