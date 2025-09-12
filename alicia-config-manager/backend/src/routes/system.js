import express from 'express';

const router = express.Router();

// Error handling middleware
router.use((req, res, next) => {
  if (!req.mqttService) {
    return res.status(500).json({ error: 'MQTT service not available' });
  }
  next();
});

// Get MQTT status and info
router.get('/mqtt', async (req, res) => {
  try {
    const status = {
      connected: req.mqttService.isConnected,
      broker_url: process.env.MQTT_BROKER + ':' + process.env.MQTT_PORT,
      topics: [
        'alicia/system/health/#',
        'alicia/system/discovery/#',
        'alicia/config/#',
        'alicia/device/#'
      ]
    };
    res.json(status);
  } catch (error) {
    res.status(500).json({ error: 'Failed to get MQTT status' });
  }
});

// Publish test message to MQTT
router.post('/mqtt/publish', async (req, res) => {
  try {
    const { topic, message } = req.body;

    if (!topic || !message) {
      return res.status(400).json({ error: 'Topic and message are required' });
    }

    const success = req.mqttService.publish(topic, message);

    if (success) {
      res.json({ status: 'Published successfully' });
    } else {
      res.status(500).json({ error: 'Failed to publish message - MQTT not connected' });
    }
  } catch (error) {
    res.status(500).json({ error: 'Failed to publish message' });
  }
});

// Get system info
router.get('/info', async (req, res) => {
  try {
    const info = {
      version: process.env.npm_package_version || '1.0.0',
      node_version: process.version,
      environment: process.env.NODE_ENV || 'development',
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      timestamp: new Date().toISOString()
    };
    res.json(info);
  } catch (error) {
    res.status(500).json({ error: 'Failed to get system info' });
  }
});

export default (mqttService) => {
  // Middleware to inject services
  router.use((req, res, next) => {
    req.mqttService = mqttService;
    next();
  });

  return router;
};
