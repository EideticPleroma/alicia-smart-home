import fs from 'fs-extra';
import path from 'path';
import { validateDevice } from '../utils/validation.js';
import { logger } from '../utils/logger.js';

export class DeviceService {
  constructor(logger) {
    this.logger = logger;
    this.devicePath = path.join(process.env.CONFIG_PATH || './config', 'devices.json');
    this.devices = new Map();
    this.isReady = false;
  }

  async initialize() {
    try {
      await this.loadDevices();
      this.isReady = true;
      this.logger.info('Device service initialized successfully');
    } catch (error) {
      this.logger.error('Failed to initialize device service:', error);
      throw error;
    }
  }

  async loadDevices() {
    try {
      if (await fs.pathExists(this.devicePath)) {
        const data = await fs.readJson(this.devicePath);
        this.devices = new Map();
        data.devices.forEach(device => {
          this.devices.set(device.device_id, device);
        });
        this.logger.info(`Loaded ${this.devices.size} devices`);
      } else {
        await this.createDefaultDevices();
      }
    } catch (error) {
      this.logger.error('Error loading devices:', error);
      throw error;
    }
  }

  async createDefaultDevices() {
    const defaultDevices = {
      devices: [
        {
          device_id: 'sonos_living_room',
          device_name: 'Sonos Living Room',
          device_type: 'hardware',
          status: 'online',
          last_seen: new Date().toISOString(),
          connection: {
            host: '192.168.1.100',
            port: 1400,
            protocol: 'http',
            authentication: {
              type: 'basic',
              credentials: {
                username: 'admin',
                password: 'password'
              }
            }
          },
          capabilities: ['play', 'pause', 'volume'],
          metadata: {
            manufacturer: 'Sonos',
            model: 'One',
            ip_address: '192.168.1.100'
          }
        },
        {
          device_id: 'tv_main',
          device_name: 'Main TV',
          device_type: 'hardware',
          status: 'online',
          last_seen: new Date().toISOString(),
          connection: {
            host: '192.168.1.101',
            port: 8000,
            protocol: 'http',
            authentication: {
              type: 'api_key',
              credentials: {
                api_key: 'tv-api-key-123'
              }
            }
          },
          capabilities: ['power', 'volume', 'input'],
          metadata: {
            manufacturer: 'Samsung',
            model: 'Q900',
            ip_address: '192.168.1.101'
          }
        }
      ]
    };

    await this.saveDevices(defaultDevices);
    this.logger.info('Created default devices file');
  }

  async saveDevices(devicesData) {
    try {
      await fs.ensureDir(path.dirname(this.devicePath));
      await fs.writeJson(this.devicePath, devicesData, { spaces: 2 });
      this.logger.info('Devices saved successfully');
    } catch (error) {
      this.logger.error('Error saving devices:', error);
      throw error;
    }
  }

  getAllDevices() {
    return Array.from(this.devices.values());
  }

  getDevice(deviceId) {
    return this.devices.get(deviceId) || null;
  }

  async updateDevice(deviceId, deviceData) {
    try {
      const { error, value } = validateDevice(deviceData);
      if (error) {
        throw new Error(`Device validation failed: ${error.details[0].message}`);
      }

      this.devices.set(deviceId, value);
      const devicesData = { devices: this.getAllDevices() };
      await this.saveDevices(devicesData);

      this.logger.info(`Device updated: ${deviceId}`);
      return value;
    } catch (error) {
      this.logger.error(`Error updating device ${deviceId}:`, error);
      throw error;
    }
  }

  async addDevice(deviceData) {
    try {
      if (this.devices.has(deviceData.device_id)) {
        throw new Error(`Device with id ${deviceData.device_id} already exists`);
      }
      return await this.updateDevice(deviceData.device_id, deviceData);
    } catch (error) {
      this.logger.error(`Error adding device ${deviceData.device_id}:`, error);
      throw error;
    }
  }

  async removeDevice(deviceId) {
    try {
      if (!this.devices.has(deviceId)) {
        throw new Error(`Device with id ${deviceId} not found`);
      }

      this.devices.delete(deviceId);
      const devicesData = { devices: this.getAllDevices() };
      await this.saveDevices(devicesData);

      this.logger.info(`Device removed: ${deviceId}`);
      return true;
    } catch (error) {
      this.logger.error(`Error removing device ${deviceId}:`, error);
      throw error;
    }
  }

  isReady() {
    return this.isReady;
  }
}
