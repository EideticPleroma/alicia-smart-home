# MQTT Disconnection Code 7 Fixes - Implementation Summary

## Problem Analysis
The MQTT broker was disconnecting with code 7 (`MOSQ_ERR_CONN_LOST`) before the speak receives the payload. This was caused by:

1. **Client ID conflicts** - Multiple instances using same client ID
2. **Connection instability** - Poor connection management and retry logic
3. **Network configuration issues** - Docker networking problems
4. **Message frequency** - Too frequent status updates overwhelming connection
5. **Missing QoS handling** - No proper message delivery guarantees

## Implemented Fixes

### 1. Client ID Management ✅
**File**: `mqtt-testing/scripts/sonos-mqtt-bridge.py`
- **Change**: Generate unique client IDs using UUID
- **Before**: `CLIENT_ID = "sonos_bridge"`
- **After**: `CLIENT_ID = f"sonos_bridge_{uuid.uuid4().hex[:8]}"`
- **Impact**: Prevents client ID conflicts that cause broker to close old connections

### 2. Connection Stability Improvements ✅
**File**: `mqtt-testing/scripts/sonos-mqtt-bridge.py`
- **Changes**:
  - Increased keepalive from 60 to 120 seconds
  - Changed `clean_session` from `True` to `False` for persistent sessions
  - Added connection state tracking (`self.is_connected`)
  - Implemented exponential backoff retry logic
  - Added connection monitoring and heartbeat tracking

### 3. Error Handling for Code 7 ✅
**File**: `mqtt-testing/scripts/sonos-mqtt-bridge.py`
- **Changes**:
  - Specific handling for disconnection code 7
  - Exponential backoff reconnection strategy
  - Separate thread for delayed reconnection
  - Maximum retry attempt limits
  - Detailed logging for debugging

### 4. Message Publishing Optimization ✅
**File**: `mqtt-testing/scripts/sonos-mqtt-bridge.py`
- **Changes**:
  - Reduced status update frequency from 30s to 60s
  - Added QoS 1 for all important messages
  - Implemented `_publish_with_qos()` method with error handling
  - Added connection state checks before publishing
  - Improved message queuing limits

### 5. Docker Configuration Improvements ✅
**File**: `docker-compose.sonos-fixed.yml`
- **Changes**:
  - Added health check for sonos-bridge container
  - Improved dependency management with health conditions
  - Better service startup ordering

### 6. MQTT Broker Configuration ✅
**File**: `mqtt/config/mosquitto.conf`
- **Changes**:
  - Added `keepalive_interval 60`
  - Improved logging with timestamps
  - Better connection timeout settings
  - Enhanced persistence configuration

## Key Technical Improvements

### Connection Management
```python
# Before: Basic connection with immediate retry
self.client.keepalive = 60
self.client.clean_session = True

# After: Robust connection with monitoring
self.client.keepalive = 120
self.client.clean_session = False
self.client.max_inflight_messages_set(20)
self.client.max_queued_messages_set(100)
```

### Error Code 7 Handling
```python
def on_disconnect(self, client, userdata, rc):
    if rc == 7:  # Connection lost
        logger.warning("Connection lost (code 7), implementing reconnection strategy...")
        self._handle_connection_lost()
```

### Message Publishing with QoS
```python
def _publish_with_qos(self, topic, payload, qos=1, retain=False):
    if not self.is_connected:
        logger.warning(f"Cannot publish to {topic}: not connected")
        return False
    result = self.client.publish(topic, payload, qos=qos, retain=retain)
    return result.rc == mqtt.MQTT_ERR_SUCCESS
```

## Testing

### Test Script
Created `test_mqtt_stability.py` to verify fixes:
- Tests connection stability for 5 minutes
- Monitors for disconnection code 7
- Tracks message delivery success
- Provides detailed logging and results

### Expected Results
- ✅ No disconnection code 7 errors
- ✅ Stable MQTT connections
- ✅ Reliable message delivery
- ✅ Proper reconnection handling
- ✅ Reduced connection churn

## Deployment Instructions

1. **Update the Sonos Bridge**:
   ```bash
   docker-compose -f docker-compose.sonos-fixed.yml down
   docker-compose -f docker-compose.sonos-fixed.yml up -d
   ```

2. **Test the fixes**:
   ```bash
   python test_mqtt_stability.py
   ```

3. **Monitor logs**:
   ```bash
   docker logs alicia_sonos_bridge -f
   ```

## Monitoring

### Key Metrics to Watch
- Connection stability (no code 7 disconnections)
- Message delivery success rate
- Reconnection frequency
- Status update intervals

### Log Patterns to Look For
- ✅ `"Connected to MQTT broker successfully"`
- ✅ `"Published to {topic} with QoS 1"`
- ❌ `"Unexpected disconnection from MQTT broker: 7"` (should be rare)
- ⚠️ `"Connection lost (code 7), implementing reconnection strategy..."` (should recover)

## Expected Impact

1. **Elimination of Code 7 Disconnections**: The specific error code 7 should be eliminated through better connection management
2. **Improved Reliability**: TTS messages should be delivered consistently
3. **Better Error Recovery**: Automatic reconnection with exponential backoff
4. **Reduced Network Load**: Less frequent status updates and better message queuing
5. **Enhanced Monitoring**: Better visibility into connection health and message flow

The fixes address the root causes of MQTT disconnection code 7 and should provide a stable, reliable connection for the Sonos MQTT bridge.
