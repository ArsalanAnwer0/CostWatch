/**
 * Loading Spinner Component - Reusable loading indicator
 */
import React from 'react';
import './LoadingSpinner.css';

function LoadingSpinner({ size = 'medium', text = 'Loading...', fullPage = false }) {
  const sizeClass = `spinner-${size}`;

  const spinnerContent = (
    <div className={`loading-spinner-container ${fullPage ? 'full-page' : ''}`}>
      <div className={`spinner ${sizeClass}`}></div>
      {text && <p className="loading-text">{text}</p>}
    </div>
  );

  return spinnerContent;
}

export default LoadingSpinner;
