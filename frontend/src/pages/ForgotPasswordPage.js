import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './InfoPage.css';

function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (event) => {
    event.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="info-page">
      <header className="info-page-header">
        <Link className="info-page-brand" to="/">
          <span className="info-page-brand-mark">CW</span>
          <span>CostWatch</span>
        </Link>

        <div className="info-page-actions">
          <Link className="info-page-link" to="/login">
            Back to login
          </Link>
        </div>
      </header>

      <main className="info-page-main">
        <section className="info-page-hero">
          <p className="info-page-eyebrow">Account Recovery</p>
          <h1>Reset access without breaking the calm.</h1>
          <p className="info-page-description">
            This flow now has a proper home in the app. The current implementation keeps things frontend-safe by
            capturing intent and showing the next recovery step.
          </p>
        </section>

        <section className="info-page-grid info-page-grid-single">
          <article className="info-page-card">
            <h2>Password reset</h2>
            {!submitted ? (
              <>
                <p>
                  Enter the email tied to your workspace. In a production-backed flow, this would trigger a reset email
                  and audit-safe recovery process.
                </p>

                <form className="info-page-form" onSubmit={handleSubmit}>
                  <label htmlFor="recovery-email">Work email</label>
                  <input
                    id="recovery-email"
                    type="email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    placeholder="you@company.com"
                    required
                  />
                  <button type="submit" className="info-page-button">
                    Continue
                  </button>
                </form>
              </>
            ) : (
              <div className="info-page-confirmation">
                <strong>Request captured</strong>
                <p>
                  If <span>{email}</span> belongs to a CostWatch workspace, the next step is to send recovery instructions
                  and surface backup support channels for urgent access issues.
                </p>
                <div className="info-page-cta-actions">
                  <Link className="info-page-button" to="/login">
                    Return to login
                  </Link>
                  <Link className="info-page-button-secondary" to="/contact">
                    Contact support
                  </Link>
                </div>
              </div>
            )}
          </article>
        </section>
      </main>
    </div>
  );
}

export default ForgotPasswordPage;
