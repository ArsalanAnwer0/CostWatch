import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { STORAGE_KEYS } from '../constants';
import { API_ENDPOINTS } from '../config/api';
import './AuthPages.css';

async function getCurrentUser(token, fallbackEmail) {
  try {
    const response = await fetch(API_ENDPOINTS.gateway.auth.me, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      return { email: fallbackEmail };
    }

    return await response.json();
  } catch (error) {
    return { email: fallbackEmail };
  }
}

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

    try {
      const response = await fetch(API_ENDPOINTS.gateway.auth.login, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        const token = data.token || data.access_token;
        const user = data.user || await getCurrentUser(token, formData.email);

        localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
        localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(user));
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
          <button className="btn-social" type="button" disabled aria-disabled="true">
            <span>Google Soon</span>
          </button>
          <button className="btn-social" type="button" disabled aria-disabled="true">
            <span>GitHub Soon</span>
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
