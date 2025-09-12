import fs from 'fs-extra';
import path from 'path';
import Joi from 'joi';
import { logger } from '../utils/logger.js';

const CONFIG_SCHEMA = Joi.object({
  service_name: Joi.string().required(),
  service_type: Joi.string().valid('stt', 'tts', 'llm', 'device_control', 'voice_router').required(),
  status: Joi.string().valid('healthy', 'unhealthy', 'unknown').required(),
  enabled: Joi.boolean().required(),
  version: Joi.string().required(),
  last_updated: Joi.string().isoDate().required(),
  config: Joi.object({
    api_key: Joi.string().optional(),
    provider: Joi.string().optional(),
    model: Joi.string().optional(),
    voice: Joi.string().optional(),
    language: Joi.string().optional(),
    endpoints: Joi.array().items(Joi.object({
      type: Joi.string().required(),
      model: Joi.string().optional(),
      ip: Joi.string().required(),
      port: Joi.number().optional(),
      protocol: Joi.string().valid('http', 'https', 'tcp', 'udp').optional()
    })).required(),
    settings: Joi.object().optional()
  }).required()
});

export class ConfigService {
  constructor(logger) {
    this.logger = logger;
    this.configPath = path.join(process.env.CONFIG_PATH || './config', 'config.json');
    this.configs = new Map();
    this.isReady = false;
  }

  async initialize() {
    try {
      await this.loadConfigs();
      this.isReady = true;
      this.logger.info('Config service initialized successfully');
    } catch (error) {
      this.logger.error('Failed to initialize config service:', error);
      throw error;
    }
  }

  async loadConfigs() {
    try {
      if (await fs.pathExists(this.configPath)) {
        const data = await fs.readJson(this.configPath);
        this.configs = new Map(Object.entries(data));
        this.logger.info(`Loaded ${this.configs.size} configurations`);
      } else {
        await this.createDefaultConfig();
      }
    } catch (error) {
      this.logger.error('Error loading configurations:', error);
      throw error;
    }
  }

  async createDefaultConfig() {
    const defaultConfigs = {
      'whisper-service': {
        service_name: 'whisper-service',
        service_type: 'stt',
        status: 'unknown',
        enabled: true,
        version: '1.0.0',
        last_updated: new Date().toISOString(),
        config: {
          api_key: '',
          provider: 'openai',
          model: 'whisper-1',
          language: 'en',
          endpoints: [{
            type: 'stt',
            model: 'whisper-1',
            ip: 'http://whisper:8001',
            port: 8001,
            protocol: 'http'
          }],
          settings: {
            temperature: 0.0,
            max_tokens: 1000,
            timeout: 30
          }
        }
      }
    };

    await this.saveConfigs(defaultConfigs);
    this.logger.info('Created default configuration file');
  }

  async saveConfigs(configs) {
    try {
      await fs.ensureDir(path.dirname(this.configPath));
      await fs.writeJson(this.configPath, configs, { spaces: 2 });
      this.logger.info('Configurations saved successfully');
    } catch (error) {
      this.logger.error('Error saving configurations:', error);
      throw error;
    }
  }

  getAllConfigs() {
    return Object.fromEntries(this.configs);
  }

  getConfig(serviceName) {
    return this.configs.get(serviceName) || null;
  }

  async updateConfig(serviceName, config) {
    try {
      const { error, value } = CONFIG_SCHEMA.validate(config);
      if (error) {
        throw new Error(`Configuration validation failed: ${error.details[0].message}`);
      }

      this.configs.set(serviceName, value);
      await this.saveConfigs(this.getAllConfigs());

      this.logger.info(`Configuration updated for ${serviceName}`);
      return value;
    } catch (error) {
      this.logger.error(`Error updating configuration for ${serviceName}:`, error);
      throw error;
    }
  }

  isReady() {
    return this.isReady;
  }
}
