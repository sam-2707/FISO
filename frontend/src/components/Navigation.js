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
    <AppBar 
      position="static" 
      elevation={0} 
      sx={{ 
        backgroundColor: '#ffffff',
        color: '#2d3748',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        borderBottom: '1px solid rgba(226, 232, 240, 0.8)',
        mb: 0
      }}
    >
      <Container maxWidth="xl">
        <Toolbar sx={{ px: 0, py: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
            <img 
              src="/atharman_logo.svg" 
              alt="Atharman" 
              style={{ 
                height: 40, 
                marginRight: 16
              }}
            />
            <Box>
              <Typography
                variant="h6"
                component="div"
                sx={{ 
                  fontWeight: 700,
                  color: '#2d3748',
                  mb: -0.5
                }}
              >
                Atharman
              </Typography>
              <Typography
                variant="caption"
                sx={{ 
                  color: '#718096',
                  fontWeight: 500,
                  letterSpacing: '0.5px',
                  textTransform: 'uppercase',
                  fontSize: '0.7rem'
                }}
              >
                AI Financial Intelligence
              </Typography>
            </Box>
          </Box>
          
          <Box>
            <Tabs
              value={getCurrentTab()}
              onChange={handleTabChange}
              sx={{
                '& .MuiTab-root': {
                  color: '#718096',
                  fontWeight: 500,
                  textTransform: 'none',
                  minHeight: 48,
                  padding: '8px 16px',
                  borderRadius: 1,
                  margin: '0 4px',
                  transition: 'all 0.2s ease-in-out',
                  '&.Mui-selected': {
                    color: '#2d3748',
                    backgroundColor: '#f7fafc',
                    fontWeight: 600,
                  },
                  '&:hover': {
                    backgroundColor: '#f7fafc',
                  },
                },
                '& .MuiTabs-indicator': {
                  display: 'none',
                },
              }}
            >
              <Tab
                icon={<DashboardIcon />}
                label="Dashboard"
                iconPosition="start"
              />
              <Tab
                icon={<SettingsIcon />}
                label="Operations"
                iconPosition="start"
              />
            </Tabs>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Navigation;