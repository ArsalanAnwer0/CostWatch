/**
 * Mock Data for CostWatch - Makes the app functional without backend
 * This provides realistic AWS cost data for demo purposes
 */

// Mock user data
export const mockUser = {
  id: '1',
  email: 'demo@costwatch.com',
  name: 'Demo User',
  company: 'Demo Company',
  aws_account_id: '123456789012',
};

// Mock cost summary
export const mockCostSummary = {
  currentMonth: 12450.67,
  lastMonth: 15230.45,
  percentChange: -18.3,
  savingsOpportunity: 4250.30,
  totalResources: 87,
  unusedResources: 12,
  underutilizedResources: 23,
};

// Mock cost trends (30 days)
export const mockCostTrends = Array.from({ length: 30 }, (_, i) => ({
  date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  cost: 350 + Math.random() * 200 + Math.sin(i / 7) * 100,
  forecast: i > 20 ? 400 + Math.random() * 150 : null,
}));

// Mock resource breakdown
export const mockResourceBreakdown = [
  { service: 'EC2', count: 24, cost: 4560.23, percentage: 36.6 },
  { service: 'RDS', count: 8, cost: 3120.45, percentage: 25.1 },
  { service: 'S3', count: 45, cost: 2340.12, percentage: 18.8 },
  { service: 'Lambda', count: 156, cost: 1245.67, percentage: 10.0 },
  { service: 'DynamoDB', count: 12, cost: 890.34, percentage: 7.1 },
  { service: 'CloudWatch', count: 89, cost: 293.86, percentage: 2.4 },
];

// Mock EC2 instances
export const mockEC2Instances = [
  {
    id: 'i-1234567890abcdef0',
    name: 'web-server-prod-1',
    type: 't3.medium',
    state: 'running',
    region: 'us-west-2',
    monthlyCost: 45.60,
    utilizationCPU: 23,
    utilizationMemory: 45,
    recommendation: 'Right-size to t3.small',
    potentialSavings: 22.80,
  },
  {
    id: 'i-0987654321fedcba0',
    name: 'api-server-prod-1',
    type: 'm5.large',
    state: 'running',
    region: 'us-west-2',
    monthlyCost: 89.28,
    utilizationCPU: 67,
    utilizationMemory: 72,
    recommendation: 'Properly sized',
    potentialSavings: 0,
  },
  {
    id: 'i-abcdef1234567890',
    name: 'batch-processor',
    type: 'c5.xlarge',
    state: 'stopped',
    region: 'us-east-1',
    monthlyCost: 0,
    utilizationCPU: 0,
    utilizationMemory: 0,
    recommendation: 'Consider terminating - stopped for 30+ days',
    potentialSavings: 156.48,
  },
  {
    id: 'i-fedcba0987654321',
    name: 'dev-server',
    type: 't3.large',
    state: 'running',
    region: 'us-west-2',
    monthlyCost: 67.20,
    utilizationCPU: 12,
    utilizationMemory: 18,
    recommendation: 'Right-size to t3.medium',
    potentialSavings: 28.80,
  },
];

// Mock RDS instances
export const mockRDSInstances = [
  {
    id: 'mydb-prod-1',
    engine: 'PostgreSQL 14.7',
    type: 'db.t3.medium',
    storage: 100,
    state: 'available',
    monthlyCost: 67.20,
    connections: 45,
    recommendation: 'Properly sized',
    potentialSavings: 0,
  },
  {
    id: 'analytics-db',
    engine: 'MySQL 8.0',
    type: 'db.m5.large',
    storage: 500,
    state: 'available',
    monthlyCost: 234.56,
    connections: 12,
    recommendation: 'Low utilization - consider downsizing',
    potentialSavings: 117.28,
  },
];

// Mock S3 buckets
export const mockS3Buckets = [
  {
    name: 'app-assets-prod',
    size: '245 GB',
    objectCount: 45678,
    monthlyCost: 5.63,
    storageClass: 'Standard',
    recommendation: 'Move old files to Glacier',
    potentialSavings: 3.12,
  },
  {
    name: 'backups-daily',
    size: '1.2 TB',
    objectCount: 892,
    monthlyCost: 27.84,
    storageClass: 'Standard',
    recommendation: 'Use Intelligent-Tiering',
    potentialSavings: 12.45,
  },
  {
    name: 'logs-archive',
    size: '3.4 TB',
    objectCount: 234567,
    monthlyCost: 78.96,
    storageClass: 'Standard',
    recommendation: 'Move to Glacier Deep Archive',
    potentialSavings: 67.23,
  },
];

// Mock optimization recommendations
export const mockOptimizations = [
  {
    id: 1,
    type: 'EC2',
    severity: 'high',
    title: 'Terminate stopped instances',
    description: '3 EC2 instances have been stopped for over 30 days',
    monthlySavings: 456.78,
    resources: ['i-abcdef1234567890', 'i-1111222233334444', 'i-5555666677778888'],
  },
  {
    id: 2,
    type: 'EC2',
    severity: 'medium',
    title: 'Right-size underutilized instances',
    description: '12 instances running at <30% CPU utilization',
    monthlySavings: 234.56,
    resources: ['i-1234567890abcdef0', 'i-fedcba0987654321'],
  },
  {
    id: 3,
    type: 'RDS',
    severity: 'medium',
    title: 'Downsize low-usage databases',
    description: '2 RDS instances with low connection counts',
    monthlySavings: 189.45,
    resources: ['analytics-db'],
  },
  {
    id: 4,
    type: 'S3',
    severity: 'low',
    title: 'Implement lifecycle policies',
    description: 'Move infrequently accessed data to cheaper storage',
    monthlySavings: 125.34,
    resources: ['logs-archive', 'backups-daily'],
  },
  {
    id: 5,
    type: 'EBS',
    severity: 'high',
    title: 'Delete unattached volumes',
    description: '8 EBS volumes not attached to any instance',
    monthlySavings: 78.90,
    resources: ['vol-1234', 'vol-5678', 'vol-9012'],
  },
];

// Mock alerts
export const mockAlerts = [
  {
    id: 1,
    type: 'cost_spike',
    severity: 'high',
    title: 'Unusual cost increase detected',
    message: 'Daily cost increased by 45% compared to 7-day average',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    read: false,
  },
  {
    id: 2,
    type: 'budget_threshold',
    severity: 'medium',
    title: 'Monthly budget at 80%',
    message: 'Current month spending has reached 80% of allocated budget',
    timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    read: false,
  },
  {
    id: 3,
    type: 'idle_resource',
    severity: 'low',
    title: 'Idle resources detected',
    message: '3 EC2 instances have been idle for over 7 days',
    timestamp: new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString(),
    read: true,
  },
];

// Mock cost predictions
export const mockPredictions = {
  nextMonth: 13450.23,
  nextQuarter: 41234.56,
  confidence: 0.87,
  trend: 'increasing',
  factors: [
    'Seasonal increase in usage expected',
    'New resources added in last 30 days',
    'Historical trend shows 8% month-over-month growth',
  ],
};

// Mock analytics insights
export const mockInsights = [
  {
    category: 'Cost Optimization',
    insights: [
      'You could save $4,250/month by implementing recommended optimizations',
      '34% of your EC2 instances are underutilized',
      'S3 storage optimization could reduce costs by 18%',
    ],
  },
  {
    category: 'Resource Usage',
    insights: [
      'Peak usage occurs between 9 AM - 5 PM EST',
      'Weekend usage is 40% lower than weekdays',
      'Lambda invocations increased 23% this month',
    ],
  },
  {
    category: 'Cost Trends',
    insights: [
      'Monthly costs decreased 18% from last month',
      'EC2 costs are the largest contributor at 37%',
      'Data transfer costs increased by 12%',
    ],
  },
];

// Mock anomalies
export const mockAnomalies = [
  {
    date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    service: 'EC2',
    expectedCost: 450.23,
    actualCost: 678.45,
    deviation: 50.7,
    reason: 'Spike in instance usage',
  },
  {
    date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    service: 'S3',
    expectedCost: 78.90,
    actualCost: 156.78,
    deviation: 98.7,
    reason: 'Unusual data transfer activity',
  },
];

export default {
  mockUser,
  mockCostSummary,
  mockCostTrends,
  mockResourceBreakdown,
  mockEC2Instances,
  mockRDSInstances,
  mockS3Buckets,
  mockOptimizations,
  mockAlerts,
  mockPredictions,
  mockInsights,
  mockAnomalies,
};
