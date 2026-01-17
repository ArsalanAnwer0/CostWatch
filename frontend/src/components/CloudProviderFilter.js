/**
 * Cloud Provider Filter Component
 * Filter dashboard by cloud provider (All, AWS, Azure, GCP)
 */
import React from 'react';
import './CloudProviderFilter.css';

function CloudProviderFilter({ selectedProvider, onProviderChange }) {
  const providers = [
    { value: 'all', label: 'All Clouds', icon: '☁️' },
    { value: 'aws', label: 'AWS', icon: '🟠' },
    { value: 'azure', label: 'Azure', icon: '🔵' },
    { value: 'gcp', label: 'GCP', icon: '🔴' },
  ];

  return (
    <div className="cloud-provider-filter">
      {providers.map((provider) => (
        <button
          key={provider.value}
          className={`provider-btn ${selectedProvider === provider.value ? 'active' : ''}`}
          onClick={() => onProviderChange(provider.value)}
        >
          <span className="provider-icon">{provider.icon}</span>
          <span className="provider-label">{provider.label}</span>
        </button>
      ))}
    </div>
  );
}

export default CloudProviderFilter;
