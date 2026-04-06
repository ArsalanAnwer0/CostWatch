import React, { useDeferredValue, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { LoadingSpinner, Toast } from '../components';
import { STORAGE_KEYS } from '../constants';
import { DashboardService } from '../services/api';
import { formatCompactNumber, formatCurrency } from '../utils';
import {
  buildDashboardModel,
  DASHBOARD_NAV_SECTIONS,
  PROVIDER_CONFIG,
  TIME_RANGE_OPTIONS,
} from '../data/dashboardData';
import './DashboardPage.css';
import '../styles/animations.css';

const PROVIDER_LABELS = PROVIDER_CONFIG.reduce((lookup, provider) => {
  lookup[provider.key] = provider.label;
  return lookup;
}, {});

function SpendTooltip({ active, label, payload }) {
  if (!active || !payload?.length) {
    return null;
  }

  const total = payload.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip-label">{label}</div>
      <div className="chart-tooltip-value">{formatCurrency(total)}</div>
      {payload.map((item) => (
        <div className="chart-tooltip-row" key={item.dataKey}>
          <span className="chart-tooltip-swatch" style={{ background: item.color }}></span>
          <span>{PROVIDER_LABELS[item.dataKey]}</span>
          <strong>{formatCurrency(item.value)}</strong>
        </div>
      ))}
    </div>
  );
}

function DonutTooltip({ active, payload }) {
  if (!active || !payload?.length) {
    return null;
  }

  const datum = payload[0].payload;

  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip-label">{datum.label}</div>
      <div className="chart-tooltip-value">{formatCurrency(datum.value)}</div>
      <div className="chart-tooltip-subtle">
        {Math.round((datum.value / datum.total) * 100)}% of current spend
      </div>
    </div>
  );
}

function RegionTooltip({ active, payload, label }) {
  if (!active || !payload?.length) {
    return null;
  }

  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip-label">{label}</div>
      <div className="chart-tooltip-value">{formatCurrency(payload[0].value)}</div>
    </div>
  );
}

function MetricCard({ metric }) {
  const value = metric.formattedValue || formatCurrency(metric.value);
  const trendLabel = metric.trend === 'positive' ? 'Improvement' : metric.trend === 'warning' ? 'Watchlist' : 'Change';

  return (
    <article className={`metric-card metric-card-${metric.trend} stagger-item`}>
      <div className="metric-card-topline">
        <span className="metric-card-title">{metric.title}</span>
        <span className="metric-card-badge">{metric.badge}</span>
      </div>
      <div className="metric-card-value">{value}</div>
      <div className="metric-card-footer">
        <span className="metric-card-delta">{trendLabel} {metric.delta.toFixed(1)}%</span>
        <span className="metric-card-detail">{metric.detail}</span>
      </div>
    </article>
  );
}

function getInitials(user) {
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

function parseUser() {
  try {
    const rawUser = localStorage.getItem(STORAGE_KEYS.USER_DATA);
    return rawUser ? JSON.parse(rawUser) : null;
  } catch (error) {
    return null;
  }
}

async function loadDashboardSnapshot() {
  const requests = await Promise.allSettled([
    DashboardService.getMonthly(),
    DashboardService.getSummary('90d'),
    DashboardService.getResources(),
    DashboardService.getServicesHealth(),
  ]);

  return {
    monthly: requests[0].status === 'fulfilled' ? requests[0].value : null,
    summary: requests[1].status === 'fulfilled' ? requests[1].value : null,
    resources: requests[2].status === 'fulfilled' ? requests[2].value : null,
    servicesHealth: requests[3].status === 'fulfilled' ? requests[3].value : null,
  };
}

function DashboardPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedRange, setSelectedRange] = useState('6m');
  const [searchQuery, setSearchQuery] = useState('');
  const [dashboardSnapshot, setDashboardSnapshot] = useState({});
  const [user, setUser] = useState(null);
  const [toast, setToast] = useState(null);
  const deferredSearchQuery = useDeferredValue(searchQuery);

  const dashboardData = buildDashboardModel({
    ...dashboardSnapshot,
    range: selectedRange,
  });

  const totalSpend = dashboardData.providerBreakdown.reduce((sum, provider) => sum + provider.value, 0);
  const normalizedQuery = deferredSearchQuery.trim().toLowerCase();
  const filteredServices = dashboardData.services.filter((service) => {
    if (!normalizedQuery) {
      return true;
    }

    return [
      service.service,
      PROVIDER_LABELS[service.provider],
      service.region,
      service.status,
      service.recommendation,
    ].some((value) => value.toLowerCase().includes(normalizedQuery));
  });
  const filteredAlerts = dashboardData.alerts.filter((alert) => {
    if (!normalizedQuery) {
      return true;
    }

    return [alert.title, alert.message, alert.action].some((value) =>
      value.toLowerCase().includes(normalizedQuery)
    );
  });

  const refreshDashboard = async ({ showToast = false } = {}) => {
    setRefreshing(true);

    try {
      const snapshot = await loadDashboardSnapshot();
      setDashboardSnapshot(snapshot);

      if (showToast) {
        setToast({
          type: 'success',
          message: 'Dashboard refreshed with the latest cloud spend signals.',
        });
      }
    } catch (error) {
      if (showToast) {
        setToast({
          type: 'warning',
          message: 'Live services were unavailable, so the dashboard stayed on curated demo data.',
        });
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);

    if (!token) {
      navigate('/login');
      return;
    }

    setUser(parseUser());
    refreshDashboard();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER_DATA);
    navigate('/');
  };

  const handleQuickAction = async (actionId) => {
    if (actionId === 'export-data') {
      const rows = [
        ['section', 'name', 'provider', 'value'],
        ...dashboardData.providerBreakdown.map((provider) => [
          'provider',
          provider.label,
          provider.label,
          provider.value,
        ]),
        ...dashboardData.services.map((service) => [
          'service',
          service.service,
          PROVIDER_LABELS[service.provider],
          service.monthlyCost,
        ]),
        ...dashboardData.regions.map((region) => [
          'region',
          region.region,
          'multi-cloud',
          region.cost,
        ]),
      ];
      const csv = rows.map((row) => row.join(',')).join('\n');
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');

      link.href = url;
      link.download = 'costwatch-dashboard-export.csv';
      link.click();
      URL.revokeObjectURL(url);

      setToast({
        type: 'success',
        message: 'Dashboard data exported for finance and ops workflows.',
      });
      return;
    }

    if (actionId === 'refresh-inventory') {
      await refreshDashboard({ showToast: true });
      return;
    }

    if (actionId === 'generate-report') {
      setToast({
        type: 'info',
        message: 'Executive summary generation has been queued with the current dashboard filters.',
      });
      return;
    }

    setToast({
      type: 'info',
      message: 'Optimization workflow staged. Next step is prioritizing the highest-confidence savings playbooks.',
    });
  };

  if (loading) {
    return <LoadingSpinner fullPage size="large" text="Assembling your command center..." />;
  }

  return (
    <div className="dashboard-shell">
      <aside className="dashboard-sidebar">
        <div className="sidebar-brand">
          <div className="brand-mark">CW</div>
          <div>
            <h1>CostWatch</h1>
            <p>AI cost intelligence</p>
          </div>
        </div>

        <div className="sidebar-health-card">
          <span className={`sidebar-health-indicator status-${dashboardData.meta.overallHealth}`}></span>
          <div>
            <strong>{dashboardData.meta.liveDataAvailable ? 'Live cloud telemetry' : 'Demo intelligence mode'}</strong>
            <p>{dashboardData.meta.lastUpdatedLabel}</p>
          </div>
        </div>

        <nav className="sidebar-navigation">
          {DASHBOARD_NAV_SECTIONS.map((section) => (
            <div className="sidebar-section" key={section.title}>
              <div className="sidebar-section-title">{section.title}</div>
              {section.items.map((item) => (
                <button
                  type="button"
                  className={`sidebar-nav-item ${item.active ? 'active' : ''}`}
                  key={item.id}
                >
                  <span className="sidebar-nav-icon">{item.shortLabel}</span>
                  <span>{item.label}</span>
                </button>
              ))}
            </div>
          ))}
        </nav>

        <div className="provider-status-list">
          <div className="sidebar-section-title">Provider Status</div>
          {dashboardData.providerStatuses.map((provider) => (
            <div className="provider-status-card" key={provider.key}>
              <div className="provider-status-header">
                <span
                  className="provider-status-badge"
                  style={{ color: provider.accent, background: provider.accentSoft }}
                >
                  {provider.shortLabel}
                </span>
                <div>
                  <strong>{provider.label}</strong>
                  <p>{provider.statusLabel}</p>
                </div>
              </div>
              <div className="provider-status-footer">
                <span>{formatCurrency(provider.spend)}</span>
                <span>{provider.resources} assets</span>
                <span className={`status-pill status-pill-${provider.state.toLowerCase()}`}>{provider.state}</span>
              </div>
            </div>
          ))}
        </div>
      </aside>

      <main className="dashboard-main">
        <header className="dashboard-header">
          <div className="dashboard-title-block">
            <p className="dashboard-eyebrow">Unified multi-cloud control room</p>
            <h2>Cloud spend command center</h2>
            <p className="dashboard-subtitle">
              Monitor real-time cost posture, surface anomalies, and push optimizations across AWS, Azure, and GCP.
            </p>
          </div>

          <div className="dashboard-toolbar">
            <label className="dashboard-search">
              <span>Search</span>
              <input
                type="search"
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                placeholder="Search services, alerts, regions, or recommendations"
              />
            </label>

            <label className="dashboard-range-picker">
              <span>Time range</span>
              <select value={selectedRange} onChange={(event) => setSelectedRange(event.target.value)}>
                {TIME_RANGE_OPTIONS.map((option) => (
                  <option value={option.value} key={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>

            <button
              type="button"
              className="dashboard-icon-button"
              onClick={() => refreshDashboard({ showToast: true })}
              disabled={refreshing}
              aria-label="Refresh dashboard"
            >
              {refreshing ? '...' : 'RF'}
            </button>

            <button type="button" className="dashboard-icon-button dashboard-icon-button-notification" aria-label="Notifications">
              NT
              <span className="notification-count">{dashboardData.meta.unreadAlerts}</span>
            </button>

            <div className="dashboard-user-menu">
              <div className="dashboard-user-avatar">{getInitials(user)}</div>
              <div className="dashboard-user-details">
                <strong>{user?.full_name || 'Cost operator'}</strong>
                <span>{user?.email || 'Multi-cloud workspace'}</span>
              </div>
              <button type="button" className="dashboard-ghost-button" onClick={handleLogout}>
                Logout
              </button>
            </div>
          </div>
        </header>

        <section className="dashboard-hero">
          <div className="dashboard-hero-copy">
            <div className="dashboard-hero-chip">
              <span className="status-dot"></span>
              Budgets healthy across 3 providers
            </div>
            <h3>Sharper cost visibility for a fast-moving AI startup</h3>
            <p>
              Your spend profile is concentrated in compute-heavy workloads, with the strongest short-term savings in
              AWS fleet rightsizing and Azure database elasticity.
            </p>
          </div>

          <div className="dashboard-hero-actions">
            <button type="button" className="dashboard-primary-button" onClick={() => handleQuickAction('generate-report')}>
              Generate report
            </button>
            <button type="button" className="dashboard-secondary-button" onClick={() => handleQuickAction('export-data')}>
              Export data
            </button>
          </div>
        </section>

        <section className="dashboard-metrics">
          {dashboardData.metrics.map((metric) => (
            <MetricCard metric={metric} key={metric.title} />
          ))}
        </section>

        <section className="dashboard-grid">
          <article className="dashboard-panel panel-span-2">
            <div className="panel-header">
              <div>
                <p className="panel-eyebrow">Spending Trends</p>
                <h3>Monthly spend by provider</h3>
              </div>
              <div className="panel-metric">
                <span>Total run rate</span>
                <strong>{formatCurrency(totalSpend)}</strong>
              </div>
            </div>

            <div className="chart-container chart-container-large">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={dashboardData.spendingTrend}>
                  <defs>
                    <linearGradient id="awsGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#f59e0b" stopOpacity={0.6} />
                      <stop offset="100%" stopColor="#f59e0b" stopOpacity={0.05} />
                    </linearGradient>
                    <linearGradient id="azureGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#38bdf8" stopOpacity={0.58} />
                      <stop offset="100%" stopColor="#38bdf8" stopOpacity={0.06} />
                    </linearGradient>
                    <linearGradient id="gcpGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#22c55e" stopOpacity={0.5} />
                      <stop offset="100%" stopColor="#22c55e" stopOpacity={0.05} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke="rgba(148, 163, 184, 0.12)" vertical={false} />
                  <XAxis dataKey="label" stroke="#7c8aa5" tickLine={false} axisLine={false} />
                  <YAxis
                    stroke="#7c8aa5"
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => `$${formatCompactNumber(value)}`}
                  />
                  <Tooltip content={<SpendTooltip />} />
                  <Area type="monotone" dataKey="aws" stackId="1" stroke="#f59e0b" fill="url(#awsGradient)" strokeWidth={2} />
                  <Area type="monotone" dataKey="azure" stackId="1" stroke="#38bdf8" fill="url(#azureGradient)" strokeWidth={2} />
                  <Area type="monotone" dataKey="gcp" stackId="1" stroke="#22c55e" fill="url(#gcpGradient)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-legend-list">
              {dashboardData.providerBreakdown.map((provider) => (
                <div className="chart-legend-item" key={provider.key}>
                  <span className="chart-legend-dot" style={{ background: provider.accent }}></span>
                  <span>{provider.label}</span>
                  <strong>{formatCurrency(provider.value)}</strong>
                </div>
              ))}
            </div>
          </article>

          <article className="dashboard-panel">
            <div className="panel-header">
              <div>
                <p className="panel-eyebrow">Provider Breakdown</p>
                <h3>Cost distribution</h3>
              </div>
            </div>

            <div className="donut-panel">
              <div className="chart-container chart-container-medium">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={dashboardData.providerBreakdown.map((provider) => ({
                        ...provider,
                        total: totalSpend,
                      }))}
                      dataKey="value"
                      nameKey="label"
                      innerRadius={84}
                      outerRadius={112}
                      paddingAngle={5}
                    >
                      {dashboardData.providerBreakdown.map((provider) => (
                        <Cell key={provider.key} fill={provider.accent} />
                      ))}
                    </Pie>
                    <Tooltip content={<DonutTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="donut-chart-center">
                <span>Monthly spend</span>
                <strong>{formatCurrency(totalSpend)}</strong>
              </div>

              <div className="provider-breakdown-list">
                {dashboardData.providerBreakdown.map((provider) => (
                  <div className="provider-breakdown-row" key={provider.key}>
                    <div className="provider-breakdown-label">
                      <span className="chart-legend-dot" style={{ background: provider.accent }}></span>
                      <span>{provider.label}</span>
                    </div>
                    <strong>{Math.round((provider.value / totalSpend) * 100)}%</strong>
                  </div>
                ))}
              </div>
            </div>
          </article>

          <article className="dashboard-panel">
            <div className="panel-header">
              <div>
                <p className="panel-eyebrow">Alerts Panel</p>
                <h3>Live anomalies and recommendations</h3>
              </div>
              <span className="panel-badge">{filteredAlerts.length} active</span>
            </div>

            <div className="alerts-list">
              {filteredAlerts.map((alert) => (
                <div className={`alert-card alert-card-${alert.severity}`} key={alert.title}>
                  <div className="alert-card-topline">
                    <span className={`severity-pill severity-pill-${alert.severity}`}>{alert.severity}</span>
                    <span className="alert-time">{alert.time}</span>
                  </div>
                  <h4>{alert.title}</h4>
                  <p>{alert.message}</p>
                  <button type="button" className="panel-inline-action">
                    {alert.action}
                  </button>
                </div>
              ))}
            </div>
          </article>

          <article className="dashboard-panel panel-span-2">
            <div className="panel-header">
              <div>
                <p className="panel-eyebrow">Services Table</p>
                <h3>Detailed service cost breakdown</h3>
              </div>
              <span className="panel-badge">
                {filteredServices.length} services {normalizedQuery ? 'matching search' : 'tracked'}
              </span>
            </div>

            <div className="services-table-wrapper">
              <table className="services-table">
                <thead>
                  <tr>
                    <th>Service</th>
                    <th>Provider</th>
                    <th>Region</th>
                    <th>Status</th>
                    <th>Trend</th>
                    <th>Monthly cost</th>
                    <th>Recommendation</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredServices.map((service) => (
                    <tr key={`${service.provider}-${service.service}`}>
                      <td>
                        <div className="service-name-cell">
                          <strong>{service.service}</strong>
                          <span>{service.weight * 100}% of mapped spend</span>
                        </div>
                      </td>
                      <td>
                        <span
                          className="provider-chip"
                          style={{
                            color: PROVIDER_CONFIG.find((provider) => provider.key === service.provider)?.accent,
                            background: PROVIDER_CONFIG.find((provider) => provider.key === service.provider)?.accentSoft,
                          }}
                        >
                          {PROVIDER_LABELS[service.provider]}
                        </span>
                      </td>
                      <td>{service.region}</td>
                      <td>
                        <span className={`status-pill status-pill-${service.status.toLowerCase().replace(/\s+/g, '-')}`}>
                          {service.status}
                        </span>
                      </td>
                      <td>
                        <span className={`trend-pill trend-pill-${service.trend}`}>
                          {service.change > 0 ? '+' : ''}
                          {service.change.toFixed(1)}%
                        </span>
                      </td>
                      <td>{formatCurrency(service.monthlyCost)}</td>
                      <td>{service.recommendation}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </article>

          <div className="dashboard-stack">
            <article className="dashboard-panel">
              <div className="panel-header">
                <div>
                  <p className="panel-eyebrow">Budget Tracker</p>
                  <h3>Budget utilization by provider</h3>
                </div>
              </div>

              <div className="budget-list">
                {dashboardData.budgets.map((budget) => (
                  <div className="budget-card" key={budget.key}>
                    <div className="budget-card-header">
                      <div className="provider-breakdown-label">
                        <span className="chart-legend-dot" style={{ background: budget.accent }}></span>
                        <span>{budget.label}</span>
                      </div>
                      <strong>{Math.round(budget.utilization)}%</strong>
                    </div>
                    <div className="budget-progress-track">
                      <div
                        className="budget-progress-fill"
                        style={{
                          width: `${Math.min(budget.utilization, 100)}%`,
                          background: budget.accent,
                        }}
                      ></div>
                    </div>
                    <div className="budget-card-footer">
                      <span>{formatCurrency(budget.value)} used</span>
                      <span>{formatCurrency(budget.remaining)} remaining</span>
                    </div>
                  </div>
                ))}
              </div>
            </article>

            <article className="dashboard-panel">
              <div className="panel-header">
                <div>
                  <p className="panel-eyebrow">Quick Actions</p>
                  <h3>Common operator workflows</h3>
                </div>
              </div>

              <div className="quick-actions-grid">
                {dashboardData.quickActions.map((action) => (
                  <button
                    type="button"
                    className="quick-action-card"
                    key={action.id}
                    onClick={() => handleQuickAction(action.id)}
                  >
                    <span className="quick-action-eyebrow">{action.eyebrow}</span>
                    <strong>{action.title}</strong>
                    <p>{action.description}</p>
                  </button>
                ))}
              </div>
            </article>
          </div>

          <article className="dashboard-panel panel-span-2">
            <div className="panel-header">
              <div>
                <p className="panel-eyebrow">Cost by Region</p>
                <h3>Geographic spend distribution</h3>
              </div>
              <span className="panel-badge">Top regions by cost</span>
            </div>

            <div className="chart-container chart-container-medium">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={dashboardData.regions} layout="vertical" margin={{ left: 12, right: 12 }}>
                  <CartesianGrid stroke="rgba(148, 163, 184, 0.1)" horizontal={false} />
                  <XAxis
                    type="number"
                    stroke="#7c8aa5"
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => `$${formatCompactNumber(value)}`}
                  />
                  <YAxis
                    type="category"
                    dataKey="region"
                    stroke="#7c8aa5"
                    tickLine={false}
                    axisLine={false}
                    width={110}
                  />
                  <Tooltip content={<RegionTooltip />} />
                  <Bar dataKey="cost" radius={[0, 10, 10, 0]}>
                    {dashboardData.regions.map((region, index) => (
                      <Cell
                        key={region.region}
                        fill={['#f59e0b', '#fbbf24', '#38bdf8', '#60a5fa', '#22c55e', '#86efac'][index]}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </article>
        </section>
      </main>

      {toast && (
        <Toast
          type={toast.type}
          message={toast.message}
          onClose={() => setToast(null)}
          duration={4000}
        />
      )}
    </div>
  );
}

export default DashboardPage;
