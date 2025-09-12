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
} from 'reactflow';
import 'reactflow/dist/style.css';
import ServiceNode from './ServiceNode';
import MessageEdge from './MessageEdge';
import { ServiceData, MessageData, GraphViewProps } from '../types';

const nodeTypes = {
  serviceNode: ServiceNode,
};

const edgeTypes = {
  messageEdge: MessageEdge,
};

const GraphView: React.FC<GraphViewProps> = ({ services, messageFlow, onNodeClick }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Convert services data to React Flow nodes
  const serviceNodes = useMemo(() => {
    return Object.entries(services).map(([serviceName, serviceData]: [string, ServiceData], index) => {
      const x = (index % 4) * 250 + 100;
      const y = Math.floor(index / 4) * 150 + 100;

      return {
        id: serviceName,
        type: 'serviceNode',
        position: { x, y },
        data: {
          ...serviceData,
          name: serviceName,
          onClick: () => onNodeClick({ id: serviceName, data: serviceData }),
        },
      } as Node;
    });
  }, [services, onNodeClick]);

  // Convert message flow to edges
  const messageEdges = useMemo(() => {
    const edgeMap = new Map<string, Edge>();

    messageFlow.forEach((message, index) => {
      if (message.topic && message.topic.startsWith('alicia/')) {
        const parts = message.topic.split('/');
        if (parts.length >= 3) {
          const sourceService = `alicia-${parts[1]}-service` || `alicia-${parts[1]}`;
          const targetService = parts.length > 3 ? `alicia-${parts[2]}-service` : 'alicia-bus-core';
          const edgeId = `${sourceService}-${targetService}`;

          if (!edgeMap.has(edgeId)) {
            edgeMap.set(edgeId, {
              id: edgeId,
              source: sourceService,
              target: targetService,
              type: 'messageEdge',
              data: {
                messageCount: 1,
                lastMessage: message.timestamp,
                active: true,
              },
              animated: true,
            } as Edge);
          } else {
            const existingEdge = edgeMap.get(edgeId)!;
            existingEdge.data = {
              ...existingEdge.data,
              messageCount: (existingEdge.data?.messageCount || 0) + 1,
              lastMessage: message.timestamp,
            };
          }
        }
      }
    });

    return Array.from(edgeMap.values());
  }, [messageFlow]);

  // Update nodes and edges when data changes
  React.useEffect(() => {
    setNodes(serviceNodes);
  }, [serviceNodes, setNodes]);

  React.useEffect(() => {
    setEdges(messageEdges);
  }, [messageEdges, setEdges]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <div className="graph-view">
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
        <Background color="#aaa" gap={16} />
      </ReactFlow>
    </div>
  );
};

export default GraphView;
