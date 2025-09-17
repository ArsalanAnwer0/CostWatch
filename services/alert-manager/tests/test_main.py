import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import create_app
from app.models.alert import Alert, AlertRule

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'alert-manager'

@patch('app.utils.database.get_db_connection')
def test_readiness_check(mock_db, client):
    """Test readiness check endpoint"""
    mock_conn = MagicMock()
    mock_db.return_value = mock_conn
    
    response = client.get('/ready')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ready'

@patch('app.services.notification_service.NotificationService.send_alert')
@patch('app.utils.auth.verify_api_key')
def test_send_alert(mock_auth, mock_send, client):
    """Test sending alert"""
    mock_auth.return_value = True
    mock_send.return_value = {
        'alert_id': 'test-alert',
        'channels': [],
        'success_count': 1,
        'failure_count': 0
    }
    
    alert_data = {
        'alert_id': 'test-alert',
        'alert_type': 'cost_threshold',
        'severity': 'high',
        'message': 'Test alert',
        'account_id': '123456789',
        'metadata': {}
    }
    
    response = client.post('/alerts/send',
                          data=json.dumps(alert_data),
                          content_type='application/json',
                          headers={'Authorization': 'Bearer test-key'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'sent'

def test_unauthorized_access(client):
    """Test unauthorized access"""
    response = client.post('/alerts/send',
                          data=json.dumps({}),
                          content_type='application/json')
    
    assert response.status_code == 401