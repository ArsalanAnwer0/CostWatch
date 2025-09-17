import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import create_app

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
    assert data['service'] == 'analytics-engine'

@patch('app.utils.database.get_db_connection')
def test_readiness_check(mock_db, client):
    """Test readiness check endpoint"""
    mock_conn = MagicMock()
    mock_db.return_value = mock_conn
    
    response = client.get('/ready')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ready'

@patch('app.services.analytics_service.AnalyticsService.analyze_trends')
@patch('app.utils.auth.verify_api_key')
def test_analyze_trends(mock_auth, mock_analyze, client):
    """Test trend analysis endpoint"""
    mock_auth.return_value = True
    mock_analyze.return_value = {
        'overall_trend': {'direction': 'increasing', 'strength': 12.5},
        'growth_rate': {'weekly_growth_rate': 8.3}
    }
    
    request_data = {
        'account_id': '123456789',
        'start_date': '2024-01-01',
        'end_date': '2024-01-31',
        'metrics': ['total_cost']
    }
    
    response = client.post('/analytics/trends',
                          data=json.dumps(request_data),
                          content_type='application/json',
                          headers={'Authorization': 'Bearer test-key'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['account_id'] == '123456789'
    assert 'trends' in data

def test_unauthorized_access(client):
    """Test unauthorized access"""
    response = client.post('/analytics/trends',
                          data=json.dumps({}),
                          content_type='application/json')
    
    assert response.status_code == 401