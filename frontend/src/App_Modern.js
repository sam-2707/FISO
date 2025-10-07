import React from 'react';
import CssBaseline from '@mui/material/CssBaseline';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import { EnhancedThemeProvider } from './contexts/ThemeContext';
import ModernNavigation from './components/ModernNavigation';
import ModernDashboard from './components/ModernDashboard';
import ModernBackground from './components/ModernBackground';
import ModernFloatingControls from './components/ModernFloatingControls';
import Dashboard from './components/Dashboard/Dashboard';
import CloudDashboard from './components/CloudDashboard';
import IndustryOperationsDashboard from './components/IndustryOperationsDashboard';
import ErrorBoundary from './components/ErrorBoundary';
import NotificationProvider from './components/NotificationProvider';
import './styles/atharman-theme.css';
import './styles/modern-ui.css';

function App() {
  return (
    <ErrorBoundary>
      <NotificationProvider>
        <EnhancedThemeProvider>
          <CssBaseline />
          <Router>
            <Box sx={{ display: 'flex', minHeight: '100vh' }}>
              {/* Modern Animated Background */}
              <ModernBackground />
              
              {/* Navigation */}
              <ModernNavigation />
              
              {/* Main Content Area */}
              <Box
                component="main"
                sx={{
                  flexGrow: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  position: 'relative',
                  overflow: 'hidden',
                  marginTop: '64px', // Account for app bar height
                }}
              >
                {/* Routes */}
                <Routes>
                  <Route path="/" element={<ModernDashboard />} />
                  <Route path="/dashboard" element={<ModernDashboard />} />
                  <Route path="/cloud" element={<CloudDashboard />} />
                  <Route path="/ai-insights" element={<Dashboard />} />
                  <Route path="/performance" element={<Dashboard />} />
                  <Route path="/security" element={<Dashboard />} />
                  <Route path="/analytics" element={<Dashboard />} />
                  <Route path="/operations" element={<IndustryOperationsDashboard />} />
                  <Route path="/settings" element={<Dashboard />} />
                </Routes>
              </Box>
              
              {/* Floating Controls */}
              <ModernFloatingControls />
            </Box>
          </Router>
        </EnhancedThemeProvider>
      </NotificationProvider>
    </ErrorBoundary>
  );
}

export default App;