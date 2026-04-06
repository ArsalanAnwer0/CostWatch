import { buildDashboardModel, TIME_RANGE_OPTIONS } from './dashboardData';

describe('buildDashboardModel', () => {
  it('builds a consistent model from backend snapshot data', () => {
    const model = buildDashboardModel({
      monthly: {
        current_month_cost: 120000,
        last_month_cost: 132000,
        savings_opportunity: 22000,
        total_resources: 212,
      },
      servicesHealth: {
        overall_status: 'healthy',
        services: {
          resource_scanner: 'healthy',
          cost_service: 'healthy',
        },
      },
      range: '3m',
    });

    expect(model.metrics).toHaveLength(4);
    expect(model.spendingTrend).toHaveLength(
      TIME_RANGE_OPTIONS.find((option) => option.value === '3m').points
    );
    expect(model.providerBreakdown).toHaveLength(3);
    expect(model.budgets).toHaveLength(3);
    expect(model.meta.liveDataAvailable).toBe(true);
    expect(model.meta.totalResources).toBe(212);
    expect(model.meta.overallHealth).toBe('healthy');
  });

  it('falls back to curated demo intelligence when live data is unavailable', () => {
    const model = buildDashboardModel();

    expect(model.metrics[0].title).toBe('Total Spend');
    expect(model.meta.liveDataAvailable).toBe(false);
    expect(model.meta.overallHealth).toBe('demo');
    expect(model.providerStatuses.every((provider) => provider.spend > 0)).toBe(true);
  });
});
