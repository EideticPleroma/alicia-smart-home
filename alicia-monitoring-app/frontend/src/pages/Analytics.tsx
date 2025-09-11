import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';

import { apiService } from '../services/api';

interface MetricsOverview {
  period_hours: number;
  data_points: number;
  uptime_percentage: number;
  status_breakdown: {
    healthy: number;
    degraded: number;
    critical: number;
  };
  service_metrics: Record<string, {
    average_response_time_ms: number;
    total_checks: number;
    successful_checks: number;
  }>;
  last_updated: string;
}

const Analytics: React.FC = () => {
  const [timeRange, setTimeRange] = useState(24);
  const [metricsOverview, setMetricsOverview] = useState<MetricsOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetricsOverview = async () => {
    try {
      setLoading(true);
      const data = await apiService.getMetricsOverview(timeRange);
      setMetricsOverview(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch analytics data');
      console.error('Error fetching metrics overview:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetricsOverview();
  }, [timeRange]);

  const handleTimeRangeChange = (event: any) => {
    setTimeRange(event.target.value);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!metricsOverview) {
    return (
      <Alert severity="info">
        No analytics data available for the selected time range.
      </Alert>
    );
  }

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <AnalyticsIcon />
        <Typography variant="h4" component="h1">
          Analytics & Performance
        </Typography>
      </Box>

      {/* Time Range Selector */}
      <Box display="flex" justifyContent="flex-end" mb={3}>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Time Range</InputLabel>
          <Select
            value={timeRange}
            onChange={handleTimeRangeChange}
            label="Time Range"
          >
            <MenuItem value={1}>Last Hour</MenuItem>
            <MenuItem value={6}>Last 6 Hours</MenuItem>
            <MenuItem value={24}>Last 24 Hours</MenuItem>
            <MenuItem value={168}>Last Week</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Grid container spacing={3}>
        {/* Overview Cards */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <CheckCircleIcon color="success" />
                <Typography variant="h6">
                  {metricsOverview.uptime_percentage.toFixed(1)}%
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Uptime
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <TrendingUpIcon color="primary" />
                <Typography variant="h6">
                  {metricsOverview.data_points}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Data Points
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <CheckCircleIcon color="success" />
                <Typography variant="h6">
                  {metricsOverview.status_breakdown.healthy}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Healthy Checks
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <WarningIcon color="warning" />
                <Typography variant="h6">
                  {metricsOverview.status_breakdown.degraded + metricsOverview.status_breakdown.critical}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Issues
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Service Performance Table */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Service Performance
              </Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Service</TableCell>
                      <TableCell align="right">Avg Response Time (ms)</TableCell>
                      <TableCell align="right">Total Checks</TableCell>
                      <TableCell align="right">Success Rate</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(metricsOverview.service_metrics).map(([serviceName, metrics]) => {
                      const successRate = (metrics.successful_checks / metrics.total_checks) * 100;
                      return (
                        <TableRow key={serviceName}>
                          <TableCell component="th" scope="row">
                            {serviceName.replace(/_/g, ' ').toUpperCase()}
                          </TableCell>
                          <TableCell align="right">
                            {metrics.average_response_time_ms.toFixed(1)}
                          </TableCell>
                          <TableCell align="right">
                            {metrics.total_checks}
                          </TableCell>
                          <TableCell align="right">
                            <Box display="flex" alignItems="center" justifyContent="flex-end" gap={1}>
                              {successRate.toFixed(1)}%
                              <Box
                                width={20}
                                height={4}
                                bgcolor={
                                  successRate >= 95 ? 'success.main' :
                                  successRate >= 80 ? 'warning.main' : 'error.main'
                                }
                                borderRadius={2}
                              />
                            </Box>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Status Breakdown */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Status Breakdown
              </Typography>
              <Box display="flex" flexDirection="column" gap={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box display="flex" alignItems="center" gap={1}>
                    <CheckCircleIcon color="success" />
                    <Typography>Healthy</Typography>
                  </Box>
                  <Typography variant="h6">
                    {metricsOverview.status_breakdown.healthy}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box display="flex" alignItems="center" gap={1}>
                    <WarningIcon color="warning" />
                    <Typography>Degraded</Typography>
                  </Box>
                  <Typography variant="h6">
                    {metricsOverview.status_breakdown.degraded}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box display="flex" alignItems="center" gap={1}>
                    <WarningIcon color="error" />
                    <Typography>Critical</Typography>
                  </Box>
                  <Typography variant="h6">
                    {metricsOverview.status_breakdown.critical}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Summary */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Summary
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Over the last {metricsOverview.period_hours} hours, the system has been monitored 
                with {metricsOverview.data_points} data points, achieving {metricsOverview.uptime_percentage.toFixed(1)}% uptime.
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Last updated: {new Date(metricsOverview.last_updated).toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Analytics;
