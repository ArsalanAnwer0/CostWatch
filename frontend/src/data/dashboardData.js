const FALLBACK_MONTHLY_SPEND = 184320;

const MONTH_RATIO_TEMPLATE = [
  0.72,
  0.76,
  0.81,
  0.86,
  0.89,
  0.93,
  0.96,
  0.99,
  1.03,
  1.07,
  1.04,
  1,
];

const AWS_SHARE_TEMPLATE = [
  0.54,
  0.53,
  0.53,
  0.52,
  0.52,
  0.51,
  0.51,
  0.5,
  0.5,
  0.49,
  0.49,
  0.48,
];

const AZURE_SHARE_TEMPLATE = [
  0.28,
  0.29,
  0.29,
  0.3,
  0.3,
  0.31,
  0.31,
  0.32,
  0.32,
  0.33,
  0.33,
  0.34,
];

export const TIME_RANGE_OPTIONS = [
  { value: '3m', label: '3 months', points: 3, apiPeriod: '30d' },
  { value: '6m', label: '6 months', points: 6, apiPeriod: '90d' },
  { value: '12m', label: '12 months', points: 12, apiPeriod: '90d' },
];

export const PROVIDER_CONFIG = [
  {
    key: 'aws',
    label: 'AWS',
    shortLabel: 'AW',
    accent: '#f59e0b',
    accentSoft: 'rgba(245, 158, 11, 0.18)',
    statusLabel: 'Streaming spend telemetry',
  },
  {
    key: 'azure',
    label: 'Azure',
    shortLabel: 'AZ',
    accent: '#38bdf8',
    accentSoft: 'rgba(56, 189, 248, 0.18)',
    statusLabel: 'Budgets and reservations synced',
  },
  {
    key: 'gcp',
    label: 'GCP',
    shortLabel: 'GC',
    accent: '#22c55e',
    accentSoft: 'rgba(34, 197, 94, 0.18)',
    statusLabel: 'Anomaly models calibrated',
  },
];

export const DASHBOARD_NAV_SECTIONS = [
  {
    title: 'Command Center',
    items: [
      { id: 'overview', label: 'Overview', shortLabel: 'OV', active: true },
      { id: 'spend', label: 'Spend Analysis', shortLabel: 'SA' },
      { id: 'alerts', label: 'Alerts', shortLabel: 'AL' },
    ],
  },
  {
    title: 'Optimization',
    items: [
      { id: 'budgets', label: 'Budgets', shortLabel: 'BG' },
      { id: 'services', label: 'Services', shortLabel: 'SV' },
      { id: 'regions', label: 'Regions', shortLabel: 'RG' },
    ],
  },
  {
    title: 'Operations',
    items: [
      { id: 'reports', label: 'Reports', shortLabel: 'RP' },
      { id: 'workflows', label: 'Workflows', shortLabel: 'WF' },
      { id: 'settings', label: 'Settings', shortLabel: 'ST' },
    ],
  },
];

const SERVICE_ROW_TEMPLATES = [
  {
    service: 'Elastic Kubernetes Service',
    provider: 'aws',
    region: 'us-east-1',
    status: 'Healthy',
    trend: 'up',
    change: 8.4,
    weight: 0.19,
    utilization: '72%',
    efficiencyScore: 84,
    owner: 'Platform runtime',
    riskLevel: 'Medium',
    runbook: 'Reduce baseline nodes overnight and move burst traffic to spot-backed pools.',
    recommendation: 'Tune node pools for off-peak traffic',
  },
  {
    service: 'Azure SQL Elastic Pools',
    provider: 'azure',
    region: 'eastus2',
    status: 'Attention',
    trend: 'up',
    change: 6.1,
    weight: 0.16,
    utilization: '81%',
    efficiencyScore: 69,
    owner: 'Data platform',
    riskLevel: 'High',
    runbook: 'Split write-heavy tenants into serverless pools and rebalance peak workloads.',
    recommendation: 'Shift idle capacity to serverless tiers',
  },
  {
    service: 'BigQuery Analytics',
    provider: 'gcp',
    region: 'us-central1',
    status: 'Healthy',
    trend: 'down',
    change: -4.7,
    weight: 0.12,
    utilization: '63%',
    efficiencyScore: 88,
    owner: 'ML insights',
    riskLevel: 'Low',
    runbook: 'Lock in committed slots for recurring workloads and tighten job priority rules.',
    recommendation: 'Commit slot reservations for nightly jobs',
  },
  {
    service: 'Amazon EC2 Fleet',
    provider: 'aws',
    region: 'eu-west-1',
    status: 'Optimized',
    trend: 'down',
    change: -9.2,
    weight: 0.14,
    utilization: '67%',
    efficiencyScore: 91,
    owner: 'Core application',
    riskLevel: 'Low',
    runbook: 'Maintain savings-plan coverage and keep the spot interruption playbook current.',
    recommendation: 'Savings plan coverage is working well',
  },
  {
    service: 'Azure Kubernetes Service',
    provider: 'azure',
    region: 'westeurope',
    status: 'Healthy',
    trend: 'up',
    change: 3.9,
    weight: 0.1,
    utilization: '69%',
    efficiencyScore: 78,
    owner: 'Growth engineering',
    riskLevel: 'Medium',
    runbook: 'Shift non-critical jobs to lower-cost node pools and cap baseline autoscaling.',
    recommendation: 'Rightsize baseline node groups',
  },
  {
    service: 'Cloud Storage + CDN',
    provider: 'gcp',
    region: 'europe-west1',
    status: 'Watch',
    trend: 'up',
    change: 5.2,
    weight: 0.08,
    utilization: '57%',
    efficiencyScore: 71,
    owner: 'Media delivery',
    riskLevel: 'Medium',
    runbook: 'Archive cold objects aggressively and reduce duplicate edge-caching rules.',
    recommendation: 'Apply lifecycle rules to archive cold assets',
  },
  {
    service: 'Amazon RDS Aurora',
    provider: 'aws',
    region: 'ap-southeast-1',
    status: 'Healthy',
    trend: 'up',
    change: 2.8,
    weight: 0.09,
    utilization: '74%',
    efficiencyScore: 80,
    owner: 'Customer data',
    riskLevel: 'Medium',
    runbook: 'Review burst credits before quarter close and stagger replica-intensive workloads.',
    recommendation: 'Review burst capacity before quarter close',
  },
  {
    service: 'Vertex AI Training',
    provider: 'gcp',
    region: 'us-west1',
    status: 'Attention',
    trend: 'up',
    change: 11.8,
    weight: 0.07,
    utilization: '86%',
    efficiencyScore: 64,
    owner: 'Applied AI',
    riskLevel: 'High',
    runbook: 'Reschedule experiments into discounted windows and cap concurrent training jobs.',
    recommendation: 'Schedule experiments into discounted windows',
  },
];

const ALERT_TEMPLATES = [
  {
    severity: 'critical',
    title: 'AWS compute spend is 18% over baseline',
    message: 'A production autoscaling group is expanding earlier than expected in us-east-1.',
    action: 'Review scaling policy',
    time: '2 minutes ago',
  },
  {
    severity: 'high',
    title: 'Azure database budget will breach within 4 days',
    message: 'Elastic pool usage has risen steadily for the last three billing windows.',
    action: 'Inspect workload split',
    time: '19 minutes ago',
  },
  {
    severity: 'medium',
    title: 'GCP storage growth trend is accelerating',
    message: 'Object storage retention is trending 11% above plan after the latest ingestion burst.',
    action: 'Apply lifecycle policy',
    time: '51 minutes ago',
  },
  {
    severity: 'low',
    title: 'Reserved instance coverage opportunity detected',
    message: 'Steady EC2 workloads are eligible for better committed spend pricing.',
    action: 'Open savings playbook',
    time: '2 hours ago',
  },
];

const REGION_TEMPLATES = [
  { region: 'US East', weight: 0.28 },
  { region: 'US West', weight: 0.19 },
  { region: 'Europe', weight: 0.21 },
  { region: 'Asia Pacific', weight: 0.17 },
  { region: 'Canada', weight: 0.09 },
  { region: 'South America', weight: 0.06 },
];

export const QUICK_ACTIONS = [
  {
    id: 'generate-report',
    eyebrow: 'Reporting',
    title: 'Generate executive summary',
    description: 'Package spend, forecast, and anomaly insights into a board-ready snapshot.',
  },
  {
    id: 'export-data',
    eyebrow: 'Data',
    title: 'Export current dashboard data',
    description: 'Download provider, service, and regional cost metrics for finance workflows.',
  },
  {
    id: 'refresh-inventory',
    eyebrow: 'Cloud Ops',
    title: 'Refresh cloud inventory',
    description: 'Re-sync resource coverage and surface new optimization opportunities.',
  },
  {
    id: 'open-optimizer',
    eyebrow: 'AI Copilot',
    title: 'Launch optimization workflow',
    description: 'Prioritize savings recommendations with the highest near-term impact.',
  },
];

const roundCurrency = (value) => Math.round(value * 100) / 100;

const getRangeConfig = (range) => {
  return TIME_RANGE_OPTIONS.find((option) => option.value === range) || TIME_RANGE_OPTIONS[1];
};

const getMonthLabel = (offsetFromCurrentMonth) => {
  const date = new Date();
  date.setDate(1);
  date.setMonth(date.getMonth() + offsetFromCurrentMonth);

  return date.toLocaleDateString('en-US', { month: 'short' });
};

const buildSpendingTrend = (baseSpend, range) => {
  const rangeConfig = getRangeConfig(range);
  const ratioWindow = MONTH_RATIO_TEMPLATE.slice(-rangeConfig.points);
  const awsWindow = AWS_SHARE_TEMPLATE.slice(-rangeConfig.points);
  const azureWindow = AZURE_SHARE_TEMPLATE.slice(-rangeConfig.points);

  return ratioWindow.map((ratio, index) => {
    const total = baseSpend * ratio;
    const aws = roundCurrency(total * awsWindow[index]);
    const azure = roundCurrency(total * azureWindow[index]);
    const gcp = roundCurrency(total - aws - azure);
    const monthOffset = -rangeConfig.points + index + 1;

    return {
      label: getMonthLabel(monthOffset),
      aws,
      azure,
      gcp,
      total: roundCurrency(total),
    };
  });
};

const buildProviderBreakdown = (currentSpend) => {
  const shares = {
    aws: 0.48,
    azure: 0.34,
    gcp: 0.18,
  };

  return PROVIDER_CONFIG.map((provider) => ({
    ...provider,
    value: roundCurrency(currentSpend * shares[provider.key]),
  }));
};

const buildBudgets = (providers) => {
  const utilizationTargets = {
    aws: 0.76,
    azure: 0.71,
    gcp: 0.68,
  };

  return providers.map((provider) => {
    const budget = roundCurrency(provider.value / utilizationTargets[provider.key]);
    const utilization = roundCurrency((provider.value / budget) * 100);

    return {
      ...provider,
      budget,
      utilization,
      remaining: roundCurrency(budget - provider.value),
    };
  });
};

const buildServices = (currentSpend) => {
  return SERVICE_ROW_TEMPLATES.map((template) => ({
    ...template,
    monthlyCost: roundCurrency(currentSpend * template.weight),
  }));
};

const buildRegions = (currentSpend) => {
  return REGION_TEMPLATES.map((region) => ({
    ...region,
    cost: roundCurrency(currentSpend * region.weight),
  })).sort((left, right) => right.cost - left.cost);
};

const buildMetrics = ({
  currentSpend,
  lastSpend,
  savingsPotential,
  budgets,
  totalResources,
}) => {
  const spendDelta = lastSpend > 0 ? ((currentSpend - lastSpend) / lastSpend) * 100 : 0;
  const projectedCost = roundCurrency(currentSpend * 1.11);
  const totalBudget = budgets.reduce((sum, budget) => sum + budget.budget, 0);
  const budgetUsed = totalBudget > 0 ? (currentSpend / totalBudget) * 100 : 0;

  return [
    {
      title: 'Total Spend',
      value: currentSpend,
      formattedValue: null,
      delta: Math.abs(spendDelta),
      trend: spendDelta <= 0 ? 'positive' : 'negative',
      detail: `Tracking ${totalResources} active resources this cycle`,
      badge: 'Live',
    },
    {
      title: 'Projected Cost',
      value: projectedCost,
      formattedValue: null,
      delta: 7.2,
      trend: 'negative',
      detail: 'Forecasted month-end run rate',
      badge: 'Forecast',
    },
    {
      title: 'Savings Potential',
      value: savingsPotential,
      formattedValue: null,
      delta: 13.4,
      trend: 'positive',
      detail: 'Recoverable from active recommendations',
      badge: 'AI',
    },
    {
      title: 'Budget Used',
      value: budgetUsed,
      formattedValue: `${Math.round(budgetUsed)}%`,
      delta: 4.1,
      trend: budgetUsed < 78 ? 'positive' : 'warning',
      detail: 'Across cloud budgets and spend commitments',
      badge: 'Budget',
    },
  ];
};

export const buildDashboardModel = ({
  monthly,
  summary,
  resources,
  servicesHealth,
  range = '6m',
} = {}) => {
  const liveMonthlySpend = monthly?.current_month_cost;
  const currentSpend = liveMonthlySpend || summary?.total_cost || FALLBACK_MONTHLY_SPEND;
  const lastSpend = monthly?.last_month_cost || currentSpend * 1.08;
  const totalResources =
    resources?.total ||
    monthly?.total_resources ||
    184;
  const savingsPotential = monthly?.savings_opportunity || summary?.savings_opportunity || currentSpend * 0.18;
  const liveDataAvailable = Boolean(monthly || summary || resources);

  const spendingTrend = buildSpendingTrend(currentSpend, range);
  const providerBreakdown = buildProviderBreakdown(spendingTrend[spendingTrend.length - 1].total);
  const budgets = buildBudgets(providerBreakdown);
  const services = buildServices(currentSpend);
  const regions = buildRegions(currentSpend);
  const metrics = buildMetrics({
    currentSpend,
    lastSpend,
    savingsPotential,
    budgets,
    totalResources,
  });

  const healthServices = servicesHealth?.services || {};

  return {
    metrics,
    spendingTrend,
    providerBreakdown,
    budgets,
    services,
    alerts: ALERT_TEMPLATES,
    regions,
    quickActions: QUICK_ACTIONS,
    providerStatuses: PROVIDER_CONFIG.map((provider) => ({
      ...provider,
      spend: providerBreakdown.find((entry) => entry.key === provider.key)?.value || 0,
      resources: provider.key === 'aws'
        ? totalResources
        : Math.round(totalResources * (provider.key === 'azure' ? 0.38 : 0.24)),
      state:
        provider.key === 'aws'
          ? (healthServices.resource_scanner === 'healthy' ? 'Live' : 'Fallback')
          : 'Connected',
    })),
    meta: {
      liveDataAvailable,
      totalResources,
      unreadAlerts: ALERT_TEMPLATES.filter((alert) => alert.severity === 'critical' || alert.severity === 'high').length,
      overallHealth: servicesHealth?.overall_status || (liveDataAvailable ? 'healthy' : 'demo'),
      lastUpdatedLabel: liveDataAvailable ? 'Updated moments ago' : 'Using curated demo intelligence',
    },
  };
};
