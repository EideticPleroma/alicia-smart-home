import React, { useEffect, useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

import { apiService } from '../services/api';

interface MetricsData {
  timestamp: string;
  services: Record<string, {
    status: string;
    response_time_ms: number;
  }>;
}

const MetricsChart: React.FC = () => {
  const [metricsData, setMetricsData] = useState<MetricsData[]>([]);
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h'>('24h');
  const [loading, setLoading] = useState(true);

  const fetchMetricsData = async () => {
    try {
      setLoading(true);
      const hours = timeRange === '1h' ? 1 : timeRange === '6h' ? 6 : 24;
      const data = await apiService.getMetricsOverview(hours);
      setMetricsData(data.data_points || []);
    } catch (error) {
      console.error('Error fetching metrics data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetricsData();
  }, [timeRange]);

  const handleTimeRangeChange = (
    event: React.MouseEvent<HTMLElement>,
    newTimeRange: '1h' | '6h' | '24h' | null,
  ) => {
    if (newTimeRange !== null) {
      setTimeRange(newTimeRange);
    }
  };

  // Transform data for the chart
  const chartData = metricsData.map((metric) => {
    const dataPoint: any = {
      timestamp: new Date(metric.timestamp).toLocaleTimeString(),
    };

    // Add response times for each service
    Object.entries(metric.services).forEach(([serviceName, serviceData]) => {
      dataPoint[serviceName] = serviceData.response_time_ms;
    });

    return dataPoint;
  });

  // Get service names for the chart
  const serviceNames = metricsData.length > 0 
    ? Object.keys(metricsData[0].services) 
    : [];

  const colors = [
    '#2196f3', // Blue
    '#4caf50', // Green
    '#ff9800', // Orange
    '#f44336', // Red
    '#9c27b0', // Purple
    '#00bcd4', // Cyan
  ];

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" component="h3">
            Response Time Trends
          </Typography>
          <ToggleButtonGroup
            value={timeRange}
            exclusive
            onChange={handleTimeRangeChange}
            size="small"
          >
            <ToggleButton value="1h">1H</ToggleButton>
            <ToggleButton value="6h">6H</ToggleButton>
            <ToggleButton value="24h">24H</ToggleButton>
          </ToggleButtonGroup>
        </Box>

        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" height={300}>
            <Typography>Loading metrics...</Typography>
          </Box>
        ) : chartData.length === 0 ? (
          <Box display="flex" justifyContent="center" alignItems="center" height={300}>
            <Typography color="text.secondary">No metrics data available</Typography>
          </Box>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="timestamp" 
                tick={{ fontSize: 12 }}
                interval="preserveStartEnd"
              />
              <YAxis 
                label={{ value: 'Response Time (ms)', angle: -90, position: 'insideLeft' }}
                tick={{ fontSize: 12 }}
              />
              <Tooltip 
                formatter={(value: any) => [`${value}ms`, 'Response Time']}
                labelFormatter={(label) => `Time: ${label}`}
              />
              <Legend />
              {serviceNames.map((serviceName, index) => (
                <Line
                  key={serviceName}
                  type="monotone"
                  dataKey={serviceName}
                  stroke={colors[index % colors.length]}
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  name={serviceName.replace('_', ' ').toUpperCase()}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
};

export default MetricsChart;

