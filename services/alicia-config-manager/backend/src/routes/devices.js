import express from 'express';

const router = express.Router();

// Error handling middleware
router.use((req, res, next) => {
  if (!req.deviceService || !req.mqttService) {
    return res.status(500).json({ error: 'Service not available' });
  }
  next();
});

// Get all devices
router.get('/', async (req, res) => {
  try {
    const devices = req.deviceService.getAllDevices();
    res.json(devices);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch devices' });
  }
});

// Get specific device
router.get('/:deviceId', async (req, res) => {
  try {
    const device = req.deviceService.getDevice(req.params.deviceId);
    if (!device) {
      return res.status(404).json({ error: 'Device not found' });
    }
    res.json(device);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch device' });
  }
});

// Update device
router.put('/:deviceId', async (req, res) => {
  try {
    const updatedDevice = await req.deviceService.updateDevice(req.params.deviceId, req.body);

    // Publish MQTT message about device update
    if (req.mqttService) {
      req.mqttService.publish(`alicia/device/updated`, {
        device_id: req.params.deviceId,
        timestamp: new Date().toISOString(),
        device: updatedDevice
      });
    }

    res.json(updatedDevice);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Add new device
router.post('/', async (req, res) => {
  try {
    const newDevice = await req.deviceService.addDevice(req.body);

    // Publish MQTT message about new device
    if (req.mqttService) {
      req.mqttService.publish(`alicia/device/added`, {
        device_id: req.body.device_id,
        timestamp: new Date().toISOString(),
        device: newDevice
      });
    }

    res.status(201).json(newDevice);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Remove device
router.delete('/:deviceId', async (req, res) => {
  try {
    await req.deviceService.removeDevice(req.params.deviceId);

    // Publish MQTT message about device removal
    if (req.mqttService) {
      req.mqttService.publish(`alicia/device/removed`, {
        device_id: req.params.deviceId,
        timestamp: new Date().toISOString()
      });
    }

    res.status(204).send();
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

export default (deviceService, mqttService) => {
  // Middleware to inject services
  router.use((req, res, next) => {
    req.deviceService = deviceService;
    req.mqttService = mqttService;
    next();
  });

  return router;
};
