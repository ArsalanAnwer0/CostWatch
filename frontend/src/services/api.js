/**
 * API Service - Handles all HTTP requests to backend
 */
import { API_ENDPOINTS, REQUEST_TIMEOUT, getAuthHeaders } from '../config/api';

/**
 * Make API request
 * @param {string} url - API endpoint URL
 * @param {object} options - Fetch options
 * @returns {Promise} Response data
 */
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

    // Handle non-OK responses
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

/**
 * GET request
 */
export const get = (url, options = {}) => {
  return apiRequest(url, { ...options, method: 'GET' });
};

/**
 * POST request
 */
export const post = (url, data, options = {}) => {
  return apiRequest(url, {
    ...options,
    method: 'POST',
    body: JSON.stringify(data),
  });
};

/**
 * PUT request
 */
export const put = (url, data, options = {}) => {
  return apiRequest(url, {
    ...options,
    method: 'PUT',
    body: JSON.stringify(data),
  });
};

/**
 * DELETE request
 */
export const del = (url, options = {}) => {
  return apiRequest(url, { ...options, method: 'DELETE' });
};

// Service-specific API functions
export const ResourceService = {
  scanAll: (regions = ['us-west-2'], includeCosts = true) =>
    post(API_ENDPOINTS.resources.scanAll, { regions, include_costs: includeCosts }),

  scanEC2: (region = 'us-west-2', includeCosts = true) =>
    post(API_ENDPOINTS.resources.scanEC2, { region, include_costs: includeCosts }),

  scanRDS: (region = 'us-west-2', includeCosts = true) =>
    post(API_ENDPOINTS.resources.scanRDS, { region, include_costs: includeCosts }),

  scanS3: (includeCosts = true) =>
    post(API_ENDPOINTS.resources.scanS3, { include_costs: includeCosts }),

  getOptimizations: (resourceType) =>
    get(API_ENDPOINTS.resources.optimize(resourceType)),

  getMetrics: () =>
    get(API_ENDPOINTS.resources.metrics),
};

export const CostService = {
  analyzeCosts: (accountId, startDate, endDate) =>
    post(API_ENDPOINTS.costs.analyze, {
      account_id: accountId,
      start_date: startDate,
      end_date: endDate,
    }),

  getOptimizations: (accountId, resourceTypes = ['ec2', 'rds', 'ebs', 's3']) =>
    post(API_ENDPOINTS.costs.optimize, {
      account_id: accountId,
      resource_types: resourceTypes,
    }),

  analyzeTrends: (accountId, days = 30) =>
    post(API_ENDPOINTS.costs.trends, {
      account_id: accountId,
      days,
    }),
};

export const AnalyticsService = {
  getTrends: (accountId, startDate, endDate, metrics = ['total_cost', 'daily_cost']) =>
    post(API_ENDPOINTS.analytics.trends, {
      account_id: accountId,
      start_date: startDate,
      end_date: endDate,
      metrics,
    }),

  getPredictions: (accountId, predictionType = 'cost_forecast', timeHorizon = 30) =>
    post(API_ENDPOINTS.analytics.predictions, {
      account_id: accountId,
      prediction_type: predictionType,
      time_horizon: timeHorizon,
    }),

  getInsights: (accountId, analysisType = 'cost_optimization') =>
    post(API_ENDPOINTS.analytics.insights, {
      account_id: accountId,
      analysis_type: analysisType,
    }),

  getDashboard: (accountId, period = 'last_30_days', includeForecasts = true) =>
    get(`${API_ENDPOINTS.analytics.dashboard(accountId)}?period=${period}&include_forecasts=${includeForecasts}`),

  getBenchmarks: (accountId, industry = 'technology', companySize = 'medium') =>
    get(`${API_ENDPOINTS.analytics.benchmarks(accountId)}?industry=${industry}&company_size=${companySize}`),

  getAnomalies: (accountId, days = 30, sensitivity = 'medium') =>
    get(`${API_ENDPOINTS.analytics.anomalies(accountId)}?days=${days}&sensitivity=${sensitivity}`),
};

export const AlertService = {
  sendAlert: (alertData) =>
    post(API_ENDPOINTS.alerts.send, alertData),

  createRule: (ruleData) =>
    post(API_ENDPOINTS.alerts.createRule, ruleData),

  getRule: (ruleId) =>
    get(API_ENDPOINTS.alerts.getRule(ruleId)),

  checkAlerts: (accountId, costData = null) =>
    post(API_ENDPOINTS.alerts.check, {
      account_id: accountId,
      cost_data: costData,
    }),

  startMonitoring: (accountId, intervalMinutes = 60) =>
    post(API_ENDPOINTS.alerts.monitor, {
      account_id: accountId,
      interval_minutes: intervalMinutes,
    }),

  getHistory: (accountId, limit = 50, offset = 0) =>
    get(`${API_ENDPOINTS.alerts.history(accountId)}?limit=${limit}&offset=${offset}`),
};

// Health check for all services
export const checkServiceHealth = async () => {
  const services = [
    { name: 'Resource Scanner', url: API_ENDPOINTS.resources.health },
    { name: 'Cost Analyzer', url: API_ENDPOINTS.costs.health },
    { name: 'Analytics Engine', url: API_ENDPOINTS.analytics.health },
    { name: 'Alert Manager', url: API_ENDPOINTS.alerts.health },
  ];

  const results = await Promise.allSettled(
    services.map(async (service) => {
      try {
        const response = await get(service.url);
        return { name: service.name, status: 'healthy', data: response };
      } catch (error) {
        return { name: service.name, status: 'unhealthy', error: error.message };
      }
    })
  );

  return results.map((result, index) => ({
    ...services[index],
    ...(result.status === 'fulfilled' ? result.value : { status: 'error', error: result.reason }),
  }));
};

export default {
  get,
  post,
  put,
  del,
  ResourceService,
  CostService,
  AnalyticsService,
  AlertService,
  checkServiceHealth,
};
