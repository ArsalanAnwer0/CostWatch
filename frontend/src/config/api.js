/**
 * API Configuration for CostWatch Frontend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8002';

export const API_ENDPOINTS = {
  gateway: {
    health: `${API_BASE_URL}/health`,
    auth: {
      login: `${API_BASE_URL}/auth/login`,
      register: `${API_BASE_URL}/auth/register`,
      logout: `${API_BASE_URL}/auth/logout`,
    },
  },
  costs: {
    analyze: `${API_BASE_URL}/costs/analyze`,
    trends: `${API_BASE_URL}/costs/trends`,
  },
  resources: {
    scanAll: `${API_BASE_URL}/costs/resources`,
  },
};

export const REQUEST_TIMEOUT = 30000;

export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
};

export const getAuthToken = () => {
  return localStorage.getItem('auth_token');
};

export const getAuthHeaders = () => {
  const token = getAuthToken();
  return token
    ? { ...DEFAULT_HEADERS, Authorization: `Bearer ${token}` }
    : DEFAULT_HEADERS;
};

export default API_ENDPOINTS;
