import express from 'express';
import { logger } from '../utils/logger.js';

const router = express.Router();

// Middleware to inject envConfig service
router.use((req, res, next) => {
  req.envConfigService = req.app.get('envConfigService');
  next();
});

// GET /api/env - Get all environment variables (masked)
router.get('/', async (req, res) => {
  try {
    const envVars = req.envConfigService.getMaskedEnvVars();
    res.json({
      success: true,
      data: envVars,
      count: Object.keys(envVars).length
    });
  } catch (error) {
    logger.error('Error getting environment variables:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get environment variables'
    });
  }
});

// GET /api/env/:key - Get specific environment variable (masked)
router.get('/:key', async (req, res) => {
  try {
    const { key } = req.params;
    const value = req.envConfigService.getEnvVar(key);
    
    if (value === null) {
      return res.status(404).json({
        success: false,
        error: 'Environment variable not found'
      });
    }

    const maskedValue = req.envConfigService.getMaskedValue(key, value);
    
    res.json({
      success: true,
      data: {
        key,
        value: maskedValue,
        isSensitive: req.envConfigService.getSensitiveKeys().includes(key)
      }
    });
  } catch (error) {
    logger.error(`Error getting environment variable ${req.params.key}:`, error);
    res.status(500).json({
      success: false,
      error: 'Failed to get environment variable'
    });
  }
});

// PUT /api/env/:key - Update specific environment variable
router.put('/:key', async (req, res) => {
  try {
    const { key } = req.params;
    const { value } = req.body;

    if (value === undefined || value === null) {
      return res.status(400).json({
        success: false,
        error: 'Value is required'
      });
    }

    // Create backup before updating
    await req.envConfigService.backupEnvFile();

    const result = await req.envConfigService.updateEnvVar(key, value);

    // Emit update event via Socket.io
    if (req.app.get('io')) {
      req.app.get('io').emit('env:update', {
        key: result.key,
        value: req.envConfigService.getMaskedValue(key, result.value),
        isSensitive: req.envConfigService.getSensitiveKeys().includes(key)
      });
    }

    res.json({
      success: true,
      data: {
        key: result.key,
        value: req.envConfigService.getMaskedValue(key, result.value),
        isSensitive: req.envConfigService.getSensitiveKeys().includes(key)
      }
    });
  } catch (error) {
    logger.error(`Error updating environment variable ${req.params.key}:`, error);
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to update environment variable'
    });
  }
});

// PUT /api/env - Update multiple environment variables
router.put('/', async (req, res) => {
  try {
    const { updates } = req.body;

    if (!updates || typeof updates !== 'object') {
      return res.status(400).json({
        success: false,
        error: 'Updates object is required'
      });
    }

    // Create backup before updating
    await req.envConfigService.backupEnvFile();

    const results = await req.envConfigService.updateMultipleEnvVars(updates);

    // Emit update event via Socket.io
    if (req.app.get('io')) {
      const maskedResults = results.map(({ key, value }) => ({
        key,
        value: req.envConfigService.getMaskedValue(key, value),
        isSensitive: req.envConfigService.getSensitiveKeys().includes(key)
      }));
      
      req.app.get('io').emit('env:bulk-update', maskedResults);
    }

    res.json({
      success: true,
      data: results.map(({ key, value }) => ({
        key,
        value: req.envConfigService.getMaskedValue(key, value),
        isSensitive: req.envConfigService.getSensitiveKeys().includes(key)
      })),
      count: results.length
    });
  } catch (error) {
    logger.error('Error updating multiple environment variables:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to update environment variables'
    });
  }
});

// POST /api/env/backup - Create backup of current .env file
router.post('/backup', async (req, res) => {
  try {
    const backupPath = await req.envConfigService.backupEnvFile();
    
    res.json({
      success: true,
      data: {
        backupPath,
        message: 'Environment file backed up successfully'
      }
    });
  } catch (error) {
    logger.error('Error creating environment backup:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to create backup'
    });
  }
});

// POST /api/env/restore - Restore .env file from backup
router.post('/restore', async (req, res) => {
  try {
    const { backupPath } = req.body;

    if (!backupPath) {
      return res.status(400).json({
        success: false,
        error: 'Backup path is required'
      });
    }

    await req.envConfigService.restoreEnvFile(backupPath);

    // Emit restore event via Socket.io
    if (req.app.get('io')) {
      req.app.get('io').emit('env:restore', {
        message: 'Environment file restored successfully'
      });
    }

    res.json({
      success: true,
      data: {
        message: 'Environment file restored successfully'
      }
    });
  } catch (error) {
    logger.error('Error restoring environment file:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to restore environment file'
    });
  }
});

// GET /api/env/sensitive-keys - Get list of sensitive keys
router.get('/sensitive-keys', async (req, res) => {
  try {
    const sensitiveKeys = req.envConfigService.getSensitiveKeys();
    
    res.json({
      success: true,
      data: sensitiveKeys
    });
  } catch (error) {
    logger.error('Error getting sensitive keys:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get sensitive keys'
    });
  }
});

export default router;
