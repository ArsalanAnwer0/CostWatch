import React, { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
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

const trustedTeams = ['Northstar AI', 'Ledger Forge', 'Orbit Cloud', 'Signal Stack', 'Nova Platform'];

const testimonials = [
  {
    quote:
      'CostWatch gave our engineering and finance teams the same spend story for the first time. That alone changed how we operate.',
    author: 'Mina Patel',
    role: 'VP Platform, Orbit Cloud',
  },
  {
    quote:
      'We moved from reactive cost reviews to a weekly optimization rhythm. The product feels more like an operating system than a dashboard.',
    author: 'Jonas Reed',
    role: 'Director of Infrastructure, Signal Stack',
  },
  {
    quote:
      'The UI makes complex cost movement legible. Our leadership team can see the signal without needing a walkthrough every time.',
    author: 'Lena Brooks',
    role: 'Finance Lead, Northstar AI',
  },
];

const faqs = [
  {
    question: 'Does CostWatch support multi-cloud teams or only AWS-heavy companies?',
    answer:
      'The frontend is designed around AWS, Azure, and GCP from the start, with provider-aware breakdowns, filters, and operator workflows throughout the dashboard.',
  },
  {
    question: 'Can finance and engineering use the same dashboard without getting lost?',
    answer:
      'That is the point of the product direction. The experience is intentionally built to give finance, platform, and leadership a shared operating view with different levels of detail.',
  },
  {
    question: 'How fast can a team start seeing value?',
    answer:
      'The current product flow is optimized around fast visibility: connect accounts, sync spend drivers, surface anomalies, and prioritize savings opportunities in the first session.',
  },
];

const storySections = [
  { id: 'hero', label: 'Intro' },
  { id: 'signal', label: 'Signal' },
  { id: 'features', label: 'Product' },
  { id: 'how-it-works', label: 'Flow' },
  { id: 'compare', label: 'Why' },
  { id: 'proof', label: 'Proof' },
  { id: 'pricing', label: 'Pricing' },
  { id: 'faq', label: 'Questions' },
  { id: 'start', label: 'Start' },
];

const topNavItems = [
  { label: 'Features', target: 'features' },
  { label: 'How it works', target: 'how-it-works' },
  { label: 'Pricing', target: 'pricing' },
  { label: 'FAQ', target: 'faq' },
];

function LandingPage() {
  const navigate = useNavigate();
  const scrollContainerRef = useRef(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [activeSectionId, setActiveSectionId] = useState(storySections[0].id);

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

  return (
    <div className="landing-page" ref={scrollContainerRef}>
      <button
        type="button"
        className={`landing-mobile-overlay ${isMobileMenuOpen ? 'visible' : ''}`}
        onClick={() => setIsMobileMenuOpen(false)}
        aria-label="Close mobile navigation"
      ></button>

      <nav className="navbar">
        <div className="logo">
          <div className="logo-mark">CW</div>
          <div>
            <h1>CostWatch</h1>
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

      <div className="landing-story-rail" aria-label="Landing page progress">
        {storySections.map((section) => (
          <button
            type="button"
            key={section.id}
            className={`landing-story-rail-item ${activeSectionId === section.id ? 'active' : ''}`}
            onClick={() => scrollToSection(section.id)}
            aria-label={`Jump to ${section.label}`}
          >
            <span className="landing-story-rail-label">{section.label}</span>
            <span className="landing-story-rail-dot"></span>
          </button>
        ))}
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
              Instead of compressing everything into one dense page, this landing flow gives each idea room to land:
              trust, product depth, operating model, proof, pricing, and the final call to action.
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
              The page should feel like a narrative, not a cramped feature dump. This section shows the product breadth,
              but still gives the content enough space to breathe.
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
        </div>
      </section>

      <section id="compare" data-story-section className="landing-story-section">
        <div className="landing-story-shell landing-story-surface">
          <div className="section-heading">
            <p className="section-kicker">Why it matters</p>
            <h2 className="section-title">Each scroll should move the story forward, not pile on more noise.</h2>
          </div>

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
        </div>
      </section>

      <section id="proof" data-story-section className="landing-story-section">
        <div className="landing-story-shell landing-story-surface">
          <div className="section-heading">
            <p className="section-kicker">Customer signal</p>
            <h2 className="section-title">Teams should feel calmer after opening a cost product, not more overwhelmed.</h2>
          </div>

          <div className="testimonial-grid">
            {testimonials.map((testimonial) => (
              <article className="testimonial-card" key={testimonial.author}>
                <p className="testimonial-quote">"{testimonial.quote}"</p>
                <div className="testimonial-meta">
                  <strong>{testimonial.author}</strong>
                  <span>{testimonial.role}</span>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="pricing" data-story-section className="landing-story-section">
        <div className="landing-story-shell landing-story-surface">
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
        </div>
      </section>

      <section id="faq" data-story-section className="landing-story-section">
        <div className="landing-story-shell landing-story-surface">
          <div className="section-heading">
            <p className="section-kicker">FAQ</p>
            <h2 className="section-title">A few practical questions teams ask before they commit.</h2>
          </div>

          <div className="faq-grid">
            {faqs.map((faq) => (
              <article className="faq-card" key={faq.question}>
                <h3>{faq.question}</h3>
                <p>{faq.answer}</p>
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
                <button type="button" className="footer-link-button" onClick={() => scrollToSection('pricing')}>
                  Pricing
                </button>
                <Link to="/docs">Documentation</Link>
              </div>
              <div className="footer-section">
                <h4>Company</h4>
                <Link to="/about">About us</Link>
                <Link to="/contact">Contact</Link>
                <Link to="/careers">Careers</Link>
              </div>
              <div className="footer-section">
                <h4>Legal</h4>
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
