/**
 * Health Check Caching Middleware
 * Optimizes health monitoring by caching results and reducing redundant checks
 */

class HealthCache {
  constructor(cacheTTL = 30000) { // 30 seconds default TTL
    this.cache = new Map();
    this.cacheTTL = cacheTTL;
    this.stats = {
      hits: 0,
      misses: 0,
      evictions: 0,
      totalRequests: 0
    };
  }

  // Get cached health data
  get(serviceId) {
    this.stats.totalRequests++;

    const cached = this.cache.get(serviceId);
    if (!cached) {
      this.stats.misses++;
      return null;
    }

    const now = Date.now();
    if (now - cached.timestamp > this.cacheTTL) {
      // Cache expired
      this.cache.delete(serviceId);
      this.stats.evictions++;
      this.stats.misses++;
      return null;
    }

    this.stats.hits++;
    return cached.data;
  }

  // Set cached health data
  set(serviceId, data) {
    this.cache.set(serviceId, {
      data,
      timestamp: Date.now()
    });

    // Clean up expired entries periodically
    if (this.cache.size > 100) {
      this.cleanup();
    }
  }

  // Clean up expired cache entries
  cleanup() {
    const now = Date.now();
    let evicted = 0;

    for (const [key, value] of this.cache.entries()) {
      if (now - value.timestamp > this.cacheTTL) {
        this.cache.delete(key);
        evicted++;
      }
    }

    this.stats.evictions += evicted;
  }

  // Get cache statistics
  getStats() {
    const hitRate = this.stats.totalRequests > 0
      ? (this.stats.hits / this.stats.totalRequests * 100).toFixed(2)
      : '0.00';

    return {
      ...this.stats,
      hitRate: `${hitRate}%`,
      cacheSize: this.cache.size,
      cacheTTL: this.cacheTTL
    };
  }

  // Clear all cache
  clear() {
    this.cache.clear();
    this.stats = {
      hits: 0,
      misses: 0,
      evictions: 0,
      totalRequests: 0
    };
  }
}

// Optimized health check function with caching
async function createCachedHealthChecker(axios, cache = new HealthCache()) {
  return async function checkServiceHealth(service) {
    const cacheKey = `${service.name}:${service.host}:${service.port}`;

    // Check cache first
    const cachedResult = cache.get(cacheKey);
    if (cachedResult) {
      return cachedResult;
    }

    // Perform actual health check
    let result;

    if (service.type === 'mqtt') {
      // For MQTT broker, check if we can connect
      result = {
        name: service.name,
        status: 'unknown', // Will be updated by MQTT client status
        timestamp: new Date().toISOString(),
        uptime: 'Checking...',
        cached: false
      };
    } else {
      try {
        const startTime = Date.now();
        const response = await axios.get(`http://${service.host}:${service.port}${service.healthEndpoint}`, {
          timeout: 5000,
          headers: {
            'User-Agent': 'Alicia-Monitor-Health-Check/1.0'
          }
        });

        const responseTime = Date.now() - startTime;

        result = {
          name: service.name,
          status: 'healthy',
          timestamp: new Date().toISOString(),
          uptime: response.data.uptime || 'Unknown',
          latency: response.headers['x-response-time'] || responseTime,
          details: response.data,
          cached: false
        };
      } catch (error) {
        result = {
          name: service.name,
          status: 'unhealthy',
          timestamp: new Date().toISOString(),
          error: error.message,
          cached: false
        };
      }
    }

    // Cache the result
    cache.set(cacheKey, result);

    return result;
  };
}

// Health check batch processor for multiple services
async function createBatchHealthChecker(axios, cache = new HealthCache(), concurrency = 5) {
  return async function checkServicesBatch(services) {
    const results = [];
    const batches = [];

    // Split services into batches
    for (let i = 0; i < services.length; i += concurrency) {
      batches.push(services.slice(i, i + concurrency));
    }

    // Process batches sequentially to avoid overwhelming services
    for (const batch of batches) {
      const batchPromises = batch.map(service => {
        const cacheKey = `${service.name}:${service.host}:${service.port}`;

        // Check cache first
        const cached = cache.get(cacheKey);
        if (cached) {
          return Promise.resolve(cached);
        }

        // Perform health check
        return checkServiceHealth(service, axios, cache);
      });

      const batchResults = await Promise.allSettled(batchPromises);
      results.push(...batchResults.map(result =>
        result.status === 'fulfilled' ? result.value : null
      ).filter(Boolean));
    }

    return results;
  };
}

// Individual health check with caching
async function checkServiceHealth(service, axios, cache) {
  const cacheKey = `${service.name}:${service.host}:${service.port}`;

  try {
    const startTime = Date.now();
    const response = await axios.get(`http://${service.host}:${service.port}${service.healthEndpoint}`, {
      timeout: 5000,
      headers: {
        'User-Agent': 'Alicia-Monitor-Health-Check/1.0'
      }
    });

    const responseTime = Date.now() - startTime;

    const result = {
      name: service.name,
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: response.data.uptime || 'Unknown',
      latency: response.headers['x-response-time'] || responseTime,
      details: response.data,
      cached: false
    };

    cache.set(cacheKey, result);
    return result;

  } catch (error) {
    const result = {
      name: service.name,
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error.message,
      cached: false
    };

    cache.set(cacheKey, result);
    return result;
  }
}

module.exports = {
  HealthCache,
  createCachedHealthChecker,
  createBatchHealthChecker
};
