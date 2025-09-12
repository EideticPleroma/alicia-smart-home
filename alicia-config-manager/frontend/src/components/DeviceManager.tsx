import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { X, Plus, Trash2, Edit, Loader2 } from 'lucide-react';
import { Device } from '../types';
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts';

interface DeviceManagerProps {
  devices: Device[];
  onAddDevice: (device: Device) => Promise<void>;
  onUpdateDevice: (id: string, device: Device) => Promise<void>;
  onDeleteDevice: (id: string) => Promise<void>;
  onClose: () => void;
}

export const DeviceManager: React.FC<DeviceManagerProps> = ({
  devices,
  onAddDevice,
  onUpdateDevice,
  onDeleteDevice,
  onClose,
}) => {
  const [isAdding, setIsAdding] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { register, handleSubmit, reset, formState: { isSubmitting } } = useForm<Device>();

  const onSubmit = async (data: Device) => {
    setLoading(true);
    try {
      if (editingId) {
        await onUpdateDevice(editingId, data);
        setEditingId(null);
      } else {
        await onAddDevice(data);
      }
      reset();
      setIsAdding(false);
    } catch (error) {
      console.error('Failed to submit device:', error);
      // Error is already handled by the hook with toasts
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (device: Device) => {
    setEditingId(device.device_id);
    reset(device);
    setIsAdding(true);
  };

  const handleDelete = (id: string) => {
    if (window.confirm('Are you sure you want to delete this device?')) {
      onDeleteDevice(id);
    }
  };

  const handleCancel = () => {
    setIsAdding(false);
    setEditingId(null);
    reset();
  };

  // Keyboard shortcuts for device manager
  useKeyboardShortcuts({
    onEscape: () => {
      if (isAdding) {
        handleCancel();
      } else {
        onClose();
      }
    },
    onSave: isAdding ? handleSubmit(onSubmit) : undefined,
    onCancel: isAdding ? handleCancel : undefined,
  });

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-white">Device Manager</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        <div className="space-y-4">
          {/* Add/Edit Form */}
          {isAdding && (
            <form onSubmit={handleSubmit(onSubmit)} className="bg-gray-700 p-4 rounded-lg space-y-4">
              <h3 className="text-lg font-semibold text-white">
                {editingId ? 'Edit Device' : 'Add New Device'}
              </h3>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Device Name
                  </label>
                  <input
                    {...register('device_name', { required: true })}
                    className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter device name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Device Type
                  </label>
                  <select
                    {...register('device_type', { required: true })}
                    className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="external_api">External API</option>
                    <option value="local_service">Local Service</option>
                    <option value="hardware">Hardware</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Host
                  </label>
                  <input
                    {...register('connection.host', { required: true })}
                    className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="IP address or hostname"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Port
                  </label>
                  <input
                    {...register('connection.port', { required: true, valueAsNumber: true })}
                    type="number"
                    className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Port number"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Protocol
                  </label>
                  <select
                    {...register('connection.protocol', { required: true })}
                    className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="http">HTTP</option>
                    <option value="https">HTTPS</option>
                    <option value="tcp">TCP</option>
                    <option value="udp">UDP</option>
                    <option value="mqtt">MQTT</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={handleCancel}
                  className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading || isSubmitting}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-md transition-colors flex items-center gap-2"
                >
                  {(loading || isSubmitting) && <Loader2 size={16} className="animate-spin" />}
                  {loading || isSubmitting
                    ? 'Processing...'
                    : editingId ? 'Update Device' : 'Add Device'
                  }
                </button>
              </div>
            </form>
          )}

          {/* Device List */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-white">Devices</h3>
              <button
                onClick={() => setIsAdding(true)}
                disabled={loading}
                className="flex items-center px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-md text-sm font-medium transition-colors"
              >
                <Plus size={16} className="mr-2" />
                Add Device
              </button>
            </div>

            {devices.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                No devices configured
              </div>
            ) : (
              <div className="space-y-2">
                {devices.map((device) => (
                  <div
                    key={device.device_id}
                    className="flex items-center justify-between p-4 bg-gray-700 rounded-lg"
                  >
                    <div className="flex items-center space-x-4">
                      <div className={`w-3 h-3 rounded-full ${
                        device.status === 'online' ? 'bg-green-500' : 'bg-red-500'
                      }`} />
                      <div>
                        <div className="font-medium text-white">{device.device_name}</div>
                        <div className="text-sm text-gray-400">
                          {device.connection.host}:{device.connection.port} ({device.connection.protocol})
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleEdit(device)}
                        className="p-2 text-gray-400 hover:text-white transition-colors"
                      >
                        <Edit size={16} />
                      </button>
                      <button
                        onClick={() => handleDelete(device.device_id)}
                        className="p-2 text-red-400 hover:text-red-300 transition-colors"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
