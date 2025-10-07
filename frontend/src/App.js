import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeContextProvider } from './contexts/ThemeContext';
import ModernDashboard from './components/ModernDashboard';
import Dashboard from './components/Dashboard/Dashboard';
import CloudDashboard from './components/CloudDashboard';
import IndustryOperationsDashboard from './components/IndustryOperationsDashboard';
import ErrorBoundary from './components/ErrorBoundary';
import NotificationProvider from './components/NotificationProvider';
import './styles/atharman-theme.css';

function App() {
  return (
    <ErrorBoundary>
      <NotificationProvider>
        <ThemeContextProvider>
          <Router>
            <div className="App">
              <Routes>
                <Route path="/" element={<ModernDashboard />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/modern" element={<ModernDashboard />} />
                <Route path="/cloud" element={<CloudDashboard />} />
                <Route path="/operations" element={<IndustryOperationsDashboard />} />
                <Route path="/operational" element={<CloudDashboard />} />
              </Routes>
            </div>
          </Router>
        </ThemeContextProvider>
      </NotificationProvider>
    </ErrorBoundary>
  );
}

export default App;
