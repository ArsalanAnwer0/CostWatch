import React from 'react';
import { formatCurrency } from '../../utils';
import { PROVIDER_LABELS } from './dashboardUtils';

export function SpendTooltip({ active, label, payload }) {
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

export function DonutTooltip({ active, payload }) {
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

export function RegionTooltip({ active, payload, label }) {
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
