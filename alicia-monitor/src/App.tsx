import React, { useState, useEffect } from 'react';
import GraphView from './components/GraphView';
import StatusBar from './components/StatusBar';
import SidePanel from './components/SidePanel';
import { useSocket } from './hooks/useSocket';
import { ServiceData, MessageData } from './types';
import './App.css';

function App() {
  const [services, setServices] = useState<Record<string, ServiceData>>({});
  const [messageFlow, setMessageFlow] = useState<MessageData[]>([]);
  const [selectedNode, setSelectedNode] = useState<{ id: string; data: ServiceData } | null>(null);

  const { socket, isConnected, error } = useSocket({
    url: process.env.REACT_APP_SOCKET_URL || 'http://localhost:3001',
    autoConnect: true,
    reconnectAttempts: 5,
    reconnectDelay: 1000
  });

  useEffect(() => {
    if (!socket) return;

    // Health updates
    socket.on('health_update', (healthData: Record<string, ServiceData>) => {
      setServices(healthData);
    });

    // Message flow updates
    socket.on('message_flow', (flowData: MessageData[]) => {
      setMessageFlow(flowData);
    });

    // MQTT message updates
    socket.on('mqtt_message', (message: MessageData) => {
      console.log('MQTT Message:', message);
      setMessageFlow(prev => [message, ...prev.slice(0, 99)]);
    });

    return () => {
      socket.off('health_update');
      socket.off('message_flow');
      socket.off('mqtt_message');
    };
  }, [socket]);

  const handleNodeClick = (node: { id: string; data: ServiceData }) => {
    setSelectedNode(node);
  };

  const handleClosePanel = () => {
    setSelectedNode(null);
  };

  return (
    <div className="App">
      <StatusBar
        isConnected={isConnected}
        serviceCount={Object.keys(services).length}
        healthyCount={Object.values(services).filter(s => s.status === 'healthy').length}
      />

      <div className="main-content">
        <GraphView
          services={services}
          messageFlow={messageFlow}
          onNodeClick={handleNodeClick}
        />

        <SidePanel
          node={selectedNode}
          onClose={handleClosePanel}
        />
      </div>
    </div>
  );
}

export default App;
