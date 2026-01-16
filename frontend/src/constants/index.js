/**
 * Application-wide constants
 */

// API Configuration
export const API_TIMEOUT = 30000; // 30 seconds
export const REQUEST_RETRY_COUNT = 3;
export const REQUEST_RETRY_DELAY = 1000; // 1 second

// AWS Regions
export const AWS_REGIONS = [
  { code: 'us-east-1', name: 'US East (N. Virginia)' },
  { code: 'us-east-2', name: 'US East (Ohio)' },
  { code: 'us-west-1', name: 'US West (N. California)' },
  { code: 'us-west-2', name: 'US West (Oregon)' },
  { code: 'eu-west-1', name: 'EU (Ireland)' },
  { code: 'eu-west-2', name: 'EU (London)' },
  { code: 'eu-west-3', name: 'EU (Paris)' },
  { code: 'eu-central-1', name: 'EU (Frankfurt)' },
  { code: 'ap-southeast-1', name: 'Asia Pacific (Singapore)' },
  { code: 'ap-southeast-2', name: 'Asia Pacific (Sydney)' },
  { code: 'ap-northeast-1', name: 'Asia Pacific (Tokyo)' },
  { code: 'ap-northeast-2', name: 'Asia Pacific (Seoul)' },
  { code: 'sa-east-1', name: 'South America (São Paulo)' },
  { code: 'ca-central-1', name: 'Canada (Central)' },
];

// AWS Services
export const AWS_SERVICES = [
  'EC2',
  'RDS',
  'S3',
  'Lambda',
  'DynamoDB',
  'CloudFront',
  'ELB',
  'EBS',
  'ElastiCache',
  'Redshift',
];

// Resource States
export const RESOURCE_STATES = {
  RUNNING: 'running',
  STOPPED: 'stopped',
  TERMINATED: 'terminated',
  AVAILABLE: 'available',
  PENDING: 'pending',
};

// Alert Severity Levels
export const SEVERITY_LEVELS = {
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low',
};

// Optimization Types
export const OPTIMIZATION_TYPES = {
  RIGHT_SIZING: 'right-sizing',
  UNUSED_RESOURCES: 'unused-resources',
  RESERVED_INSTANCES: 'reserved-instances',
  STORAGE_OPTIMIZATION: 'storage-optimization',
  COST_ALLOCATION: 'cost-allocation',
};

// Time Ranges
export const TIME_RANGES = [
  { label: 'Last 7 Days', value: 7 },
  { label: 'Last 30 Days', value: 30 },
  { label: 'Last 60 Days', value: 60 },
  { label: 'Last 90 Days', value: 90 },
  { label: 'Last 6 Months', value: 180 },
  { label: 'Last Year', value: 365 },
];

// Chart Colors
export const CHART_COLORS = {
  PRIMARY: '#3b82f6',
  SUCCESS: '#10b981',
  WARNING: '#f59e0b',
  DANGER: '#ef4444',
  INFO: '#6366f1',
  GRAY: '#6b7280',
};

// Status Colors
export const STATUS_COLORS = {
  running: '#10b981',
  stopped: '#ef4444',
  terminated: '#6b7280',
  available: '#10b981',
  pending: '#f59e0b',
};

// Pagination
export const DEFAULT_PAGE_SIZE = 20;
export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100];

// Local Storage Keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'token',
  USER_DATA: 'user',
  PREFERENCES: 'preferences',
  SELECTED_REGION: 'selectedRegion',
  THEME: 'theme',
};

// Date Formats
export const DATE_FORMATS = {
  SHORT: 'MMM D, YYYY',
  LONG: 'MMMM D, YYYY h:mm A',
  ISO: 'YYYY-MM-DD',
};

// Password Requirements
export const PASSWORD_REQUIREMENTS = {
  MIN_LENGTH: 8,
  REQUIRE_UPPERCASE: true,
  REQUIRE_LOWERCASE: true,
  REQUIRE_NUMBER: true,
  REQUIRE_SPECIAL: true,
};

// File Upload Limits
export const FILE_UPLOAD = {
  MAX_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_TYPES: ['image/jpeg', 'image/png', 'application/pdf'],
};

// Notification Duration
export const NOTIFICATION_DURATION = 5000; // 5 seconds

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  UNAUTHORIZED: 'You are not authorized. Please log in.',
  SERVER_ERROR: 'Server error. Please try again later.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  NOT_FOUND: 'The requested resource was not found.',
};

// Success Messages
export const SUCCESS_MESSAGES = {
  LOGIN: 'Successfully logged in!',
  LOGOUT: 'Successfully logged out.',
  REGISTER: 'Account created successfully!',
  UPDATE: 'Changes saved successfully!',
  DELETE: 'Deleted successfully.',
};
