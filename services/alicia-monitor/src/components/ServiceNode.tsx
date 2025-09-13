import React, { memo, useMemo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';

interface ServiceNodeData {
  name: string;
  status: 'healthy' | 'unhealthy' | 'unknown';
  uptime?: string;
  latency?: string;
  messageCount?: number;
  onClick?: () => void;
}

const ServiceNode: React.FC<NodeProps<ServiceNodeData>> = memo(({ data }) => {
  const getNodeColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-healthy';
      case 'unhealthy':
        return 'bg-unhealthy';
      default:
        return 'bg-inactive';
    }
  };

  const getNodeSize = (messageCount?: number) => {
    if (!messageCount) return 'w-16 h-16';
    // Scale size based on message count (min 60px, max 120px)
    const size = Math.min(120, Math.max(60, 60 + Math.log10(messageCount + 1) * 20));
    const tailwindSize = Math.round(size / 4); // Convert to Tailwind units
    return `w-${tailwindSize} h-${tailwindSize}`;
  };

  const nodeColor = getNodeColor(data.status);
  const nodeSize = getNodeSize(data.messageCount);

  return (
    <div
      className={`service-node ${nodeColor} ${nodeSize} rounded-full border-4 border-white shadow-lg flex flex-col items-center justify-center cursor-pointer hover:scale-110 transition-all duration-300 relative`}
      onClick={data.onClick}
    >
      {/* Service name */}
      <div className="text-white text-xs font-bold text-center text-shadow mb-1 max-w-4/5 overflow-hidden truncate">
        {data.name.replace('alicia-', '').replace('-service', '')}
      </div>

      {/* Status indicator */}
      <div className="w-2 h-2 rounded-full bg-white opacity-80" />

      {/* Message count badge */}
      {data.messageCount && data.messageCount > 0 && (
        <div className="absolute -top-2 -right-2 bg-blue-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold border-2 border-white">
          {data.messageCount > 99 ? '99+' : data.messageCount}
        </div>
      )}

      {/* Connection handles */}
      <Handle
        type="target"
        position={Position.Top}
        className="w-2 h-2 bg-white border-2 border-gray-600"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-2 h-2 bg-white border-2 border-gray-600"
      />
      <Handle
        type="target"
        position={Position.Left}
        className="w-2 h-2 bg-white border-2 border-gray-600"
      />
      <Handle
        type="source"
        position={Position.Right}
        className="w-2 h-2 bg-white border-2 border-gray-600"
      />
    </div>
  );
});

export default ServiceNode;
