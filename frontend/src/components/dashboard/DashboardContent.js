import React from 'react';
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
import { PROVIDER_CONFIG } from '../../data/dashboardData';
import { formatCompactNumber, formatCurrency } from '../../utils';
import { CloseIcon } from './DashboardIcons';
import { DonutTooltip, RegionTooltip, SpendTooltip } from './DashboardTooltips';
import { PROVIDER_LABELS } from './dashboardUtils';

const ALERT_SEVERITY_OPTIONS = [
  { value: 'all', label: 'All severities' },
  { value: 'critical', label: 'Critical only' },
  { value: 'high', label: 'High and above' },
  { value: 'medium', label: 'Medium and above' },
  { value: 'low', label: 'Low and above' },
];

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

function DashboardHero({ onQuickAction }) {
  return (
    <section className="dashboard-hero" id="overview">
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
        <button type="button" className="dashboard-primary-button" onClick={() => onQuickAction('generate-report')}>
          Generate report
        </button>
        <button type="button" className="dashboard-secondary-button" onClick={() => onQuickAction('export-data')}>
          Export data
        </button>
      </div>
    </section>
  );
}

function DashboardMetrics({ metrics }) {
  return (
    <section className="dashboard-metrics">
      {metrics.map((metric) => (
        <MetricCard metric={metric} key={metric.title} />
      ))}
    </section>
  );
}

function DashboardFilters({
  selectedProvider,
  selectedAlertSeverity,
  onProviderChange,
  onAlertSeverityChange,
  onReset,
}) {
  return (
    <section className="dashboard-filters">
      <div className="dashboard-filter-group">
        <span className="dashboard-filter-label">Provider focus</span>
        <div className="dashboard-filter-chips">
          <button
            type="button"
            className={`dashboard-filter-chip ${selectedProvider === 'all' ? 'active' : ''}`}
            onClick={() => onProviderChange('all')}
          >
            All providers
          </button>
          {PROVIDER_CONFIG.map((provider) => (
            <button
              type="button"
              key={provider.key}
              className={`dashboard-filter-chip ${selectedProvider === provider.key ? 'active' : ''}`}
              onClick={() => onProviderChange(provider.key)}
            >
              {provider.label}
            </button>
          ))}
        </div>
      </div>

      <div className="dashboard-filter-group dashboard-filter-group-inline">
        <span className="dashboard-filter-label">Alert threshold</span>
        <select
          className="dashboard-filter-select"
          value={selectedAlertSeverity}
          onChange={(event) => onAlertSeverityChange(event.target.value)}
        >
          {ALERT_SEVERITY_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <button type="button" className="dashboard-filter-reset" onClick={onReset}>
          Reset filters
        </button>
      </div>
    </section>
  );
}

function SpendingTrendsPanel({ spendingTrend, providerBreakdown, totalSpend, activeProviderKeys }) {
  return (
    <article className="dashboard-panel panel-span-2" id="spend">
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
          <AreaChart data={spendingTrend}>
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
            {activeProviderKeys.map((providerKey) => (
              <Area
                key={providerKey}
                type="monotone"
                dataKey={providerKey}
                stackId="1"
                stroke={providerKey === 'aws' ? '#f59e0b' : providerKey === 'azure' ? '#38bdf8' : '#22c55e'}
                fill={`url(#${providerKey}Gradient)`}
                strokeWidth={2}
              />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-legend-list">
        {providerBreakdown.map((provider) => (
          <div className="chart-legend-item" key={provider.key}>
            <span className="chart-legend-dot" style={{ background: provider.accent }}></span>
            <span>{provider.label}</span>
            <strong>{formatCurrency(provider.value)}</strong>
          </div>
        ))}
      </div>
    </article>
  );
}

function ProviderBreakdownPanel({ providerBreakdown, totalSpend }) {
  return (
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
                data={providerBreakdown.map((provider) => ({
                  ...provider,
                  total: totalSpend,
                }))}
                dataKey="value"
                nameKey="label"
                innerRadius={84}
                outerRadius={112}
                paddingAngle={5}
              >
                {providerBreakdown.map((provider) => (
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
          {providerBreakdown.map((provider) => (
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
  );
}

function AlertDetailDrawer({ alert, onClose }) {
  if (!alert) {
    return null;
  }

  return (
    <div className="alert-detail-drawer">
      <div className="alert-detail-header">
        <div>
          <p className="panel-eyebrow">Alert Detail</p>
          <h3>{alert.title}</h3>
        </div>
        <button type="button" className="service-detail-close" onClick={onClose} aria-label="Close alert detail">
          <CloseIcon />
          <span className="sr-only">Close alert detail</span>
        </button>
      </div>

      <div className="alert-detail-grid">
        <div className="service-detail-card">
          <span className="service-detail-label">Provider</span>
          <strong>{PROVIDER_LABELS[alert.provider]}</strong>
        </div>
        <div className="service-detail-card">
          <span className="service-detail-label">Impact</span>
          <strong>{alert.impact}</strong>
        </div>
        <div className="service-detail-card">
          <span className="service-detail-label">Owner</span>
          <strong>{alert.owner}</strong>
        </div>
        <div className="service-detail-card">
          <span className="service-detail-label">Confidence</span>
          <strong>{alert.confidence}</strong>
        </div>
      </div>

      <div className="service-detail-block">
        <span className="service-detail-label">Alert summary</span>
        <p>{alert.message}</p>
      </div>

      <div className="service-detail-block">
        <span className="service-detail-label">Recommended next step</span>
        <p>{alert.nextStep}</p>
      </div>
    </div>
  );
}

function AlertsPanel({ alerts, selectedAlert, onSelectAlert, onCloseAlert }) {
  return (
    <article className="dashboard-panel" id="alerts">
      <div className="panel-header">
        <div>
          <p className="panel-eyebrow">Alerts Panel</p>
          <h3>Live anomalies and recommendations</h3>
        </div>
        <span className="panel-badge">{alerts.length} active</span>
      </div>

      <div className="alerts-list">
        {alerts.length > 0 ? (
          alerts.map((alert) => (
            <div className={`alert-card alert-card-${alert.severity}`} key={alert.title}>
              <div className="alert-card-topline">
                <span className={`severity-pill severity-pill-${alert.severity}`}>{alert.severity}</span>
                <span className="alert-time">{alert.time}</span>
              </div>
              <h4>{alert.title}</h4>
              <p>{alert.message}</p>
              <button type="button" className="panel-inline-action" onClick={() => onSelectAlert(alert)}>
                {alert.action}
              </button>
            </div>
          ))
        ) : (
          <div className="panel-empty-state">
            <strong>No alerts match this search</strong>
            <p>Try a broader query to surface anomaly and recommendation results.</p>
          </div>
        )}
      </div>

      <AlertDetailDrawer alert={selectedAlert} onClose={onCloseAlert} />
    </article>
  );
}

function ServiceDetailDrawer({ service, onClose }) {
  if (!service) {
    return null;
  }

  return (
    <div className="service-detail-drawer">
      <div className="service-detail-header">
        <div>
          <p className="panel-eyebrow">Service Detail</p>
          <h3>{service.service}</h3>
        </div>
        <button type="button" className="service-detail-close" onClick={onClose} aria-label="Close service detail">
          <CloseIcon />
          <span className="sr-only">Close service detail</span>
        </button>
      </div>

      <div className="service-detail-grid">
        <div className="service-detail-card">
          <span className="service-detail-label">Monthly cost</span>
          <strong>{formatCurrency(service.monthlyCost)}</strong>
        </div>
        <div className="service-detail-card">
          <span className="service-detail-label">Efficiency score</span>
          <strong>{service.efficiencyScore}/100</strong>
        </div>
        <div className="service-detail-card">
          <span className="service-detail-label">Utilization</span>
          <strong>{service.utilization}</strong>
        </div>
        <div className="service-detail-card">
          <span className="service-detail-label">Owner</span>
          <strong>{service.owner}</strong>
        </div>
      </div>

      <div className="service-detail-block">
        <span className="service-detail-label">Operational context</span>
        <p>
          {PROVIDER_LABELS[service.provider]} workload in {service.region} with a <strong>{service.riskLevel}</strong> optimization risk level.
          Current status is <strong>{service.status}</strong>, with a <strong>{service.change > 0 ? '+' : ''}{service.change.toFixed(1)}%</strong> trend versus the previous period.
        </p>
      </div>

      <div className="service-detail-block">
        <span className="service-detail-label">Recommended move</span>
        <p>{service.recommendation}</p>
      </div>

      <div className="service-detail-block">
        <span className="service-detail-label">Execution playbook</span>
        <p>{service.runbook}</p>
      </div>
    </div>
  );
}

function ServicesPanel({ services, normalizedQuery, selectedService, onSelectService, onCloseService }) {
  return (
    <article className="dashboard-panel panel-span-2" id="services">
      <div className="panel-header">
        <div>
          <p className="panel-eyebrow">Services Table</p>
          <h3>Detailed service cost breakdown</h3>
        </div>
        <span className="panel-badge">
          {services.length} services {normalizedQuery ? 'matching search' : 'tracked'}
        </span>
      </div>

      {services.length > 0 ? (
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
                <th></th>
              </tr>
            </thead>
            <tbody>
              {services.map((service) => {
                const provider = PROVIDER_CONFIG.find((entry) => entry.key === service.provider);

                return (
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
                          color: provider?.accent,
                          background: provider?.accentSoft,
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
                    <td>
                      <button
                        type="button"
                        className="table-action-button"
                        onClick={() => onSelectService(service)}
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="panel-empty-state">
          <strong>No services match this search</strong>
          <p>Try a provider name, region, or recommendation keyword to widen the result set.</p>
        </div>
      )}

      <ServiceDetailDrawer service={selectedService} onClose={onCloseService} />
    </article>
  );
}

function DashboardStack({ budgets, quickActions, onQuickAction }) {
  return (
    <div className="dashboard-stack">
      <article className="dashboard-panel" id="budgets">
        <div className="panel-header">
          <div>
            <p className="panel-eyebrow">Budget Tracker</p>
            <h3>Budget utilization by provider</h3>
          </div>
        </div>

        <div className="budget-list">
          {budgets.map((budget) => (
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

      <article className="dashboard-panel" id="workflows">
        <div className="panel-header">
          <div>
            <p className="panel-eyebrow">Quick Actions</p>
            <h3>Common operator workflows</h3>
          </div>
        </div>

        <div className="quick-actions-grid">
          {quickActions.map((action) => (
            <button
              type="button"
              className="quick-action-card"
              key={action.id}
              onClick={() => onQuickAction(action.id)}
            >
              <span className="quick-action-eyebrow">{action.eyebrow}</span>
              <strong>{action.title}</strong>
              <p>{action.description}</p>
            </button>
          ))}
        </div>
      </article>
    </div>
  );
}

function RegionsPanel({ regions }) {
  return (
    <article className="dashboard-panel panel-span-2" id="regions">
      <div className="panel-header">
        <div>
          <p className="panel-eyebrow">Cost by Region</p>
          <h3>Geographic spend distribution</h3>
        </div>
        <span className="panel-badge">Top regions by cost</span>
      </div>

      <div className="chart-container chart-container-medium">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={regions} layout="vertical" margin={{ left: 12, right: 12 }}>
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
              {regions.map((region, index) => (
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
  );
}

function DashboardContent({
  dashboardData,
  selectedProvider,
  selectedAlertSeverity,
  filteredServices,
  filteredAlerts,
  filteredBudgets,
  filteredProviderBreakdown,
  filteredRegions,
  selectedAlert,
  selectedService,
  normalizedQuery,
  totalSpend,
  activeProviderKeys,
  onProviderChange,
  onAlertSeverityChange,
  onResetFilters,
  onSelectAlert,
  onCloseAlert,
  onSelectService,
  onCloseService,
  onQuickAction,
}) {
  return (
    <>
      <DashboardHero onQuickAction={onQuickAction} />
      <DashboardFilters
        selectedProvider={selectedProvider}
        selectedAlertSeverity={selectedAlertSeverity}
        onProviderChange={onProviderChange}
        onAlertSeverityChange={onAlertSeverityChange}
        onReset={onResetFilters}
      />
      <DashboardMetrics metrics={dashboardData.metrics} />

      <section className="dashboard-grid">
        <SpendingTrendsPanel
          spendingTrend={dashboardData.spendingTrend}
          providerBreakdown={filteredProviderBreakdown}
          totalSpend={totalSpend}
          activeProviderKeys={activeProviderKeys}
        />
        <ProviderBreakdownPanel providerBreakdown={filteredProviderBreakdown} totalSpend={totalSpend} />
        <AlertsPanel
          alerts={filteredAlerts}
          selectedAlert={selectedAlert}
          onSelectAlert={onSelectAlert}
          onCloseAlert={onCloseAlert}
        />
        <ServicesPanel
          services={filteredServices}
          normalizedQuery={normalizedQuery}
          selectedService={selectedService}
          onSelectService={onSelectService}
          onCloseService={onCloseService}
        />
        <DashboardStack
          budgets={filteredBudgets}
          quickActions={dashboardData.quickActions}
          onQuickAction={onQuickAction}
        />
        <RegionsPanel regions={filteredRegions} />
      </section>
    </>
  );
}

export default DashboardContent;
