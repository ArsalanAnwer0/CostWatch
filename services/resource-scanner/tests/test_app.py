import pytest
import json
from app.app import app

@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['service'] == 'CostWatch Resource Scanner'
    assert data['status'] == 'operational'

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'costwatch-resource-scanner'

def test_scan_all_resources(client):
    """Test scanning all resources."""
    response = client.post('/scan/all', 
                          json={'regions': ['us-west-2'], 'include_costs': True})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'scan_id' in data
    assert 'services' in data
    assert 'summary' in data

def test_scan_ec2_resources(client):
    """Test scanning EC2 resources."""
    response = client.post('/scan/ec2', 
                          json={'region': 'us-west-2', 'include_costs': True})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['scan_type'] == 'ec2'
    assert 'results' in data

def test_scan_rds_resources(client):
    """Test scanning RDS resources."""
    response = client.post('/scan/rds', 
                          json={'region': 'us-west-2', 'include_costs': True})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['scan_type'] == 'rds'
    assert 'results' in data

def test_scan_s3_resources(client):
    """Test scanning S3 resources."""
    response = client.post('/scan/s3', 
                          json={'include_costs': True})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['scan_type'] == 's3'
    assert 'results' in data

def test_optimization_recommendations(client):
    """Test optimization recommendations."""
    response = client.get('/optimize/ec2')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['resource_type'] == 'ec2'
    assert 'recommendations' in data

def test_metrics_endpoint(client):
    """Test metrics endpoint."""
    response = client.get('/metrics')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['service'] == 'resource-scanner'

def test_invalid_optimization_type(client):
    """Test invalid optimization resource type."""
    response = client.get('/optimize/invalid')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_404_endpoint(client):
    """Test 404 handling."""
    response = client.get('/nonexistent')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert 'available_endpoints' in data