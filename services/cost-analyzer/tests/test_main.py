import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "cost-analyzer"

@patch('app.utils.database.get_db_connection')
def test_readiness_check(mock_db):
    """Test readiness check endpoint"""
    # Mock database connection
    mock_conn = MagicMock()
    mock_db.return_value = mock_conn
    
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"

@patch('app.services.cost_calculator.CostCalculator.calculate_costs')
@patch('app.utils.auth.verify_api_key')
def test_analyze_costs(mock_auth, mock_calculate):
    """Test cost analysis endpoint"""
    # Mock authentication
    mock_auth.return_value = "valid-api-key"
    
    # Mock cost calculation
    mock_calculate.return_value = MagicMock(
        account_id="123456789",
        total_cost=1000.50,
        daily_average=33.35
    )
    
    response = client.post(
        "/analyze/costs",
        params={
            "account_id": "123456789",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        },
        headers={"Authorization": "Bearer valid-api-key"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["account_id"] == "123456789"

@patch('app.services.optimizer.ResourceOptimizer.get_recommendations')
@patch('app.utils.auth.verify_api_key')
def test_optimize_resources(mock_auth, mock_optimize):
    """Test resource optimization endpoint"""
    # Mock authentication
    mock_auth.return_value = "valid-api-key"
    
    # Mock optimization
    mock_optimize.return_value = []
    
    response = client.post(
        "/optimize/resources",
        params={"account_id": "123456789"},
        headers={"Authorization": "Bearer valid-api-key"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["account_id"] == "123456789"
    assert "recommendations" in data

def test_unauthorized_access():
    """Test unauthorized access"""
    response = client.post(
        "/analyze/costs",
        params={
            "account_id": "123456789",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        }
    )
    
    assert response.status_code == 403  # No authorization header

