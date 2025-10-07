import React from 'react';
import { Typography, Box } from '@mui/material';

const TestDashboard = () => {
  return (
    <Box sx={{ p: 4, backgroundColor: '#ff0000', color: 'white' }}>
      <Typography variant="h1" sx={{ mb: 2 }}>
        🚨 TEST DASHBOARD - IF YOU SEE THIS, ROUTING WORKS! 🚨
      </Typography>
      <Typography variant="h2" sx={{ mb: 2 }}>
        This is the TEST component - not the real dashboard
      </Typography>
      <Typography variant="body1">
        If you can see this red screen, then the routing is working correctly
        and we can fix the CloudDashboard component.
      </Typography>
    </Box>
  );
};

export default TestDashboard;