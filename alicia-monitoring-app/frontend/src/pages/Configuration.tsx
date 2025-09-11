import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Settings as SettingsIcon } from '@mui/icons-material';

import { apiService, ServiceConfig } from '../services/api';
import ServiceConfigCard from '../components/ServiceConfigCard';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`config-tabpanel-${index}`}
      aria-labelledby={`config-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const Configuration: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [configs, setConfigs] = useState<Record<string, ServiceConfig>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [environment, setEnvironment] = useState('production');

  const fetchConfigs = async () => {
    try {
      setLoading(true);
      const data = await apiService.getAllConfigs(environment);
      setConfigs(data.configs);
      setError(null);
    } catch (err) {
      setError('Failed to fetch configuration data');
      console.error('Error fetching configs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConfigs();
  }, [environment]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleConfigUpdate = async (service: string, config: Record<string, any>) => {
    try {
      await apiService.updateServiceConfig(service, config, environment);
      await fetchConfigs(); // Refresh configs
    } catch (err) {
      console.error('Error updating config:', err);
    }
  };

  const handleConfigTest = async (service: string) => {
    try {
      const result = await apiService.testServiceConfig(service, environment);
      console.log('Test result:', result);
      // In a real app, you'd show this result to the user
    } catch (err) {
      console.error('Error testing config:', err);
    }
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

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <SettingsIcon />
        <Typography variant="h4" component="h1">
          Configuration Management
        </Typography>
      </Box>

      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="Production" />
            <Tab label="Development" />
            <Tab label="Staging" />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          <Typography variant="h6" gutterBottom>
            Production Environment
          </Typography>
          <Grid container spacing={3}>
            {Object.entries(configs).map(([serviceName, config]) => (
              <Grid item xs={12} md={6} key={serviceName}>
                <ServiceConfigCard
                  serviceName={serviceName}
                  config={config.config}
                  onUpdate={(newConfig) => handleConfigUpdate(serviceName, newConfig)}
                  onTest={() => handleConfigTest(serviceName)}
                />
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Typography variant="h6" gutterBottom>
            Development Environment
          </Typography>
          <Alert severity="info">
            Development environment configuration will be loaded when you switch to this tab.
          </Alert>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            Staging Environment
          </Typography>
          <Alert severity="info">
            Staging environment configuration will be loaded when you switch to this tab.
          </Alert>
        </TabPanel>
      </Card>
    </Box>
  );
};

export default Configuration;

