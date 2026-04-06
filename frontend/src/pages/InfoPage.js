import React from 'react';
import { Link } from 'react-router-dom';
import { SITE_PAGES } from '../content/siteContent';
import './InfoPage.css';

function InfoPage({ pageKey }) {
  const page = SITE_PAGES[pageKey];

  if (!page) {
    return null;
  }

  return (
    <div className="info-page">
      <header className="info-page-header">
        <Link className="info-page-brand" to="/">
          <span className="info-page-brand-mark">CW</span>
          <span>CostWatch</span>
        </Link>

        <div className="info-page-actions">
          <Link className="info-page-link" to="/login">
            Login
          </Link>
          <Link className="info-page-button" to="/register">
            Get started
          </Link>
        </div>
      </header>

      <main className="info-page-main">
        <section className="info-page-hero">
          <p className="info-page-eyebrow">{page.eyebrow}</p>
          <h1>{page.title}</h1>
          <p className="info-page-description">{page.description}</p>

          <div className="info-page-stats">
            {page.heroStats.map((stat) => (
              <div className="info-stat-card" key={stat.label}>
                <strong>{stat.value}</strong>
                <span>{stat.label}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="info-page-grid">
          {page.sections.map((section) => (
            <article className="info-page-card" key={section.title}>
              <h2>{section.title}</h2>
              <p>{section.body}</p>
            </article>
          ))}
        </section>

        <section className="info-page-cta">
          <div className="info-page-card">
            <p className="info-page-eyebrow">Next move</p>
            <h2>See the product instead of reading about it.</h2>
            <p>
              The supporting pages are now real routes, but the main signal is still the product itself:
              the dashboard, the alerts, and the optimization workflows.
            </p>
            <div className="info-page-cta-actions">
              <Link className="info-page-button" to="/register">
                Start free trial
              </Link>
              <Link className="info-page-button-secondary" to="/login">
                Open dashboard
              </Link>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default InfoPage;
