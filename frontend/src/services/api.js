/**
 * API Service - Handles all HTTP requests to backend
 */
import { API_ENDPOINTS, REQUEST_TIMEOUT, getAuthHeaders } from '../config/api';

const apiRequest = async (url, options = {}) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...getAuthHeaders(),
        ...options.headers,
      },
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        message: `HTTP ${response.status}: ${response.statusText}`,
      }));
      throw new Error(error.message || 'Request failed');
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);

    if (error.name === 'AbortError') {
      throw new Error('Request timeout - please try again');
    }

    throw error;
  }
};

export const get = (url, options = {}) => {
  return apiRequest(url, { ...options, method: 'GET' });
};

export const post = (url, data, options = {}) => {
  return apiRequest(url, {
    ...options,
    method: 'POST',
    body: JSON.stringify(data),
  });
};

export const ResourceService = {
  scanAll: () => get(API_ENDPOINTS.resources.scanAll),
};

export const CostService = {
  analyzeCosts: (accountId, startDate, endDate) =>
    post(API_ENDPOINTS.costs.analyze, {
      account_id: accountId,
      start_date: startDate,
      end_date: endDate,
    }),

  analyzeTrends: (accountId, days = 30) =>
    post(API_ENDPOINTS.costs.trends, {
      account_id: accountId,
      days,
    }),
};

export const checkServiceHealth = async () => {
  try {
    const response = await get(API_ENDPOINTS.gateway.health);
    return { status: 'healthy', data: response };
  } catch (error) {
    return { status: 'unhealthy', error: error.message };
  }
};

export default {
  get,
  post,
  ResourceService,
  CostService,
  checkServiceHealth,
};
