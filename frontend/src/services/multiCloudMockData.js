/**
 * Multi-Cloud Mock Data
 * Mock data for AWS, Azure, and GCP resources
 */

// Generate mock multi-cloud resources
export const generateMultiCloudResources = () => {
  const awsResources = [
    {
      id: 'i-aws-001',
      provider: 'aws',
      type: 'compute',
      name: 'web-server-01',
      region: 'us-east-1',
      status: 'running',
      instanceType: 't3.medium',
      monthlyCost: 30.37,
      tags: { Environment: 'Production', App: 'Web' }
    },
    {
      id: 'i-aws-002',
      provider: 'aws',
      type: 'compute',
      name: 'api-server-01',
      region: 'us-west-2',
      status: 'running',
      instanceType: 't3.large',
      monthlyCost: 60.74,
      tags: { Environment: 'Production', App: 'API' }
    },
    {
      id: 'db-aws-001',
      provider: 'aws',
      type: 'database',
      name: 'prod-database',
      region: 'us-east-1',
      status: 'running',
      instanceType: 'db.t3.medium',
      engine: 'postgres',
      monthlyCost: 61.32,
      tags: { Environment: 'Production' }
    },
    {
      id: 's3-aws-001',
      provider: 'aws',
      type: 'storage',
      name: 'app-backups',
      region: 'us-east-1',
      status: 'active',
      sizeGB: 245.5,
      storageClass: 'STANDARD',
      monthlyCost: 5.65,
      tags: { DataType: 'Backups' }
    },
  ];

  const azureResources = [
    {
      id: 'vm-azure-001',
      provider: 'azure',
      type: 'compute',
      name: 'vm-eastus-01',
      region: 'eastus',
      status: 'running',
      instanceType: 'Standard_D2s_v3',
      monthlyCost: 96.00,
      tags: { Environment: 'Production', App: 'Analytics' }
    },
    {
      id: 'vm-azure-002',
      provider: 'azure',
      type: 'compute',
      name: 'vm-westeurope-01',
      region: 'westeurope',
      status: 'stopped',
      instanceType: 'Standard_B2s',
      monthlyCost: 4.00,
      tags: { Environment: 'Development' }
    },
    {
      id: 'sql-azure-001',
      provider: 'azure',
      type: 'database',
      name: 'sqldb-prod',
      region: 'eastus',
      status: 'running',
      instanceType: 'Standard_S2',
      engine: 'sqlserver',
      monthlyCost: 85.00,
      tags: { Environment: 'Production' }
    },
    {
      id: 'blob-azure-001',
      provider: 'azure',
      type: 'storage',
      name: 'blob-logs',
      region: 'eastus',
      status: 'active',
      sizeGB: 1250.0,
      storageClass: 'Hot',
      monthlyCost: 23.00,
      tags: { DataType: 'Logs' }
    },
  ];

  const gcpResources = [
    {
      id: 'gce-gcp-001',
      provider: 'gcp',
      type: 'compute',
      name: 'gce-central-01',
      region: 'us-central1',
      status: 'running',
      instanceType: 'n1-standard-2',
      monthlyCost: 48.55,
      tags: { env: 'prod', app: 'web' }
    },
    {
      id: 'gce-gcp-002',
      provider: 'gcp',
      type: 'compute',
      name: 'gce-europe-01',
      region: 'europe-west1',
      status: 'running',
      instanceType: 'e2-standard-4',
      monthlyCost: 113.81,
      tags: { env: 'prod', app: 'data' }
    },
    {
      id: 'sql-gcp-001',
      provider: 'gcp',
      type: 'database',
      name: 'cloudsql-prod',
      region: 'us-central1',
      status: 'running',
      instanceType: 'db-n1-standard-2',
      engine: 'postgres',
      monthlyCost: 155.60,
      tags: { environment: 'production' }
    },
    {
      id: 'bucket-gcp-001',
      provider: 'gcp',
      type: 'storage',
      name: 'bucket-media',
      region: 'us-central1',
      status: 'active',
      sizeGB: 3500.0,
      storageClass: 'STANDARD',
      monthlyCost: 70.00,
      tags: { 'data-type': 'media' }
    },
  ];

  return [...awsResources, ...azureResources, ...gcpResources];
};

// Calculate multi-cloud summary
export const calculateMultiCloudSummary = (resources) => {
  const summary = {
    total: resources.length,
    totalCost: 0,
    byProvider: {
      aws: { count: 0, cost: 0 },
      azure: { count: 0, cost: 0 },
      gcp: { count: 0, cost: 0 },
    },
    byType: {
      compute: { count: 0, cost: 0 },
      database: { count: 0, cost: 0 },
      storage: { count: 0, cost: 0 },
    },
  };

  resources.forEach((resource) => {
    const cost = resource.monthlyCost || 0;
    summary.totalCost += cost;

    // By provider
    if (summary.byProvider[resource.provider]) {
      summary.byProvider[resource.provider].count++;
      summary.byProvider[resource.provider].cost += cost;
    }

    // By type
    if (summary.byType[resource.type]) {
      summary.byType[resource.type].count++;
      summary.byType[resource.type].cost += cost;
    }
  });

  return summary;
};

// Filter resources by provider
export const filterResourcesByProvider = (resources, provider) => {
  if (provider === 'all') return resources;
  return resources.filter((r) => r.provider === provider);
};

// Generate provider breakdown for pie chart
export const generateProviderBreakdown = (summary) => {
  return [
    {
      name: 'AWS',
      value: summary.byProvider.aws.cost,
      percentage: ((summary.byProvider.aws.cost / summary.totalCost) * 100).toFixed(1),
      color: '#FF9900', // AWS Orange
    },
    {
      name: 'Azure',
      value: summary.byProvider.azure.cost,
      percentage: ((summary.byProvider.azure.cost / summary.totalCost) * 100).toFixed(1),
      color: '#0089D6', // Azure Blue
    },
    {
      name: 'GCP',
      value: summary.byProvider.gcp.cost,
      percentage: ((summary.byProvider.gcp.cost / summary.totalCost) * 100).toFixed(1),
      color: '#EA4335', // GCP Red
    },
  ];
};

export const mockMultiCloudData = {
  resources: generateMultiCloudResources(),
  summary: null, // Will be calculated
};

// Initialize summary
mockMultiCloudData.summary = calculateMultiCloudSummary(mockMultiCloudData.resources);
