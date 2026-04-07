import {
  aggregateRegionCosts,
  buildDashboardExportCsv,
  filterAlerts,
  filterServices,
  getInitials,
  PROVIDER_LABELS,
} from './dashboardUtils';

describe('dashboardUtils', () => {
  it('maps provider keys to readable labels', () => {
    expect(PROVIDER_LABELS.aws).toBe('AWS');
    expect(PROVIDER_LABELS.azure).toBe('Azure');
    expect(PROVIDER_LABELS.gcp).toBe('GCP');
  });

  it('builds initials from a user full name', () => {
    expect(getInitials({ full_name: 'Taylor Nguyen' })).toBe('TN');
  });

  it('falls back to email initials when a name is not available', () => {
    expect(getInitials({ email: 'owner@costwatch.com' })).toBe('OW');
  });

  it('returns the product fallback when no user details exist', () => {
    expect(getInitials(null)).toBe('CW');
  });

  it('filters services by provider and search query', () => {
    const services = [
      {
        service: 'Amazon EC2 Fleet',
        provider: 'aws',
        region: 'us-east-1',
        status: 'Healthy',
        recommendation: 'Tune node pools',
        owner: 'Platform runtime',
        riskLevel: 'Medium',
      },
      {
        service: 'BigQuery Analytics',
        provider: 'gcp',
        region: 'us-central1',
        status: 'Attention',
        recommendation: 'Reduce slot usage',
        owner: 'Applied AI',
        riskLevel: 'High',
      },
    ];

    expect(filterServices({ services, selectedProvider: 'aws', query: 'node' })).toHaveLength(1);
    expect(filterServices({ services, selectedProvider: 'aws', query: 'bigquery' })).toHaveLength(0);
  });

  it('filters alerts by exact provider, minimum severity, and search text', () => {
    const alerts = [
      {
        severity: 'critical',
        provider: 'aws',
        title: 'AWS compute spend is over baseline',
        message: 'Autoscaling is rising',
        action: 'Review scaling policy',
        owner: 'Platform runtime',
        impact: '$9.4K projected overrun',
        nextStep: 'Lower overnight floor',
      },
      {
        severity: 'medium',
        provider: 'gcp',
        title: 'GCP storage growth is accelerating',
        message: 'Retention is trending up',
        action: 'Apply lifecycle policy',
        owner: 'Media delivery',
        impact: '$2.2K monthly drift',
        nextStep: 'Tighten archive rules',
      },
    ];

    const filtered = filterAlerts({
      alerts,
      selectedProvider: 'aws',
      minimumSeverity: 'high',
      query: 'scaling',
    });

    expect(filtered).toHaveLength(1);
    expect(filtered[0].provider).toBe('aws');
  });

  it('aggregates region costs into descending totals', () => {
    const regions = aggregateRegionCosts([
      { region: 'us-east-1', monthlyCost: 3200.2 },
      { region: 'us-east-1', monthlyCost: 799.8 },
      { region: 'eu-west-1', monthlyCost: 1200 },
    ]);

    expect(regions).toEqual([
      { region: 'us-east-1', cost: 4000 },
      { region: 'eu-west-1', cost: 1200 },
    ]);
  });

  it('builds csv output with proper escaping', () => {
    const csv = buildDashboardExportCsv({
      providerBreakdown: [{ label: 'AWS', value: 120000 }],
      services: [{ service: 'Cloud Storage, CDN', provider: 'gcp', monthlyCost: 4200 }],
      regions: [{ region: 'US East', cost: 6400 }],
      regionProviderLabel: 'Filtered view',
    });

    expect(csv).toContain('"Cloud Storage, CDN"');
    expect(csv).toContain('region,US East,Filtered view,6400');
  });
});
