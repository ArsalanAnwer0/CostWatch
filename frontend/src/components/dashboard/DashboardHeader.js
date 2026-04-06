import React from 'react';
import { getInitials } from './dashboardUtils';

function DashboardHeader({
  user,
  searchQuery,
  selectedRange,
  rangeOptions,
  refreshing,
  liveDataAvailable,
  lastUpdatedLabel,
  unreadAlerts,
  onOpenMenu,
  onSearchChange,
  onRangeChange,
  onRefresh,
  onOpenAlerts,
  onLogout,
}) {
  return (
    <header className="dashboard-header">
      <div className="dashboard-title-block">
        <button
          type="button"
          className="dashboard-mobile-menu"
          onClick={onOpenMenu}
          aria-label="Open navigation"
        >
          MN
        </button>
        <p className="dashboard-eyebrow">Unified multi-cloud control room</p>
        <h2>Cloud spend command center</h2>
        <p className="dashboard-subtitle">
          Monitor real-time cost posture, surface anomalies, and push optimizations across AWS, Azure, and GCP.
        </p>
        <div className={`dashboard-status-chip ${refreshing ? 'syncing' : ''}`}>
          <span className={`dashboard-status-dot ${refreshing ? 'syncing' : liveDataAvailable ? 'live' : 'fallback'}`}></span>
          <span>{refreshing ? 'Syncing live telemetry' : lastUpdatedLabel}</span>
        </div>
      </div>

      <div className="dashboard-toolbar">
        <label className="dashboard-search">
          <span>Search</span>
          <input
            type="search"
            value={searchQuery}
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder="Search services, alerts, regions, or recommendations"
          />
        </label>

        <label className="dashboard-range-picker">
          <span>Time range</span>
          <select value={selectedRange} onChange={(event) => onRangeChange(event.target.value)}>
            {rangeOptions.map((option) => (
              <option value={option.value} key={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <button
          type="button"
          className="dashboard-icon-button"
          onClick={onRefresh}
          disabled={refreshing}
          aria-label="Refresh dashboard"
        >
          {refreshing ? '...' : 'RF'}
        </button>

        <button
          type="button"
          className="dashboard-icon-button dashboard-icon-button-notification"
          aria-label="Notifications"
          onClick={onOpenAlerts}
        >
          NT
          <span className="notification-count">{unreadAlerts}</span>
        </button>

        <div className="dashboard-user-menu">
          <div className="dashboard-user-avatar">{getInitials(user)}</div>
          <div className="dashboard-user-details">
            <strong>{user?.full_name || 'Cost operator'}</strong>
            <span>{user?.email || 'Multi-cloud workspace'}</span>
          </div>
          <button type="button" className="dashboard-ghost-button" onClick={onLogout}>
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}

export default DashboardHeader;
