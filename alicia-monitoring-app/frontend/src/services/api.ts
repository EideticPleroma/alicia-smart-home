import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);
    return Promise.reject(error);
  }
);

export interface HealthData {
  timestamp: string;
  services: Record<string, {
    status: 'healthy' | 'unhealthy' | 'timeout' | 'error';
    response_time_ms: number;
    last_check: string;
    error?: string;
  }>;
  overall_status: 'healthy' | 'degraded' | 'critical';
  summary: {
    total_services: number;
    healthy_services: number;
    unhealthy_services: number;
    error_services: number;
  };
}

export interface ServiceConfig {
  service: string;
  environment: string;
  config: Record<string, any>;
  last_updated: string;
}

export interface TestRequest {
  test_type: string;
  input_text?: string;
  input_audio?: string;
  component?: string;
  parameters?: Record<string, any>;
}

export interface TestResult {
  test_id: string;
  test_type: string;
  status: 'running' | 'completed' | 'failed';
  input: string;
  output?: string;
  error?: string;
  duration_ms: number;
  metrics?: Record<string, any>;
  timestamp: string;
}

export const apiService = {
  // Health endpoints
  getHealthStatus: async (): Promise<HealthData> => {
    const response = await api.get('/api/health/');
    return response.data;
  },

  getServicesStatus: async () => {
    const response = await api.get('/api/health/services');
    return response.data;
  },

  getServiceStatus: async (serviceName: string) => {
    const response = await api.get(`/api/health/services/${serviceName}`);
    return response.data;
  },

  refreshHealthStatus: async () => {
    const response = await api.post('/api/health/refresh');
    return response.data;
  },

  // Configuration endpoints
  getAllConfigs: async (environment: string = 'production') => {
    const response = await api.get(`/api/config/?environment=${environment}`);
    return response.data;
  },

  getServiceConfig: async (service: string, environment: string = 'production') => {
    const response = await api.get(`/api/config/${service}?environment=${environment}`);
    return response.data;
  },

  updateServiceConfig: async (service: string, config: Record<string, any>, environment: string = 'production') => {
    const response = await api.put(`/api/config/${service}?environment=${environment}`, config);
    return response.data;
  },

  testServiceConfig: async (service: string, environment: string = 'production') => {
    const response = await api.post(`/api/config/${service}/test?environment=${environment}`);
    return response.data;
  },

  getEnvironments: async () => {
    const response = await api.get('/api/config/environments');
    return response.data;
  },

  // Testing endpoints
  runTest: async (testRequest: TestRequest) => {
    const response = await api.post('/api/testing/run', testRequest);
    return response.data;
  },

  getTestResult: async (testId: string) => {
    const response = await api.get(`/api/testing/results/${testId}`);
    return response.data;
  },

  getTestResults: async (limit: number = 50, testType?: string, status?: string) => {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit.toString());
    if (testType) params.append('test_type', testType);
    if (status) params.append('status', status);
    
    const response = await api.get(`/api/testing/results?${params.toString()}`);
    return response.data;
  },

  deleteTestResult: async (testId: string) => {
    const response = await api.delete(`/api/testing/results/${testId}`);
    return response.data;
  },

  runTestSuite: async () => {
    const response = await api.post('/api/testing/run-suite');
    return response.data;
  },

  getTestStats: async () => {
    const response = await api.get('/api/testing/stats');
    return response.data;
  },

  // Metrics endpoints
  getMetricsOverview: async (hours: number = 24) => {
    const response = await api.get(`/api/metrics/overview?hours=${hours}`);
    return response.data;
  },

  getServiceMetrics: async (serviceName: string, hours: number = 24) => {
    const response = await api.get(`/api/metrics/services/${serviceName}?hours=${hours}`);
    return response.data;
  },

  getPerformanceMetrics: async (hours: number = 24) => {
    const response = await api.get(`/api/metrics/performance?hours=${hours}`);
    return response.data;
  },

  getAlertMetrics: async (hours: number = 24) => {
    const response = await api.get(`/api/metrics/alerts?hours=${hours}`);
    return response.data;
  },

  exportMetrics: async (hours: number = 24, format: string = 'json') => {
    const response = await api.get(`/api/metrics/export?hours=${hours}&format=${format}`);
    return response.data;
  },
};

export default api;

