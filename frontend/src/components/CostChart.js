/**
 * Simple Cost Chart Component - Displays cost trends
 * Uses basic SVG for simplicity (no external chart library needed)
 */
import React from 'react';
import './CostChart.css';

function CostChart({ data, height = 200 }) {
  if (!data || data.length === 0) {
    return (
      <div className="chart-empty">
        <p>No cost data available</p>
      </div>
    );
  }

  const width = 800;
  const padding = { top: 20, right: 20, bottom: 40, left: 60 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Get min/max values
  const costs = data.map(d => d.cost);
  const minCost = Math.min(...costs);
  const maxCost = Math.max(...costs);
  const costRange = maxCost - minCost;

  // Scale functions
  const xScale = (index) => (index / (data.length - 1)) * chartWidth + padding.left;
  const yScale = (value) => chartHeight - ((value - minCost) / costRange) * chartHeight + padding.top;

  // Create path for line
  const linePath = data.map((d, i) => {
    const x = xScale(i);
    const y = yScale(d.cost);
    return i === 0 ? `M ${x} ${y}` : `L ${x} ${y}`;
  }).join(' ');

  // Create area path
  const areaPath = `
    ${linePath}
    L ${xScale(data.length - 1)} ${chartHeight + padding.top}
    L ${xScale(0)} ${chartHeight + padding.top}
    Z
  `;

  // Format currency
  const formatCurrency = (value) => {
    return `$${Math.round(value)}`;
  };

  // Get tick values for Y axis
  const yTicks = [minCost, (minCost + maxCost) / 2, maxCost];

  return (
    <div className="cost-chart-container">
      <svg width={width} height={height} className="cost-chart">
        {/* Grid lines */}
        {yTicks.map((tick, i) => (
          <g key={i}>
            <line
              x1={padding.left}
              y1={yScale(tick)}
              x2={width - padding.right}
              y2={yScale(tick)}
              stroke="#e5e7eb"
              strokeWidth="1"
              strokeDasharray="4 4"
            />
            <text
              x={padding.left - 10}
              y={yScale(tick) + 4}
              textAnchor="end"
              fontSize="12"
              fill="#6b7280"
            >
              {formatCurrency(tick)}
            </text>
          </g>
        ))}

        {/* Area fill */}
        <path
          d={areaPath}
          fill="url(#gradient)"
          opacity="0.3"
        />

        {/* Line */}
        <path
          d={linePath}
          fill="none"
          stroke="#3b82f6"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Data points */}
        {data.map((d, i) => (
          <circle
            key={i}
            cx={xScale(i)}
            cy={yScale(d.cost)}
            r="4"
            fill="#3b82f6"
            className="chart-point"
          >
            <title>{`${d.date}: ${formatCurrency(d.cost)}`}</title>
          </circle>
        ))}

        {/* X-axis labels (show every 5th day) */}
        {data.map((d, i) => {
          if (i % 5 === 0 || i === data.length - 1) {
            return (
              <text
                key={i}
                x={xScale(i)}
                y={height - padding.bottom + 20}
                textAnchor="middle"
                fontSize="11"
                fill="#6b7280"
              >
                {new Date(d.date).getDate()}
              </text>
            );
          }
          return null;
        })}

        {/* Gradient definition */}
        <defs>
          <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
          </linearGradient>
        </defs>
      </svg>

      <div className="chart-legend">
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#3b82f6' }}></div>
          <span>Daily Cost</span>
        </div>
      </div>
    </div>
  );
}

export default CostChart;
