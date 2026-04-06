/**
 * ProtectedRoute Component - Requires authentication to access
 */
import React from 'react';
import { Navigate } from 'react-router-dom';
import { STORAGE_KEYS } from '../constants';

function ProtectedRoute({ children }) {
  const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);

  // If no token, redirect to login
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // If token exists, render the protected component
  return children;
}

export default ProtectedRoute;
