/**
 * Badge Component - Status indicators and labels
 */
import React from 'react';
import './Badge.css';

function Badge({ children, variant = 'default', size = 'medium', icon }) {
  return (
    <span className={`badge badge-${variant} badge-${size}`}>
      {icon && <span className="badge-icon">{icon}</span>}
      {children}
    </span>
  );
}

export default Badge;
