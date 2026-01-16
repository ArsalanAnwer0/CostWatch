import React from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';

function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="landing-page">
      {/* Hero Section */}
      <header className="hero">
        <nav className="navbar">
          <div className="logo">
            <h1>CostWatch</h1>
          </div>
          <div className="nav-links">
            <a href="#features">Features</a>
            <a href="#how-it-works">How It Works</a>
            <a href="#pricing">Pricing</a>
            <button className="btn-secondary" onClick={() => navigate('/login')}>
              Login
            </button>
            <button className="btn-primary" onClick={() => navigate('/register')}>
              Get Started
            </button>
          </div>
        </nav>

        <div className="hero-content">
          <h1 className="hero-title">
            Reduce Your AWS Costs by 35%
          </h1>
          <p className="hero-subtitle">
            Smart cloud cost optimization platform that helps companies eliminate waste
            through intelligent monitoring and automated recommendations
          </p>
          <div className="hero-cta">
            <button className="btn-primary-large" onClick={() => navigate('/register')}>
              Start Free Trial
            </button>
            <button className="btn-secondary-large" onClick={() => navigate('/login')}>
              View Demo
            </button>
          </div>
          <p className="hero-note">No credit card required • 14-day free trial</p>
        </div>
      </header>

      {/* Stats Section */}
      <section className="stats">
        <div className="stats-container">
          <div className="stat-item">
            <h3>35%</h3>
            <p>Average Cost Reduction</p>
          </div>
          <div className="stat-item">
            <h3>$2.4M</h3>
            <p>Saved for Customers</p>
          </div>
          <div className="stat-item">
            <h3>500+</h3>
            <p>Companies Trust Us</p>
          </div>
          <div className="stat-item">
            <h3>24/7</h3>
            <p>Cost Monitoring</p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features">
        <h2 className="section-title">Powerful Features to Optimize Your Cloud Spending</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Real-Time Cost Monitoring</h3>
            <p>
              Track AWS spending across all services in real-time with detailed breakdowns
              by service, region, and department
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">💡</div>
            <h3>Smart Recommendations</h3>
            <p>
              AI-powered optimization recommendations for right-sizing instances,
              removing idle resources, and choosing better pricing models
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🔔</div>
            <h3>Intelligent Alerts</h3>
            <p>
              Get notified instantly about cost anomalies, budget overruns, and
              optimization opportunities before they impact your bottom line
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📈</div>
            <h3>Predictive Analytics</h3>
            <p>
              Machine learning-powered forecasting to predict future costs and
              plan budgets with confidence
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🔍</div>
            <h3>Resource Discovery</h3>
            <p>
              Automatically scan and identify all AWS resources including EC2, RDS,
              S3, and more for complete visibility
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📑</div>
            <h3>Custom Reports</h3>
            <p>
              Generate detailed cost reports for executives, finance teams, and
              stakeholders with customizable dashboards
            </p>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="how-it-works">
        <h2 className="section-title">Get Started in Minutes</h2>
        <div className="steps">
          <div className="step">
            <div className="step-number">1</div>
            <h3>Connect Your AWS Account</h3>
            <p>Securely connect your AWS account using read-only IAM roles</p>
          </div>

          <div className="step">
            <div className="step-number">2</div>
            <h3>Scan Your Resources</h3>
            <p>Our platform automatically discovers all your AWS resources and costs</p>
          </div>

          <div className="step">
            <div className="step-number">3</div>
            <h3>Get Recommendations</h3>
            <p>Receive instant optimization recommendations with potential savings</p>
          </div>

          <div className="step">
            <div className="step-number">4</div>
            <h3>Take Action & Save</h3>
            <p>Implement recommendations and watch your costs drop month over month</p>
          </div>
        </div>
      </section>

      {/* Problem/Solution Section */}
      <section className="problem-solution">
        <div className="problem-solution-container">
          <div className="problem">
            <h2>The Cloud Waste Problem</h2>
            <ul>
              <li>Companies waste 32% of their cloud spending on average</li>
              <li>Lack of visibility into what drives costs</li>
              <li>Unused EC2 instances running 24/7</li>
              <li>Over-provisioned resources</li>
              <li>Surprise AWS bills at end of month</li>
            </ul>
          </div>

          <div className="solution">
            <h2>The CostWatch Solution</h2>
            <ul>
              <li>Complete visibility into every dollar spent</li>
              <li>Automated waste detection and alerts</li>
              <li>Right-sizing recommendations based on usage</li>
              <li>Predictive budgeting and forecasting</li>
              <li>Real-time cost monitoring and controls</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="pricing">
        <h2 className="section-title">Simple, Transparent Pricing</h2>
        <div className="pricing-cards">
          <div className="pricing-card">
            <h3>Starter</h3>
            <div className="price">
              <span className="currency">$</span>
              <span className="amount">49</span>
              <span className="period">/month</span>
            </div>
            <ul className="pricing-features">
              <li>Up to $10K AWS spend</li>
              <li>5 AWS accounts</li>
              <li>Basic cost monitoring</li>
              <li>Email alerts</li>
              <li>7-day data retention</li>
            </ul>
            <button className="btn-pricing" onClick={() => navigate('/register')}>
              Start Free Trial
            </button>
          </div>

          <div className="pricing-card featured">
            <div className="popular-badge">Most Popular</div>
            <h3>Professional</h3>
            <div className="price">
              <span className="currency">$</span>
              <span className="amount">199</span>
              <span className="period">/month</span>
            </div>
            <ul className="pricing-features">
              <li>Up to $50K AWS spend</li>
              <li>20 AWS accounts</li>
              <li>Advanced analytics</li>
              <li>Slack & email alerts</li>
              <li>90-day data retention</li>
              <li>Custom dashboards</li>
            </ul>
            <button className="btn-pricing-primary" onClick={() => navigate('/register')}>
              Start Free Trial
            </button>
          </div>

          <div className="pricing-card">
            <h3>Enterprise</h3>
            <div className="price">
              <span className="currency">$</span>
              <span className="amount">499</span>
              <span className="period">/month</span>
            </div>
            <ul className="pricing-features">
              <li>Unlimited AWS spend</li>
              <li>Unlimited accounts</li>
              <li>ML-powered forecasting</li>
              <li>Multi-channel alerts</li>
              <li>1-year data retention</li>
              <li>Dedicated support</li>
              <li>Custom integrations</li>
            </ul>
            <button className="btn-pricing" onClick={() => navigate('/register')}>
              Contact Sales
            </button>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta">
        <h2>Ready to Optimize Your AWS Costs?</h2>
        <p>Join hundreds of companies saving millions on cloud infrastructure</p>
        <button className="btn-primary-large" onClick={() => navigate('/register')}>
          Start Your Free Trial
        </button>
        <p className="cta-note">14-day free trial • No credit card required • Cancel anytime</p>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>CostWatch</h4>
            <p>Smart cloud cost optimization for modern teams</p>
          </div>
          <div className="footer-section">
            <h4>Product</h4>
            <a href="#features">Features</a>
            <a href="#pricing">Pricing</a>
            <a href="/docs">Documentation</a>
          </div>
          <div className="footer-section">
            <h4>Company</h4>
            <a href="/about">About Us</a>
            <a href="/contact">Contact</a>
            <a href="/careers">Careers</a>
          </div>
          <div className="footer-section">
            <h4>Legal</h4>
            <a href="/privacy">Privacy Policy</a>
            <a href="/terms">Terms of Service</a>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2024 CostWatch. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;
