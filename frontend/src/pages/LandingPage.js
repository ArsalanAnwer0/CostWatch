import React from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';

const stats = [
  { value: '35%', label: 'Average cost reduction' },
  { value: '$2.4M', label: 'Customer savings unlocked' },
  { value: '500+', label: 'Teams monitoring spend daily' },
  { value: '24/7', label: 'Automated anomaly coverage' },
];

const features = [
  {
    label: 'MC',
    title: 'Multi-cloud command center',
    description: 'Monitor AWS, Azure, and GCP from one polished control surface built for finance and engineering leaders.',
  },
  {
    label: 'AI',
    title: 'AI-powered optimization',
    description: 'Turn noisy cost telemetry into ranked actions with projected savings, confidence signals, and execution paths.',
  },
  {
    label: 'AL',
    title: 'Anomaly detection',
    description: 'Catch spend spikes early with context-rich alerts that explain why the change happened and what to do next.',
  },
  {
    label: 'FC',
    title: 'Forecasting and planning',
    description: 'See where month-end run rate is headed and plan budgets using live provider trends and workload signals.',
  },
  {
    label: 'RG',
    title: 'Service and region intelligence',
    description: 'Pinpoint expensive workloads across regions, environments, and platforms without digging through multiple consoles.',
  },
  {
    label: 'RP',
    title: 'Executive-ready reporting',
    description: 'Generate clean summaries for leadership, finance, and platform teams without hand-building spreadsheets.',
  },
];

const steps = [
  {
    number: '01',
    title: 'Connect cloud accounts',
    description: 'Securely attach read-only cloud access and sync spending, budgets, and workload metadata.',
  },
  {
    number: '02',
    title: 'Map spend drivers',
    description: 'CostWatch groups spend by provider, service, and region so the expensive patterns stand out instantly.',
  },
  {
    number: '03',
    title: 'Prioritize actions',
    description: 'AI recommendations rank the fastest wins, from rightsizing fleets to tightening lifecycle policies.',
  },
  {
    number: '04',
    title: 'Measure savings',
    description: 'Track realized impact over time and keep leadership aligned on efficiency progress.',
  },
];

const pricingPlans = [
  {
    name: 'Starter',
    price: '49',
    description: 'For lean teams beginning to formalize cloud cost visibility.',
    features: ['Up to $10K cloud spend', '5 cloud accounts', 'Core alerts and dashboards', '7-day history'],
    cta: 'Start free trial',
    featured: false,
  },
  {
    name: 'Professional',
    price: '199',
    description: 'For scaling product teams that need actionable optimization workflows.',
    features: ['Up to $50K cloud spend', '20 cloud accounts', 'Forecasting and budget controls', '90-day history', 'Slack and email alerts'],
    cta: 'Start free trial',
    featured: true,
  },
  {
    name: 'Enterprise',
    price: '499',
    description: 'For multi-team organizations with advanced reporting and governance needs.',
    features: ['Unlimited cloud spend', 'Unlimited accounts', 'Custom dashboards', 'Dedicated support', '1-year history'],
    cta: 'Contact sales',
    featured: false,
  },
];

function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="landing-page">
      <header className="hero">
        <nav className="navbar">
          <div className="logo">
            <div className="logo-mark">CW</div>
            <div>
              <h1>CostWatch</h1>
              <p>AI cost intelligence</p>
            </div>
          </div>

          <div className="nav-links">
            <a href="#features">Features</a>
            <a href="#how-it-works">How it works</a>
            <a href="#pricing">Pricing</a>
            <button type="button" className="landing-btn-secondary" onClick={() => navigate('/login')}>
              Login
            </button>
            <button type="button" className="landing-btn-primary" onClick={() => navigate('/register')}>
              Get started
            </button>
          </div>
        </nav>

        <div className="hero-layout">
          <div className="hero-content">
            <div className="hero-kicker">Built for modern platform, finance, and AI teams</div>
            <h2 className="hero-title">Turn multi-cloud cost chaos into a high-signal operating system.</h2>
            <p className="hero-subtitle">
              CostWatch helps ambitious companies see live spend across AWS, Azure, and GCP, understand what is changing,
              and act on the highest-confidence savings opportunities fast.
            </p>

            <div className="hero-provider-row">
              <span className="provider-pill provider-pill-aws">AWS</span>
              <span className="provider-pill provider-pill-azure">Azure</span>
              <span className="provider-pill provider-pill-gcp">GCP</span>
            </div>

            <div className="hero-cta">
              <button type="button" className="landing-btn-primary-large" onClick={() => navigate('/register')}>
                Start free trial
              </button>
              <button type="button" className="landing-btn-secondary-large" onClick={() => navigate('/login')}>
                View live dashboard
              </button>
            </div>

            <p className="hero-note">No credit card required. 14-day trial. Executive-ready reporting from day one.</p>
          </div>

          <div className="hero-visual">
            <div className="hero-panel hero-panel-main">
              <div className="hero-panel-topline">
                <span>Live spend pulse</span>
                <strong>Healthy</strong>
              </div>

              <div className="hero-panel-metric">
                <div>
                  <small>Total tracked spend</small>
                  <h3>$184.3K</h3>
                </div>
                <div className="hero-metric-badge">-12.4%</div>
              </div>

              <div className="hero-provider-metrics">
                <div>
                  <span>AWS</span>
                  <strong>$88.5K</strong>
                </div>
                <div>
                  <span>Azure</span>
                  <strong>$62.1K</strong>
                </div>
                <div>
                  <span>GCP</span>
                  <strong>$33.7K</strong>
                </div>
              </div>
            </div>

            <div className="hero-panel-grid">
              <div className="hero-panel">
                <span>Projected savings</span>
                <strong>$28.4K</strong>
                <small>this billing cycle</small>
              </div>
              <div className="hero-panel">
                <span>Top recommendation</span>
                <strong>Rightsize AKS + EKS</strong>
                <small>high confidence</small>
              </div>
            </div>
          </div>
        </div>
      </header>

      <section className="stats">
        <div className="stats-container">
          {stats.map((stat) => (
            <div className="stat-item" key={stat.label}>
              <h3>{stat.value}</h3>
              <p>{stat.label}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="features" className="features">
        <div className="section-heading">
          <p className="section-kicker">Product Surface</p>
          <h2 className="section-title">One front end for cost visibility, optimization, and operator confidence.</h2>
        </div>

        <div className="features-grid">
          {features.map((feature) => (
            <article className="feature-card" key={feature.title}>
              <div className="feature-icon">{feature.label}</div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="how-it-works" className="how-it-works">
        <div className="section-heading">
          <p className="section-kicker">Workflow</p>
          <h2 className="section-title">Go from connected accounts to measurable savings in four steps.</h2>
        </div>

        <div className="steps">
          {steps.map((step) => (
            <article className="step" key={step.number}>
              <div className="step-number">{step.number}</div>
              <h3>{step.title}</h3>
              <p>{step.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="problem-solution">
        <div className="problem-solution-container">
          <div className="problem">
            <p className="section-kicker">Without CostWatch</p>
            <h2>The cloud waste problem</h2>
            <ul>
              <li>Spend data lives in too many consoles and billing exports.</li>
              <li>Teams only notice overruns after finance closes the month.</li>
              <li>Idle resources, overprovisioning, and retention sprawl compound quietly.</li>
              <li>Engineering and finance lack a shared source of truth.</li>
            </ul>
          </div>

          <div className="solution">
            <p className="section-kicker">With CostWatch</p>
            <h2>The CostWatch operating model</h2>
            <ul>
              <li>Unified dashboards surface provider, service, and regional cost drivers instantly.</li>
              <li>Alerts and forecasts keep teams ahead of billing surprises.</li>
              <li>Optimization recommendations translate waste into clear savings paths.</li>
              <li>Leadership gets a calmer, cleaner story about cloud efficiency.</li>
            </ul>
          </div>
        </div>
      </section>

      <section id="pricing" className="pricing">
        <div className="section-heading">
          <p className="section-kicker">Pricing</p>
          <h2 className="section-title">Simple plans for companies growing their cloud footprint fast.</h2>
        </div>

        <div className="pricing-cards">
          {pricingPlans.map((plan) => (
            <article className={`pricing-card ${plan.featured ? 'featured' : ''}`} key={plan.name}>
              {plan.featured && <div className="popular-badge">Most popular</div>}
              <h3>{plan.name}</h3>
              <p className="pricing-description">{plan.description}</p>
              <div className="price">
                <span className="currency">$</span>
                <span className="amount">{plan.price}</span>
                <span className="period">/month</span>
              </div>
              <ul className="pricing-features">
                {plan.features.map((feature) => (
                  <li key={feature}>{feature}</li>
                ))}
              </ul>
              <button
                type="button"
                className={plan.featured ? 'landing-btn-pricing-primary' : 'landing-btn-pricing'}
                onClick={() => navigate('/register')}
              >
                {plan.cta}
              </button>
            </article>
          ))}
        </div>
      </section>

      <section className="cta">
        <div className="cta-card">
          <p className="section-kicker">Ready to move faster</p>
          <h2>Build a cleaner, sharper cloud cost workflow with CostWatch.</h2>
          <p>Join teams using CostWatch to turn cost telemetry into confident action.</p>
          <button type="button" className="landing-btn-primary-large" onClick={() => navigate('/register')}>
            Start your free trial
          </button>
          <p className="cta-note">14-day trial. No credit card required. Cancel anytime.</p>
        </div>
      </section>

      <footer className="footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>CostWatch</h4>
            <p>Premium multi-cloud cost intelligence for fast-scaling teams.</p>
          </div>
          <div className="footer-section">
            <h4>Product</h4>
            <a href="#features">Features</a>
            <a href="#pricing">Pricing</a>
            <a href="/docs">Documentation</a>
          </div>
          <div className="footer-section">
            <h4>Company</h4>
            <a href="/about">About us</a>
            <a href="/contact">Contact</a>
            <a href="/careers">Careers</a>
          </div>
          <div className="footer-section">
            <h4>Legal</h4>
            <a href="/privacy">Privacy policy</a>
            <a href="/terms">Terms of service</a>
          </div>
        </div>

        <div className="footer-bottom">
          <p>&copy; 2026 CostWatch. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;
