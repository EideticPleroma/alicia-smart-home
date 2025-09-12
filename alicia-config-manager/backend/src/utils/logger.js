import winston from 'winston';

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({
      filename: process.env.ERROR_LOG_FILE || 'logs/error.log',
      level: 'error'
    }),
    new winston.transports.File({
      filename: process.env.LOG_FILE || 'logs/combined.log'
    }),
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});

export { logger };
