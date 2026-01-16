/**
 * Resource Table Component - Displays AWS resources in a table
 */
import React, { useState } from 'react';
import './ResourceTable.css';

function ResourceTable({ resources, type = 'ec2' }) {
  const [sortField, setSortField] = useState('monthlyCost');
  const [sortDirection, setSortDirection] = useState('desc');

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(value);
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const sortedResources = [...resources].sort((a, b) => {
    const aValue = a[sortField];
    const bValue = b[sortField];

    if (sortDirection === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });

  const getStatusBadge = (state) => {
    const statusColors = {
      running: '#10b981',
      stopped: '#ef4444',
      available: '#10b981',
      pending: '#f59e0b',
    };

    return (
      <span
        className="status-badge"
        style={{ backgroundColor: statusColors[state] || '#6b7280' }}
      >
        {state}
      </span>
    );
  };

  const getSavingsBadge = (savings) => {
    if (savings === 0) {
      return <span className="savings-badge savings-none">Optimized</span>;
    }
    if (savings > 100) {
      return <span className="savings-badge savings-high">High Savings</span>;
    }
    if (savings > 20) {
      return <span className="savings-badge savings-medium">Medium Savings</span>;
    }
    return <span className="savings-badge savings-low">Low Savings</span>;
  };

  return (
    <div className="resource-table-container">
      <table className="resource-table">
        <thead>
          <tr>
            <th onClick={() => handleSort('name')}>
              Name {sortField === 'name' && (sortDirection === 'asc' ? '↑' : '↓')}
            </th>
            <th onClick={() => handleSort('type')}>
              Type {sortField === 'type' && (sortDirection === 'asc' ? '↑' : '↓')}
            </th>
            <th onClick={() => handleSort('state')}>
              Status {sortField === 'state' && (sortDirection === 'asc' ? '↑' : '↓')}
            </th>
            <th>Region</th>
            <th onClick={() => handleSort('monthlyCost')}>
              Monthly Cost {sortField === 'monthlyCost' && (sortDirection === 'asc' ? '↑' : '↓')}
            </th>
            <th>Recommendation</th>
            <th onClick={() => handleSort('potentialSavings')}>
              Potential Savings {sortField === 'potentialSavings' && (sortDirection === 'asc' ? '↑' : '↓')}
            </th>
          </tr>
        </thead>
        <tbody>
          {sortedResources.map((resource) => (
            <tr key={resource.id}>
              <td className="resource-name">{resource.name || resource.id}</td>
              <td className="resource-type">{resource.type}</td>
              <td>{getStatusBadge(resource.state)}</td>
              <td>{resource.region}</td>
              <td className="cost-cell">{formatCurrency(resource.monthlyCost)}</td>
              <td className="recommendation-cell">{resource.recommendation}</td>
              <td>
                {getSavingsBadge(resource.potentialSavings)}
                <span className="savings-amount">
                  {resource.potentialSavings > 0 && formatCurrency(resource.potentialSavings)}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {resources.length === 0 && (
        <div className="empty-state">
          <p>No resources found</p>
          <p className="empty-state-subtitle">Run a scan to discover your AWS resources</p>
        </div>
      )}
    </div>
  );
}

export default ResourceTable;
