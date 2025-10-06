/**
 * Connection Status Component
 * Shows real-time connection status to backend and API endpoints
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  CircularProgress,
  Button,
  Alert,
  Collapse,
  Grid,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import apiService from '../services/apiService';

const ConnectionStatus = () => {
  const [connectionStatus, setConnectionStatus] = useState({
    status: 'checking',
    health: null,
    error: null,
    lastCheck: null,
  });
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState(false);

  const checkConnectionStatus = async () => {
    setLoading(true);
    try {
      // Test connection using production endpoints
      const [healthData, pricingData] = await Promise.all([
        apiService.getHealthStatus(),
        apiService.getPricingData()
      ]);
      
      setConnectionStatus({
        status: 'connected',
        health: healthData,
        sampleData: pricingData,
        error: null,
        lastCheck: new Date().toLocaleTimeString(),
      });
    } catch (error) {
      setConnectionStatus({
        status: 'disconnected',
        health: null,
        error: error.message,
        lastCheck: new Date().toLocaleTimeString(),
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkConnectionStatus();
    
    // Check connection every 30 seconds
    const interval = setInterval(checkConnectionStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    switch (connectionStatus.status) {
      case 'connected': return 'success';
      case 'disconnected': return 'error';
      case 'checking': return 'info';
      default: return 'warning';
    }
  };

  const getStatusIcon = () => {
    if (loading) return <CircularProgress size={16} />;
    
    switch (connectionStatus.status) {
      case 'connected': return <CheckCircleIcon />;
      case 'disconnected': return <ErrorIcon />;
      default: return <CircularProgress size={16} />;
    }
  };

  return (
    <Card elevation={2} sx={{ mb: 2 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
          <Typography variant="h6">Backend Connection</Typography>
          
          <Box display="flex" alignItems="center" gap={1}>
            <Chip
              icon={getStatusIcon()}
              label={connectionStatus.status.toUpperCase()}
              color={getStatusColor()}
              size="small"
            />
            
            <Button
              size="small"
              startIcon={<RefreshIcon />}
              onClick={checkConnectionStatus}
              disabled={loading}
            >
              Refresh
            </Button>
            
            <Button
              size="small"
              endIcon={expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              onClick={() => setExpanded(!expanded)}
            >
              Details
            </Button>
          </Box>
        </Box>

        {connectionStatus.lastCheck && (
          <Typography variant="caption" color="text.secondary">
            Last checked: {connectionStatus.lastCheck}
          </Typography>
        )}

        {connectionStatus.error && (
          <Alert severity="error" sx={{ mt: 1 }}>
            {connectionStatus.error}
          </Alert>
        )}

        <Collapse in={expanded}>
          <Box mt={2}>
            {connectionStatus.health && (
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Backend Health:
                  </Typography>
                  <Box pl={2}>
                    <Typography variant="body2">
                      Status: <Chip label={connectionStatus.health.status} size="small" color="success" />
                    </Typography>
                    <Typography variant="body2">
                      Version: {connectionStatus.health.version}
                    </Typography>
                    <Typography variant="body2">
                      AI Engine: <Chip 
                        label={connectionStatus.health.ai_engine_status} 
                        size="small" 
                        color={connectionStatus.health.ai_engine_status === 'operational' ? 'success' : 'warning'} 
                      />
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Available Services:
                  </Typography>
                  <Box pl={2}>
                    {connectionStatus.health.services && Object.entries(connectionStatus.health.services).map(([service, status]) => (
                      <Typography key={service} variant="body2">
                        {service}: <Chip 
                          label={status ? 'Available' : 'Unavailable'} 
                          size="small" 
                          color={status ? 'success' : 'error'} 
                        />
                      </Typography>
                    ))}
                  </Box>
                </Grid>
              </Grid>
            )}

            {connectionStatus.sampleData && (
              <Box mt={2}>
                <Typography variant="subtitle2" gutterBottom>
                  Sample API Response:
                </Typography>
                <Box 
                  component="pre" 
                  sx={{ 
                    backgroundColor: '#f5f5f5',
                    p: 1,
                    borderRadius: 1,
                    fontSize: '0.75rem',
                    overflow: 'auto',
                    maxHeight: 200,
                  }}
                >
                  {JSON.stringify(connectionStatus.sampleData, null, 2)}
                </Box>
              </Box>
            )}
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
};

export default ConnectionStatus;