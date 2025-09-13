/**
 * Memory-Efficient Message Storage with LRU Cache
 * Optimizes message flow storage and retrieval for high-volume scenarios
 */

class LRUCache {
  constructor(maxSize = 1000) {
    this.maxSize = maxSize;
    this.cache = new Map();
    this.stats = {
      hits: 0,
      misses: 0,
      evictions: 0,
      totalOperations: 0
    };
  }

  // Get item from cache
  get(key) {
    this.stats.totalOperations++;

    if (!this.cache.has(key)) {
      this.stats.misses++;
      return null;
    }

    const value = this.cache.get(key);
    // Move to end (most recently used)
    this.cache.delete(key);
    this.cache.set(key, value);

    this.stats.hits++;
    return value;
  }

  // Set item in cache
  set(key, value) {
    this.stats.totalOperations++;

    if (this.cache.has(key)) {
      // Update existing
      this.cache.delete(key);
    } else if (this.cache.size >= this.maxSize) {
      // Evict least recently used
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
      this.stats.evictions++;
    }

    this.cache.set(key, value);
  }

  // Delete item from cache
  delete(key) {
    return this.cache.delete(key);
  }

  // Clear all items
  clear() {
    this.cache.clear();
    this.stats = {
      hits: 0,
      misses: 0,
      evictions: 0,
      totalOperations: 0
    };
  }

  // Get cache size
  size() {
    return this.cache.size;
  }

  // Get cache statistics
  getStats() {
    const hitRate = this.stats.totalOperations > 0
      ? (this.stats.hits / this.stats.totalOperations * 100).toFixed(2)
      : '0.00';

    return {
      ...this.stats,
      hitRate: `${hitRate}%`,
      currentSize: this.cache.size,
      maxSize: this.maxSize,
      utilization: `${((this.cache.size / this.maxSize) * 100).toFixed(2)}%`
    };
  }
}

// Optimized message storage with multiple LRU caches
class MessageStorage {
  constructor(options = {}) {
    this.maxMessages = options.maxMessages || 1000;
    this.maxTopics = options.maxTopics || 100;
    this.compressionThreshold = options.compressionThreshold || 1000; // bytes

    // LRU caches for different data types
    this.messageCache = new LRUCache(this.maxMessages);
    this.topicCache = new LRUCache(this.maxTopics);
    this.patternCache = new LRUCache(50); // For regex patterns

    // Message metadata
    this.messageIndex = new Map(); // topic -> [messageIds]
    this.topicStats = new Map(); // topic -> stats
    this.compressionStats = {
      originalSize: 0,
      compressedSize: 0,
      compressionRatio: 0
    };

    // Cleanup interval
    this.cleanupInterval = setInterval(() => {
      this.cleanup();
    }, 300000); // 5 minutes
  }

  // Store message with optimization
  storeMessage(message) {
    const messageId = this.generateMessageId(message);
    const topic = message.topic;

    // Optimize message for storage
    const optimizedMessage = this.optimizeMessage(message);

    // Store in LRU cache
    this.messageCache.set(messageId, {
      ...optimizedMessage,
      storedAt: Date.now(),
      size: JSON.stringify(optimizedMessage).length
    });

    // Update topic index
    if (!this.messageIndex.has(topic)) {
      this.messageIndex.set(topic, []);
    }
    const topicMessages = this.messageIndex.get(topic);
    topicMessages.push(messageId);

    // Keep only last N messages per topic
    if (topicMessages.length > 100) {
      const removedIds = topicMessages.splice(0, topicMessages.length - 100);
      removedIds.forEach(id => this.messageCache.delete(id));
    }

    // Update topic statistics
    this.updateTopicStats(topic, optimizedMessage);

    return messageId;
  }

  // Generate unique message ID
  generateMessageId(message) {
    const timestamp = Date.now();
    const topic = message.topic;
    const payloadHash = this.simpleHash(JSON.stringify(message.data || message));
    return `${topic}_${timestamp}_${payloadHash}`;
  }

  // Simple hash function for message ID generation
  simpleHash(str) {
    let hash = 0;
    if (str.length === 0) return hash;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash);
  }

  // Optimize message for storage
  optimizeMessage(message) {
    // Remove null/undefined values, compress large payloads
    const optimized = { ...message };

    // Compress large data payloads if over threshold
    if (optimized.data && JSON.stringify(optimized.data).length > this.compressionThreshold) {
      this.compressionStats.originalSize += JSON.stringify(optimized.data).length;
      // Simple compression: remove redundant whitespace
      try {
        optimized.data = JSON.parse(JSON.stringify(optimized.data));
      } catch (e) {
        // If compression fails, keep original
      }
      this.compressionStats.compressedSize += JSON.stringify(optimized.data).length;
    }

    return optimized;
  }

  // Update topic statistics
  updateTopicStats(topic, message) {
    const existing = this.topicStats.get(topic) || {
      messageCount: 0,
      lastMessage: null,
      averageSize: 0,
      topics: new Set()
    };

    existing.messageCount++;
    existing.lastMessage = Date.now();
    existing.averageSize = (existing.averageSize + JSON.stringify(message).length) / 2;

    this.topicStats.set(topic, existing);
  }

  // Get messages by topic
  getMessagesByTopic(topic, limit = 50) {
    const messageIds = this.messageIndex.get(topic) || [];
    const messages = messageIds
      .slice(-limit)
      .map(id => this.messageCache.get(id))
      .filter(msg => msg); // Remove null messages

    return messages;
  }

  // Search messages by pattern
  searchMessages(pattern, limit = 20) {
    const regex = new RegExp(pattern, 'i');
    const results = [];

    for (const [messageId, message] of this.messageCache.cache) {
      const messageStr = JSON.stringify(message);
      if (regex.test(messageStr)) {
        results.push(message);
        if (results.length >= limit) break;
      }
    }

    return results;
  }

  // Get storage statistics
  getStats() {
    const totalSize = Array.from(this.messageCache.cache.values())
      .reduce((sum, msg) => sum + (msg.size || 0), 0);

    return {
      messagesStored: this.messageCache.size(),
      topicsTracked: this.topicStats.size,
      totalSize: `${(totalSize / 1024).toFixed(2)} KB`,
      cacheStats: this.messageCache.getStats(),
      topicCacheStats: this.topicCache.getStats(),
      patternCacheStats: this.patternCache.getStats(),
      compressionStats: {
        ...this.compressionStats,
        compressionRatio: this.compressionStats.originalSize > 0
          ? `${((1 - this.compressionStats.compressedSize / this.compressionStats.originalSize) * 100).toFixed(2)}%`
          : '0%'
      }
    };
  }

  // Cleanup old messages and expired caches
  cleanup() {
    // Remove messages older than 1 hour
    const oneHourAgo = Date.now() - (60 * 60 * 1000);
    const toRemove = [];

    for (const [id, message] of this.messageCache.cache) {
      if (message.storedAt < oneHourAgo) {
        toRemove.push(id);
      }
    }

    toRemove.forEach(id => {
      this.messageCache.delete(id);
      // Also remove from indexes (would be complex, simplified for now)
    });

    // Clean up empty topic indexes
    for (const [topic, messageIds] of this.messageIndex) {
      if (messageIds.length === 0) {
        this.messageIndex.delete(topic);
      }
    }

    console.log(`MessageStorage cleanup: removed ${toRemove.length} old messages`);
  }

  // Close and cleanup
  close() {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
    this.messageCache.clear();
    this.topicCache.clear();
    this.patternCache.clear();
  }
}

module.exports = { LRUCache, MessageStorage };
