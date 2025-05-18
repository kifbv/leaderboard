import axios, { AxiosRequestConfig } from 'axios';
import { fetchAuthSession } from 'aws-amplify/auth';

const API_URL = 'https://fx3sr38767.execute-api.eu-central-1.amazonaws.com/dev';

// Create axios instance with base URL
const apiClient = axios.create({
  baseURL: API_URL,
});

// Add request interceptor to add authentication token
apiClient.interceptors.request.use(
  async (config) => {
    try {
      // Get current authenticated user's session
      const session = await fetchAuthSession();
      const token = session.tokens?.idToken?.toString();
      
      // Add token to request headers if available
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }
    } catch (error) {
      // If not authenticated, proceed without token
      console.log('User not authenticated');
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Generic GET request helper
export const get = async <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
  const response = await apiClient.get<T>(url, config);
  return response.data;
};

// Generic POST request helper
export const post = async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
  const response = await apiClient.post<T>(url, data, config);
  return response.data;
};

// Generic PUT request helper
export const put = async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
  const response = await apiClient.put<T>(url, data, config);
  return response.data;
};

// Generic DELETE request helper
export const del = async <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
  const response = await apiClient.delete<T>(url, config);
  return response.data;
};