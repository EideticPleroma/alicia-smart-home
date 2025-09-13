import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../utils/apiClient';

export interface EnvVariable {
  key: string;
  value: string;
  isSensitive: boolean;
}

export interface EnvConfigHook {
  envVars: Record<string, string>;
  loading: boolean;
  error: string | null;
  updateEnvVar: (key: string, value: string) => Promise<void>;
  updateMultipleEnvVars: (updates: Record<string, string>) => Promise<void>;
  createBackup: () => Promise<string>;
  restoreFromBackup: (backupPath: string) => Promise<void>;
  refreshEnvVars: () => Promise<void>;
}

export const useEnvConfig = (): EnvConfigHook => {
  const [envVars, setEnvVars] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchEnvVars = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.get('/api/env');
      
      if (response.data.success) {
        setEnvVars(response.data.data);
      } else {
        throw new Error(response.data.error || 'Failed to fetch environment variables');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch environment variables';
      setError(errorMessage);
      console.error('Error fetching environment variables:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const updateEnvVar = useCallback(async (key: string, value: string) => {
    try {
      setError(null);
      
      const response = await apiClient.put(`/api/env/${key}`, { value });
      
      if (response.data.success) {
        // Update local state with masked value
        setEnvVars(prev => ({
          ...prev,
          [key]: response.data.data.value
        }));
      } else {
        throw new Error(response.data.error || 'Failed to update environment variable');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update environment variable';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const updateMultipleEnvVars = useCallback(async (updates: Record<string, string>) => {
    try {
      setError(null);
      
      const response = await apiClient.put('/api/env', { updates });
      
      if (response.data.success) {
        // Update local state with masked values
        const updatedVars = { ...envVars };
        response.data.data.forEach((item: EnvVariable) => {
          updatedVars[item.key] = item.value;
        });
        setEnvVars(updatedVars);
      } else {
        throw new Error(response.data.error || 'Failed to update environment variables');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update environment variables';
      setError(errorMessage);
      throw err;
    }
  }, [envVars]);

  const createBackup = useCallback(async (): Promise<string> => {
    try {
      setError(null);
      
      const response = await apiClient.post('/api/env/backup');
      
      if (response.data.success) {
        return response.data.data.backupPath;
      } else {
        throw new Error(response.data.error || 'Failed to create backup');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create backup';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const restoreFromBackup = useCallback(async (backupPath: string) => {
    try {
      setError(null);
      
      const response = await apiClient.post('/api/env/restore', { backupPath });
      
      if (response.data.success) {
        // Refresh environment variables after restore
        await fetchEnvVars();
      } else {
        throw new Error(response.data.error || 'Failed to restore from backup');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to restore from backup';
      setError(errorMessage);
      throw err;
    }
  }, [fetchEnvVars]);

  const refreshEnvVars = useCallback(async () => {
    await fetchEnvVars();
  }, [fetchEnvVars]);

  useEffect(() => {
    fetchEnvVars();
  }, [fetchEnvVars]);

  return {
    envVars,
    loading,
    error,
    updateEnvVar,
    updateMultipleEnvVars,
    createBackup,
    restoreFromBackup,
    refreshEnvVars
  };
};
