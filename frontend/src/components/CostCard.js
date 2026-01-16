/**
 * Cost Card Component - Displays cost metric with trend
 */
import React from 'react';
import './CostCard.css';
import '../styles/animations.css';

function CostCard({ title, amount, change, icon, trend = 'neutral' }) {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(value);
  };

  const getTrendColor = () => {
    if (trend === 'up') return '#ef4444'; // red
    if (trend === 'down') return '#10b981'; // green
    return '#6b7280'; // gray
  };

  const getTrendIcon = () => {
    if (trend === 'up') return '↑';
    if (trend === 'down') return '↓';
    return '−';
  };

  return (
    <div className="cost-card">
      <div className="cost-card-header">
        <span className="cost-card-icon">{icon}</span>
        <h3 className="cost-card-title">{title}</h3>
      </div>

      <div className="cost-card-amount">
        {formatCurrency(amount)}
      </div>

      {change !== undefined && (
        <div className="cost-card-change" style={{ color: getTrendColor() }}>
          <span className="trend-icon">{getTrendIcon()}</span>
          <span className="change-value">{Math.abs(change).toFixed(1)}%</span>
          <span className="change-label">vs last month</span>
        </div>
      )}
    </div>
  );
}

export default CostCard;
