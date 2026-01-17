/**
 * Settings Page - Manage Cloud Accounts
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AddCloudAccountModal from '../components/AddCloudAccountModal';
import './SettingsPage.css';

function SettingsPage() {
  const navigate = useNavigate();
  const [showAddModal, setShowAddModal] = useState(false);
  const [cloudAccounts, setCloudAccounts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch cloud accounts on mount
  useEffect(() => {
    fetchCloudAccounts();
  }, []);

  const fetchCloudAccounts = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await fetch('http://localhost:8002/accounts', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setCloudAccounts(data);
      } else if (response.status === 401) {
        navigate('/login');
      } else {
        console.error('Failed to fetch cloud accounts');
      }
    } catch (err) {
      console.error('Error fetching cloud accounts:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddAccount = async (accountData) => {
    try {
      const token = localStorage.getItem('token');

      // Prepare credentials based on provider
      let credentials = {};
      if (accountData.provider === 'aws') {
        credentials = {
          access_key_id: accountData.awsAccessKey,
          secret_access_key: accountData.awsSecretKey,
          region: accountData.awsRegion,
        };
      } else if (accountData.provider === 'azure') {
        credentials = {
          subscription_id: accountData.azureSubscriptionId,
          tenant_id: accountData.azureTenantId,
          client_id: accountData.azureClientId,
          client_secret: accountData.azureClientSecret,
        };
      } else if (accountData.provider === 'gcp') {
        credentials = {
          project_id: accountData.gcpProjectId,
          service_account_key: accountData.gcpServiceAccountKey,
        };
      }

      const response = await fetch('http://localhost:8002/accounts', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: accountData.name,
          provider: accountData.provider,
          description: accountData.description || '',
          credentials: credentials,
        }),
      });

      if (response.ok) {
        const newAccount = await response.json();
        setCloudAccounts([...cloudAccounts, newAccount]);
        setShowAddModal(false);
      } else {
        const error = await response.json();
        alert(`Failed to add account: ${error.detail || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Error adding cloud account:', err);
      alert('Failed to add cloud account. Please try again.');
    }
  };

  const handleDeleteAccount = async (id) => {
    if (!window.confirm('Are you sure you want to remove this cloud account?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8002/accounts/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok || response.status === 204) {
        setCloudAccounts(cloudAccounts.filter(acc => acc.id !== id));
      } else {
        alert('Failed to delete account');
      }
    } catch (err) {
      console.error('Error deleting cloud account:', err);
      alert('Failed to delete account. Please try again.');
    }
  };

  const handleScanAccount = async (id, provider) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8002/accounts/${id}/scan`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        alert(`Resource scan initiated for ${provider.toUpperCase()} account!`);
      } else {
        alert('Failed to initiate scan');
      }
    } catch (err) {
      console.error('Error scanning account:', err);
      alert('Failed to initiate scan. Please try again.');
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

        {loading ? (
          <div className="loading-state">
            <p>Loading cloud accounts...</p>
          </div>
        ) : cloudAccounts.length === 0 ? (
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
                  <button className="btn-secondary" onClick={() => handleScanAccount(account.id, account.provider)}>
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
