/**
 * Settings Page - Manage Cloud Accounts
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AddCloudAccountModal from '../components/AddCloudAccountModal';
import './SettingsPage.css';

function SettingsPage() {
  const navigate = useNavigate();
  const [showAddModal, setShowAddModal] = useState(false);
  const [cloudAccounts, setCloudAccounts] = useState([
    // Mock data for now
    { id: 1, provider: 'aws', name: 'Production AWS', status: 'connected' },
    { id: 2, provider: 'azure', name: 'Development Azure', status: 'connected' },
  ]);

  const handleAddAccount = (account) => {
    // Add new account to list
    const newAccount = {
      id: Date.now(),
      ...account,
      status: 'connected',
    };
    setCloudAccounts([...cloudAccounts, newAccount]);
    setShowAddModal(false);
  };

  const handleDeleteAccount = (id) => {
    if (window.confirm('Are you sure you want to remove this cloud account?')) {
      setCloudAccounts(cloudAccounts.filter(acc => acc.id !== id));
    }
  };

  const getProviderIcon = (provider) => {
    switch (provider) {
      case 'aws':
        return '🟠';
      case 'azure':
        return '🔵';
      case 'gcp':
        return '🔴';
      default:
        return '☁️';
    }
  };

  return (
    <div className="settings-page">
      {/* Header */}
      <div className="settings-header">
        <div>
          <h1>Settings</h1>
          <p>Manage your cloud accounts and preferences</p>
        </div>
        <button className="btn-back" onClick={() => navigate('/dashboard')}>
          ← Back to Dashboard
        </button>
      </div>

      {/* Cloud Accounts Section */}
      <div className="settings-section">
        <div className="section-header">
          <h2>Cloud Accounts</h2>
          <button className="btn-add" onClick={() => setShowAddModal(true)}>
            + Add Cloud Account
          </button>
        </div>

        {cloudAccounts.length === 0 ? (
          <div className="empty-state">
            <p>No cloud accounts connected</p>
            <button className="btn-primary" onClick={() => setShowAddModal(true)}>
              Add Your First Cloud Account
            </button>
          </div>
        ) : (
          <div className="accounts-grid">
            {cloudAccounts.map((account) => (
              <div key={account.id} className="account-card">
                <div className="account-header">
                  <span className="provider-icon">{getProviderIcon(account.provider)}</span>
                  <div className="account-info">
                    <h3>{account.name}</h3>
                    <span className="provider-label">{account.provider.toUpperCase()}</span>
                  </div>
                  <span className={`status-badge status-${account.status}`}>
                    {account.status}
                  </span>
                </div>
                <div className="account-actions">
                  <button className="btn-secondary" onClick={() => alert('Scan initiated!')}>
                    Scan Resources
                  </button>
                  <button className="btn-danger" onClick={() => handleDeleteAccount(account.id)}>
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add Account Modal */}
      {showAddModal && (
        <AddCloudAccountModal
          onClose={() => setShowAddModal(false)}
          onAdd={handleAddAccount}
        />
      )}
    </div>
  );
}

export default SettingsPage;
