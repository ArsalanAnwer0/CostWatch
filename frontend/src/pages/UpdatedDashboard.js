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
  costSummary,
  costTrends,
  resourceBreakdown,
  ec2Instances,
  rdsInstances,
  s3Buckets,
  optimizations,
  alerts,
} from '../services/mockData';
import './UpdatedDashboard.css';

function UpdatedDashboard() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedService, setSelectedService] = useState('ec2');
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState({ name: 'Demo User', email: 'demo@costwatch.com' });

  // State for API data (fallback to mock data if API fails)
  const [costSummary, setCostSummary] = useState(costSummary);
  const [costTrends, setCostTrends] = useState(costTrends);
  const [resourceBreakdown, setResourceBreakdown] = useState(resourceBreakdown);
  const [ec2Instances, setEC2Instances] = useState(ec2Instances);
  const [rdsInstances, setRDSInstances] = useState(rdsInstances);
  const [s3Buckets, setS3Buckets] = useState(s3Buckets);
  const [optimizations, setOptimizations] = useState(optimizations);
  const [alerts, setAlerts] = useState(alerts);

  useEffect(() => {
    // Check auth
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    // Load user from localStorage
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }

    // Fetch data from backend
    fetchDashboardData(token);
  }, []);

  const fetchDashboardData = async (token) => {
    setLoading(true);

    try {
      // Try to fetch from backend API
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      };

      // Fetch cost summary
      try {
        const costResponse = await fetch('http://localhost:8002/costs/summary?period=30d', { headers });
        if (costResponse.ok) {
          const costData = await costResponse.json();
          if (costData) setCostSummary(costData);
        }
      } catch (err) {
        console.log('Using mock cost data');
      }

      // Fetch resources (EC2, RDS, S3)
      try {
        const ec2Response = await fetch('http://localhost:8000/scan/ec2', { headers });
        if (ec2Response.ok) {
          const ec2Data = await ec2Response.json();
          if (ec2Data?.resources) setEC2Instances(ec2Data.resources);
        }
      } catch (err) {
        console.log('Using mock EC2 data');
      }

    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      // Keep using mock data as fallback
    } finally {
      setLoading(false);
    }
  };

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
          amount={costSummary.currentMonth}
          change={costSummary.percentChange}
          icon="💰"
          trend={costSummary.percentChange < 0 ? 'down' : 'up'}
        />
        <CostCard
          title="Last Month Cost"
          amount={costSummary.lastMonth}
          icon="📊"
        />
        <CostCard
          title="Savings Opportunity"
          amount={costSummary.savingsOpportunity}
          icon="💡"
          trend="down"
        />
        <CostCard
          title="Total Resources"
          amount={costSummary.totalResources}
          icon="🖥️"
        />
      </div>

      {/* Cost Trend Chart */}
      <div className="chart-section">
        <div className="section-header">
          <h2>Cost Trends (Last 30 Days)</h2>
          <p className="section-subtitle">Daily AWS spending pattern</p>
        </div>
        <CostChart data={costTrends} height={250} />
      </div>

      {/* Service Breakdown */}
      <div className="service-breakdown-section">
        <div className="section-header">
          <h2>Cost by Service</h2>
          <p className="section-subtitle">Distribution of AWS costs</p>
        </div>
        <div className="service-breakdown-grid">
          {resourceBreakdown.map((service) => (
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
          {optimizations.slice(0, 3).map((opt) => (
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
            EC2 ({ec2Instances.length})
          </button>
          <button
            className={selectedService === 'rds' ? 'tab-active' : 'tab'}
            onClick={() => setSelectedService('rds')}
          >
            RDS ({rdsInstances.length})
          </button>
          <button
            className={selectedService === 's3' ? 'tab-active' : 'tab'}
            onClick={() => setSelectedService('s3')}
          >
            S3 ({s3Buckets.length})
          </button>
        </div>
      </div>

      {selectedService === 'ec2' && <ResourceTable resources={ec2Instances} type="ec2" />}
      {selectedService === 'rds' && <ResourceTable resources={rdsInstances} type="rds" />}
      {selectedService === 's3' && <ResourceTable resources={s3Buckets} type="s3" />}
    </div>
  );

  const renderOptimizations = () => (
    <div className="all-optimizations-section">
      <div className="section-header">
        <h2>All Optimization Recommendations</h2>
        <p className="section-subtitle">
          Total potential savings: ${optimizations.reduce((sum, opt) => sum + opt.monthlySavings, 0).toFixed(2)}/month
        </p>
      </div>
      <div className="optimizations-list">
        {optimizations.map((opt) => (
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
        <p className="section-subtitle">{alerts.filter(a => !a.read).length} unread alerts</p>
      </div>
      <div className="alerts-list">
        {alerts.map((alert) => (
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
          <button className="btn-settings" onClick={() => navigate('/settings')}>
            ⚙️ Settings
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
            🔔 Alerts {alerts.filter(a => !a.read).length > 0 && (
              <span className="badge">{alerts.filter(a => !a.read).length}</span>
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
