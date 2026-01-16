/**
 * Toast Container Component - Manages multiple toasts
 */
import React, { useState, useCallback } from 'react';
import Toast from './Toast';

// Global toast functions
let addToastFn = null;

export const toast = {
  success: (message, duration) => addToastFn?.({ message, type: 'success', duration }),
  error: (message, duration) => addToastFn?.({ message, type: 'error', duration }),
  warning: (message, duration) => addToastFn?.({ message, type: 'warning', duration }),
  info: (message, duration) => addToastFn?.({ message, type: 'info', duration }),
};

function ToastContainer() {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback(({ message, type, duration = 5000 }) => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { id, message, type, duration }]);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  // Set global function
  React.useEffect(() => {
    addToastFn = addToast;
    return () => {
      addToastFn = null;
    };
  }, [addToast]);

  return (
    <div className="toast-container">
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          message={toast.message}
          type={toast.type}
          duration={toast.duration}
          onClose={() => removeToast(toast.id)}
        />
      ))}
    </div>
  );
}

export default ToastContainer;
