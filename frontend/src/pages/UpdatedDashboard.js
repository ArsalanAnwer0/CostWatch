/**
 * Updated Dashboard Page - Fully Functional with All Components
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import CostCard from '../components/CostCard';
import CostChart from '../components/CostChart';
import ResourceTable from '../components/ResourceTable';
import OptimizationCard from '../components/OptimizationCard';
import LoadingSpinner from '../components/LoadingSpinner';
import {
  mockCostSummary,
  mockCostTrends,
  mockResourceBreakdown,
  mockEC2Instances,
  mockRDSInstances,
  mockS3Buckets,
  mockOptimizations,
  mockAlerts,
} from '../services/mockData';
import './UpdatedDashboard.css';

function UpdatedDashboard() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedService, setSelectedService] = useState('ec2');
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState({ name: 'Demo User', email: 'demo@costwatch.com' });

  useEffect(() => {
    // Simulate loading
    setTimeout(() => setLoading(false), 500);

    // Check auth (optional for demo)
    const token = localStorage.getItem('token');
    if (!token) {
      // For demo, create a mock token
      localStorage.setItem('token', 'demo-token-12345');
      localStorage.setItem('user', JSON.stringify(user));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/');
  };

  const handleScanResources = () => {
    alert('🔄 Resource scan initiated! In a production environment, this would scan your AWS account.');
  };

  const handleImplementOptimization = (optimization) => {
    alert(`✅ Implementing: ${optimization.title}\n\nThis would apply the optimization in production.`);
  };

  if (loading) {
    return <LoadingSpinner size="large" text="Loading dashboard..." fullPage />;
  }

  const renderOverview = () => (
    <div className="overview-section">
      {/* Cost Summary Cards */}
      <div className="cost-cards-grid">
        <CostCard
          title="Current Month Cost"
          amount={mockCostSummary.currentMonth}
          change={mockCostSummary.percentChange}
          icon="💰"
          trend={mockCostSummary.percentChange < 0 ? 'down' : 'up'}
        />
        <CostCard
          title="Last Month Cost"
          amount={mockCostSummary.lastMonth}
          icon="📊"
        />
        <CostCard
          title="Savings Opportunity"
          amount={mockCostSummary.savingsOpportunity}
          icon="💡"
          trend="down"
        />
        <CostCard
          title="Total Resources"
          amount={mockCostSummary.totalResources}
          icon="🖥️"
        />
      </div>

      {/* Cost Trend Chart */}
      <div className="chart-section">
        <div className="section-header">
          <h2>Cost Trends (Last 30 Days)</h2>
          <p className="section-subtitle">Daily AWS spending pattern</p>
        </div>
        <CostChart data={mockCostTrends} height={250} />
      </div>

      {/* Service Breakdown */}
      <div className="service-breakdown-section">
        <div className="section-header">
          <h2>Cost by Service</h2>
          <p className="section-subtitle">Distribution of AWS costs</p>
        </div>
        <div className="service-breakdown-grid">
          {mockResourceBreakdown.map((service) => (
            <div key={service.service} className="service-card">
              <div className="service-header">
                <h3>{service.service}</h3>
                <span className="service-percentage">{service.percentage}%</span>
              </div>
              <div className="service-details">
                <span className="service-count">{service.count} resources</span>
                <span className="service-cost">${service.cost.toFixed(2)}/mo</span>
              </div>
              <div className="service-bar">
                <div
                  className="service-bar-fill"
                  style={{ width: `${service.percentage}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Top Optimizations */}
      <div className="optimizations-section">
        <div className="section-header">
          <h2>Top Optimization Opportunities</h2>
          <p className="section-subtitle">Recommended cost-saving actions</p>
        </div>
        <div className="optimizations-grid">
          {mockOptimizations.slice(0, 3).map((opt) => (
            <OptimizationCard
              key={opt.id}
              optimization={opt}
              onImplement={handleImplementOptimization}
            />
          ))}
        </div>
      </div>
    </div>
  );

  const renderResources = () => (
    <div className="resources-section">
      <div className="section-header">
        <h2>AWS Resources</h2>
        <div className="resource-tabs">
          <button
            className={selectedService === 'ec2' ? 'tab-active' : 'tab'}
            onClick={() => setSelectedService('ec2')}
          >
            EC2 ({mockEC2Instances.length})
          </button>
          <button
            className={selectedService === 'rds' ? 'tab-active' : 'tab'}
            onClick={() => setSelectedService('rds')}
          >
            RDS ({mockRDSInstances.length})
          </button>
          <button
            className={selectedService === 's3' ? 'tab-active' : 'tab'}
            onClick={() => setSelectedService('s3')}
          >
            S3 ({mockS3Buckets.length})
          </button>
        </div>
      </div>

      {selectedService === 'ec2' && <ResourceTable resources={mockEC2Instances} type="ec2" />}
      {selectedService === 'rds' && <ResourceTable resources={mockRDSInstances} type="rds" />}
      {selectedService === 's3' && <ResourceTable resources={mockS3Buckets} type="s3" />}
    </div>
  );

  const renderOptimizations = () => (
    <div className="all-optimizations-section">
      <div className="section-header">
        <h2>All Optimization Recommendations</h2>
        <p className="section-subtitle">
          Total potential savings: ${mockOptimizations.reduce((sum, opt) => sum + opt.monthlySavings, 0).toFixed(2)}/month
        </p>
      </div>
      <div className="optimizations-list">
        {mockOptimizations.map((opt) => (
          <OptimizationCard
            key={opt.id}
            optimization={opt}
            onImplement={handleImplementOptimization}
          />
        ))}
      </div>
    </div>
  );

  const renderAlerts = () => (
    <div className="alerts-section">
      <div className="section-header">
        <h2>Alerts & Notifications</h2>
        <p className="section-subtitle">{mockAlerts.filter(a => !a.read).length} unread alerts</p>
      </div>
      <div className="alerts-list">
        {mockAlerts.map((alert) => (
          <div key={alert.id} className={`alert-card alert-${alert.severity} ${alert.read ? 'read' : 'unread'}`}>
            <div className="alert-header">
              <span className="alert-icon">
                {alert.severity === 'high' && '🚨'}
                {alert.severity === 'medium' && '⚠️'}
                {alert.severity === 'low' && 'ℹ️'}
              </span>
              <h3>{alert.title}</h3>
              <span className="alert-time">
                {new Date(alert.timestamp).toLocaleString()}
              </span>
            </div>
            <p className="alert-message">{alert.message}</p>
            <div className="alert-actions">
              <button className="btn-acknowledge">Acknowledge</button>
              <button className="btn-view">View Details</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="dashboard-container">
      {/* Top Navigation */}
      <nav className="dashboard-nav">
        <div className="nav-left">
          <h1 className="dashboard-logo">💰 CostWatch</h1>
        </div>
        <div className="nav-right">
          <button className="btn-scan" onClick={handleScanResources}>
            🔄 Scan Resources
          </button>
          <div className="user-menu">
            <span className="user-name">{user.name}</span>
            <button className="btn-logout" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="dashboard-content">
        {/* Sidebar */}
        <aside className="dashboard-sidebar">
          <button
            className={activeTab === 'overview' ? 'sidebar-item active' : 'sidebar-item'}
            onClick={() => setActiveTab('overview')}
          >
            📊 Overview
          </button>
          <button
            className={activeTab === 'resources' ? 'sidebar-item active' : 'sidebar-item'}
            onClick={() => setActiveTab('resources')}
          >
            🖥️ Resources
          </button>
          <button
            className={activeTab === 'optimizations' ? 'sidebar-item active' : 'sidebar-item'}
            onClick={() => setActiveTab('optimizations')}
          >
            💡 Optimizations
          </button>
          <button
            className={activeTab === 'alerts' ? 'sidebar-item active' : 'sidebar-item'}
            onClick={() => setActiveTab('alerts')}
          >
            🔔 Alerts {mockAlerts.filter(a => !a.read).length > 0 && (
              <span className="badge">{mockAlerts.filter(a => !a.read).length}</span>
            )}
          </button>
        </aside>

        {/* Main Area */}
        <main className="dashboard-main">
          {activeTab === 'overview' && renderOverview()}
          {activeTab === 'resources' && renderResources()}
          {activeTab === 'optimizations' && renderOptimizations()}
          {activeTab === 'alerts' && renderAlerts()}
        </main>
      </div>
    </div>
  );
}

export default UpdatedDashboard;
