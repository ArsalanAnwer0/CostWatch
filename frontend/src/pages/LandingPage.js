import React, { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './LandingPage.css';

const stats = [
  { value: '35%', label: 'Average cost reduction' },
  { value: '3 Clouds', label: 'AWS, Azure, GCP in one view' },
  { value: 'Minutes', label: 'Time to surface top cost drivers' },
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
];

const trustedTeams = ['Northstar AI', 'Orbit Cloud', 'Signal Stack'];

const storySections = [
  { id: 'hero', label: 'Intro' },
  { id: 'signal', label: 'Signal' },
  { id: 'features', label: 'Product' },
  { id: 'how-it-works', label: 'Flow' },
  { id: 'start', label: 'Start' },
];

const topNavItems = [
  { label: 'Features', target: 'features' },
  { label: 'How it works', target: 'how-it-works' },
  { label: 'Start', target: 'start' },
];

function LandingPage() {
  const navigate = useNavigate();
  const scrollContainerRef = useRef(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [activeSectionId, setActiveSectionId] = useState(storySections[0].id);
  const showTopNav = activeSectionId === 'hero';

  const handleNavigate = (path) => {
    setIsMobileMenuOpen(false);
    navigate(path);
  };

  const scrollToSection = (sectionId) => {
    const container = scrollContainerRef.current;
    const target = container?.querySelector(`#${sectionId}`);

    if (!target) {
      return;
    }

    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    setActiveSectionId(sectionId);
    setIsMobileMenuOpen(false);
  };

  useEffect(() => {
    const root = scrollContainerRef.current;

    if (!root) {
      return undefined;
    }

    const sections = root.querySelectorAll('[data-story-section]');
    const observer = new IntersectionObserver(
      (entries) => {
        const visibleEntry = entries
          .filter((entry) => entry.isIntersecting)
          .sort((left, right) => right.intersectionRatio - left.intersectionRatio)[0];

        if (visibleEntry?.target?.id) {
          setActiveSectionId(visibleEntry.target.id);
        }
      },
      {
        root,
        threshold: [0.45, 0.6, 0.8],
      }
    );

    sections.forEach((section) => observer.observe(section));

    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!showTopNav && isMobileMenuOpen) {
      setIsMobileMenuOpen(false);
    }
  }, [isMobileMenuOpen, showTopNav]);

  return (
    <div className="landing-page" ref={scrollContainerRef}>
      <button
        type="button"
        className={`landing-mobile-overlay ${isMobileMenuOpen ? 'visible' : ''}`}
        onClick={() => setIsMobileMenuOpen(false)}
        aria-label="Close mobile navigation"
      ></button>

      <nav className={`navbar ${showTopNav ? 'navbar-visible' : 'navbar-hidden'}`}>
        <div className="logo">
          <div>
            <h1>Cost Watch</h1>
            <p>AI cost intelligence</p>
          </div>
        </div>

        <button
          type="button"
          className="landing-mobile-toggle"
          onClick={() => setIsMobileMenuOpen(true)}
          aria-label="Open navigation"
        >
          Menu
        </button>

        <div className="nav-links">
          {topNavItems.map((item) => (
            <button
              type="button"
              key={item.target}
              className={`landing-nav-link ${activeSectionId === item.target ? 'active' : ''}`}
              onClick={() => scrollToSection(item.target)}
            >
              {item.label}
            </button>
          ))}
          <button type="button" className="landing-btn-secondary" onClick={() => navigate('/login')}>
            Login
          </button>
          <button type="button" className="landing-btn-primary" onClick={() => navigate('/register')}>
            Get started
          </button>
        </div>
      </nav>

      <div className={`landing-mobile-menu ${isMobileMenuOpen ? 'open' : ''}`}>
        <div className="landing-mobile-menu-header">
          <strong>Navigate</strong>
          <button
            type="button"
            className="landing-mobile-toggle landing-mobile-toggle-close"
            onClick={() => setIsMobileMenuOpen(false)}
            aria-label="Close navigation"
          >
            Close
          </button>
        </div>
        <div className="landing-mobile-links">
          {topNavItems.map((item) => (
            <button type="button" key={item.target} className="landing-mobile-link" onClick={() => scrollToSection(item.target)}>
              {item.label}
            </button>
          ))}
          <button type="button" className="landing-btn-secondary" onClick={() => handleNavigate('/login')}>
            Login
          </button>
          <button type="button" className="landing-btn-primary" onClick={() => handleNavigate('/register')}>
            Get started
          </button>
        </div>
      </div>

      <section id="hero" data-story-section className="landing-story-section landing-story-section-hero">
        <header className="hero landing-story-shell">
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
                    <h3>$184K</h3>
                  </div>
                  <div className="hero-metric-badge">-12%</div>
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
            </div>
          </div>

          <button type="button" className="landing-scroll-cue" onClick={() => scrollToSection('signal')}>
            Scroll to the next chapter
          </button>
        </header>
      </section>

      <section id="signal" data-story-section className="landing-story-section">
        <div className="landing-story-shell landing-story-surface landing-story-surface-wide">
          <div className="section-heading section-heading-left">
            <p className="section-kicker">Signal</p>
            <h2 className="section-title">One clear proof point per screen keeps the product story easy to follow.</h2>
            <p className="landing-section-description">
              CostWatch focuses on the essentials: clear spend visibility, actionable recommendations, and fast decisions.
            </p>
          </div>

          <div className="landing-signal-stack">
            <div className="stats-container">
              {stats.map((stat) => (
                <div className="stat-item" key={stat.label}>
                  <h3>{stat.value}</h3>
                  <p>{stat.label}</p>
                </div>
              ))}
            </div>

            <div className="landing-trust-block">
              <p className="section-kicker">Trusted by fast-moving teams</p>
              <div className="trust-marquee">
                {trustedTeams.map((team) => (
                  <div className="trust-pill" key={team}>
                    {team}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" data-story-section className="landing-story-section">
        <div className="landing-story-shell landing-story-surface landing-story-surface-split">
          <div className="landing-story-copy">
            <p className="section-kicker">Product surface</p>
            <h2 className="section-title">One front end for cost visibility, optimization, and operator confidence.</h2>
            <p className="landing-section-description">
              Fewer moving parts, better focus. The product view keeps only the signals teams act on.
            </p>
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
        </div>
      </section>

      <section id="how-it-works" data-story-section className="landing-story-section">
        <div className="landing-story-shell landing-story-surface">
          <div className="section-heading">
            <p className="section-kicker">Workflow</p>
            <h2 className="section-title">Go from connected accounts to savings in three clear steps.</h2>
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
        </div>
      </section>

      <section id="start" data-story-section className="landing-story-section landing-story-section-end">
        <div className="landing-story-shell landing-end-shell">
          <div className="cta-card">
            <p className="section-kicker">Ready to move faster</p>
            <h2>Build a cleaner, sharper cloud cost workflow with CostWatch.</h2>
            <p>Join teams using CostWatch to turn cost telemetry into confident action.</p>
            <button type="button" className="landing-btn-primary-large" onClick={() => navigate('/register')}>
              Start your free trial
            </button>
            <p className="cta-note">14-day trial. No credit card required. Cancel anytime.</p>
          </div>

          <footer className="footer">
            <div className="footer-content">
              <div className="footer-section">
                <h4>CostWatch</h4>
                <p>Premium multi-cloud cost intelligence for fast-scaling teams.</p>
              </div>
              <div className="footer-section">
                <h4>Product</h4>
                <button type="button" className="footer-link-button" onClick={() => scrollToSection('features')}>
                  Features
                </button>
                <Link to="/docs">Documentation</Link>
              </div>
              <div className="footer-section">
                <h4>Company</h4>
                <Link to="/about">About us</Link>
                <Link to="/contact">Contact</Link>
                <Link to="/privacy">Privacy policy</Link>
                <Link to="/terms">Terms of service</Link>
              </div>
            </div>

            <div className="footer-bottom">
              <p>&copy; 2026 CostWatch. All rights reserved.</p>
            </div>
          </footer>
        </div>
      </section>
    </div>
  );
}

export default LandingPage;
