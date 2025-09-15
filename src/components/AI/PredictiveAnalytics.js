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
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress
} from '@mui/material';
import {
  Timeline,
  TrendingUp,
  Warning,
  CheckCircle,
  ExpandMore,
  Psychology,
  ModelTraining,
  Analytics
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
  Scatter
} from 'recharts';

const PredictiveAnalytics = ({ pricingData }) => {
  const [predictions, setPredictions] = useState({});
  const [anomalies, setAnomalies] = useState([]);
  const [modelPerformance, setModelPerformance] = useState({});
  const [loading, setLoading] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState('aws');
  const [selectedService, setSelectedService] = useState('ec2');
  const [horizon, setHorizon] = useState(24);

  // Generate predictions
  const generatePredictions = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/ai/predict-costs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          provider: selectedProvider,
          service_type: selectedService,
          horizon_hours: horizon
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        setPredictions(data.predictions);
      }
    } catch (error) {
      console.error('Error generating predictions:', error);
      // Fallback to demo data
      setPredictions(generateDemoPredictions());
    } finally {
      setLoading(false);
    }
  };

  // Detect anomalies
  const detectAnomalies = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/ai/detect-anomalies?provider=${selectedProvider}&service_type=${selectedService}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setAnomalies(data.anomalies);
      }
    } catch (error) {
      console.error('Error detecting anomalies:', error);
      setAnomalies(generateDemoAnomalies());
    }
  };

  // Get model performance
  const getModelPerformance = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/ai/model-performance');
      const data = await response.json();
      
      if (data.status === 'success') {
        setModelPerformance(data.performance);
      }
    } catch (error) {
      console.error('Error getting model performance:', error);
      setModelPerformance(generateDemoPerformance());
    }
  };

  // Train models
  const trainModels = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/ai/train-models', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      const data = await response.json();
      if (data.status === 'success') {
        await getModelPerformance(); // Refresh performance data
        alert('Models retrained successfully!');
      }
    } catch (error) {
      console.error('Error training models:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    generatePredictions();
    detectAnomalies();
    getModelPerformance();
  }, [selectedProvider, selectedService]);

  // Demo data generators
  const generateDemoPredictions = () => {
    const now = new Date();
    const predictions = [];
    const confidence_lower = [];
    const confidence_upper = [];

    for (let i = 0; i < horizon; i++) {
      const time = new Date(now.getTime() + i * 60 * 60 * 1000);
      const baseValue = 0.085 + Math.sin(i * 0.1) * 0.02 + Math.random() * 0.01;
      
      predictions.push(baseValue);
      confidence_lower.push(baseValue * 0.9);
      confidence_upper.push(baseValue * 1.1);
    }

    return {
      predictions,
      confidence_lower,
      confidence_upper,
      model_type: 'LSTM',
      horizon_hours: horizon
    };
  };

  const generateDemoAnomalies = () => [
    {
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      provider: 'AWS',
      service_type: 'ec2',
      actual_cost: 0.245,
      expected_cost: 0.089,
      anomaly_score: 0.92,
      severity: 'high',
      description: 'Unusual cost spike detected in EC2 instances'
    },
    {
      timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
      provider: 'Azure',
      service_type: 'vm',
      actual_cost: 0.134,
      expected_cost: 0.096,
      anomaly_score: 0.67,
      severity: 'medium',
      description: 'Moderate cost increase in VM usage'
    }
  ];

  const generateDemoPerformance = () => ({
    aws_ec2: {
      provider: 'aws',
      service_type: 'ec2',
      accuracy: 0.87,
      model_type: 'LSTM',
      last_trained: new Date().toISOString()
    },
    azure_vm: {
      provider: 'azure',
      service_type: 'vm',
      accuracy: 0.82,
      model_type: 'statistical',
      last_trained: new Date().toISOString()
    },
    gcp_compute: {
      provider: 'gcp',
      service_type: 'compute',
      accuracy: 0.89,
      model_type: 'LSTM',
      last_trained: new Date().toISOString()
    }
  });

  // Create chart data
  const chartData = useMemo(() => {
    if (!predictions.predictions) return [];

    const now = new Date();
    return predictions.predictions.map((value, index) => ({
      time: new Date(now.getTime() + index * 60 * 60 * 1000).toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      }),
      predicted: value,
      lower: predictions.confidence_lower?.[index] || value * 0.9,
      upper: predictions.confidence_upper?.[index] || value * 1.1
    }));
  }, [predictions]);

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getModelTypeIcon = (modelType) => {
    switch (modelType) {
      case 'LSTM': return <Psychology color="primary" />;
      case 'statistical': return <Analytics color="secondary" />;
      default: return <ModelTraining color="action" />;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Timeline />
        Predictive Analytics Dashboard
        <Chip label="AI-Powered" color="primary" variant="outlined" />
      </Typography>

      {/* Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item>
              <Typography variant="subtitle2">Provider:</Typography>
              <ButtonGroup size="small">
                {['aws', 'azure', 'gcp'].map((provider) => (
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
              <Typography variant="subtitle2">Service:</Typography>
              <ButtonGroup size="small">
                {['ec2', 'lambda', 'rds', 'vm', 'functions', 'compute'].map((service) => (
                  <Button
                    key={service}
                    variant={selectedService === service ? 'contained' : 'outlined'}
                    onClick={() => setSelectedService(service)}
                  >
                    {service.toUpperCase()}
                  </Button>
                ))}
              </ButtonGroup>
            </Grid>
            
            <Grid item>
              <Typography variant="subtitle2">Horizon:</Typography>
              <ButtonGroup size="small">
                {[12, 24, 48, 72].map((hours) => (
                  <Button
                    key={hours}
                    variant={horizon === hours ? 'contained' : 'outlined'}
                    onClick={() => setHorizon(hours)}
                  >
                    {hours}h
                  </Button>
                ))}
              </ButtonGroup>
            </Grid>
            
            <Grid item>
              <Button
                variant="contained"
                onClick={generatePredictions}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={16} /> : <TrendingUp />}
              >
                Generate Predictions
              </Button>
            </Grid>
            
            <Grid item>
              <Button
                variant="outlined"
                onClick={trainModels}
                disabled={loading}
                startIcon={<ModelTraining />}
              >
                Retrain Models
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        {/* Predictions Chart */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cost Predictions - {selectedProvider.toUpperCase()} {selectedService.toUpperCase()}
              </Typography>
              
              {predictions.model_type && (
                <Box sx={{ mb: 2 }}>
                  <Chip 
                    label={`Model: ${predictions.model_type}`}
                    color="primary"
                    size="small"
                    icon={getModelTypeIcon(predictions.model_type)}
                  />
                </Box>
              )}

              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis tickFormatter={(value) => `$${value.toFixed(4)}`} />
                  <RechartsTooltip formatter={(value) => [`$${value.toFixed(4)}`, 'Cost']} />
                  
                  <Area
                    dataKey="upper"
                    stackId="1"
                    stroke="none"
                    fill="#e3f2fd"
                    fillOpacity={0.6}
                  />
                  <Area
                    dataKey="lower"
                    stackId="1"
                    stroke="none"
                    fill="#ffffff"
                    fillOpacity={1}
                  />
                  <Line
                    type="monotone"
                    dataKey="predicted"
                    stroke="#1976d2"
                    strokeWidth={2}
                    dot={{ fill: '#1976d2', strokeWidth: 2, r: 3 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Model Performance */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Model Performance
              </Typography>
              
              {Object.entries(modelPerformance).map(([key, model]) => (
                <Box key={key} sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {getModelTypeIcon(model.model_type)}
                      <Typography variant="body2">
                        {model.provider.toUpperCase()} {model.service_type.toUpperCase()}
                      </Typography>
                    </Box>
                    <Chip 
                      label={`${Math.round(model.accuracy * 100)}%`}
                      color={model.accuracy > 0.8 ? 'success' : 'warning'}
                      size="small"
                    />
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={model.accuracy * 100}
                    color={model.accuracy > 0.8 ? 'success' : 'warning'}
                  />
                  <Typography variant="caption" color="text.secondary">
                    {model.model_type} model
                  </Typography>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Anomalies */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Warning />
                Cost Anomalies Detected
              </Typography>
              
              {anomalies.length === 0 ? (
                <Alert severity="success" icon={<CheckCircle />}>
                  No anomalies detected in the recent data. Your costs are following normal patterns.
                </Alert>
              ) : (
                anomalies.map((anomaly, index) => (
                  <Accordion key={index}>
                    <AccordionSummary expandIcon={<ExpandMore />}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                        <Chip 
                          label={anomaly.severity}
                          color={getSeverityColor(anomaly.severity)}
                          size="small"
                        />
                        <Typography variant="body2" sx={{ flexGrow: 1 }}>
                          {anomaly.provider} {anomaly.service_type.toUpperCase()} - ${anomaly.actual_cost.toFixed(4)}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {new Date(anomaly.timestamp).toLocaleString()}
                        </Typography>
                      </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Grid container spacing={2}>
                        <Grid item xs={12} md={6}>
                          <Typography variant="body2" gutterBottom>
                            <strong>Description:</strong> {anomaly.description}
                          </Typography>
                          <Typography variant="body2" gutterBottom>
                            <strong>Anomaly Score:</strong> {Math.round(anomaly.anomaly_score * 100)}%
                          </Typography>
                        </Grid>
                        <Grid item xs={12} md={6}>
                          <Typography variant="body2" gutterBottom>
                            <strong>Actual Cost:</strong> ${anomaly.actual_cost.toFixed(4)}
                          </Typography>
                          <Typography variant="body2" gutterBottom>
                            <strong>Expected Cost:</strong> ${anomaly.expected_cost?.toFixed(4) || 'N/A'}
                          </Typography>
                        </Grid>
                      </Grid>
                    </AccordionDetails>
                  </Accordion>
                ))
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default PredictiveAnalytics;