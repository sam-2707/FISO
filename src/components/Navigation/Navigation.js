import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Box,
  Divider,
  Switch,
  FormControlLabel,
  Avatar,
  Chip,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Assessment as AssessmentIcon,
  Psychology as AIIcon,
  Settings as SettingsIcon,
  LightMode,
  DarkMode,
  CloudQueue as CloudIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const DRAWER_WIDTH = 280;

const Navigation = ({ user, onThemeToggle, currentTheme }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      text: 'Dashboard',
      icon: <DashboardIcon />,
      path: '/',
      description: 'Overview & Real-time Metrics'
    },
    {
      text: 'Cost Analysis',
      icon: <AssessmentIcon />,
      path: '/cost-analysis',
      description: 'Multi-cloud Cost Comparison'
    },
    {
      text: 'AI Insights',
      icon: <AIIcon />,
      path: '/ai-insights',
      description: 'Predictive Analytics & Optimization'
    },
    {
      text: 'Settings',
      icon: <SettingsIcon />,
      path: '/settings',
      description: 'Configuration & Preferences'
    },
  ];

  const isCurrentPath = (path) => {
    if (path === '/' && location.pathname === '/') return true;
    if (path !== '/' && location.pathname.startsWith(path)) return true;
    return false;
  };

  return (
    <Drawer
      variant="permanent"
      anchor="left"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
          backgroundColor: 'background.paper',
          borderRight: '1px solid',
          borderColor: 'divider',
        },
      }}
    >
      {/* Header Section */}
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
          <CloudIcon sx={{ fontSize: 40, color: 'primary.main', mr: 1 }} />
          <Typography variant="h5" fontWeight="700" color="primary.main">
            FISO
          </Typography>
        </Box>
        <Typography variant="body2" color="text.secondary">
          Enterprise Cloud Intelligence Platform
        </Typography>
      </Box>

      <Divider />

      {/* User Section */}
      {user && (
        <>
          <Box sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Avatar sx={{ width: 32, height: 32, mr: 1.5, bgcolor: 'primary.main' }}>
                {user.name?.charAt(0) || 'U'}
              </Avatar>
              <Box sx={{ flex: 1 }}>
                <Typography variant="subtitle2" fontWeight="600">
                  {user.name || 'Enterprise User'}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {user.email}
                </Typography>
              </Box>
            </Box>
            <Chip 
              label={user.mode === 'demo' ? 'Demo Mode' : 'Production'} 
              size="small" 
              color={user.mode === 'demo' ? 'warning' : 'success'}
              variant="outlined"
            />
          </Box>
          <Divider />
        </>
      )}

      {/* Navigation Menu */}
      <List sx={{ flex: 1, px: 1 }}>
        {menuItems.map((item) => (
          <ListItem key={item.path} disablePadding sx={{ mb: 0.5 }}>
            <ListItemButton
              onClick={() => navigate(item.path)}
              selected={isCurrentPath(item.path)}
              sx={{
                borderRadius: 2,
                mx: 1,
                '&.Mui-selected': {
                  backgroundColor: 'primary.main',
                  color: 'primary.contrastText',
                  '& .MuiListItemIcon-root': {
                    color: 'primary.contrastText',
                  },
                  '&:hover': {
                    backgroundColor: 'primary.dark',
                  },
                },
                '&:hover': {
                  backgroundColor: 'action.hover',
                },
              }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={
                  <Typography variant="subtitle2" fontWeight="500">
                    {item.text}
                  </Typography>
                }
                secondary={
                  <Typography variant="caption" color="text.secondary">
                    {item.description}
                  </Typography>
                }
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      <Divider />

      {/* Theme Toggle */}
      <Box sx={{ p: 2 }}>
        <FormControlLabel
          control={
            <Switch
              checked={currentTheme === 'dark'}
              onChange={onThemeToggle}
              color="primary"
            />
          }
          label={
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              {currentTheme === 'dark' ? (
                <DarkMode sx={{ mr: 1, fontSize: 20 }} />
              ) : (
                <LightMode sx={{ mr: 1, fontSize: 20 }} />
              )}
              <Typography variant="body2">
                {currentTheme === 'dark' ? 'Dark' : 'Light'} Mode
              </Typography>
            </Box>
          }
        />
      </Box>

      {/* Footer */}
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          Version 2.0.0 • Phase 3
        </Typography>
      </Box>
    </Drawer>
  );
};

export default Navigation;
