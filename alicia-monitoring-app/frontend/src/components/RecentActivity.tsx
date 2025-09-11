import React, { useEffect, useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Divider,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

import { apiService } from '../services/api';

interface ActivityItem {
  timestamp: string;
  type: 'health_update' | 'test_result' | 'config_update' | 'error';
  message: string;
  severity: 'low' | 'medium' | 'high';
  service?: string;
}

const RecentActivity: React.FC = () => {
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchActivities = async () => {
    try {
      setLoading(true);
      // For now, we'll simulate some activity data
      // In a real implementation, this would come from the API
      const mockActivities: ActivityItem[] = [
        {
          timestamp: new Date().toISOString(),
          type: 'health_update',
          message: 'All services healthy',
          severity: 'low',
        },
        {
          timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
          type: 'test_result',
          message: 'End-to-end test completed successfully',
          severity: 'low',
        },
        {
          timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
          type: 'config_update',
          message: 'Whisper configuration updated',
          severity: 'medium',
          service: 'whisper',
        },
        {
          timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
          type: 'error',
          message: 'MQTT connection timeout',
          severity: 'high',
          service: 'mqtt',
        },
        {
          timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
          type: 'health_update',
          message: 'System status restored',
          severity: 'low',
        },
      ];
      setActivities(mockActivities);
    } catch (error) {
      console.error('Error fetching activities:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActivities();
    
    // Refresh activities every 30 seconds
    const interval = setInterval(fetchActivities, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'health_update':
        return <CheckCircleIcon />;
      case 'test_result':
        return <InfoIcon />;
      case 'config_update':
        return <RefreshIcon />;
      case 'error':
        return <ErrorIcon />;
      default:
        return <InfoIcon />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low':
        return 'success';
      case 'medium':
        return 'warning';
      case 'high':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" component="h3">
            Recent Activity
          </Typography>
          <RefreshIcon 
            onClick={fetchActivities} 
            style={{ cursor: 'pointer' }}
          />
        </Box>

        {loading ? (
          <Typography>Loading activities...</Typography>
        ) : activities.length === 0 ? (
          <Typography color="text.secondary">No recent activity</Typography>
        ) : (
          <List dense>
            {activities.map((activity, index) => (
              <React.Fragment key={index}>
                <ListItem alignItems="flex-start">
                  <ListItemIcon sx={{ minWidth: 40 }}>
                    {getActivityIcon(activity.type)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1} mb={0.5}>
                        <Typography variant="body2">
                          {activity.message}
                        </Typography>
                        <Chip
                          label={activity.severity.toUpperCase()}
                          color={getSeverityColor(activity.severity) as any}
                          size="small"
                          variant="outlined"
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          {formatTimestamp(activity.timestamp)}
                        </Typography>
                        {activity.service && (
                          <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                            • {activity.service}
                          </Typography>
                        )}
                      </Box>
                    }
                  />
                </ListItem>
                {index < activities.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  );
};

export default RecentActivity;

