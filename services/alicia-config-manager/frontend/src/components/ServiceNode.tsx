import { Handle, Position, NodeProps } from 'reactflow';
import { memo } from 'react';
import { ServiceConfig } from '../types';

interface ServiceNodeData extends ServiceConfig {
  name: string;
  onClick: () => void;
}

export const ServiceNode = memo(({ data }: NodeProps<ServiceNodeData>) => {
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
});

ServiceNode.displayName = 'ServiceNode';
