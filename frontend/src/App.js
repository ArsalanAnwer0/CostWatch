import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import InfoPage from './pages/InfoPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import NotFoundPage from './pages/NotFoundPage';
import ErrorBoundary from './components/ErrorBoundary';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/docs" element={<InfoPage pageKey="docs" />} />
          <Route path="/about" element={<InfoPage pageKey="about" />} />
          <Route path="/contact" element={<InfoPage pageKey="contact" />} />
          <Route path="/careers" element={<InfoPage pageKey="careers" />} />
          <Route path="/terms" element={<InfoPage pageKey="terms" />} />
          <Route path="/privacy" element={<InfoPage pageKey="privacy" />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
