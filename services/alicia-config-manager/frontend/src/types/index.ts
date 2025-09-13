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
    endpoints: {
      type: string;
      model?: string;
      ip: string;
      port?: number;
      protocol: string;
    }[];
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

export interface ServiceNodeData {
  id: string;
  label: string;
  status: 'healthy' | 'unhealthy' | 'unknown';
  type: string;
  position: { x: number; y: number };
}

export interface DeviceNodeData {
  id: string;
  label: string;
  status: 'online' | 'offline' | 'unknown';
  type: string;
  position: { x: number; y: number };
}

export interface MQTTMessage {
  topic: string;
  data: any;
  timestamp: string;
}

export type NodeData = ServiceNodeData | DeviceNodeData;
