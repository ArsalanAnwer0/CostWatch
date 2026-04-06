import React from 'react';
import { formatCurrency } from '../../utils';

function DashboardSidebar({
  navigationSections,
  dashboardMeta,
  providerStatuses,
  activeSectionId,
  onNavigate,
}) {
  return (
    <aside className="dashboard-sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark">CW</div>
        <div>
          <h1>CostWatch</h1>
          <p>AI cost intelligence</p>
        </div>
      </div>

      <div className="sidebar-health-card">
        <span className={`sidebar-health-indicator status-${dashboardMeta.overallHealth}`}></span>
        <div>
          <strong>{dashboardMeta.liveDataAvailable ? 'Live cloud telemetry' : 'Demo intelligence mode'}</strong>
          <p>{dashboardMeta.lastUpdatedLabel}</p>
        </div>
      </div>

      <nav className="sidebar-navigation">
        {navigationSections.map((section) => (
          <div className="sidebar-section" key={section.title}>
            <div className="sidebar-section-title">{section.title}</div>
            {section.items.map((item) => (
              <button
                type="button"
                className={`sidebar-nav-item ${activeSectionId === item.id || (!activeSectionId && item.active) ? 'active' : ''}`}
                key={item.id}
                onClick={() => onNavigate(item.id)}
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
        {providerStatuses.map((provider) => (
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
  );
}

export default DashboardSidebar;
