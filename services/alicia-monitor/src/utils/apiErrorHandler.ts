export interface ApiError {
  message: string;
  status?: number;
  retryable: boolean;
}

export const handleApiError = (error: any): ApiError => {
  if (error.response) {
    return {
      message: error.response.data?.message || 'Server error',
      status: error.response.status,
      retryable: error.response.status >= 500
    };
  } else if (error.request) {
    return {
      message: 'Network error - please check your connection',
      retryable: true
    };
  } else {
    return {
      message: error.message || 'Unknown error occurred',
      retryable: false
    };
  }
};

export const retryApiCall = async <T>(
  apiCall: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> => {
  let lastError: any;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await apiCall();
    } catch (error) {
      lastError = error;
      const apiError = handleApiError(error);

      if (!apiError.retryable || i === maxRetries - 1) {
        throw error;
      }

      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
    }
  }

  throw lastError;
};
