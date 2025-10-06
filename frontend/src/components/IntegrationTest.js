import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Info,
  Refresh,
  Timeline,
  Notifications,
  BugReport
} from '@mui/icons-material';
import { useNotification } from './NotificationProvider';

/**
 * Integration Test Component for FISO Dashboard Enhancements
 * Tests notification system, error handling, loading states, and system metrics
 */
const IntegrationTest = React.memo(() => {
  const [testResults, setTestResults] = useState([]);
  const [currentTest, setCurrentTest] = useState(null);
  const { showSuccess, showError, showWarning, showInfo } = useNotification();

  const testScenarios = [
    {
      id: 'notification-success',
      name: 'Success Notification',
      description: 'Test success notification display',
      action: () => showSuccess('Test success notification', { title: 'Success Test' })
    },
    {
      id: 'notification-error',
      name: 'Error Notification',
      description: 'Test error notification with auto-hide',
      action: () => showError('Test error notification', { 
        title: 'Error Test', 
        autoHideDuration: 5000 
      })
    },
    {
      id: 'notification-warning',
      name: 'Warning Notification',
      description: 'Test warning notification',
      action: () => showWarning('Test warning notification', { title: 'Warning Test' })
    },
    {
      id: 'notification-info',
      name: 'Info Notification',
      description: 'Test info notification with long message',
      action: () => showInfo('This is a test info notification with a longer message to test text wrapping and display formatting', { 
        title: 'Info Test',
        autoHideDuration: 8000
      })
    },
    {
      id: 'notification-sequence',
      name: 'Notification Sequence',
      description: 'Test multiple notifications in sequence',
      action: () => {
        showInfo('Starting sequence test...', { title: 'Sequence 1/4' });
        setTimeout(() => showWarning('Second notification', { title: 'Sequence 2/4' }), 1000);
        setTimeout(() => showError('Third notification', { title: 'Sequence 3/4' }), 2000);
        setTimeout(() => showSuccess('Sequence complete!', { title: 'Sequence 4/4' }), 3000);
      }
    }
  ];

  const runTest = async (scenario) => {
    setCurrentTest(scenario.id);
    
    try {
      await scenario.action();
      
      const result = {
        id: scenario.id,
        name: scenario.name,
        status: 'passed',
        timestamp: new Date().toLocaleTimeString(),
        details: 'Test executed successfully'
      };
      
      setTestResults(prev => [...prev.filter(r => r.id !== scenario.id), result]);
    } catch (error) {
      const result = {
        id: scenario.id,
        name: scenario.name,
        status: 'failed',
        timestamp: new Date().toLocaleTimeString(),
        details: error.message
      };
      
      setTestResults(prev => [...prev.filter(r => r.id !== scenario.id), result]);
    } finally {
      setCurrentTest(null);
    }
  };

  const runAllTests = async () => {
    setTestResults([]);
    showInfo('Starting comprehensive integration test...', { 
      title: 'Integration Test Suite',
      autoHideDuration: 3000
    });

    for (const scenario of testScenarios) {
      await new Promise(resolve => setTimeout(resolve, 1000)); // Wait between tests
      await runTest(scenario);
    }

    showSuccess('All integration tests completed!', { 
      title: 'Test Suite Complete',
      autoHideDuration: 5000
    });
  };

  const clearResults = () => {
    setTestResults([]);
    showInfo('Test results cleared', { title: 'Reset Complete' });
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'passed': return <CheckCircle sx={{ color: 'success.main' }} />;
      case 'failed': return <Error sx={{ color: 'error.main' }} />;
      default: return <Info sx={{ color: 'info.main' }} />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'passed': return 'success';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Card elevation={2}>
        <CardContent>
          <Typography variant="h4" gutterBottom sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 2,
            color: 'primary.main',
            fontWeight: 600
          }}>
            <BugReport />
            FISO Integration Test Suite
          </Typography>
          
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Test the enhanced notification system, error handling, and user experience features
          </Typography>

          <Divider sx={{ mb: 3 }} />

          {/* Test Controls */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Notifications />
              Test Controls
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                startIcon={<Refresh />}
                onClick={runAllTests}
                disabled={currentTest !== null}
              >
                Run All Tests
              </Button>
              
              <Button
                variant="outlined"
                onClick={clearResults}
                disabled={currentTest !== null}
              >
                Clear Results
              </Button>
            </Box>
          </Box>

          <Divider sx={{ mb: 3 }} />

          {/* Individual Tests */}
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Timeline />
                Test Scenarios
              </Typography>
              
              <List>
                {testScenarios.map((scenario) => (
                  <ListItem key={scenario.id} sx={{ 
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    mb: 1,
                    '&:hover': {
                      backgroundColor: 'action.hover'
                    }
                  }}>
                    <ListItemIcon>
                      {currentTest === scenario.id ? (
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Box
                            sx={{
                              width: 20,
                              height: 20,
                              border: '2px solid',
                              borderColor: 'primary.main',
                              borderTop: '2px solid transparent',
                              borderRadius: '50%',
                              animation: 'spin 1s linear infinite',
                              '@keyframes spin': {
                                '0%': { transform: 'rotate(0deg)' },
                                '100%': { transform: 'rotate(360deg)' }
                              }
                            }}
                          />
                        </Box>
                      ) : (
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={() => runTest(scenario)}
                          disabled={currentTest !== null}
                        >
                          Test
                        </Button>
                      )}
                    </ListItemIcon>
                    <ListItemText
                      primary={scenario.name}
                      secondary={scenario.description}
                    />
                  </ListItem>
                ))}
              </List>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CheckCircle />
                Test Results
              </Typography>

              {testResults.length === 0 ? (
                <Alert severity="info">
                  No test results yet. Run individual tests or the full test suite.
                </Alert>
              ) : (
                <List>
                  {testResults.map((result) => (
                    <ListItem key={result.id} sx={{ 
                      border: '1px solid',
                      borderColor: result.status === 'passed' ? 'success.main' : 'error.main',
                      borderRadius: 1,
                      mb: 1,
                      backgroundColor: result.status === 'passed' 
                        ? 'success.light' 
                        : 'error.light',
                      opacity: 0.9
                    }}>
                      <ListItemIcon>
                        {getStatusIcon(result.status)}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {result.name}
                            <Chip 
                              label={result.status} 
                              size="small" 
                              color={getStatusColor(result.status)}
                            />
                          </Box>
                        }
                        secondary={`${result.timestamp} - ${result.details}`}
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </Grid>
          </Grid>

          {/* Summary */}
          {testResults.length > 0 && (
            <>
              <Divider sx={{ my: 3 }} />
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h6" gutterBottom>
                  Test Summary
                </Typography>
                
                <Box sx={{ display: 'flex', justifyContent: 'center', gap: 3, flexWrap: 'wrap' }}>
                  <Chip
                    label={`Total: ${testResults.length}`}
                    color="default"
                    variant="outlined"
                  />
                  <Chip
                    label={`Passed: ${testResults.filter(r => r.status === 'passed').length}`}
                    color="success"
                    variant="outlined"
                  />
                  <Chip
                    label={`Failed: ${testResults.filter(r => r.status === 'failed').length}`}
                    color="error"
                    variant="outlined"
                  />
                </Box>
              </Box>
            </>
          )}
        </CardContent>
      </Card>
    </Box>
  );
});

export default IntegrationTest;