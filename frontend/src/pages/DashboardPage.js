import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './DashboardPage.css';

function DashboardPage() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [costData, setCostData] = useState({
    currentMonth: 0,
    lastMonth: 0,
    savingsOpportunity: 0,
    totalResources: 0,
  });

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');

    if (!token) {
      navigate('/login');
      return;
    }

    if (userData) {
      setUser(JSON.parse(userData));
    }

    // Fetch cost data
    fetchCostData(token);
  }, [navigate]);

  const fetchCostData = async (token) => {
    try {
      const response = await fetch('http://localhost:8002/costs/monthly', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setCostData({
          currentMonth: data.current_month_cost || 12450.67,
          lastMonth: data.last_month_cost || 15230.45,
          savingsOpportunity: data.savings_opportunity || 4250.30,
          totalResources: data.total_resources || 87,
        });
      } else {
        // Use mock data if API fails
        setCostData({
          currentMonth: 12450.67,
          lastMonth: 15230.45,
          savingsOpportunity: 4250.30,
          totalResources: 87,
        });
      }
    } catch (err) {
      console.error('Error fetching cost data:', err);
      // Use mock data
      setCostData({
        currentMonth: 12450.67,
        lastMonth: 15230.45,
        savingsOpportunity: 4250.30,
        totalResources: 87,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/');
  };

  const handleScanResources = async () => {
    const token = localStorage.getItem('token');
    try {
      const response = await fetch('http://localhost:8000/scan/all', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          regions: ['us-west-2', 'us-east-1'],
          include_costs: true,
        }),
      });

      if (response.ok) {
        alert('Resource scan started! This may take a few minutes.');
        fetchCostData(token);
      } else {
        alert('Failed to start resource scan. Please try again.');
      }
    } catch (err) {
      console.error('Error starting scan:', err);
      alert('Failed to start resource scan. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="loading">Loading dashboard...</div>
      </div>
    );
  }

  const savingsPercentage = ((costData.lastMonth - costData.currentMonth) / costData.lastMonth * 100).toFixed(1);

  return (
    <div className="dashboard-page">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1>CostWatch</h1>
        </div>
        <nav className="sidebar-nav">
          <a href="#" className="nav-item active">
            <span className="nav-icon">📊</span>
            <span>Dashboard</span>
          </a>
          <a href="#" className="nav-item">
            <span className="nav-icon">💰</span>
            <span>Costs</span>
          </a>
          <a href="#" className="nav-item">
            <span className="nav-icon">🔍</span>
            <span>Resources</span>
          </a>
          <a href="#" className="nav-item">
            <span className="nav-icon">💡</span>
            <span>Recommendations</span>
          </a>
          <a href="#" className="nav-item">
            <span className="nav-icon">🔔</span>
            <span>Alerts</span>
          </a>
          <a href="#" className="nav-item">
            <span className="nav-icon">📈</span>
            <span>Reports</span>
          </a>
          <a href="#" className="nav-item">
            <span className="nav-icon">⚙️</span>
            <span>Settings</span>
          </a>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* Top Bar */}
        <header className="top-bar">
          <div className="search-bar">
            <input type="text" placeholder="Search resources, costs, or alerts..." />
          </div>
          <div className="top-bar-actions">
            <button className="btn-icon">🔔</button>
            <div className="user-menu">
              <div className="user-avatar">{user?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}</div>
              <span className="user-name">{user?.full_name || user?.email || 'User'}</span>
              <button className="btn-logout" onClick={handleLogout}>Logout</button>
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <div className="dashboard-content">
          <div className="page-header">
            <h1>Cost Overview</h1>
            <div className="page-actions">
              <button className="btn-secondary" onClick={handleScanResources}>
                Scan Resources
              </button>
              <button className="btn-primary">Generate Report</button>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-header">
                <h3>Current Month Cost</h3>
                <span className="stat-icon">💰</span>
              </div>
              <div className="stat-value">${costData.currentMonth.toLocaleString()}</div>
              <div className="stat-change positive">
                ↓ {savingsPercentage}% from last month
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-header">
                <h3>Last Month Cost</h3>
                <span className="stat-icon">📅</span>
              </div>
              <div className="stat-value">${costData.lastMonth.toLocaleString()}</div>
              <div className="stat-change neutral">
                Previous billing period
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-header">
                <h3>Savings Opportunity</h3>
                <span className="stat-icon">💡</span>
              </div>
              <div className="stat-value">${costData.savingsOpportunity.toLocaleString()}</div>
              <div className="stat-change positive">
                ↑ Potential monthly savings
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-header">
                <h3>Total Resources</h3>
                <span className="stat-icon">🔍</span>
              </div>
              <div className="stat-value">{costData.totalResources}</div>
              <div className="stat-change neutral">
                Across all AWS accounts
              </div>
            </div>
          </div>

          {/* Charts and Tables */}
          <div className="dashboard-grid">
            {/* Cost Breakdown */}
            <div className="dashboard-card">
              <div className="card-header">
                <h3>Cost by Service</h3>
                <select className="card-select">
                  <option>Last 30 days</option>
                  <option>Last 90 days</option>
                  <option>Last 12 months</option>
                </select>
              </div>
              <div className="card-content">
                <div className="service-list">
                  <div className="service-item">
                    <div className="service-info">
                      <div className="service-name">EC2</div>
                      <div className="service-bar">
                        <div className="service-bar-fill" style={{ width: '65%' }}></div>
                      </div>
                    </div>
                    <div className="service-cost">$8,093</div>
                  </div>
                  <div className="service-item">
                    <div className="service-info">
                      <div className="service-name">RDS</div>
                      <div className="service-bar">
                        <div className="service-bar-fill" style={{ width: '20%' }}></div>
                      </div>
                    </div>
                    <div className="service-cost">$2,490</div>
                  </div>
                  <div className="service-item">
                    <div className="service-info">
                      <div className="service-name">S3</div>
                      <div className="service-bar">
                        <div className="service-bar-fill" style={{ width: '10%' }}></div>
                      </div>
                    </div>
                    <div className="service-cost">$1,245</div>
                  </div>
                  <div className="service-item">
                    <div className="service-info">
                      <div className="service-name">Lambda</div>
                      <div className="service-bar">
                        <div className="service-bar-fill" style={{ width: '3%' }}></div>
                      </div>
                    </div>
                    <div className="service-cost">$373</div>
                  </div>
                  <div className="service-item">
                    <div className="service-info">
                      <div className="service-name">Other</div>
                      <div className="service-bar">
                        <div className="service-bar-fill" style={{ width: '2%' }}></div>
                      </div>
                    </div>
                    <div className="service-cost">$250</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Optimization Recommendations */}
            <div className="dashboard-card">
              <div className="card-header">
                <h3>Top Recommendations</h3>
                <a href="#" className="card-link">View All</a>
              </div>
              <div className="card-content">
                <div className="recommendation-list">
                  <div className="recommendation-item">
                    <div className="recommendation-icon">💡</div>
                    <div className="recommendation-info">
                      <div className="recommendation-title">Right-size EC2 instances</div>
                      <div className="recommendation-desc">3 instances are over-provisioned</div>
                    </div>
                    <div className="recommendation-savings">Save $1,850/mo</div>
                  </div>
                  <div className="recommendation-item">
                    <div className="recommendation-icon">🔴</div>
                    <div className="recommendation-info">
                      <div className="recommendation-title">Stop idle resources</div>
                      <div className="recommendation-desc">5 resources unused for 30+ days</div>
                    </div>
                    <div className="recommendation-savings">Save $1,200/mo</div>
                  </div>
                  <div className="recommendation-item">
                    <div className="recommendation-icon">💾</div>
                    <div className="recommendation-info">
                      <div className="recommendation-title">Delete unattached volumes</div>
                      <div className="recommendation-desc">12 EBS volumes not in use</div>
                    </div>
                    <div className="recommendation-savings">Save $720/mo</div>
                  </div>
                  <div className="recommendation-item">
                    <div className="recommendation-icon">📦</div>
                    <div className="recommendation-info">
                      <div className="recommendation-title">Use Reserved Instances</div>
                      <div className="recommendation-desc">Convert 4 on-demand instances</div>
                    </div>
                    <div className="recommendation-savings">Save $480/mo</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="dashboard-card full-width">
              <div className="card-header">
                <h3>Recent Activity</h3>
                <a href="#" className="card-link">View All</a>
              </div>
              <div className="card-content">
                <div className="activity-list">
                  <div className="activity-item">
                    <div className="activity-icon">🔍</div>
                    <div className="activity-info">
                      <div className="activity-title">Resource scan completed</div>
                      <div className="activity-time">2 hours ago</div>
                    </div>
                  </div>
                  <div className="activity-item">
                    <div className="activity-icon">🔔</div>
                    <div className="activity-info">
                      <div className="activity-title">Budget alert triggered</div>
                      <div className="activity-time">5 hours ago</div>
                    </div>
                  </div>
                  <div className="activity-item">
                    <div className="activity-icon">💡</div>
                    <div className="activity-info">
                      <div className="activity-title">New optimization recommendation</div>
                      <div className="activity-time">1 day ago</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default DashboardPage;
