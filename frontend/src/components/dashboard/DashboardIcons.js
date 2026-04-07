import React from 'react';

function IconBase({ children, className = '' }) {
  return (
    <svg
      className={`dashboard-control-icon ${className}`.trim()}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

export function MenuIcon() {
  return (
    <IconBase>
      <path d="M4 7h16" />
      <path d="M4 12h16" />
      <path d="M4 17h16" />
    </IconBase>
  );
}

export function CloseIcon() {
  return (
    <IconBase>
      <path d="M6 6l12 12" />
      <path d="M18 6L6 18" />
    </IconBase>
  );
}

export function RefreshIcon({ spinning = false }) {
  return (
    <IconBase className={spinning ? 'is-spinning' : ''}>
      <path d="M20 11a8 8 0 0 0-14.9-3" />
      <path d="M4 4v5h5" />
      <path d="M4 13a8 8 0 0 0 14.9 3" />
      <path d="M20 20v-5h-5" />
    </IconBase>
  );
}

export function BellIcon() {
  return (
    <IconBase>
      <path d="M15 17H9" />
      <path d="M18 17H6l1.5-2.6V10a4.5 4.5 0 0 1 9 0v4.4L18 17Z" />
      <path d="M10 20a2 2 0 0 0 4 0" />
    </IconBase>
  );
}
