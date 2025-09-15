import React from 'react';
import { Box, Typography, Button, Card, CardContent } from '@mui/material';
import { Error as ErrorIcon } from '@mui/icons-material';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box sx={{ p: 3, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
          <Card sx={{ maxWidth: 500, textAlign: 'center' }}>
            <CardContent>
              <ErrorIcon sx={{ fontSize: 60, color: 'error.main', mb: 2 }} />
              <Typography variant="h5" gutterBottom>
                Something went wrong
              </Typography>
              <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
                An error occurred while rendering this component. Please try refreshing the page.
              </Typography>
              <Button 
                variant="contained" 
                onClick={() => window.location.reload()}
                sx={{ mr: 2 }}
              >
                Refresh Page
              </Button>
              <Button 
                variant="outlined" 
                onClick={() => this.setState({ hasError: false, error: null, errorInfo: null })}
              >
                Try Again
              </Button>
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <Box sx={{ mt: 3, textAlign: 'left' }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Error Details:
                  </Typography>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem', color: 'error.main' }}>
                    {this.state.error.toString()}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;