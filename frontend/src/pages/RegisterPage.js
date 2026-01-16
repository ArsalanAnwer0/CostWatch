import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './AuthPages.css';

function RegisterPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    confirmPassword: '',
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

  const validatePassword = () => {
    if (formData.password.length < 8) {
      return 'Password must be at least 8 characters long';
    }
    if (!/[A-Z]/.test(formData.password)) {
      return 'Password must contain at least one uppercase letter';
    }
    if (!/[a-z]/.test(formData.password)) {
      return 'Password must contain at least one lowercase letter';
    }
    if (!/[0-9]/.test(formData.password)) {
      return 'Password must contain at least one number';
    }
    if (formData.password !== formData.confirmPassword) {
      return 'Passwords do not match';
    }
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validate password
    const passwordError = validatePassword();
    if (passwordError) {
      setError(passwordError);
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:8002/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          full_name: formData.full_name,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Auto-login after successful registration
        if (data.token || data.access_token) {
          localStorage.setItem('token', data.token || data.access_token);
          localStorage.setItem('user', JSON.stringify(data.user || { email: formData.email, full_name: formData.full_name }));
          navigate('/dashboard');
        } else {
          // If no token returned, redirect to login
          navigate('/login');
        }
      } else {
        setError(data.message || data.detail || 'Registration failed. Please try again.');
      }
    } catch (err) {
      setError('Unable to connect to server. Please try again later.');
      console.error('Registration error:', err);
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
          <h2>Create Your Account</h2>
          <p>Start optimizing your AWS costs today</p>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="full_name">Full Name</label>
            <input
              type="text"
              id="full_name"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              placeholder="John Doe"
              required
              autoComplete="name"
            />
          </div>

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
              placeholder="Create a strong password"
              required
              autoComplete="new-password"
            />
            <small className="form-hint">
              Must be at least 8 characters with uppercase, lowercase, and number
            </small>
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Confirm your password"
              required
              autoComplete="new-password"
            />
          </div>

          <div className="form-options">
            <label className="checkbox-label">
              <input type="checkbox" required />
              <span>
                I agree to the <Link to="/terms">Terms of Service</Link> and{' '}
                <Link to="/privacy">Privacy Policy</Link>
              </span>
            </label>
          </div>

          <button
            type="submit"
            className="btn-submit"
            disabled={loading}
          >
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Already have an account?{' '}
            <Link to="/login">Login here</Link>
          </p>
        </div>

        <div className="auth-divider">
          <span>or sign up with</span>
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

export default RegisterPage;
