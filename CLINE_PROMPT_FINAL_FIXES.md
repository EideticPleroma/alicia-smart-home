# Cline Prompt: Alicia Monitor - Final TypeScript & Environment Fixes

## 🎯 **Project Context**
Alicia Smart Home AI Assistant monitoring web app has been significantly improved with security, performance, and error handling. Need to complete the final TypeScript fixes and environment configuration.

## 🚨 **Critical Issues to Fix**

### **1. Create Environment Files (CRITICAL)**

#### **Frontend Environment File**
Create `alicia-monitor/.env`:
```
REACT_APP_SOCKET_URL=http://localhost:3001
REACT_APP_MQTT_BROKER=localhost
REACT_APP_MQTT_PORT=1883
REACT_APP_MQTT_USERNAME=monitor
REACT_APP_MQTT_PASSWORD=alicia_monitor_2024
```

#### **Backend Environment File**
Create `alicia-monitor-proxy/.env`:
```
NODE_ENV=production
PORT=3001
MQTT_BROKER=alicia_bus_core
MQTT_PORT=1883
MQTT_USERNAME=monitor_proxy
MQTT_PASSWORD=alicia_monitor_2024
CORS_ORIGIN=http://localhost:3000
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
```

### **2. Fix TypeScript Issues (HIGH PRIORITY)**

#### **Update GraphView.tsx**
Replace `any` types with proper interfaces from `types/index.ts`:

```typescript
// alicia-monitor/src/components/GraphView.tsx
import { ServiceData, MessageData } from '../types';

interface GraphViewProps {
  services: Record<string, ServiceData>;
  messageFlow: MessageData[];
  onNodeClick: (node: { id: string; data: ServiceData }) => void;
}

// Update the serviceNodes useMemo to use proper types
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
```

#### **Update SidePanel.tsx**
Replace `any` type with proper type:

```typescript
// alicia-monitor/src/components/SidePanel.tsx
interface ServiceData {
  name: string;
  status: 'healthy' | 'unhealthy' | 'unknown';
  uptime?: string;
  latency?: string;
  timestamp?: string;
  error?: string;
  details?: Record<string, unknown>; // Changed from any
  subscribedTopics?: string[];
  publishedTopics?: string[];
}
```

### **3. Update Dependencies (MEDIUM PRIORITY)**

#### **Update Frontend Dependencies**
```bash
cd alicia-monitor
npm update react react-dom typescript @types/react @types/react-dom
```

**Target Versions:**
- React: 18.3.1
- TypeScript: 5.6.3
- @types/react: 18.3.12
- @types/react-dom: 18.3.1

### **4. Add Socket Reconnection Logic (MEDIUM PRIORITY)**

#### **Create useSocket Hook**
Create `alicia-monitor/src/hooks/useSocket.ts`:

```typescript
import { useEffect, useRef, useState } from 'react';
import { io, Socket } from 'socket.io-client';

interface UseSocketOptions {
  url: string;
  autoConnect?: boolean;
  reconnectAttempts?: number;
  reconnectDelay?: number;
}

export const useSocket = ({
  url,
  autoConnect = true,
  reconnectAttempts = 5,
  reconnectDelay = 1000
}: UseSocketOptions) => {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const socketRef = useRef<Socket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectCountRef = useRef(0);

  const connect = () => {
    if (socketRef.current?.connected) return;

    try {
      socketRef.current = io(url, {
        autoConnect: false,
        reconnection: false // We'll handle reconnection manually
      });

      socketRef.current.on('connect', () => {
        setIsConnected(true);
        setError(null);
        reconnectCountRef.current = 0;
      });

      socketRef.current.on('disconnect', () => {
        setIsConnected(false);
        attemptReconnect();
      });

      socketRef.current.on('connect_error', (err) => {
        setError(err.message);
        attemptReconnect();
      });

      socketRef.current.connect();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connection failed');
    }
  };

  const attemptReconnect = () => {
    if (reconnectCountRef.current >= reconnectAttempts) {
      setError('Max reconnection attempts reached');
      return;
    }

    reconnectCountRef.current++;
    const delay = reconnectDelay * Math.pow(2, reconnectCountRef.current - 1);
    
    reconnectTimeoutRef.current = setTimeout(() => {
      connect();
    }, delay);
  };

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    socketRef.current?.disconnect();
    setIsConnected(false);
  };

  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [url, autoConnect]);

  return {
    socket: socketRef.current,
    isConnected,
    error,
    connect,
    disconnect
  };
};
```

#### **Update App.tsx to use useSocket Hook**
```typescript
// alicia-monitor/src/App.tsx
import { useSocket } from './hooks/useSocket';

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
    socket.on('health_update', (healthData) => {
      setServices(healthData);
    });

    // Message flow updates
    socket.on('message_flow', (flowData) => {
      setMessageFlow(flowData);
    });

    // MQTT message updates
    socket.on('mqtt_message', (message) => {
      console.log('MQTT Message:', message);
      setMessageFlow(prev => [message, ...prev.slice(0, 99)]);
    });

    return () => {
      socket.off('health_update');
      socket.off('message_flow');
      socket.off('mqtt_message');
    };
  }, [socket]);

  // ... rest of component
}
```

### **5. Improve SidePanel Styling (LOW PRIORITY)**

#### **Convert Inline Styles to Tailwind**
Replace inline styles in `SidePanel.tsx` with Tailwind classes:

```typescript
// Replace inline styles with Tailwind classes
<div className="mb-5">
  <h3 className="text-lg font-semibold text-gray-700 mb-2">
    {data.name}
  </h3>
</div>

<div className="mb-5">
  <div className="flex items-center gap-2 mb-2">
    <div 
      className="w-3 h-3 rounded-full"
      style={{ backgroundColor: getStatusColor(data.status) }}
    />
    <span className="text-base font-medium text-gray-900 capitalize">
      {data.status}
    </span>
  </div>
</div>

<div className="grid grid-cols-2 gap-4 mb-6">
  <div>
    <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
      Uptime
    </label>
    <div className="text-sm text-gray-900 font-medium">
      {formatUptime(data.uptime || 'Unknown')}
    </div>
  </div>
  // ... continue with other fields
</div>
```

### **6. Add Error Recovery for API Calls (LOW PRIORITY)**

#### **Create API Error Handler**
Create `alicia-monitor/src/utils/apiErrorHandler.ts`:

```typescript
export interface ApiError {
  message: string;
  status?: number;
  retryable: boolean;
}

export const handleApiError = (error: any): ApiError => {
  if (error.response) {
    return {
      message: error.response.data?.message || 'Server error',
      status: error.response.status,
      retryable: error.response.status >= 500
    };
  } else if (error.request) {
    return {
      message: 'Network error - please check your connection',
      retryable: true
    };
  } else {
    return {
      message: error.message || 'Unknown error occurred',
      retryable: false
    };
  }
};

export const retryApiCall = async <T>(
  apiCall: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> => {
  let lastError: any;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await apiCall();
    } catch (error) {
      lastError = error;
      const apiError = handleApiError(error);
      
      if (!apiError.retryable || i === maxRetries - 1) {
        throw error;
      }
      
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
    }
  }
  
  throw lastError;
};
```

## 🎯 **Implementation Steps**

1. **Create environment files** for both frontend and backend
2. **Update GraphView.tsx** to use proper TypeScript types
3. **Update SidePanel.tsx** to use proper TypeScript types
4. **Update dependencies** to latest versions
5. **Create useSocket hook** for reconnection logic
6. **Update App.tsx** to use the new socket hook
7. **Convert SidePanel inline styles** to Tailwind classes
8. **Add API error handling** utilities

## ✅ **Expected Results**

After implementation:
- ✅ **Environment Variables**: Proper configuration for all environments
- ✅ **Type Safety**: Complete TypeScript coverage with no `any` types
- ✅ **Socket Reliability**: Automatic reconnection and error recovery
- ✅ **Consistent Styling**: All components using Tailwind classes
- ✅ **Error Handling**: Robust error recovery for API calls
- ✅ **Production Ready**: Enterprise-grade monitoring application

## 🚀 **Quick Test**

After implementation:
1. `cd alicia-monitor && npm start`
2. `cd alicia-monitor-proxy && npm start`
3. Open http://localhost:3000
4. Verify real-time monitoring works
5. Test socket reconnection by stopping/starting proxy
6. Check browser console for TypeScript errors
7. Verify all components render correctly

This focused approach completes the final improvements needed for a production-ready monitoring application.
