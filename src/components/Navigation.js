import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Tabs,
  Tab,
  Box,
  Container
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import DashboardIcon from '@mui/icons-material/Dashboard';
import SettingsIcon from '@mui/icons-material/Settings';

const Navigation = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Determine current tab based on route
  const getCurrentTab = () => {
    if (location.pathname === '/operations') {
      return 1;
    }
    return 0; // Default to dashboard
  };

  const handleTabChange = (event, newValue) => {
    if (newValue === 0) {
      navigate('/');
    } else if (newValue === 1) {
      navigate('/operations');
    }
  };

  return (
    <AppBar position="static" elevation={1} sx={{ backgroundColor: '#1976d2', mb: 3 }}>
      <Container maxWidth="xl">
        <Toolbar sx={{ px: 0 }}>
          <Typography
            variant="h6"
            component="div"
            sx={{ flexGrow: 1, fontWeight: 'bold' }}
          >
            FISO - Cloud Cost Optimization
          </Typography>
          
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs
              value={getCurrentTab()}
              onChange={handleTabChange}
              textColor="inherit"
              indicatorColor="secondary"
              sx={{
                '& .MuiTab-root': {
                  color: 'rgba(255, 255, 255, 0.7)',
                  '&.Mui-selected': {
                    color: 'white',
                  },
                },
                '& .MuiTabs-indicator': {
                  backgroundColor: 'white',
                },
              }}
            >
              <Tab
                icon={<DashboardIcon />}
                label="Dashboard"
                iconPosition="start"
                sx={{ minHeight: 64 }}
              />
              <Tab
                icon={<SettingsIcon />}
                label="Operations"
                iconPosition="start"
                sx={{ minHeight: 64 }}
              />
            </Tabs>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Navigation;