import express from 'express';

const router = express.Router();

// Error handling middleware
router.use((req, res, next) => {
  if (!req.configService || !req.mqttService) {
    return res.status(500).json({ error: 'Service not available' });
  }
  next();
});

// Get all configurations
router.get('/', async (req, res) => {
  try {
    const configs = req.configService.getAllConfigs();
    res.json(configs);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch configurations' });
  }
});

// Get specific configuration
router.get('/:serviceName', async (req, res) => {
  try {
    const config = req.configService.getConfig(req.params.serviceName);
    if (!config) {
      return res.status(404).json({ error: 'Configuration not found' });
    }
    res.json(config);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch configuration' });
  }
});

// Update configuration
router.put('/:serviceName', async (req, res) => {
  try {
    const updatedConfig = await req.configService.updateConfig(req.params.serviceName, req.body);

    // Publish MQTT message about config update
    if (req.mqttService) {
      req.mqttService.publish(`alicia/config/updated`, {
        service_name: req.params.serviceName,
        timestamp: new Date().toISOString(),
        config: updatedConfig
      });
    }

    res.json(updatedConfig);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Create new configuration
router.post('/', async (req, res) => {
  try {
    const newConfig = await req.configService.updateConfig(req.body.service_name, req.body);

    // Publish MQTT message about new config
    if (req.mqttService) {
      req.mqttService.publish(`alicia/config/created`, {
        service_name: req.body.service_name,
        timestamp: new Date().toISOString(),
        config: newConfig
      });
    }

    res.status(201).json(newConfig);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

export default (configService, mqttService) => {
  // Middleware to inject services
  router.use((req, res, next) => {
    req.configService = configService;
    req.mqttService = mqttService;
    next();
  });

  return router;
};
