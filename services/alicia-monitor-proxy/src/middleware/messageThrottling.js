const rateLimit = require('express-rate-limit');

/**
 * Message Throttling Middleware for MQTT Messages
 * Prevents message flooding and optimizes real-time updates
 */

// Throttle MQTT message broadcasts to prevent overwhelming clients
const messageThrottleMiddleware = (io) => {
  let lastBroadcastTime = 0;
  const throttleInterval = 100; // Minimum 100ms between broadcasts
  let messageBuffer = [];
  const maxBufferSize = 50;

  return {
    // Throttle individual message broadcasts
    throttleMessage: (event, data) => {
      const now = Date.now();
      if (now - lastBroadcastTime >= throttleInterval) {
        io.emit(event, data);
        lastBroadcastTime = now;
        return true;
      }
      return false;
    },

    // Buffer messages for batched updates
    bufferMessage: (event, data) => {
      messageBuffer.push({ event, data, timestamp: Date.now() });

      // Keep buffer size manageable
      if (messageBuffer.length > maxBufferSize) {
        messageBuffer = messageBuffer.slice(-maxBufferSize);
      }

      // Broadcast buffered messages in batches
      const now = Date.now();
      if (now - lastBroadcastTime >= throttleInterval * 5) { // 500ms for batches
        if (messageBuffer.length > 0) {
          io.emit('batch_update', messageBuffer);
          messageBuffer = [];
          lastBroadcastTime = now;
        }
      }
    },

    // Force broadcast (for critical messages)
    forceBroadcast: (event, data) => {
      io.emit(event, data);
      lastBroadcastTime = Date.now();
    },

    // Get buffer status
    getBufferStatus: () => ({
      size: messageBuffer.length,
      maxSize: maxBufferSize,
      lastBroadcast: lastBroadcastTime
    })
  };
};

// Socket.IO rate limiting for individual clients
const createSocketRateLimit = (io) => {
  const clientLimits = new Map();

  return (socket) => {
    const clientId = socket.id;
    const now = Date.now();

    // Initialize client tracking
    if (!clientLimits.has(clientId)) {
      clientLimits.set(clientId, {
        messageCount: 0,
        windowStart: now,
        blocked: false
      });
    }

    const clientData = clientLimits.get(clientId);

    // Reset window if needed (1 minute window)
    if (now - clientData.windowStart > 60000) {
      clientData.messageCount = 0;
      clientData.windowStart = now;
      clientData.blocked = false;
    }

    // Check rate limit (100 messages per minute)
    if (clientData.messageCount >= 100) {
      if (!clientData.blocked) {
        clientData.blocked = true;
        socket.emit('rate_limited', {
          message: 'Too many messages. Please slow down.',
          retryAfter: 60000 - (now - clientData.windowStart)
        });
      }
      return false; // Block message
    }

    clientData.messageCount++;
    return true; // Allow message
  };
};

// MQTT message debouncing to prevent duplicate rapid messages
const createMessageDebouncer = (io) => {
  const messageCache = new Map();
  const debounceTime = 500; // 500ms debounce

  return (topic, message) => {
    const cacheKey = `${topic}:${JSON.stringify(message)}`;
    const now = Date.now();

    if (messageCache.has(cacheKey)) {
      const lastTime = messageCache.get(cacheKey);
      if (now - lastTime < debounceTime) {
        return false; // Debounce duplicate
      }
    }

    messageCache.set(cacheKey, now);

    // Clean up old entries (keep cache small)
    for (const [key, time] of messageCache.entries()) {
      if (now - time > debounceTime * 2) {
        messageCache.delete(key);
      }
    }

    return true; // Allow message
  };
};

module.exports = {
  messageThrottleMiddleware,
  createSocketRateLimit,
  createMessageDebouncer
};
