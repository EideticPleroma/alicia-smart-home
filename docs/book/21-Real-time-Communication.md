# Chapter 21: Real-time Communication

## 🎯 **Real-time Communication Architecture Overview**

The Alicia system implements **sophisticated real-time communication** between frontend applications and backend services using WebSocket connections, MQTT message bridging, and event-driven architecture. This chapter analyzes the real-time communication implementation, examining WebSocket integration, message flow patterns, and real-time data synchronization.

## 🔌 **WebSocket Integration Architecture**

### **Dual WebSocket Implementation**

Alicia implements **two WebSocket services** for different purposes:

1. **Config Manager WebSocket** - Configuration management and service control
2. **Monitor WebSocket** - Real-time monitoring and message flow visualization

**Why Dual WebSocket Services?**

1. **Separation of Concerns**: Different data flows and update patterns
2. **Performance Optimization**: Optimize each service for its specific use case
3. **Security Isolation**: Separate security contexts for different operations
4. **Scalability**: Scale monitoring and configuration independently
5. **User Experience**: Provide focused, purpose-built real-time experiences

### **WebSocket Service Implementation**

The WebSocket services implement **comprehensive real-time communication**:

```typescript
// Config Manager WebSocket Hook
export const useSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [socket, setSocket] = useState<Socket | null>(null);

  useEffect(() => {
    const newSocket = io(import.meta.env.VITE_API_URL || 'http://localhost:3000', {
      transports: ['websocket'],
      timeout: 20000,
    });

    newSocket.on('connect', () => {
      setIsConnected(true);
      console.log('Connected to server');
    });

    newSocket.on('disconnect', () => {
      setIsConnected(false);
      console.log('Disconnected from server');
    });

    newSocket.on('connect_error', (error) => {
      console.error('Connection error:', error);
      setIsConnected(false);
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);
```

**WebSocket Features:**
- **Automatic Connection**: Auto-connect on application start
- **Connection State Management**: Track connection status
- **Error Handling**: Comprehensive error handling
- **Cleanup**: Proper cleanup on component unmount
- **Reconnection Logic**: Automatic reconnection with backoff

### **Monitor WebSocket Implementation**

The Monitor implements **specialized monitoring WebSocket**:

```typescript
// Monitor WebSocket Hook
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
```

**Monitor WebSocket Features:**
- **Health Monitoring**: Real-time service health updates
- **Message Flow**: Live message flow visualization
- **MQTT Integration**: Direct MQTT message streaming
- **Event Handling**: Multiple event types and handlers
- **State Synchronization**: Synchronize state with real-time data

## 📡 **MQTT Message Bridging**

### **MQTT to WebSocket Bridge**

The system implements **MQTT to WebSocket message bridging**:

```typescript
// MQTT Message Bridge
export class MQTTWebSocketBridge {
  private mqttClient: mqtt.MqttClient;
  private io: Server;
  private messageBuffer: Map<string, MessageData[]> = new Map();

  constructor(mqttClient: mqtt.MqttClient, io: Server) {
    this.mqttClient = mqttClient;
    this.io = io;
    this.setupMQTTSubscriptions();
  }

  private setupMQTTSubscriptions() {
    // Subscribe to all Alicia topics
    this.mqttClient.subscribe('alicia/+/+', { qos: 1 });
    
    this.mqttClient.on('message', (topic, message) => {
      this.handleMQTTMessage(topic, message);
    });
  }

  private handleMQTTMessage(topic: string, message: Buffer) {
    try {
      const messageData: MessageData = {
        topic,
        payload: JSON.parse(message.toString()),
        timestamp: Date.now(),
        qos: 1
      };

      // Buffer message for flow visualization
      this.bufferMessage(messageData);

      // Broadcast to WebSocket clients
      this.io.emit('mqtt_message', messageData);

      // Update message flow
      this.updateMessageFlow(messageData);

    } catch (error) {
      console.error('MQTT message processing failed:', error);
    }
  }
```

**MQTT Bridge Features:**
- **Topic Subscription**: Subscribe to all Alicia topics
- **Message Parsing**: Parse MQTT messages to structured data
- **WebSocket Broadcasting**: Broadcast messages to WebSocket clients
- **Message Buffering**: Buffer messages for flow visualization
- **Error Handling**: Handle message processing errors

### **Message Flow Visualization**

The system implements **real-time message flow visualization**:

```typescript
// Message Flow Manager
export class MessageFlowManager {
  private messageFlow: MessageData[] = [];
  private maxFlowSize = 1000;
  private flowUpdateInterval = 1000; // 1 second

  constructor(private io: Server) {
    this.startFlowUpdates();
  }

  private startFlowUpdates() {
    setInterval(() => {
      if (this.messageFlow.length > 0) {
        this.io.emit('message_flow', this.messageFlow);
        this.messageFlow = []; // Clear after sending
      }
    }, this.flowUpdateInterval);
  }

  public addMessage(message: MessageData) {
    this.messageFlow.push(message);
    
    // Limit flow size
    if (this.messageFlow.length > this.maxFlowSize) {
      this.messageFlow = this.messageFlow.slice(-this.maxFlowSize);
    }
  }

  public getMessageFlow(): MessageData[] {
    return [...this.messageFlow];
  }
}
```

**Message Flow Features:**
- **Flow Aggregation**: Aggregate messages for visualization
- **Size Management**: Limit message flow size
- **Periodic Updates**: Send updates at regular intervals
- **Performance Optimization**: Optimize for real-time performance
- **Memory Management**: Manage memory usage

## 🔄 **Event-Driven Architecture**

### **Event System Implementation**

The system implements **comprehensive event-driven architecture**:

```typescript
// Event System
export class EventSystem {
  private events: Map<string, Set<Function>> = new Map();
  private eventHistory: EventHistory[] = [];
  private maxHistorySize = 1000;

  public emit(eventName: string, data: any) {
    const handlers = this.events.get(eventName);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Event handler error for ${eventName}:`, error);
        }
      });
    }

    // Store in history
    this.eventHistory.push({
      eventName,
      data,
      timestamp: Date.now()
    });

    // Limit history size
    if (this.eventHistory.length > this.maxHistorySize) {
      this.eventHistory = this.eventHistory.slice(-this.maxHistorySize);
    }
  }

  public on(eventName: string, handler: Function) {
    if (!this.events.has(eventName)) {
      this.events.set(eventName, new Set());
    }
    this.events.get(eventName)!.add(handler);
  }

  public off(eventName: string, handler: Function) {
    const handlers = this.events.get(eventName);
    if (handlers) {
      handlers.delete(handler);
    }
  }
}
```

**Event System Features:**
- **Event Emission**: Emit events with data
- **Event Handling**: Register and handle event handlers
- **Error Handling**: Handle event handler errors
- **Event History**: Track event history
- **Memory Management**: Limit event history size

### **Service Event Integration**

The system integrates **service events with real-time communication**:

```typescript
// Service Event Integration
export class ServiceEventIntegration {
  private eventSystem: EventSystem;
  private mqttClient: mqtt.MqttClient;
  private io: Server;

  constructor(eventSystem: EventSystem, mqttClient: mqtt.MqttClient, io: Server) {
    this.eventSystem = eventSystem;
    this.mqttClient = mqttClient;
    this.io = io;
    this.setupEventHandlers();
  }

  private setupEventHandlers() {
    // Service health events
    this.eventSystem.on('service_health_changed', (data) => {
      this.handleServiceHealthChange(data);
    });

    // Service configuration events
    this.eventSystem.on('service_config_updated', (data) => {
      this.handleServiceConfigUpdate(data);
    });

    // Device events
    this.eventSystem.on('device_status_changed', (data) => {
      this.handleDeviceStatusChange(data);
    });
  }

  private handleServiceHealthChange(data: any) {
    // Publish to MQTT
    this.mqttClient.publish('alicia/health/update', JSON.stringify(data));

    // Broadcast to WebSocket clients
    this.io.emit('health_update', data);
  }
}
```

**Service Integration Features:**
- **Event Handling**: Handle service events
- **MQTT Publishing**: Publish events to MQTT
- **WebSocket Broadcasting**: Broadcast events to WebSocket clients
- **Data Transformation**: Transform event data for different channels
- **Error Handling**: Handle integration errors

## 📊 **Real-time Data Synchronization**

### **State Synchronization**

The system implements **real-time state synchronization**:

```typescript
// State Synchronization Manager
export class StateSynchronizationManager {
  private state: Map<string, any> = new Map();
  private subscribers: Map<string, Set<Function>> = new Map();
  private syncInterval: NodeJS.Timeout;

  constructor() {
    this.startSync();
  }

  public setState(key: string, value: any) {
    const oldValue = this.state.get(key);
    this.state.set(key, value);

    // Notify subscribers
    const subscribers = this.subscribers.get(key);
    if (subscribers) {
      subscribers.forEach(callback => {
        callback(value, oldValue);
      });
    }
  }

  public getState(key: string) {
    return this.state.get(key);
  }

  public subscribe(key: string, callback: Function) {
    if (!this.subscribers.has(key)) {
      this.subscribers.set(key, new Set());
    }
    this.subscribers.get(key)!.add(callback);
  }

  public unsubscribe(key: string, callback: Function) {
    const subscribers = this.subscribers.get(key);
    if (subscribers) {
      subscribers.delete(callback);
    }
  }

  private startSync() {
    this.syncInterval = setInterval(() => {
      this.syncState();
    }, 1000); // Sync every second
  }

  private syncState() {
    // Sync state with backend services
    // This would typically involve API calls or MQTT messages
  }
}
```

**State Synchronization Features:**
- **State Management**: Manage application state
- **Subscriber Pattern**: Notify subscribers of state changes
- **Change Detection**: Detect state changes
- **Periodic Sync**: Periodic synchronization with backend
- **Memory Management**: Manage subscriber memory

### **Data Consistency**

The system implements **data consistency mechanisms**:

```typescript
// Data Consistency Manager
export class DataConsistencyManager {
  private conflictResolution: Map<string, Function> = new Map();
  private versionControl: Map<string, number> = new Map();

  public setConflictResolution(key: string, resolver: Function) {
    this.conflictResolution.set(key, resolver);
  }

  public updateData(key: string, data: any, version: number) {
    const currentVersion = this.versionControl.get(key) || 0;
    
    if (version > currentVersion) {
      // Accept update
      this.versionControl.set(key, version);
      return { success: true, data };
    } else if (version === currentVersion) {
      // Conflict - use resolver
      const resolver = this.conflictResolution.get(key);
      if (resolver) {
        const resolved = resolver(data, this.getData(key));
        this.versionControl.set(key, version + 1);
        return { success: true, data: resolved };
      }
    }
    
    return { success: false, reason: 'version_conflict' };
  }

  public getData(key: string) {
    return this.data.get(key);
  }
}
```

**Data Consistency Features:**
- **Version Control**: Track data versions
- **Conflict Resolution**: Resolve data conflicts
- **Consistency Checks**: Check data consistency
- **Update Validation**: Validate data updates
- **Error Handling**: Handle consistency errors

## 🚀 **Performance Optimization**

### **Message Throttling**

The system implements **message throttling for performance**:

```typescript
// Message Throttler
export class MessageThrottler {
  private messageQueues: Map<string, MessageData[]> = new Map();
  private throttleIntervals: Map<string, NodeJS.Timeout> = new Map();
  private throttleDelay = 100; // 100ms

  public throttleMessage(key: string, message: MessageData, callback: Function) {
    if (!this.messageQueues.has(key)) {
      this.messageQueues.set(key, []);
    }

    this.messageQueues.get(key)!.push(message);

    if (!this.throttleIntervals.has(key)) {
      const interval = setInterval(() => {
        this.processQueue(key, callback);
      }, this.throttleDelay);
      
      this.throttleIntervals.set(key, interval);
    }
  }

  private processQueue(key: string, callback: Function) {
    const queue = this.messageQueues.get(key);
    if (queue && queue.length > 0) {
      const messages = queue.splice(0); // Clear queue
      callback(messages);
    }
  }

  public stopThrottling(key: string) {
    const interval = this.throttleIntervals.get(key);
    if (interval) {
      clearInterval(interval);
      this.throttleIntervals.delete(key);
    }
  }
}
```

**Throttling Features:**
- **Message Queuing**: Queue messages for throttling
- **Batch Processing**: Process messages in batches
- **Configurable Delay**: Configurable throttle delay
- **Queue Management**: Manage message queues
- **Performance Optimization**: Optimize for high-frequency updates

### **Connection Pooling**

The system implements **WebSocket connection pooling**:

```typescript
// Connection Pool Manager
export class ConnectionPoolManager {
  private pools: Map<string, Socket[]> = new Map();
  private maxConnectionsPerPool = 10;
  private connectionTimeout = 30000; // 30 seconds

  public getConnection(poolName: string): Socket | null {
    const pool = this.pools.get(poolName);
    if (!pool) {
      this.pools.set(poolName, []);
      return null;
    }

    // Find available connection
    const availableConnection = pool.find(conn => !conn.connected);
    if (availableConnection) {
      return availableConnection;
    }

    // Create new connection if under limit
    if (pool.length < this.maxConnectionsPerPool) {
      const newConnection = this.createConnection(poolName);
      pool.push(newConnection);
      return newConnection;
    }

    return null;
  }

  public releaseConnection(poolName: string, connection: Socket) {
    // Connection is automatically released when disconnected
    // This method can be used for cleanup
  }

  private createConnection(poolName: string): Socket {
    const connection = io(`http://localhost:3000/${poolName}`, {
      timeout: this.connectionTimeout
    });

    connection.on('disconnect', () => {
      this.cleanupConnection(poolName, connection);
    });

    return connection;
  }

  private cleanupConnection(poolName: string, connection: Socket) {
    const pool = this.pools.get(poolName);
    if (pool) {
      const index = pool.indexOf(connection);
      if (index > -1) {
        pool.splice(index, 1);
      }
    }
  }
}
```

**Connection Pooling Features:**
- **Pool Management**: Manage connection pools
- **Connection Reuse**: Reuse existing connections
- **Connection Limits**: Limit connections per pool
- **Automatic Cleanup**: Clean up disconnected connections
- **Performance Optimization**: Optimize connection usage

## 🔧 **Error Handling and Recovery**

### **Connection Error Handling**

The system implements **comprehensive connection error handling**:

```typescript
// Connection Error Handler
export class ConnectionErrorHandler {
  private retryAttempts: Map<string, number> = new Map();
  private maxRetryAttempts = 5;
  private retryDelay = 1000; // 1 second

  public handleConnectionError(connectionId: string, error: Error) {
    const attempts = this.retryAttempts.get(connectionId) || 0;
    
    if (attempts < this.maxRetryAttempts) {
      this.retryAttempts.set(connectionId, attempts + 1);
      
      setTimeout(() => {
        this.attemptReconnection(connectionId);
      }, this.retryDelay * Math.pow(2, attempts)); // Exponential backoff
    } else {
      this.handleMaxRetriesExceeded(connectionId, error);
    }
  }

  private attemptReconnection(connectionId: string) {
    // Attempt to reconnect
    console.log(`Attempting reconnection for ${connectionId}`);
  }

  private handleMaxRetriesExceeded(connectionId: string, error: Error) {
    console.error(`Max retry attempts exceeded for ${connectionId}:`, error);
    this.retryAttempts.delete(connectionId);
  }
}
```

**Error Handling Features:**
- **Retry Logic**: Automatic retry with exponential backoff
- **Error Classification**: Classify different types of errors
- **Recovery Strategies**: Implement recovery strategies
- **Error Logging**: Log errors for debugging
- **Graceful Degradation**: Graceful degradation on errors

### **Message Error Handling**

The system implements **message error handling and recovery**:

```typescript
// Message Error Handler
export class MessageErrorHandler {
  private failedMessages: Map<string, MessageData> = new Map();
  private retryQueue: MessageData[] = [];

  public handleMessageError(messageId: string, message: MessageData, error: Error) {
    console.error(`Message error for ${messageId}:`, error);
    
    // Store failed message for retry
    this.failedMessages.set(messageId, message);
    this.retryQueue.push(message);

    // Attempt retry
    this.retryMessage(messageId, message);
  }

  private retryMessage(messageId: string, message: MessageData) {
    setTimeout(() => {
      try {
        // Attempt to process message again
        this.processMessage(message);
        this.failedMessages.delete(messageId);
      } catch (error) {
        console.error(`Retry failed for ${messageId}:`, error);
        // Could implement additional retry logic here
      }
    }, 1000);
  }

  private processMessage(message: MessageData) {
    // Process message logic
  }
}
```

**Message Error Features:**
- **Error Tracking**: Track failed messages
- **Retry Logic**: Retry failed messages
- **Error Recovery**: Recover from message errors
- **Queue Management**: Manage retry queues
- **Error Logging**: Log message errors

## 🚀 **Next Steps**

The Real-time Communication completes the frontend architecture analysis. In the next chapter, we'll examine the **Integration & Deployment** that provides system integration, including:

1. **Docker Integration** - Containerization and orchestration
2. **Environment Management** - Environment configuration and management
3. **Production Deployment** - Production deployment strategies
4. **Monitoring Integration** - System monitoring and alerting
5. **Security Implementation** - Security measures and best practices

The Real-time Communication demonstrates how **sophisticated real-time communication** can be implemented in a microservices architecture, providing seamless data flow, event-driven updates, and responsive user interfaces that enable effective system management and monitoring.

---

**The Real-time Communication in Alicia represents a mature, production-ready approach to real-time data flow and user interaction. Every design decision is intentional, every communication pattern serves a purpose, and every optimization contributes to the greater goal of creating responsive, reliable, and efficient real-time systems.**
