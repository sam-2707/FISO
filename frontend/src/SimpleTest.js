import React from 'react';

function SimpleTest() {
  return (
    <div style={{ 
      padding: '2rem', 
      backgroundColor: '#f0f0f0', 
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'column'
    }}>
      <h1 style={{ color: '#0066cc', marginBottom: '1rem' }}>
        🚀 FISO React App is Working!
      </h1>
      <p style={{ fontSize: '1.2rem', color: '#333' }}>
        Modern React frontend successfully loaded
      </p>
      <div style={{ 
        marginTop: '2rem', 
        padding: '1rem', 
        backgroundColor: 'white', 
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        <p><strong>Status:</strong> ✅ React Development Server Running</p>
        <p><strong>Port:</strong> 3000</p>
        <p><strong>Backend API:</strong> localhost:5000</p>
        <p><strong>Environment:</strong> Development</p>
      </div>
    </div>
  );
}

export default SimpleTest;
