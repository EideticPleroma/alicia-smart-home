import fs from 'fs-extra';
import path from 'path';
import { logger } from '../utils/logger.js';

export class EnvConfigService {
  constructor(logger) {
    this.logger = logger;
    this.envPath = path.join(process.cwd(), '.env');
    this.envTemplatePath = path.join(process.cwd(), 'env.template');
    this.envVars = new Map();
    this.isReady = false;
  }

  async initialize() {
    try {
      await this.loadEnvFile();
      this.isReady = true;
      this.logger.info('Environment configuration service initialized successfully');
    } catch (error) {
      this.logger.error('Failed to initialize environment configuration service:', error);
      throw error;
    }
  }

  async loadEnvFile() {
    try {
      if (await fs.pathExists(this.envPath)) {
        const content = await fs.readFile(this.envPath, 'utf8');
        this.parseEnvContent(content);
        this.logger.info(`Loaded ${this.envVars.size} environment variables`);
      } else {
        await this.createEnvFromTemplate();
      }
    } catch (error) {
      this.logger.error('Error loading .env file:', error);
      throw error;
    }
  }

  parseEnvContent(content) {
    this.envVars.clear();
    const lines = content.split('\n');
    
    for (const line of lines) {
      const trimmedLine = line.trim();
      
      // Skip empty lines and comments
      if (!trimmedLine || trimmedLine.startsWith('#')) {
        continue;
      }
      
      // Parse KEY=VALUE format
      const equalIndex = trimmedLine.indexOf('=');
      if (equalIndex > 0) {
        const key = trimmedLine.substring(0, equalIndex).trim();
        const value = trimmedLine.substring(equalIndex + 1).trim();
        this.envVars.set(key, value);
      }
    }
  }

  async createEnvFromTemplate() {
    try {
      if (await fs.pathExists(this.envTemplatePath)) {
        await fs.copy(this.envTemplatePath, this.envPath);
        await this.loadEnvFile();
        this.logger.info('Created .env file from template');
      } else {
        // Create a basic .env file
        const basicEnv = `# Alicia Smart Home AI Assistant - Environment Configuration
NODE_ENV=development
MQTT_BROKER=alicia_bus_core
MQTT_PORT=1883
MQTT_USERNAME=admin
MQTT_PASSWORD=alicia_admin_2024
GROK_API_KEY=your_grok_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
HA_TOKEN=your_home_assistant_token_here
JWT_SECRET=your_jwt_secret_key_here
`;
        await fs.writeFile(this.envPath, basicEnv);
        await this.loadEnvFile();
        this.logger.info('Created basic .env file');
      }
    } catch (error) {
      this.logger.error('Error creating .env file:', error);
      throw error;
    }
  }

  getAllEnvVars() {
    return Object.fromEntries(this.envVars);
  }

  getEnvVar(key) {
    return this.envVars.get(key) || null;
  }

  async updateEnvVar(key, value) {
    try {
      // Validate key format
      if (!key || !/^[A-Z_][A-Z0-9_]*$/.test(key)) {
        throw new Error('Invalid environment variable key format');
      }

      // Update the in-memory map
      this.envVars.set(key, value);

      // Write back to .env file
      await this.writeEnvFile();

      this.logger.info(`Environment variable ${key} updated`);
      return { key, value };
    } catch (error) {
      this.logger.error(`Error updating environment variable ${key}:`, error);
      throw error;
    }
  }

  async updateMultipleEnvVars(updates) {
    try {
      const results = [];
      
      for (const [key, value] of Object.entries(updates)) {
        if (value !== undefined && value !== null) {
          this.envVars.set(key, value);
          results.push({ key, value });
        }
      }

      // Write back to .env file
      await this.writeEnvFile();

      this.logger.info(`Updated ${results.length} environment variables`);
      return results;
    } catch (error) {
      this.logger.error('Error updating multiple environment variables:', error);
      throw error;
    }
  }

  async writeEnvFile() {
    try {
      const lines = [];
      
      // Read the original file to preserve comments and structure
      if (await fs.pathExists(this.envPath)) {
        const originalContent = await fs.readFile(this.envPath, 'utf8');
        const originalLines = originalContent.split('\n');
        
        for (const line of originalLines) {
          const trimmedLine = line.trim();
          
          if (!trimmedLine || trimmedLine.startsWith('#')) {
            // Keep comments and empty lines as-is
            lines.push(line);
          } else {
            const equalIndex = trimmedLine.indexOf('=');
            if (equalIndex > 0) {
              const key = trimmedLine.substring(0, equalIndex).trim();
              const value = this.envVars.get(key);
              
              if (value !== undefined) {
                lines.push(`${key}=${value}`);
              } else {
                lines.push(line); // Keep original line if not in our map
              }
            } else {
              lines.push(line); // Keep malformed lines as-is
            }
          }
        }
      } else {
        // Create new file
        for (const [key, value] of this.envVars) {
          lines.push(`${key}=${value}`);
        }
      }

      // Add any new variables that weren't in the original file
      const existingKeys = new Set();
      for (const line of lines) {
        const trimmedLine = line.trim();
        if (trimmedLine && !trimmedLine.startsWith('#')) {
          const equalIndex = trimmedLine.indexOf('=');
          if (equalIndex > 0) {
            existingKeys.add(trimmedLine.substring(0, equalIndex).trim());
          }
        }
      }

      for (const [key, value] of this.envVars) {
        if (!existingKeys.has(key)) {
          lines.push(`${key}=${value}`);
        }
      }

      await fs.writeFile(this.envPath, lines.join('\n'));
    } catch (error) {
      this.logger.error('Error writing .env file:', error);
      throw error;
    }
  }

  async backupEnvFile() {
    try {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const backupPath = `${this.envPath}.backup.${timestamp}`;
      await fs.copy(this.envPath, backupPath);
      this.logger.info(`Environment file backed up to ${backupPath}`);
      return backupPath;
    } catch (error) {
      this.logger.error('Error backing up .env file:', error);
      throw error;
    }
  }

  async restoreEnvFile(backupPath) {
    try {
      if (await fs.pathExists(backupPath)) {
        await fs.copy(backupPath, this.envPath);
        await this.loadEnvFile();
        this.logger.info(`Environment file restored from ${backupPath}`);
      } else {
        throw new Error(`Backup file not found: ${backupPath}`);
      }
    } catch (error) {
      this.logger.error('Error restoring .env file:', error);
      throw error;
    }
  }

  getSensitiveKeys() {
    // List of keys that should be masked in logs
    return [
      'GROK_API_KEY',
      'OPENAI_API_KEY',
      'HA_TOKEN',
      'JWT_SECRET',
      'MQTT_PASSWORD',
      'SMTP_PASS',
      'FCM_SERVER_KEY',
      'GOOGLE_CLOUD_CREDENTIALS',
      'AZURE_SPEECH_KEY',
      'AZURE_TTS_KEY'
    ];
  }

  getMaskedValue(key, value) {
    if (this.getSensitiveKeys().includes(key)) {
      return value ? '*'.repeat(Math.min(value.length, 8)) : '***';
    }
    return value;
  }

  getMaskedEnvVars() {
    const masked = {};
    for (const [key, value] of this.envVars) {
      masked[key] = this.getMaskedValue(key, value);
    }
    return masked;
  }

  isReady() {
    return this.isReady;
  }
}
