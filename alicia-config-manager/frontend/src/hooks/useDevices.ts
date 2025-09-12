import { useState, useEffect } from 'react';
import { useSocket } from './useSocket';
import { Device } from '../types';
import { api } from '../services/api';
import { toast } from 'react-hot-toast';
import { handleApiError } from '../utils/apiErrorHandler';

export const useDevices = () => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { on, off } = useSocket();

  useEffect(() => {
    loadDevices();
  }, []);

  useEffect(() => {
    const handleDevicesUpdate = (data: Device[]) => {
      setDevices(data);
    };

    on('devices:update', handleDevicesUpdate);

    return () => {
      off('devices:update', handleDevicesUpdate);
    };
  }, [on, off]);

  const loadDevices = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/devices');
      setDevices(response.data);
    } catch (err) {
      const { userMessage } = handleApiError(err, 'loading devices');
      setError(userMessage);
    } finally {
      setLoading(false);
    }
  };

  const addDevice = async (device: Device) => {
    try {
      const response = await api.post('/devices', device);
      setDevices(prev => [...prev, response.data]);
      toast.success(`Device ${device.device_name} added successfully`);
      return response.data;
    } catch (err) {
      const { userMessage, parsedError } = handleApiError(err, `adding device ${device.device_name}`);

      // Show specific error message for conflicts
      const finalMessage = parsedError.code === 'DEVICE_EXISTS_ERROR'
        ? `A device with this name or configuration already exists`
        : userMessage;

      toast.error(finalMessage);
      setError(finalMessage);
      throw err;
    }
  };

  const updateDevice = async (deviceId: string, device: Device) => {
    try {
      const response = await api.put(`/devices/${deviceId}`, device);
      setDevices(prev => prev.map(d => d.device_id === deviceId ? response.data : d));
      toast.success(`Device ${device.device_name} updated successfully`);
      return response.data;
    } catch (err) {
      const { userMessage, parsedError } = handleApiError(err, `updating device ${device.device_name}`);

      toast.error(parsedError.code === 'DEVICE_CONNECT_ERROR'
        ? 'Failed to connect to device. Check network settings.'
        : userMessage);
      setError(userMessage);
      throw err;
    }
  };

  const deleteDevice = async (deviceId: string) => {
    try {
      await api.delete(`/devices/${deviceId}`);
      setDevices(prev => prev.filter(d => d.device_id !== deviceId));
      toast.success('Device deleted successfully');
    } catch (err) {
      const { userMessage } = handleApiError(err, 'deleting device');
      toast.error('Failed to delete device. Please try again.');
      setError(userMessage);
      throw err;
    }
  };

  return {
    devices,
    loading,
    error,
    addDevice,
    updateDevice,
    deleteDevice,
  };
};
