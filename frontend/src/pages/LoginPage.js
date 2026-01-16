import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './AuthPages.css';

function LoginPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // For demo: auto-login with any credentials
    setTimeout(() => {
      localStorage.setItem('token', 'demo-token-' + Date.now());
      localStorage.setItem('user', JSON.stringify({
        email: formData.email,
        name: 'Demo User',
        aws_account_id: '123456789012'
      }));
      navigate('/dashboard');
    }, 500);

    /* Production login code (commented for demo):
    try {
      const response = await fetch('http://localhost:8002/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('token', data.token || data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user || { email: formData.email }));
        navigate('/dashboard');
      } else {
        setError(data.message || data.detail || 'Login failed. Please check your credentials.');
      }
    } catch (err) {
      setError('Unable to connect to server. Please try again later.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
    */
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1 onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
            CostWatch
          </h1>
          <h2>Welcome Back</h2>
          <p>Login to your account to continue</p>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="you@example.com"
              required
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter your password"
              required
              autoComplete="current-password"
            />
          </div>

          <div className="form-options">
            <label className="checkbox-label">
              <input type="checkbox" />
              <span>Remember me</span>
            </label>
            <Link to="/forgot-password" className="forgot-link">
              Forgot password?
            </Link>
          </div>

          <button
            type="submit"
            className="btn-submit"
            disabled={loading}
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Don't have an account?{' '}
            <Link to="/register">Sign up for free</Link>
          </p>
        </div>

        <div className="auth-divider">
          <span>or continue with</span>
        </div>

        <div className="social-login">
          <button className="btn-social">
            <span>Google</span>
          </button>
          <button className="btn-social">
            <span>GitHub</span>
          </button>
        </div>

        <div className="back-home">
          <Link to="/">← Back to Home</Link>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
