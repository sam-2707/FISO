import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard/Dashboard';
import CloudDashboard from './components/CloudDashboard';
import IndustryOperationsDashboard from './components/IndustryOperationsDashboard';
import Navigation from './components/Navigation';
import ErrorBoundary from './components/ErrorBoundary';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#0066cc',
      dark: '#0052a3',
    },
    secondary: {
      main: '#28a745',
    },
    background: {
      default: '#f8f9fa',
      paper: '#ffffff',
    },
    text: {
      primary: '#2c3e50',
      secondary: '#6c757d',
    },
  },
  typography: {
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif',
    h4: {
      fontWeight: 700,
    },
    h6: {
      fontWeight: 600,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
  },
});

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <div className="App">
            <Navigation />
            <Routes>
              <Route path="/" element={<CloudDashboard />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/operations" element={<IndustryOperationsDashboard />} />
              <Route path="/operational" element={<CloudDashboard />} />
            </Routes>
          </div>
        </Router>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
