/**
 * API Configuration for CostWatch Frontend
 * Centralized API endpoint management
 */

// Get API base URL from environment or use default
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8002';
const RESOURCE_SCANNER_URL = process.env.REACT_APP_RESOURCE_SCANNER_URL || 'http://localhost:8000';
const COST_ANALYZER_URL = process.env.REACT_APP_COST_ANALYZER_URL || 'http://localhost:8001';
const ANALYTICS_ENGINE_URL = process.env.REACT_APP_ANALYTICS_ENGINE_URL || 'http://localhost:8003';
const ALERT_MANAGER_URL = process.env.REACT_APP_ALERT_MANAGER_URL || 'http://localhost:8004';

// API Endpoints
export const API_ENDPOINTS = {
  // Gateway endpoints (use API Gateway for production)
  gateway: {
    health: `${API_BASE_URL}/health`,
    auth: {
      login: `${API_BASE_URL}/auth/login`,
      register: `${API_BASE_URL}/auth/register`,
      logout: `${API_BASE_URL}/auth/logout`,
    },
  },

  // Resource Scanner endpoints
  resources: {
    scanAll: `${RESOURCE_SCANNER_URL}/scan/all`,
    scanEC2: `${RESOURCE_SCANNER_URL}/scan/ec2`,
    scanRDS: `${RESOURCE_SCANNER_URL}/scan/rds`,
    scanS3: `${RESOURCE_SCANNER_URL}/scan/s3`,
    optimize: (resourceType) => `${RESOURCE_SCANNER_URL}/optimize/${resourceType}`,
    metrics: `${RESOURCE_SCANNER_URL}/metrics`,
    health: `${RESOURCE_SCANNER_URL}/health`,
  },

  // Cost Analyzer endpoints
  costs: {
    analyze: `${COST_ANALYZER_URL}/analyze/costs`,
    optimize: `${COST_ANALYZER_URL}/optimize/resources`,
    trends: `${COST_ANALYZER_URL}/analyze/trends`,
    health: `${COST_ANALYZER_URL}/health`,
  },

  // Analytics Engine endpoints
  analytics: {
    trends: `${ANALYTICS_ENGINE_URL}/analytics/trends`,
    predictions: `${ANALYTICS_ENGINE_URL}/analytics/predictions`,
    insights: `${ANALYTICS_ENGINE_URL}/analytics/insights`,
    dashboard: (accountId) => `${ANALYTICS_ENGINE_URL}/analytics/dashboard/${accountId}`,
    benchmarks: (accountId) => `${ANALYTICS_ENGINE_URL}/analytics/benchmarks/${accountId}`,
    anomalies: (accountId) => `${ANALYTICS_ENGINE_URL}/analytics/anomalies/${accountId}`,
    health: `${ANALYTICS_ENGINE_URL}/health`,
  },

  // Alert Manager endpoints
  alerts: {
    send: `${ALERT_MANAGER_URL}/alerts/send`,
    createRule: `${ALERT_MANAGER_URL}/alerts/rules`,
    getRule: (ruleId) => `${ALERT_MANAGER_URL}/alerts/rules/${ruleId}`,
    check: `${ALERT_MANAGER_URL}/alerts/check`,
    monitor: `${ALERT_MANAGER_URL}/alerts/monitor`,
    history: (accountId) => `${ALERT_MANAGER_URL}/alerts/history/${accountId}`,
    health: `${ALERT_MANAGER_URL}/health`,
  },
};

// Request timeout
export const REQUEST_TIMEOUT = 30000; // 30 seconds

// Default headers
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
};

// Get auth token from localStorage
export const getAuthToken = () => {
  return localStorage.getItem('auth_token');
};

// Get auth headers
export const getAuthHeaders = () => {
  const token = getAuthToken();
  return token
    ? { ...DEFAULT_HEADERS, Authorization: `Bearer ${token}` }
    : DEFAULT_HEADERS;
};

export default API_ENDPOINTS;
