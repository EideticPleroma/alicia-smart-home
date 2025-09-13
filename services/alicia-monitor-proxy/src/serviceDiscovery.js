const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

class ServiceDiscovery {
  constructor() {
    this.services = [];
    this.dockerComposePath = path.join(__dirname, '../../docker-compose.bus.yml');
  }

  // Parse docker-compose.bus.yml to discover services
  async discoverServices() {
    try {
      console.log('Discovering services from docker-compose.bus.yml...');

      if (!fs.existsSync(this.dockerComposePath)) {
        console.warn('docker-compose.bus.yml not found, using default services');
        return this.getDefaultServices();
      }

      const fileContents = fs.readFileSync(this.dockerComposePath, 'utf8');
      const dockerCompose = yaml.load(fileContents);

      if (!dockerCompose.services) {
        console.warn('No services found in docker-compose file');
        return this.getDefaultServices();
      }

      const discoveredServices = [];

      for (const [serviceName, serviceConfig] of Object.entries(dockerCompose.services)) {
        if (serviceName.startsWith('alicia-')) {
          const service = this.parseServiceConfig(serviceName, serviceConfig);
          if (service) {
            discoveredServices.push(service);
          }
        }
      }

      console.log(`Discovered ${discoveredServices.length} services`);
      this.services = discoveredServices;
      return this.services;

    } catch (error) {
      console.error('Error discovering services:', error);
      return this.getDefaultServices();
    }
  }

  // Parse individual service configuration
  parseServiceConfig(serviceName, serviceConfig) {
    try {
      // Extract port from ports array
      let port = null;
      let healthEndpoint = '/health';

      if (serviceConfig.ports && serviceConfig.ports.length > 0) {
        // Extract port number from "8081:8081" format
        const portMapping = serviceConfig.ports[0];
        if (typeof portMapping === 'string') {
          const parts = portMapping.split(':');
          port = parseInt(parts[0]);
        }
      }

      // Determine service type based on name
      let type = 'http';
      if (serviceName === 'alicia-bus-core') {
        type = 'mqtt';
        healthEndpoint = null;
      }

      // Extract environment variables for additional config
      let mqttConfig = {};
      if (serviceConfig.environment) {
        const envVars = Array.isArray(serviceConfig.environment)
          ? serviceConfig.environment
          : Object.entries(serviceConfig.environment).map(([key, value]) => `${key}=${value}`);

        mqttConfig = this.extractMQTTConfig(envVars);
      }

      return {
        name: serviceName,
        host: 'localhost',
        port: port,
        type: type,
        healthEndpoint: healthEndpoint,
        mqttConfig: mqttConfig,
        discovered: true,
        lastSeen: new Date().toISOString()
      };

    } catch (error) {
      console.error(`Error parsing service ${serviceName}:`, error);
      return null;
    }
  }

  // Extract MQTT configuration from environment variables
  extractMQTTConfig(envVars) {
    const config = {};

    envVars.forEach(envVar => {
      if (typeof envVar === 'string') {
        const [key, value] = envVar.split('=');
        if (key && value) {
          if (key.startsWith('MQTT_')) {
            config[key] = value;
          }
        }
      }
    });

    return config;
  }

  // Get default services when discovery fails
  getDefaultServices() {
    console.log('Using default service configuration');
    return [
      {
        name: 'alicia-bus-core',
        host: 'localhost',
        port: 1883,
        type: 'mqtt',
        healthEndpoint: null,
        discovered: false
      },
      {
        name: 'alicia-health-monitor',
        host: 'localhost',
        port: 8083,
        type: 'http',
        healthEndpoint: '/health',
        discovered: false
      },
      {
        name: 'alicia-device-registry',
        host: 'localhost',
        port: 8081,
        type: 'http',
        healthEndpoint: '/health',
        discovered: false
      },
      {
        name: 'alicia-stt-service',
        host: 'localhost',
        port: 8001,
        type: 'http',
        healthEndpoint: '/health',
        discovered: false
      },
      {
        name: 'alicia-ai-service',
        host: 'localhost',
        port: 8002,
        type: 'http',
        healthEndpoint: '/health',
        discovered: false
      },
      {
        name: 'alicia-tts-service',
        host: 'localhost',
        port: 8003,
        type: 'http',
        healthEndpoint: '/health',
        discovered: false
      }
    ];
  }

  // Get all discovered services
  getServices() {
    return this.services;
  }

  // Get service by name
  getServiceByName(name) {
    return this.services.find(service => service.name === name);
  }

  // Update service last seen timestamp
  updateServiceLastSeen(name) {
    const service = this.getServiceByName(name);
    if (service) {
      service.lastSeen = new Date().toISOString();
    }
  }

  // Get service health summary
  getHealthSummary() {
    const summary = {
      total: this.services.length,
      healthy: 0,
      unhealthy: 0,
      unknown: 0,
      discovered: 0
    };

    this.services.forEach(service => {
      if (service.discovered) summary.discovered++;
      // Health status will be determined by health checker
    });

    return summary;
  }
}

module.exports = ServiceDiscovery;
