import React from 'react';
import { Card, CardContent, Typography, Box, Avatar } from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';

const MetricsCard = ({ 
  title, 
  value, 
  change, 
  icon, 
  loading = false, 
  color = 'primary' 
}) => {
  const isPositive = change > 0;
  const changeColor = title.includes('Savings') 
    ? (isPositive ? 'success' : 'error')
    : (isPositive ? 'success' : 'error');

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Avatar sx={{ bgcolor: `${color}.main`, width: 48, height: 48 }}>
            {icon}
          </Avatar>
          {change !== 0 && (
            <Box sx={{ display: 'flex', alignItems: 'center', color: `${changeColor}.main` }}>
              {isPositive ? <TrendingUp /> : <TrendingDown />}
              <Typography variant="body2" sx={{ ml: 0.5 }}>
                {Math.abs(change).toFixed(1)}%
              </Typography>
            </Box>
          )}
        </Box>
        
        <Typography variant="h4" fontWeight="700" gutterBottom>
          {loading ? '...' : value}
        </Typography>
        
        <Typography variant="body2" color="text.secondary">
          {title}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default MetricsCard;
