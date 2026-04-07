export const PROVIDER_LABELS = {
  aws: 'AWS',
  azure: 'Azure',
  gcp: 'GCP',
};

export const ALERT_SEVERITY_RANK = {
  low: 0,
  medium: 1,
  high: 2,
  critical: 3,
};

export function getInitials(user) {
  const name = user?.full_name || user?.name;

  if (name) {
    return name
      .split(' ')
      .slice(0, 2)
      .map((part) => part.charAt(0).toUpperCase())
      .join('');
  }

  return user?.email?.slice(0, 2).toUpperCase() || 'CW';
}

export function normalizeSearchQuery(query = '') {
  return query.trim().toLowerCase();
}

export function aggregateRegionCosts(services) {
  const totals = services.reduce((accumulator, service) => {
    accumulator[service.region] = (accumulator[service.region] || 0) + service.monthlyCost;
    return accumulator;
  }, {});

  return Object.entries(totals)
    .map(([region, cost]) => ({
      region,
      cost: Math.round(cost * 100) / 100,
    }))
    .sort((left, right) => right.cost - left.cost);
}

export function filterServices({ services, selectedProvider = 'all', query = '' }) {
  const normalizedQuery = normalizeSearchQuery(query);
  const providerFilteredServices = services.filter((service) =>
    selectedProvider === 'all' ? true : service.provider === selectedProvider
  );

  return providerFilteredServices.filter((service) => {
    if (!normalizedQuery) {
      return true;
    }

    return [
      service.service,
      PROVIDER_LABELS[service.provider],
      service.region,
      service.status,
      service.recommendation,
      service.owner,
      service.riskLevel,
    ].some((value) => value.toLowerCase().includes(normalizedQuery));
  });
}

export function filterAlerts({
  alerts,
  selectedProvider = 'all',
  minimumSeverity = 'all',
  query = '',
}) {
  const normalizedQuery = normalizeSearchQuery(query);

  return alerts.filter((alert) => {
    const providerMatches = selectedProvider === 'all' ? true : alert.provider === selectedProvider;
    const severityMatches = minimumSeverity === 'all'
      ? true
      : ALERT_SEVERITY_RANK[alert.severity] >= ALERT_SEVERITY_RANK[minimumSeverity];

    if (!providerMatches || !severityMatches) {
      return false;
    }

    if (!normalizedQuery) {
      return true;
    }

    return [
      alert.title,
      alert.message,
      alert.action,
      alert.owner,
      alert.impact,
      alert.nextStep,
    ].some((value) => value.toLowerCase().includes(normalizedQuery));
  });
}

function escapeCsvValue(value) {
  const stringValue = String(value ?? '');

  if (/[",\n]/.test(stringValue)) {
    return `"${stringValue.replace(/"/g, '""')}"`;
  }

  return stringValue;
}

export function buildDashboardExportCsv({
  providerBreakdown,
  services,
  regions,
  regionProviderLabel = 'Multi-cloud',
}) {
  const rows = [
    ['section', 'name', 'provider', 'value'],
    ...providerBreakdown.map((provider) => [
      'provider',
      provider.label,
      provider.label,
      provider.value,
    ]),
    ...services.map((service) => [
      'service',
      service.service,
      PROVIDER_LABELS[service.provider],
      service.monthlyCost,
    ]),
    ...regions.map((region) => [
      'region',
      region.region,
      regionProviderLabel,
      region.cost,
    ]),
  ];

  return rows.map((row) => row.map(escapeCsvValue).join(',')).join('\n');
}
