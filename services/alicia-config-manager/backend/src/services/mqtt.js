import mqtt from 'mqtt';
import { logger } from '../utils/logger.js';

export class MQTTService {
  constructor(logger) {
    this.logger = logger;
    this.client = null;
    this.isConnected = false;
    this.subscriptions = new Map();
  }

  async connect() {
    const brokerUrl = `mqtt://${process.env.MQTT_BROKER}:${process.env.MQTT_PORT}`;

    this.client = mqtt.connect(brokerUrl, {
      username: process.env.MQTT_USERNAME,
      password: process.env.MQTT_PASSWORD,
      clientId: 'alicia-config-manager',
      clean: true,
      reconnectPeriod: 5000,
      connectTimeout: 30 * 1000
    });

    this.client.on('connect', () => {
      this.isConnected = true;
      this.logger.info('Connected to MQTT broker');
      this.subscribeToTopics();
    });

    this.client.on('disconnect', () => {
      this.isConnected = false;
      this.logger.warn('Disconnected from MQTT broker');
    });

    this.client.on('error', (error) => {
      this.logger.error('MQTT connection error:', error);
    });

    this.client.on('message', (topic, message) => {
      this.handleMessage(topic, message);
    });
  }

  subscribeToTopics() {
    const topics = [
      'alicia/system/health/#',
      'alicia/system/discovery/#',
      'alicia/config/#',
      'alicia/device/#'
    ];

    topics.forEach(topic => {
      this.client.subscribe(topic, (err) => {
        if (err) {
          this.logger.error(`Failed to subscribe to ${topic}:`, err);
        } else {
          this.logger.info(`Subscribed to ${topic}`);
        }
      });
    });
  }

  handleMessage(topic, message) {
    try {
      const data = JSON.parse(message.toString());
      this.logger.debug(`MQTT message received on ${topic}:`, data);

      // Emit to connected Socket.io clients
      if (this.io) {
        this.io.emit('mqtt:message', { topic, data, timestamp: new Date().toISOString() });
      }
    } catch (error) {
      this.logger.error('Error parsing MQTT message:', error);
    }
  }

  publish(topic, message) {
    if (!this.isConnected) {
      this.logger.warn('MQTT not connected, cannot publish message');
      return false;
    }

    const payload = JSON.stringify(message);
    this.client.publish(topic, payload, (err) => {
      if (err) {
        this.logger.error(`Failed to publish to ${topic}:`, err);
      } else {
        this.logger.debug(`Published to ${topic}:`, message);
      }
    });
    return true;
  }

  setSocketIO(io) {
    this.io = io;
  }

  disconnect() {
    if (this.client) {
      this.client.end();
    }
  }
}
