import React from 'react';
import { Box, Typography, Container } from '@mui/material';

const Settings = () => {
  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Typography variant="h4" fontWeight="700" gutterBottom>
        Settings
      </Typography>
      <Box sx={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography color="text.secondary">
          Settings and configuration components will be implemented in Phase 3 continuation
        </Typography>
      </Box>
    </Container>
  );
};

export default Settings;
