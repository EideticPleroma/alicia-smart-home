import Joi from 'joi';

export const deviceSchema = Joi.object({
  device_id: Joi.string().required(),
  device_name: Joi.string().required(),
  device_type: Joi.string().valid('external_api', 'local_service', 'hardware').required(),
  status: Joi.string().valid('online', 'offline', 'unknown').required(),
  last_seen: Joi.string().isoDate().required(),
  connection: Joi.object({
    host: Joi.string().required(),
    port: Joi.number().required(),
    protocol: Joi.string().valid('http', 'https', 'tcp', 'udp', 'mqtt').required(),
    authentication: Joi.object({
      type: Joi.string().valid('api_key', 'oauth', 'basic', 'certificate').required(),
      credentials: Joi.object().required()
    }).required()
  }).required(),
  capabilities: Joi.array().items(Joi.string()).required(),
  metadata: Joi.object().optional()
});

export const validateDevice = (device) => {
  return deviceSchema.validate(device);
};
