import { useState, useEffect } from 'react';
import { useSocket } from './useSocket';
import { ServiceConfig } from '../types';
import { api } from '../services/api';
import { toast } from 'react-hot-toast';
import { handleApiError } from '../utils/apiErrorHandler';

export const useConfig = () => {
  const [configs, setConfigs] = useState<Record<string, ServiceConfig>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { on, off } = useSocket();

  useEffect(() => {
    loadConfigs();
  }, []);

  useEffect(() => {
    const handleConfigUpdate = (data: Record<string, ServiceConfig>) => {
      setConfigs(data);
    };

    on('config:update', handleConfigUpdate);

    return () => {
      off('config:update', handleConfigUpdate);
    };
  }, [on, off]);

  const loadConfigs = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/config');
      setConfigs(response.data);
    } catch (err) {
      const { userMessage } = handleApiError(err, 'loading configs');
      setError(userMessage);
    } finally {
      setLoading(false);
    }
  };

  const updateConfig = async (serviceName: string, config: ServiceConfig) => {
    try {
      const response = await api.patch(`/config/${serviceName}`, config);
      setConfigs(prev => ({
        ...prev,
        [serviceName]: response.data
      }));
      toast.success(`Configuration updated for ${serviceName}`);
      return response.data;
    } catch (err) {
      const { userMessage, parsedError } = handleApiError(err, `updating config for ${serviceName}`);

      // Show specific error message based on error type
      toast.error(parsedError.code === 'VALIDATION_ERROR' ? 'Invalid configuration data provided' : userMessage);
      setError(userMessage);
      throw err;
    }
  };

  const reloadConfigs = async () => {
    try {
      await api.post('/config/reload');
      await loadConfigs();
      toast.success('All configurations reloaded successfully');
    } catch (err) {
      const { userMessage } = handleApiError(err, 'reloading configs');
      setError(userMessage);
      toast.error('Failed to reload configurations. Please try again.');
      throw err;
    }
  };

  return {
    configs,
    loading,
    error,
    updateConfig,
    reloadConfigs,
  };
};
