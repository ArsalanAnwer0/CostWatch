import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "CostWatch API Gateway"
    assert data["status"] == "operational"

def test_info_endpoint():
    """Test the info endpoint."""
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "costwatch-api-gateway"
    assert data["version"] == "1.0.0"

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "costwatch-api-gateway"

def test_openapi_docs():
    """Test that OpenAPI docs are accessible."""
    response = client.get("/docs")
    assert response.status_code == 200

def test_redoc():
    """Test that ReDoc is accessible."""
    response = client.get("/redoc")
    assert response.status_code == 200