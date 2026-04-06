import React from 'react';
import { Link } from 'react-router-dom';
import './InfoPage.css';

function NotFoundPage() {
  return (
    <div className="info-page">
      <header className="info-page-header">
        <Link className="info-page-brand" to="/">
          <span className="info-page-brand-mark">CW</span>
          <span>CostWatch</span>
        </Link>
      </header>

      <main className="info-page-main">
        <section className="info-page-hero">
          <p className="info-page-eyebrow">404</p>
          <h1>This route does not exist yet.</h1>
          <p className="info-page-description">
            Instead of silently bouncing you back home, the app now tells you exactly what happened and gives you a clear
            path forward.
          </p>
          <div className="info-page-cta-actions">
            <Link className="info-page-button" to="/">
              Go home
            </Link>
            <Link className="info-page-button-secondary" to="/login">
              Open login
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
}

export default NotFoundPage;
