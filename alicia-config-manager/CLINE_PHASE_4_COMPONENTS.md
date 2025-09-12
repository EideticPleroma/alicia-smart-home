# Cline Phase 4: React Flow Components and Service Visualization

## 🎯 **Goal**
Create the React Flow components for service visualization and configuration management.

## 📁 **Component Structure**

```
frontend/src/components/
├── ServiceGraph.tsx
├── ServiceNode.tsx
├── ConfigModal.tsx
├── DeviceManager.tsx
├── ReloadButton.tsx
├── StatusBar.tsx
└── MessageEdge.tsx
```

## 🎨 **Service Graph Component**

**frontend/src/components/ServiceGraph.tsx:**
```typescript
import React, { useCallback, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  MiniMap,
  NodeTypes,
  EdgeTypes,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { ServiceNode } from './ServiceNode';
import { MessageEdge } from './MessageEdge';
import { ServiceConfig, Device } from '../types';

interface ServiceGraphProps {
  services: Record<string, ServiceConfig>;
  devices: Device[];
  onServiceClick: (serviceName: string) => void;
}

const nodeTypes: NodeTypes = {
  serviceNode: ServiceNode,
};

const edgeTypes: EdgeTypes = {
  messageEdge: MessageEdge,
};

export const ServiceGraph: React.FC<ServiceGraphProps> = ({
  services,
  devices,
  onServiceClick,
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Convert services to React Flow nodes
  const serviceNodes = useMemo(() => {
    return Object.entries(services).map(([serviceName, serviceData], index) => {
      const x = (index % 4) * 300 + 100;
      const y = Math.floor(index / 4) * 200 + 100;

      return {
        id: serviceName,
        type: 'serviceNode',
        position: { x, y },
        data: {
          ...serviceData,
          name: serviceName,
          onClick: () => onServiceClick(serviceName),
        },
      } as Node;
    });
  }, [services, onServiceClick]);

  // Convert devices to React Flow nodes
  const deviceNodes = useMemo(() => {
    return devices.map((device, index) => {
      const x = 1200 + (index % 2) * 300;
      const y = 100 + Math.floor(index / 2) * 200;

      return {
        id: `device-${device.device_id}`,
        type: 'serviceNode',
        position: { x, y },
        data: {
          ...device,
          name: device.device_name,
          service_type: 'device',
          onClick: () => {}, // Devices don't have config modals
        },
      } as Node;
    });
  }, [devices]);

  // Create edges between services
  const serviceEdges = useMemo(() => {
    const edges: Edge[] = [];
    const serviceNames = Object.keys(services);
    
    // Create connections based on service types
    serviceNames.forEach((source, index) => {
      const target = serviceNames[(index + 1) % serviceNames.length];
      if (source !== target) {
        edges.push({
          id: `${source}-${target}`,
          source,
          target,
          type: 'messageEdge',
          animated: true,
          data: {
            messageCount: Math.floor(Math.random() * 10) + 1,
            lastMessage: new Date().toISOString(),
          },
        });
      }
    });

    return edges;
  }, [services]);

  // Update nodes when data changes
  React.useEffect(() => {
    setNodes([...serviceNodes, ...deviceNodes]);
  }, [serviceNodes, deviceNodes, setNodes]);

  React.useEffect(() => {
    setEdges(serviceEdges);
  }, [serviceEdges, setEdges]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <div className="w-full h-screen">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        attributionPosition="top-right"
      >
        <Controls />
        <MiniMap />
        <Background color="#374151" gap={16} />
      </ReactFlow>
    </div>
  );
};
```

## 🔧 **Service Node Component**

**frontend/src/components/ServiceNode.tsx:**
```typescript
import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { ServiceConfig, Device } from '../types';

interface ServiceNodeData extends ServiceConfig {
  name: string;
  onClick: () => void;
}

export const ServiceNode: React.FC<NodeProps<ServiceNodeData>> = ({ data }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-500';
      case 'unhealthy':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getServiceIcon = (serviceType: string) => {
    switch (serviceType) {
      case 'stt':
        return '🎤';
      case 'tts':
        return '🔊';
      case 'llm':
        return '🧠';
      case 'device_control':
        return '🏠';
      case 'voice_router':
        return '🔄';
      case 'device':
        return '📱';
      default:
        return '⚙️';
    }
  };

  return (
    <div
      className="bg-gray-800 border border-gray-600 rounded-lg p-4 min-w-[200px] shadow-lg hover:shadow-xl transition-shadow cursor-pointer"
      onClick={data.onClick}
    >
      <Handle type="target" position={Position.Top} className="w-3 h-3" />
      <Handle type="source" position={Position.Bottom} className="w-3 h-3" />
      
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <span className="text-2xl">{getServiceIcon(data.service_type)}</span>
          <span className="font-semibold text-white">{data.name}</span>
        </div>
        <div className={`w-3 h-3 rounded-full ${getStatusColor(data.status)}`} />
      </div>
      
      <div className="text-sm text-gray-300 space-y-1">
        <div>Type: {data.service_type}</div>
        <div>Status: {data.status}</div>
        <div>Version: {data.version}</div>
        {data.enabled ? (
          <div className="text-green-400">✓ Enabled</div>
        ) : (
          <div className="text-red-400">✗ Disabled</div>
        )}
      </div>
    </div>
  );
};
```

## ⚙️ **Configuration Modal Component**

**frontend/src/components/ConfigModal.tsx:**
```typescript
import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { ServiceConfig } from '../types';
import { X, Save, RotateCcw } from 'lucide-react';

interface ConfigModalProps {
  serviceName: string;
  config: ServiceConfig;
  onSave: (config: ServiceConfig) => void;
  onClose: () => void;
}

export const ConfigModal: React.FC<ConfigModalProps> = ({
  serviceName,
  config,
  onSave,
  onClose,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const { register, handleSubmit, reset, watch } = useForm<ServiceConfig>({
    defaultValues: config,
  });

  const watchedValues = watch();

  useEffect(() => {
    reset(config);
  }, [config, reset]);

  const onSubmit = async (data: ServiceConfig) => {
    setIsLoading(true);
    try {
      await onSave(data);
    } catch (error) {
      console.error('Failed to save configuration:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    reset(config);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-white">
            Configure {serviceName}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Basic Configuration */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Basic Settings</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Service Type
                </label>
                <select
                  {...register('service_type')}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="stt">Speech-to-Text</option>
                  <option value="tts">Text-to-Speech</option>
                  <option value="llm">Large Language Model</option>
                  <option value="device_control">Device Control</option>
                  <option value="voice_router">Voice Router</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Status
                </label>
                <select
                  {...register('status')}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="healthy">Healthy</option>
                  <option value="unhealthy">Unhealthy</option>
                  <option value="unknown">Unknown</option>
                </select>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  {...register('enabled')}
                  className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-300">Enabled</span>
              </label>
            </div>
          </div>

          {/* API Configuration */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">API Configuration</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                API Key
              </label>
              <input
                type="password"
                {...register('config.api_key')}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter API key..."
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Provider
                </label>
                <input
                  {...register('config.provider')}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., openai, elevenlabs"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Model
                </label>
                <input
                  {...register('config.model')}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., whisper-1, gpt-4"
                />
              </div>
            </div>
          </div>

          {/* Endpoints */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Endpoints</h3>
            <div className="space-y-2">
              {watchedValues.config?.endpoints?.map((endpoint, index) => (
                <div key={index} className="grid grid-cols-4 gap-2 p-3 bg-gray-700 rounded-md">
                  <input
                    {...register(`config.endpoints.${index}.type`)}
                    placeholder="Type"
                    className="px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                  />
                  <input
                    {...register(`config.endpoints.${index}.ip`)}
                    placeholder="IP Address"
                    className="px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                  />
                  <input
                    {...register(`config.endpoints.${index}.port`)}
                    placeholder="Port"
                    type="number"
                    className="px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                  />
                  <select
                    {...register(`config.endpoints.${index}.protocol`)}
                    className="px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                  >
                    <option value="http">HTTP</option>
                    <option value="https">HTTPS</option>
                    <option value="tcp">TCP</option>
                    <option value="udp">UDP</option>
                  </select>
                </div>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-4 pt-6 border-t border-gray-600">
            <button
              type="button"
              onClick={handleReset}
              className="flex items-center px-4 py-2 text-gray-300 hover:text-white transition-colors"
            >
              <RotateCcw size={16} className="mr-2" />
              Reset
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-md transition-colors"
            >
              <Save size={16} className="mr-2" />
              {isLoading ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
```

## 🎯 **Implementation Steps**

1. **Create all component files** with the exact content provided
2. **Install React Flow dependencies** if not already installed
3. **Test each component** individually
4. **Integrate components** into the main App
5. **Test the complete application**

## ✅ **Verification**

After implementation, verify:
- [ ] Service graph renders correctly
- [ ] Service nodes display with proper styling
- [ ] Configuration modal opens and closes
- [ ] Form validation works
- [ ] Real-time updates are reflected in the graph

**Next Phase**: API integration and real-time updates

