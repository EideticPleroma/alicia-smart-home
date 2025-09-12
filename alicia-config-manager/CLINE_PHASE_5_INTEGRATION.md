# Cline Phase 5: API Integration and Real-time Updates

## 🎯 **Goal**
Complete the API integration, add missing components, and implement real-time updates.

## 📁 **Missing Components**

**frontend/src/components/StatusBar.tsx:**
```typescript
import React from 'react';
import { Wifi, WifiOff, Server, Database } from 'lucide-react';

interface StatusBarProps {
  isConnected: boolean;
  serviceCount: number;
  deviceCount: number;
}

export const StatusBar: React.FC<StatusBarProps> = ({
  isConnected,
  serviceCount,
  deviceCount,
}) => {
  return (
    <div className="flex items-center space-x-4 text-sm">
      <div className="flex items-center space-x-2">
        {isConnected ? (
          <Wifi className="w-4 h-4 text-green-400" />
        ) : (
          <WifiOff className="w-4 h-4 text-red-400" />
        )}
        <span className={isConnected ? 'text-green-400' : 'text-red-400'}>
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
      </div>
      
      <div className="flex items-center space-x-2">
        <Server className="w-4 h-4 text-blue-400" />
        <span className="text-blue-400">{serviceCount} Services</span>
      </div>
      
      <div className="flex items-center space-x-2">
        <Database className="w-4 h-4 text-purple-400" />
        <span className="text-purple-400">{deviceCount} Devices</span>
      </div>
    </div>
  );
};
```

**frontend/src/components/ReloadButton.tsx:**
```typescript
import React, { useState } from 'react';
import { RotateCcw, Loader } from 'lucide-react';
import toast from 'react-hot-toast';

interface ReloadButtonProps {
  onReload: () => Promise<void>;
}

export const ReloadButton: React.FC<ReloadButtonProps> = ({ onReload }) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleReload = async () => {
    setIsLoading(true);
    try {
      await onReload();
      toast.success('Configuration reloaded successfully');
    } catch (error) {
      toast.error('Failed to reload configuration');
      console.error('Reload error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      onClick={handleReload}
      disabled={isLoading}
      className="flex items-center px-3 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white rounded-md text-sm font-medium transition-colors"
    >
      {isLoading ? (
        <Loader className="w-4 h-4 mr-2 animate-spin" />
      ) : (
        <RotateCcw className="w-4 h-4 mr-2" />
      )}
      {isLoading ? 'Reloading...' : 'Reload Config'}
    </button>
  );
};
```

**frontend/src/components/DeviceManager.tsx:**
```typescript
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { X, Plus, Trash2, Edit } from 'lucide-react';
import { Device } from '../types';

interface DeviceManagerProps {
  devices: Device[];
  onAddDevice: (device: Device) => void;
  onUpdateDevice: (id: string, device: Device) => void;
  onDeleteDevice: (id: string) => void;
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
  const { register, handleSubmit, reset } = useForm<Device>();

  const onSubmit = (data: Device) => {
    if (editingId) {
      onUpdateDevice(editingId, data);
      setEditingId(null);
    } else {
      onAddDevice(data);
    }
    reset();
    setIsAdding(false);
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
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
                >
                  {editingId ? 'Update' : 'Add'} Device
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
                className="flex items-center px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium transition-colors"
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
```

**frontend/src/components/MessageEdge.tsx:**
```typescript
import React from 'react';
import { EdgeProps, getBezierPath } from 'reactflow';

export const MessageEdge: React.FC<EdgeProps> = ({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
}) => {
  const [edgePath] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  return (
    <>
      <path
        id={id}
        className="react-flow__edge-path"
        d={edgePath}
        stroke="#3b82f6"
        strokeWidth={2}
        fill="none"
      />
      {data?.messageCount && (
        <text>
          <textPath href={`#${id}`} style={{ fontSize: 12, fill: '#9ca3af' }}>
            {data.messageCount} messages
          </textPath>
        </text>
      )}
    </>
  );
};
```

## 🔧 **API Service**

**frontend/src/services/api.ts:**
```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001';

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);
    return Promise.reject(error);
  }
);
```

## 🎯 **Type Definitions**

**frontend/src/types/index.ts:**
```typescript
export interface ServiceConfig {
  service_name: string;
  service_type: 'stt' | 'tts' | 'llm' | 'device_control' | 'voice_router';
  status: 'healthy' | 'unhealthy' | 'unknown';
  enabled: boolean;
  version: string;
  last_updated: string;
  config: {
    api_key?: string;
    provider?: string;
    model?: string;
    voice?: string;
    language?: string;
    temperature?: number;
    max_tokens?: number;
    endpoints: Array<{
      type: string;
      model?: string;
      ip: string;
      port?: number;
      protocol?: 'http' | 'https' | 'tcp' | 'udp';
    }>;
    settings?: Record<string, any>;
  };
}

export interface Device {
  device_id: string;
  device_name: string;
  device_type: 'external_api' | 'local_service' | 'hardware';
  status: 'online' | 'offline' | 'unknown';
  last_seen: string;
  connection: {
    host: string;
    port: number;
    protocol: 'http' | 'https' | 'tcp' | 'udp' | 'mqtt';
    authentication: {
      type: 'api_key' | 'oauth' | 'basic' | 'certificate';
      credentials: Record<string, any>;
    };
  };
  capabilities: string[];
  metadata: Record<string, any>;
}

export interface MQTTMessage {
  topic: string;
  data: any;
  timestamp: string;
}
```

## 🎯 **Implementation Steps**

1. **Create all missing components** with the exact content provided
2. **Create the API service** for HTTP requests
3. **Create the type definitions** for TypeScript
4. **Test the complete application** end-to-end
5. **Verify real-time updates** work correctly

## ✅ **Verification**

After implementation, verify:
- [ ] All components render without errors
- [ ] API calls work correctly
- [ ] Real-time updates are received
- [ ] Configuration changes are saved
- [ ] Device management works
- [ ] Error handling works properly

**Next Phase**: Testing and deployment

