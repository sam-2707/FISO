import React from 'react';
import {
  Box,
  Chip,
  Typography,
  Tooltip,
  Card,
  CardContent,
  Grid
} from '@mui/material';
import {
  Wifi as WifiIcon,
  WifiOff as WifiOffIcon,
  Update as UpdateIcon,
  NotificationsActive as NotificationsActiveIcon,
  TrendingUp as TrendingUpIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';

const RealTimeStatus = ({ 
  connectionStatus, 
  realTimeData, 
  realTimeEnabled,
  onToggleRealTime,
  onRefresh 
}) => {
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Never';
    return new Date(timestamp).toLocaleTimeString();
  };

  const getConnectionColor = () => {
    return connectionStatus.isConnected ? 'success' : 'error';
  };

  const getConnectionIcon = () => {
    return connectionStatus.isConnected ? <WifiIcon /> : <WifiOffIcon />;
  };

  return (
    <Card sx={{ mb: 2, border: '1px solid #e0e0e0' }}>
      <CardContent sx={{ py: 1.5 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={3}>
            <Box display="flex" alignItems="center" gap={1}>
              <Chip
                icon={getConnectionIcon()}
                label={connectionStatus.isConnected ? 'Live Connection' : 'Disconnected'}
                color={getConnectionColor()}
                size="small"
              />
              <Tooltip title="Toggle real-time updates">
                <Chip
                  icon={<UpdateIcon />}
                  label={realTimeEnabled ? 'Real-Time ON' : 'Real-Time OFF'}
                  color={realTimeEnabled ? 'primary' : 'default'}
                  size="small"
                  onClick={onToggleRealTime}
                  clickable
                />
              </Tooltip>
              {onRefresh && (
                <Tooltip title="Refresh data now">
                  <Chip
                    icon={<RefreshIcon />}
                    label="Refresh"
                    color="secondary"
                    size="small"
                    onClick={onRefresh}
                    clickable
                  />
                </Tooltip>
              )}
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box display="flex" alignItems="center" gap={1}>
              <UpdateIcon fontSize="small" color="action" />
              <Typography variant="caption" color="text.secondary">
                Last Update: {formatTimestamp(realTimeData.lastUpdate)}
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box display="flex" alignItems="center" gap={1}>
              <NotificationsActiveIcon fontSize="small" color="action" />
              <Typography variant="caption" color="text.secondary">
                Alerts: {realTimeData.alertCount || 0}
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box display="flex" alignItems="center" gap={1}>
              <TrendingUpIcon fontSize="small" color="action" />
              <Typography variant="caption" color="text.secondary">
                Active Streams: {connectionStatus.activeSubscriptions?.length || 0}
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {realTimeData.lastAlert && (
          <Box mt={1}>
            <Chip
              icon={<NotificationsActiveIcon />}
              label={`Latest: ${realTimeData.lastAlert.title} - ${realTimeData.lastAlert.message}`}
              color="warning"
              size="small"
              sx={{ maxWidth: '100%' }}
            />
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default RealTimeStatus;