import React from 'react';
import {
  Box,
  Alert,
  AlertTitle,
  Button,
  Typography,
  Card,
  CardContent
} from '@mui/material';
import { Refresh, BugReport, Home } from '@mui/icons-material';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null,
      retryCount: 0
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
    
    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('🚨 React Error Boundary caught an error:', error, errorInfo);
    }
  }

  handleRetry = () => {
    this.setState(prevState => ({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: prevState.retryCount + 1
    }));
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      const { error, errorInfo, retryCount } = this.state;
      const isReactError = error?.name === 'ChunkLoadError' || error?.message?.includes('Loading chunk');
      
      return (
        <Box 
          sx={{ 
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: '#f5f5f5',
            padding: 3
          }}
        >
          <Card sx={{ maxWidth: 600, width: '100%' }}>
            <CardContent sx={{ padding: 4 }}>
              {/* Error Icon and Title */}
              <Box sx={{ textAlign: 'center', mb: 3 }}>
                <BugReport sx={{ fontSize: 64, color: 'error.main', mb: 2 }} />
                <Typography variant="h4" component="h1" gutterBottom>
                  Oops! Something went wrong
                </Typography>
                <Typography variant="body1" color="text.secondary" paragraph>
                  {isReactError 
                    ? "There was an issue loading the application. This might be due to a network issue or an updated version."
                    : "An unexpected error occurred while running the application."
                  }
                </Typography>
              </Box>

              {/* Error Details (Development Mode) */}
              {process.env.NODE_ENV === 'development' && error && (
                <Alert severity="error" sx={{ mb: 3, textAlign: 'left' }}>
                  <AlertTitle>Error Details (Development Mode)</AlertTitle>
                  <Typography variant="body2" component="pre" sx={{ 
                    whiteSpace: 'pre-wrap', 
                    fontSize: '0.8rem',
                    maxHeight: 200,
                    overflow: 'auto'
                  }}>
                    {error.toString()}
                    {errorInfo.componentStack}
                  </Typography>
                </Alert>
              )}

              {/* Retry Information */}
              {retryCount > 0 && (
                <Alert severity="info" sx={{ mb: 3 }}>
                  <Typography variant="body2">
                    Retry attempt: {retryCount}/3
                  </Typography>
                </Alert>
              )}

              {/* Action Buttons */}
              <Box sx={{ 
                display: 'flex', 
                gap: 2, 
                justifyContent: 'center',
                flexWrap: 'wrap'
              }}>
                <Button
                  variant="contained"
                  startIcon={<Refresh />}
                  onClick={this.handleRetry}
                  disabled={retryCount >= 3}
                  sx={{ minWidth: 140 }}
                >
                  {retryCount >= 3 ? 'Max Retries' : 'Try Again'}
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<Home />}
                  onClick={this.handleGoHome}
                  sx={{ minWidth: 140 }}
                >
                  Go Home
                </Button>
                
                {isReactError && (
                  <Button
                    variant="text"
                    onClick={() => window.location.reload()}
                    sx={{ minWidth: 140 }}
                  >
                    Force Reload
                  </Button>
                )}
              </Box>

              {/* Additional Help */}
              <Box sx={{ mt: 4, textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  If this problem persists, please try:
                </Typography>
                <Typography variant="body2" color="text.secondary" component="ul" sx={{ mt: 1, textAlign: 'left' }}>
                  <li>Refreshing the page</li>
                  <li>Clearing your browser cache</li>
                  <li>Checking your internet connection</li>
                  <li>Contacting support if the issue continues</li>
                </Typography>
              </Box>

            </CardContent>
          </Card>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;