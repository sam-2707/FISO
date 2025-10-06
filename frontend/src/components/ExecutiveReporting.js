import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider
} from '@mui/material';
import {
  Assessment,
  PictureAsPdf,
  Schedule,
  Download,
  Refresh,
  Business,
  TrendingUp,
  CalendarToday
} from '@mui/icons-material';
import axios from 'axios';

const ExecutiveReporting = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [generateDialogOpen, setGenerateDialogOpen] = useState(false);
  const [selectedReportType, setSelectedReportType] = useState('executive');

  const API_BASE = 'http://localhost:5001';

  useEffect(() => {
    loadReportsList();
  }, []);

  const loadReportsList = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API_BASE}/api/reports/list`);
      setReports(response.data.reports || []);
    } catch (err) {
      setError('Failed to load reports list');
      console.error('Error loading reports:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async (reportType) => {
    try {
      setGenerating(true);
      setError(null);

      let endpoint;
      if (reportType === 'executive') {
        endpoint = `${API_BASE}/api/reports/executive-summary`;
      } else {
        endpoint = `${API_BASE}/api/reports/scheduled/${reportType}`;
      }

      const response = await axios.post(endpoint, {
        include_charts: true,
        include_recommendations: true,
        format: 'pdf'
      });

      if (response.data.status === 'success') {
        // Refresh the reports list
        await loadReportsList();
        setGenerateDialogOpen(false);
        
        // Show success message
        setError(null);
      } else {
        setError('Failed to generate report');
      }
    } catch (err) {
      setError(`Failed to generate ${reportType} report`);
      console.error('Error generating report:', err);
    } finally {
      setGenerating(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes || bytes === 0) return '0 Bytes';
    if (typeof bytes !== 'number') return 'Unknown';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDateTime = (isoString) => {
    if (!isoString) return 'Unknown';
    try {
      const date = new Date(isoString);
      return isNaN(date.getTime()) ? 'Invalid Date' : date.toLocaleString();
    } catch (error) {
      return 'Invalid Date';
    }
  };

  const getReportTypeIcon = (type) => {
    switch (type) {
      case 'executive':
        return <Business color="primary" />;
      case 'daily':
        return <CalendarToday color="info" />;
      case 'weekly':
        return <Schedule color="success" />;
      case 'monthly':
        return <TrendingUp color="warning" />;
      default:
        return <Assessment color="action" />;
    }
  };

  const getReportTypeColor = (type) => {
    switch (type) {
      case 'executive':
        return 'primary';
      case 'daily':
        return 'info';
      case 'weekly':
        return 'success';
      case 'monthly':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ color: '#1976d2', fontWeight: 'bold' }}>
          📊 Executive Reporting System
        </Typography>
        <Typography variant="h6" color="textSecondary" gutterBottom>
          Generate comprehensive reports with AI insights and cost analysis
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <Assessment sx={{ mr: 1 }} />
                Quick Actions
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<Business />}
                  onClick={() => {
                    setSelectedReportType('executive');
                    setGenerateDialogOpen(true);
                  }}
                  disabled={generating}
                  fullWidth
                >
                  Generate Executive Summary
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<CalendarToday />}
                  onClick={() => {
                    setSelectedReportType('daily');
                    setGenerateDialogOpen(true);
                  }}
                  disabled={generating}
                  fullWidth
                >
                  Daily Report
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<Schedule />}
                  onClick={() => {
                    setSelectedReportType('weekly');
                    setGenerateDialogOpen(true);
                  }}
                  disabled={generating}
                  fullWidth
                >
                  Weekly Report
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<TrendingUp />}
                  onClick={() => {
                    setSelectedReportType('monthly');
                    setGenerateDialogOpen(true);
                  }}
                  disabled={generating}
                  fullWidth
                >
                  Monthly Report
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Reports List */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>
                  <PictureAsPdf sx={{ mr: 1 }} />
                  Generated Reports ({reports.length})
                </Typography>
                <Button
                  startIcon={<Refresh />}
                  onClick={loadReportsList}
                  disabled={loading}
                  size="small"
                >
                  Refresh
                </Button>
              </Box>

              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : reports.length === 0 ? (
                <Box sx={{ textAlign: 'center', p: 3 }}>
                  <Typography color="textSecondary">
                    No reports generated yet. Click "Generate Executive Summary" to create your first report.
                  </Typography>
                </Box>
              ) : (
                <List>
                  {reports.map((report, index) => (
                    <React.Fragment key={report.id || report.filename || index}>
                      <ListItem
                        sx={{
                          border: '1px solid #e0e0e0',
                          borderRadius: 1,
                          mb: 1,
                          bgcolor: '#fafafa'
                        }}
                      >
                        <ListItemIcon>
                          {getReportTypeIcon(report.type)}
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography variant="subtitle2">
                                {report.filename ? report.filename.replace(/^FISO_|_\d{8}_\d{6}\.pdf$/g, '') : (report.name || 'Unnamed Report')}
                              </Typography>
                              <Chip
                                label={report.type || 'unknown'}
                                size="small"
                                color={getReportTypeColor(report.type)}
                              />
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="body2" color="textSecondary">
                                Created: {report.created_at ? formatDateTime(report.created_at) : 'Unknown'}
                              </Typography>
                              <Typography variant="body2" color="textSecondary">
                                Size: {report.size ? formatFileSize(report.size) : 'Unknown'}
                              </Typography>
                            </Box>
                          }
                        />
                        <Button
                          startIcon={<Download />}
                          size="small"
                          disabled={!report.filename}
                          onClick={() => {
                            if (report.filename) {
                              // In a real implementation, this would download the file
                              window.open(`${API_BASE}/api/reports/download/${report.filename}`, '_blank');
                            }
                          }}
                        >
                          Download
                        </Button>
                      </ListItem>
                      {index < reports.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Report Statistics */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📈 Reporting Statistics
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6} sm={3}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: '#e3f2fd', borderRadius: 1 }}>
                    <Typography variant="h4" color="primary">{reports.length}</Typography>
                    <Typography variant="body2" color="textSecondary">Total Reports</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: '#e8f5e8', borderRadius: 1 }}>
                    <Typography variant="h4" color="success.main">
                      {reports.filter(r => r.type === 'executive').length}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">Executive Reports</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: '#fff3e0', borderRadius: 1 }}>
                    <Typography variant="h4" color="warning.main">
                      {formatFileSize(reports.reduce((sum, r) => sum + r.size, 0))}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">Total Size</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: '#fce4ec', borderRadius: 1 }}>
                    <Typography variant="h4" color="secondary.main">
                      {reports.length > 0 ? formatDateTime(reports[0].created_at).split(',')[0] : 'N/A'}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">Latest Report</Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Generate Report Dialog */}
      <Dialog open={generateDialogOpen} onClose={() => setGenerateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Generate Report</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Report Type</InputLabel>
              <Select
                value={selectedReportType}
                label="Report Type"
                onChange={(e) => setSelectedReportType(e.target.value)}
              >
                <MenuItem value="executive">Executive Summary</MenuItem>
                <MenuItem value="daily">Daily Report</MenuItem>
                <MenuItem value="weekly">Weekly Report</MenuItem>
                <MenuItem value="monthly">Monthly Report</MenuItem>
              </Select>
            </FormControl>
            
            <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
              {selectedReportType === 'executive' && 'Comprehensive executive summary with AI insights, cost analysis, and strategic recommendations.'}
              {selectedReportType === 'daily' && 'Daily summary of cloud costs, alerts, and optimization actions.'}
              {selectedReportType === 'weekly' && 'Weekly aggregated analysis with trend identification.'}
              {selectedReportType === 'monthly' && 'Comprehensive monthly analysis with strategic planning insights.'}
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setGenerateDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={() => generateReport(selectedReportType)}
            variant="contained"
            disabled={generating}
            startIcon={generating ? <CircularProgress size={20} /> : <Assessment />}
          >
            {generating ? 'Generating...' : 'Generate Report'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ExecutiveReporting;