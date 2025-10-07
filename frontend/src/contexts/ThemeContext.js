import React, { createContext, useContext, useState, useEffect } from 'react';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';

const ThemeContext = createContext();

export const useThemeMode = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useThemeMode must be used within a ThemeContextProvider');
  }
  return context;
};

const createCustomTheme = (mode) => {
  const isDark = mode === 'dark';
  
  return createTheme({
    palette: {
      mode,
      primary: {
        main: isDark ? '#64b5f6' : '#1976d2',
        light: isDark ? '#90caf9' : '#42a5f5',
        dark: isDark ? '#1976d2' : '#1565c0',
        contrastText: '#ffffff',
      },
      secondary: {
        main: isDark ? '#f48fb1' : '#dc004e',
        light: isDark ? '#f8bbd9' : '#e91e63',
        dark: isDark ? '#c2185b' : '#c51162',
        contrastText: '#ffffff',
      },
      success: {
        main: isDark ? '#81c784' : '#4caf50',
        light: isDark ? '#a5d6a7' : '#66bb6a',
        dark: isDark ? '#388e3c' : '#2e7d32',
      },
      warning: {
        main: isDark ? '#ffb74d' : '#ff9800',
        light: isDark ? '#ffcc02' : '#ffb74d',
        dark: isDark ? '#f57c00' : '#e65100',
      },
      error: {
        main: isDark ? '#ef5350' : '#f44336',
        light: isDark ? '#e57373' : '#ef5350',
        dark: isDark ? '#c62828' : '#d32f2f',
      },
      info: {
        main: isDark ? '#29b6f6' : '#2196f3',
        light: isDark ? '#4fc3f7' : '#42a5f5',
        dark: isDark ? '#0277bd' : '#1976d2',
      },
      background: {
        default: isDark ? '#0a0a0a' : '#f8fafc',
        paper: isDark ? '#1a1a1a' : '#ffffff',
      },
      text: {
        primary: isDark ? '#ffffff' : '#2d3748',
        secondary: isDark ? '#b0b0b0' : '#718096',
      },
      divider: isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)',
    },
    typography: {
      fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
      h1: {
        fontWeight: 700,
        fontSize: '2.5rem',
        lineHeight: 1.2,
      },
      h2: {
        fontWeight: 700,
        fontSize: '2rem',
        lineHeight: 1.3,
      },
      h3: {
        fontWeight: 600,
        fontSize: '1.75rem',
        lineHeight: 1.3,
      },
      h4: {
        fontWeight: 600,
        fontSize: '1.5rem',
        lineHeight: 1.4,
      },
      h5: {
        fontWeight: 600,
        fontSize: '1.25rem',
        lineHeight: 1.4,
      },
      h6: {
        fontWeight: 600,
        fontSize: '1.125rem',
        lineHeight: 1.4,
      },
      body1: {
        fontSize: '1rem',
        lineHeight: 1.6,
      },
      body2: {
        fontSize: '0.875rem',
        lineHeight: 1.6,
      },
      button: {
        fontWeight: 600,
        textTransform: 'none',
      },
    },
    shape: {
      borderRadius: 12,
    },
    components: {
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 16,
            boxShadow: isDark 
              ? '0 4px 20px rgba(0, 0, 0, 0.3)'
              : '0 4px 20px rgba(0, 0, 0, 0.1)',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: 'none',
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: 10,
            padding: '8px 24px',
            boxShadow: 'none',
            '&:hover': {
              boxShadow: isDark 
                ? '0 4px 12px rgba(100, 181, 246, 0.3)'
                : '0 4px 12px rgba(25, 118, 210, 0.2)',
            },
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            fontWeight: 500,
          },
        },
      },
      MuiTabs: {
        styleOverrides: {
          root: {
            '& .MuiTabs-indicator': {
              height: 3,
              borderRadius: '3px 3px 0 0',
            },
          },
        },
      },
      MuiLinearProgress: {
        styleOverrides: {
          root: {
            borderRadius: 4,
            backgroundColor: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
          },
        },
      },
      MuiTooltip: {
        styleOverrides: {
          tooltip: {
            backgroundColor: isDark ? 'rgba(255, 255, 255, 0.9)' : 'rgba(0, 0, 0, 0.8)',
            color: isDark ? '#000' : '#fff',
            backdropFilter: 'blur(10px)',
            borderRadius: 8,
          },
        },
      },
    },
  });
};

export function ThemeContextProvider({ children }) {
  const [mode, setMode] = useState(() => {
    // Check localStorage for saved theme preference
    const savedMode = localStorage.getItem('fiso-theme-mode');
    if (savedMode) {
      return savedMode;
    }
    // Check system preference
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

  const theme = createCustomTheme(mode);

  const toggleMode = () => {
    const newMode = mode === 'light' ? 'dark' : 'light';
    setMode(newMode);
    localStorage.setItem('fiso-theme-mode', newMode);
  };

  const value = {
    mode,
    toggleMode,
    theme,
  };

  // Listen for system theme changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e) => {
      // Only auto-switch if no manual preference is stored
      if (!localStorage.getItem('fiso-theme-mode')) {
        setMode(e.matches ? 'dark' : 'light');
      }
    };

    mediaQuery.addListener(handleChange);
    return () => mediaQuery.removeListener(handleChange);
  }, []);

  return (
    <ThemeContext.Provider value={value}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ThemeContext.Provider>
  );
}
