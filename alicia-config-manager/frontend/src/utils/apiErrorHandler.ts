export interface ApiError {
  message: string;
  status: number;
  code?: string;
  details?: any;
}

export class ApiErrorHandler {
  private static readonly DEFAULT_MESSAGES = {
    400: 'Bad request. Please check your input.',
    401: 'Authentication required. Please log in.',
    403: 'Access forbidden. You do not have permission.',
    404: 'Resource not found.',
    409: 'Conflict. This action would create a duplicate.',
    422: 'Validation failed. Please check your input.',
    429: 'Too many requests. Please wait and try again.',
    500: 'Server error. Please try again later.',
    503: 'Service unavailable. Please try again later.',
  };

  static parseError(error: any): ApiError {
    // Handle axios errors
    if (error.response) {
      const { data, status } = error.response;

      return {
        message: data.message || this.DEFAULT_MESSAGES[status as keyof typeof this.DEFAULT_MESSAGES] || 'An error occurred',
        status,
        code: data.code,
        details: data.details || data,
      };
    }

    // Handle network errors
    if (error.request) {
      return {
        message: 'Network error. Please check your connection and try again.',
        status: 0,
        code: 'NETWORK_ERROR',
        details: error,
      };
    }

    // Handle other errors
    return {
      message: error.message || 'An unexpected error occurred',
      status: -1,
      code: 'UNKNOWN_ERROR',
      details: error,
    };
  }

  static getUserFriendlyMessage(error: ApiError): string {
    const { code } = error;

    // Custom messages based on error code or status
    switch (code) {
      case 'VALIDATION_ERROR':
        return 'Please check your input and try again.';
      case 'NETWORK_ERROR':
        return 'Please check your internet connection and try again.';
      case 'TIMEOUT':
        return 'The request timed out. Please try again.';
      case 'CONFIG_SAVE_ERROR':
        return 'Failed to save configuration. Please try again.';
      case 'DEVICE_CONNECT_ERROR':
        return 'Failed to connect to device. Please check your settings.';
    }

    // Fallback to default message based on status
    return error.message;
  }

  static isRetryable(error: ApiError): boolean {
    // Retry for network errors, timeouts, and server errors
    return [0, 408, 429, 500, 502, 503, 504].includes(error.status);
  }

  static getRetryDelay(_error: ApiError, attemptNumber: number): number {
    // Exponential backoff with jitter
    const baseDelay = Math.min(1000 * Math.pow(2, attemptNumber), 10000);
    const jitter = Math.random() * 1000;
    return baseDelay + jitter;
  }
}

// Helper function to handle API errors in hooks
export const handleApiError = (error: any, context: string = '') => {
  const parsedError = ApiErrorHandler.parseError(error);
  const message = ApiErrorHandler.getUserFriendlyMessage(parsedError);

  console.error(`API Error ${context}:`, error, parsedError);

  return {
    parsedError,
    userMessage: message,
    isRetryable: ApiErrorHandler.isRetryable(parsedError),
  };
};
