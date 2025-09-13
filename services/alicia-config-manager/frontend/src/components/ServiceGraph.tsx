import React, { useCallback, useMemo, memo } from 'react';
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

export const ServiceGraph: React.FC<ServiceGraphProps> = memo(({
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
        // Performance optimizations
        onlyRenderVisibleElements={true}
        nodesDraggable={true}
        nodesConnectable={false}
        elementsSelectable={true}
      >
        <Controls />
        <MiniMap />
        <Background color="#374151" gap={16} />
      </ReactFlow>
    </div>
  );
});

ServiceGraph.displayName = 'ServiceGraph';
