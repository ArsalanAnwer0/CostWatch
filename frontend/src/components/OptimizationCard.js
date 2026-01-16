/**
 * Optimization Card Component - Shows cost saving opportunities
 */
import React from 'react';
import './OptimizationCard.css';

function OptimizationCard({ optimization, onImplement }) {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(value);
  };

  const getSeverityClass = () => {
    return `severity-${optimization.severity}`;
  };

  const getSeverityIcon = () => {
    const icons = {
      high: '⚠️',
      medium: '💡',
      low: 'ℹ️',
    };
    return icons[optimization.severity] || 'ℹ️';
  };

  return (
    <div className={`optimization-card ${getSeverityClass()}`}>
      <div className="optimization-header">
        <span className="severity-icon">{getSeverityIcon()}</span>
        <div className="optimization-title-section">
          <h4 className="optimization-title">{optimization.title}</h4>
          <span className="optimization-type">{optimization.type}</span>
        </div>
        <div className="savings-badge">
          {formatCurrency(optimization.monthlySavings)}/mo
        </div>
      </div>

      <p className="optimization-description">{optimization.description}</p>

      <div className="optimization-resources">
        <span className="resources-label">Affected Resources:</span>
        <span className="resources-count">{optimization.resources.length} resources</span>
      </div>

      <div className="optimization-actions">
        <button
          className="btn-view-details"
          onClick={() => console.log('View details:', optimization)}
        >
          View Details
        </button>
        {onImplement && (
          <button
            className="btn-implement"
            onClick={() => onImplement(optimization)}
          >
            Implement
          </button>
        )}
      </div>
    </div>
  );
}

export default OptimizationCard;
