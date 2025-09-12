export interface ServiceData {
  name: string;
  status: 'healthy' | 'unhealthy' | 'unknown';
  uptime?: string;
  latency?: string;
  timestamp?: string;
  error?: string;
  details?: Record<string, unknown>;
  subscribedTopics?: string[];
  publishedTopics?: string[];
}

export interface MessageData {
  topic: string;
  timestamp: string;
  data: Record<string, unknown>;
}

export interface ServiceNodeData extends ServiceData {
  messageCount?: number;
  onClick?: () => void;
}

export interface GraphViewProps {
  services: Record<string, ServiceData>;
  messageFlow: MessageData[];
  onNodeClick: (node: { id: string; data: ServiceData }) => void;
}
