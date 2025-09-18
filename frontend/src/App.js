import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>CostWatch Dashboard</h1>
        <nav>
          <ul>
            <li><a href="#dashboard">Dashboard</a></li>
            <li><a href="#costs">Cost Analysis</a></li>
            <li><a href="#resources">Resources</a></li>
            <li><a href="#alerts">Alerts</a></li>
          </ul>
        </nav>
      </header>
      
      <main className="main-content">
        <section id="dashboard">
          <h2>Cost Overview</h2>
          <div className="dashboard-cards">
            <div className="card">
              <h3>Monthly Spend</h3>
              <p className="amount">$2,847.52</p>
            </div>
            <div className="card">
              <h3>This Week</h3>
              <p className="amount">$687.23</p>
            </div>
            <div className="card">
              <h3>Active Resources</h3>
              <p className="amount">142</p>
            </div>
            <div className="card">
              <h3>Alerts</h3>
              <p className="amount alert">3</p>
            </div>
          </div>
        </section>

        <section id="costs">
          <h2>Cost Analysis</h2>
          <div className="cost-breakdown">
            <h3>Top Services by Cost</h3>
            <ul>
              <li>EC2 Instances: $1,245.30</li>
              <li>RDS Database: $892.15</li>
              <li>S3 Storage: $456.78</li>
              <li>Load Balancer: $253.29</li>
            </ul>
          </div>
        </section>

        <section id="resources">
          <h2>AWS Resources</h2>
          <div className="resources-table">
            <table>
              <thead>
                <tr>
                  <th>Resource Type</th>
                  <th>Name</th>
                  <th>Region</th>
                  <th>Monthly Cost</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>EC2</td>
                  <td>web-server-01</td>
                  <td>us-west-2</td>
                  <td>$124.50</td>
                </tr>
                <tr>
                  <td>RDS</td>
                  <td>main-database</td>
                  <td>us-west-2</td>
                  <td>$89.20</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section id="alerts">
          <h2>Cost Alerts</h2>
          <div className="alerts-list">
            <div className="alert-item high">
              <h4>High Cost Alert</h4>
              <p>Monthly budget exceeded by 15%</p>
            </div>
            <div className="alert-item medium">
              <h4>Resource Alert</h4>
              <p>Unused EC2 instance detected</p>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;