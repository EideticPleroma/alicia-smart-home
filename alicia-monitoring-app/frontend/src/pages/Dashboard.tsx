import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

import { useWebSocket } from '../hooks/useWebSocket';
import { apiService } from '../services/api';
import HealthStatusCard from '../components/HealthStatusCard';
import MetricsChart from '../components/MetricsChart';
import RecentActivity from '../components/RecentActivity';

interface ServiceStatus {
  status: 'healthy' | 'unhealthy' | 'timeout' | 'error';
  response_time_ms: number;
  last_check: string;
  error?: string;
}

interface HealthData {
  timestamp: string;
  services: Record<string, ServiceStatus>;
  overall_status: 'healthy' | 'degraded' | 'critical';
  summary: {
    total_services: number;
    healthy_services: number;
    unhealthy_services: number;
    error_services: number;
  };
}

const Dashboard: React.FC = () => {
  const { isConnected, lastMessage } = useWebSocket();
  const [healthData, setHealthData] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHealthData = async () => {
    try {
      setLoading(true);
      const data = await apiService.getHealthStatus();
      setHealthData(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch health data');
      console.error('Error fetching health data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealthData();
    
    // Set up interval to fetch data every 30 seconds
    const interval = setInterval(fetchHealthData, 30000);
    
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (lastMessage && lastMessage.type === 'health_update') {
      setHealthData(lastMessage.data);
    }
  }, [lastMessage]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'success';
      case 'unhealthy':
      case 'timeout':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircleIcon />;
      case 'unhealthy':
      case 'timeout':
        return <WarningIcon />;
      case 'error':
        return <ErrorIcon />;
      default:
        return <ErrorIcon />;
    }
  };

  if (loading && !healthData) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" action={
        <RefreshIcon 
          onClick={fetchHealthData} 
          style={{ cursor: 'pointer' }}
        />
      }>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          System Dashboard
        </Typography>
        <Box display="flex" alignItems="center" gap={2}>
          <Chip
            icon={isConnected ? <CheckCircleIcon /> : <ErrorIcon />}
            label={isConnected ? 'Connected' : 'Disconnected'}
            color={isConnected ? 'success' : 'error'}
            variant="outlined"
          />
          <RefreshIcon 
            onClick={fetchHealthData} 
            style={{ cursor: 'pointer' }}
          />
        </Box>
      </Box>

      {healthData && (
        <>
          {/* Overall Status */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Overall System Status
              </Typography>
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <Chip
                  icon={getStatusIcon(healthData.overall_status)}
                  label={healthData.overall_status.toUpperCase()}
                  color={getStatusColor(healthData.overall_status) as any}
                  size="large"
                />
                <Typography variant="body2" color="text.secondary">
                  Last updated: {new Date(healthData.timestamp).toLocaleString()}
                </Typography>
              </Box>
              <Box display="flex" gap={4}>
                <Typography variant="body2">
                  Total Services: {healthData.summary.total_services}
                </Typography>
                <Typography variant="body2" color="success.main">
                  Healthy: {healthData.summary.healthy_services}
                </Typography>
                <Typography variant="body2" color="warning.main">
                  Unhealthy: {healthData.summary.unhealthy_services}
                </Typography>
                <Typography variant="body2" color="error.main">
                  Errors: {healthData.summary.error_services}
                </Typography>
              </Box>
            </CardContent>
          </Card>

          {/* Service Status Cards */}
          <Grid container spacing={3} mb={3}>
            {Object.entries(healthData.services).map(([serviceName, serviceData]) => (
              <Grid item xs={12} sm={6} md={4} key={serviceName}>
                <HealthStatusCard
                  serviceName={serviceName}
                  status={serviceData.status}
                  responseTime={serviceData.response_time_ms}
                  lastCheck={serviceData.last_check}
                  error={serviceData.error}
                />
              </Grid>
            ))}
          </Grid>

          {/* Metrics and Activity */}
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <MetricsChart />
            </Grid>
            <Grid item xs={12} md={4}>
              <RecentActivity />
            </Grid>
          </Grid>
        </>
      )}
    </Box>
  );
};

export default Dashboard;

