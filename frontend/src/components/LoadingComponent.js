import React from 'react';
import {
  Box,
  Card,
  CardContent,
  CircularProgress,
  LinearProgress,
  Typography,
  Fade,
  Skeleton
} from '@mui/material';
import { TrendingUp, Psychology, Speed } from '@mui/icons-material';

const LoadingComponent = ({ 
  type = 'default', 
  message = 'Loading...', 
  progress = null,
  showDetails = false,
  fullScreen = false 
}) => {
  const LoadingIcon = () => {
    switch (type) {
      case 'analytics':
        return <TrendingUp sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />;
      case 'ai':
        return <Psychology sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />;
      case 'performance':
        return <Speed sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />;
      default:
        return null;
    }
  };

  const LoadingContent = () => (
    <Box sx={{ textAlign: 'center', p: 3 }}>
      <LoadingIcon />
      <CircularProgress 
        size={60} 
        thickness={4}
        sx={{ mb: 3, color: 'primary.main' }}
        value={progress}
        variant={progress !== null ? "determinate" : "indeterminate"}
      />
      <Typography variant="h6" gutterBottom color="primary">
        {message}
      </Typography>
      
      {progress !== null && (
        <Box sx={{ mt: 2, mb: 2 }}>
          <LinearProgress 
            variant="determinate" 
            value={progress} 
            sx={{ height: 6, borderRadius: 3 }}
          />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {Math.round(progress)}% complete
          </Typography>
        </Box>
      )}
      
      {showDetails && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="body2" color="text.secondary" paragraph>
            Fetching real-time data from cloud providers...
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center', flexWrap: 'wrap' }}>
            {['AWS', 'Azure', 'GCP'].map((provider, index) => (
              <Typography 
                key={provider}
                variant="caption" 
                sx={{ 
                  px: 1.5, 
                  py: 0.5, 
                  backgroundColor: 'action.hover',
                  borderRadius: 1,
                  animation: `pulse 2s infinite ${index * 0.5}s`
                }}
              >
                {provider}
              </Typography>
            ))}
          </Box>
        </Box>
      )}
    </Box>
  );

  if (fullScreen) {
    return (
      <Fade in timeout={300}>
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999
          }}
        >
          <Card elevation={3} sx={{ minWidth: 300 }}>
            <CardContent>
              <LoadingContent />
            </CardContent>
          </Card>
        </Box>
      </Fade>
    );
  }

  return (
    <Fade in timeout={300}>
      <Card sx={{ width: '100%', minHeight: 200 }}>
        <CardContent>
          <LoadingContent />
        </CardContent>
      </Card>
    </Fade>
  );
};

// Skeleton loader for dashboard components
export const DashboardSkeleton = () => (
  <Box sx={{ p: 3 }}>
    {/* Header skeleton */}
    <Box sx={{ mb: 4 }}>
      <Skeleton variant="text" width="40%" height={40} />
      <Skeleton variant="text" width="60%" height={24} />
    </Box>
    
    {/* Stats cards skeleton */}
    <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 3, mb: 4 }}>
      {[1, 2, 3, 4].map((item) => (
        <Card key={item}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Skeleton variant="circular" width={40} height={40} />
              <Box sx={{ ml: 2, flex: 1 }}>
                <Skeleton variant="text" width="80%" />
                <Skeleton variant="text" width="60%" />
              </Box>
            </Box>
            <Skeleton variant="text" width="40%" height={32} />
          </CardContent>
        </Card>
      ))}
    </Box>
    
    {/* Chart skeleton */}
    <Card>
      <CardContent>
        <Skeleton variant="text" width="30%" height={32} sx={{ mb: 2 }} />
        <Skeleton variant="rectangular" width="100%" height={300} />
      </CardContent>
    </Card>
  </Box>
);

// Table skeleton loader
export const TableSkeleton = ({ rows = 5, columns = 4 }) => (
  <Box sx={{ width: '100%' }}>
    {/* Header */}
    <Box sx={{ display: 'flex', gap: 2, mb: 2, pb: 2, borderBottom: 1, borderColor: 'divider' }}>
      {Array.from({ length: columns }).map((_, index) => (
        <Skeleton key={index} variant="text" width={`${100/columns}%`} height={24} />
      ))}
    </Box>
    
    {/* Rows */}
    {Array.from({ length: rows }).map((_, rowIndex) => (
      <Box key={rowIndex} sx={{ display: 'flex', gap: 2, mb: 1.5 }}>
        {Array.from({ length: columns }).map((_, colIndex) => (
          <Skeleton key={colIndex} variant="text" width={`${100/columns}%`} height={20} />
        ))}
      </Box>
    ))}
  </Box>
);

// Chart skeleton loader
export const ChartSkeleton = ({ height = 300 }) => (
  <Card>
    <CardContent>
      <Box sx={{ mb: 2 }}>
        <Skeleton variant="text" width="40%" height={32} />
        <Skeleton variant="text" width="60%" height={20} />
      </Box>
      <Skeleton variant="rectangular" width="100%" height={height} sx={{ borderRadius: 1 }} />
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2, gap: 2 }}>
        {[1, 2, 3].map((item) => (
          <Box key={item} sx={{ display: 'flex', alignItems: 'center' }}>
            <Skeleton variant="circular" width={12} height={12} />
            <Skeleton variant="text" width={60} sx={{ ml: 1 }} />
          </Box>
        ))}
      </Box>
    </CardContent>
  </Card>
);

export default LoadingComponent;