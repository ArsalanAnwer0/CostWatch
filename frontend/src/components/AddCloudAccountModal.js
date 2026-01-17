/**
 * Add Cloud Account Modal - Multi-cloud account setup
 */
import React, { useState } from 'react';
import Modal from './Modal';
import './AddCloudAccountModal.css';

function AddCloudAccountModal({ onClose, onAdd }) {
  const [selectedProvider, setSelectedProvider] = useState('aws');
  const [formData, setFormData] = useState({
    name: '',
    // AWS fields
    awsAccessKey: '',
    awsSecretKey: '',
    awsRegion: 'us-east-1',
    // Azure fields
    azureSubscriptionId: '',
    azureTenantId: '',
    azureClientId: '',
    azureClientSecret: '',
    // GCP fields
    gcpProjectId: '',
    gcpServiceAccountKey: '',
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onAdd({
      provider: selectedProvider,
      name: formData.name,
      credentials: {}, // In production, would include actual credentials
    });
  };

  const renderProviderFields = () => {
    switch (selectedProvider) {
      case 'aws':
        return (
          <>
            <div className="form-group">
              <label>AWS Access Key ID</label>
              <input
                type="text"
                name="awsAccessKey"
                value={formData.awsAccessKey}
                onChange={handleChange}
                placeholder="AKIAIOSFODNN7EXAMPLE"
                required
              />
            </div>
            <div className="form-group">
              <label>AWS Secret Access Key</label>
              <input
                type="password"
                name="awsSecretKey"
                value={formData.awsSecretKey}
                onChange={handleChange}
                placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
                required
              />
            </div>
            <div className="form-group">
              <label>Default Region</label>
              <select name="awsRegion" value={formData.awsRegion} onChange={handleChange}>
                <option value="us-east-1">US East (N. Virginia)</option>
                <option value="us-west-2">US West (Oregon)</option>
                <option value="eu-west-1">EU (Ireland)</option>
                <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
              </select>
            </div>
          </>
        );

      case 'azure':
        return (
          <>
            <div className="form-group">
              <label>Subscription ID</label>
              <input
                type="text"
                name="azureSubscriptionId"
                value={formData.azureSubscriptionId}
                onChange={handleChange}
                placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                required
              />
            </div>
            <div className="form-group">
              <label>Tenant ID</label>
              <input
                type="text"
                name="azureTenantId"
                value={formData.azureTenantId}
                onChange={handleChange}
                placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                required
              />
            </div>
            <div className="form-group">
              <label>Client ID</label>
              <input
                type="text"
                name="azureClientId"
                value={formData.azureClientId}
                onChange={handleChange}
                placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                required
              />
            </div>
            <div className="form-group">
              <label>Client Secret</label>
              <input
                type="password"
                name="azureClientSecret"
                value={formData.azureClientSecret}
                onChange={handleChange}
                required
              />
            </div>
          </>
        );

      case 'gcp':
        return (
          <>
            <div className="form-group">
              <label>Project ID</label>
              <input
                type="text"
                name="gcpProjectId"
                value={formData.gcpProjectId}
                onChange={handleChange}
                placeholder="my-project-123456"
                required
              />
            </div>
            <div className="form-group">
              <label>Service Account Key (JSON)</label>
              <textarea
                name="gcpServiceAccountKey"
                value={formData.gcpServiceAccountKey}
                onChange={handleChange}
                placeholder='{"type": "service_account", ...}'
                rows="6"
                required
              ></textarea>
            </div>
          </>
        );

      default:
        return null;
    }
  };

  const footer = (
    <>
      <button className="btn-modal-cancel" onClick={onClose}>
        Cancel
      </button>
      <button className="btn-modal-submit" type="submit" form="add-account-form">
        Add Account
      </button>
    </>
  );

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title="Add Cloud Account"
      footer={footer}
      size="medium"
    >
      <form id="add-account-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Account Name</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="e.g., Production AWS"
            required
          />
        </div>

        {/* Provider Selector */}
        <div className="provider-selector">
          <label>Cloud Provider</label>
          <div className="provider-tabs">
            <button
              type="button"
              className={`provider-tab ${selectedProvider === 'aws' ? 'active' : ''}`}
              onClick={() => setSelectedProvider('aws')}
            >
              🟠 AWS
            </button>
            <button
              type="button"
              className={`provider-tab ${selectedProvider === 'azure' ? 'active' : ''}`}
              onClick={() => setSelectedProvider('azure')}
            >
              🔵 Azure
            </button>
            <button
              type="button"
              className={`provider-tab ${selectedProvider === 'gcp' ? 'active' : ''}`}
              onClick={() => setSelectedProvider('gcp')}
            >
              🔴 GCP
            </button>
          </div>
        </div>

        {/* Provider-specific fields */}
        {renderProviderFields()}
      </form>
    </Modal>
  );
}

export default AddCloudAccountModal;
