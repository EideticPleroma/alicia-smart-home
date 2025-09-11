import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  AccessTime as AccessTimeIcon,
} from '@mui/icons-material';

interface HealthStatusCardProps {
  serviceName: string;
  status: 'healthy' | 'unhealthy' | 'timeout' | 'error';
  responseTime: number;
  lastCheck: string;
  error?: string;
}

const HealthStatusCard: React.FC<HealthStatusCardProps> = ({
  serviceName,
  status,
  responseTime,
  lastCheck,
  error,
}) => {
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

  const getResponseTimeColor = (time: number) => {
    if (time < 1000) return 'success';
    if (time < 3000) return 'warning';
    return 'error';
  };

  const formatServiceName = (name: string) => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" component="h3">
            {formatServiceName(serviceName)}
          </Typography>
          <Chip
            icon={getStatusIcon(status)}
            label={status.toUpperCase()}
            color={getStatusColor(status) as any}
            size="small"
          />
        </Box>

        <Box mb={2}>
          <Box display="flex" alignItems="center" gap={1} mb={1}>
            <AccessTimeIcon fontSize="small" color="action" />
            <Typography variant="body2" color="text.secondary">
              Response Time
            </Typography>
          </Box>
          <Box display="flex" alignItems="center" gap={1}>
            <Typography
              variant="h6"
              color={`${getResponseTimeColor(responseTime)}.main`}
            >
              {responseTime.toFixed(0)}ms
            </Typography>
            <LinearProgress
              variant="determinate"
              value={Math.min((responseTime / 5000) * 100, 100)}
              color={getResponseTimeColor(responseTime) as any}
              sx={{ flexGrow: 1, height: 6, borderRadius: 3 }}
            />
          </Box>
        </Box>

        <Box mb={2}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Last Check
          </Typography>
          <Typography variant="body2">
            {new Date(lastCheck).toLocaleString()}
          </Typography>
        </Box>

        {error && (
          <Box>
            <Typography variant="body2" color="error" gutterBottom>
              Error Details
            </Typography>
            <Typography variant="caption" color="error" sx={{ wordBreak: 'break-word' }}>
              {error}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default HealthStatusCard;

