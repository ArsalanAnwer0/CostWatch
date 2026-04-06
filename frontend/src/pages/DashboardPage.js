import React, { useDeferredValue, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LoadingSpinner, Toast } from '../components';
import DashboardContent from '../components/dashboard/DashboardContent';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import DashboardSidebar from '../components/dashboard/DashboardSidebar';
import { PROVIDER_LABELS } from '../components/dashboard/dashboardUtils';
import { useLocalStorage } from '../hooks';
import { STORAGE_KEYS } from '../constants';
import {
  buildDashboardModel,
  DASHBOARD_NAV_SECTIONS,
  TIME_RANGE_OPTIONS,
} from '../data/dashboardData';
import { DashboardService } from '../services/api';
import './DashboardPage.css';
import '../styles/animations.css';

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

const ALERT_SEVERITY_RANK = {
  low: 0,
  medium: 1,
  high: 2,
  critical: 3,
};

function aggregateRegionCosts(services) {
  const totals = services.reduce((accumulator, service) => {
    accumulator[service.region] = (accumulator[service.region] || 0) + service.monthlyCost;
    return accumulator;
  }, {});

  return Object.entries(totals)
    .map(([region, cost]) => ({
      region,
      cost: Math.round(cost * 100) / 100,
    }))
    .sort((left, right) => right.cost - left.cost);
}

function DashboardPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [activeSectionId, setActiveSectionId] = useState('overview');
  const [selectedRange, setSelectedRange] = useLocalStorage(STORAGE_KEYS.DASHBOARD_RANGE, '6m');
  const [selectedProvider, setSelectedProvider] = useLocalStorage(STORAGE_KEYS.DASHBOARD_PROVIDER, 'all');
  const [selectedAlertSeverity, setSelectedAlertSeverity] = useLocalStorage(STORAGE_KEYS.DASHBOARD_ALERT_SEVERITY, 'all');
  const [searchQuery, setSearchQuery] = useState('');
  const [dashboardSnapshot, setDashboardSnapshot] = useState({});
  const [user, setUser] = useState(null);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [selectedService, setSelectedService] = useState(null);
  const [toast, setToast] = useState(null);
  const deferredSearchQuery = useDeferredValue(searchQuery);

  const dashboardData = buildDashboardModel({
    ...dashboardSnapshot,
    range: selectedRange,
  });

  const activeProviderKeys = selectedProvider === 'all'
    ? dashboardData.providerBreakdown.map((provider) => provider.key)
    : [selectedProvider];
  const filteredProviderBreakdown = dashboardData.providerBreakdown.filter((provider) =>
    selectedProvider === 'all' ? true : provider.key === selectedProvider
  );
  const filteredBudgets = dashboardData.budgets.filter((budget) =>
    selectedProvider === 'all' ? true : budget.key === selectedProvider
  );
  const totalSpend = filteredProviderBreakdown.reduce((sum, provider) => sum + provider.value, 0);
  const normalizedQuery = deferredSearchQuery.trim().toLowerCase();
  const providerFilteredServices = dashboardData.services.filter((service) =>
    selectedProvider === 'all' ? true : service.provider === selectedProvider
  );
  const filteredServices = providerFilteredServices.filter((service) => {
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
    const providerMatches = selectedProvider === 'all'
      ? true
      : [alert.title, alert.message, alert.action]
        .some((value) => value.toLowerCase().includes(PROVIDER_LABELS[selectedProvider].toLowerCase()));
    const severityMatches = selectedAlertSeverity === 'all'
      ? true
      : ALERT_SEVERITY_RANK[alert.severity] >= ALERT_SEVERITY_RANK[selectedAlertSeverity];

    if (!providerMatches || !severityMatches) {
      return false;
    }

    if (!normalizedQuery) {
      return true;
    }

    return [alert.title, alert.message, alert.action].some((value) =>
      value.toLowerCase().includes(normalizedQuery)
    );
  });
  const filteredRegions = selectedProvider === 'all'
    ? dashboardData.regions
    : aggregateRegionCosts(providerFilteredServices);

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

  const scrollToSection = (sectionId) => {
    const scrollTargets = {
      overview: 'overview',
      spend: 'spend',
      alerts: 'alerts',
      budgets: 'budgets',
      services: 'services',
      regions: 'regions',
      reports: 'overview',
      workflows: 'workflows',
      settings: 'overview',
    };

    const targetId = scrollTargets[sectionId];
    const target = targetId ? document.getElementById(targetId) : null;

    setActiveSectionId(sectionId);

    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return true;
    }

    return false;
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

  const handleSidebarNavigate = (sectionId) => {
    const didScroll = scrollToSection(sectionId);
    setIsSidebarOpen(false);

    if (didScroll) {
      return;
    }

    setToast({
      type: 'info',
      message: `The ${sectionId} workspace is the next product surface to wire in.`,
    });
  };

  const handleResetFilters = () => {
    setSelectedProvider('all');
    setSelectedAlertSeverity('all');
    setSearchQuery('');
    setSelectedRange('6m');
    setSelectedAlert(null);
    setSelectedService(null);
    setToast({
      type: 'info',
      message: 'Dashboard filters reset to the default operating view.',
    });
  };

  if (loading) {
    return <LoadingSpinner fullPage size="large" text="Assembling your command center..." />;
  }

  return (
    <div className="dashboard-shell">
      <button
        type="button"
        className={`dashboard-overlay ${isSidebarOpen ? 'visible' : ''}`}
        onClick={() => setIsSidebarOpen(false)}
        aria-label="Close navigation overlay"
      ></button>

      <DashboardSidebar
        navigationSections={DASHBOARD_NAV_SECTIONS}
        dashboardMeta={dashboardData.meta}
        providerStatuses={dashboardData.providerStatuses}
        activeSectionId={activeSectionId}
        isOpen={isSidebarOpen}
        onNavigate={handleSidebarNavigate}
        onClose={() => setIsSidebarOpen(false)}
      />

      <main className="dashboard-main">
        <DashboardHeader
          user={user}
          searchQuery={searchQuery}
          selectedRange={selectedRange}
          rangeOptions={TIME_RANGE_OPTIONS}
          refreshing={refreshing}
          liveDataAvailable={dashboardData.meta.liveDataAvailable}
          lastUpdatedLabel={dashboardData.meta.lastUpdatedLabel}
          unreadAlerts={dashboardData.meta.unreadAlerts}
          onOpenMenu={() => setIsSidebarOpen(true)}
          onSearchChange={setSearchQuery}
          onRangeChange={setSelectedRange}
          onRefresh={() => refreshDashboard({ showToast: true })}
          onOpenAlerts={() => handleSidebarNavigate('alerts')}
          onLogout={handleLogout}
        />

        <div className={`dashboard-content-shell ${refreshing ? 'refreshing' : ''}`}>
          {refreshing && (
            <div className="dashboard-refresh-indicator" aria-live="polite">
              Refreshing spend snapshots, alerts, and provider health.
            </div>
          )}

          <DashboardContent
            dashboardData={dashboardData}
            selectedProvider={selectedProvider}
            selectedAlertSeverity={selectedAlertSeverity}
            filteredServices={filteredServices}
            filteredAlerts={filteredAlerts}
          filteredBudgets={filteredBudgets}
          filteredProviderBreakdown={filteredProviderBreakdown}
          filteredRegions={filteredRegions}
          selectedAlert={selectedAlert}
          selectedService={selectedService}
          normalizedQuery={normalizedQuery}
          totalSpend={totalSpend}
          activeProviderKeys={activeProviderKeys}
          onProviderChange={setSelectedProvider}
          onAlertSeverityChange={setSelectedAlertSeverity}
          onResetFilters={handleResetFilters}
          onSelectAlert={setSelectedAlert}
          onCloseAlert={() => setSelectedAlert(null)}
          onSelectService={setSelectedService}
          onCloseService={() => setSelectedService(null)}
          onQuickAction={handleQuickAction}
        />
        </div>
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
