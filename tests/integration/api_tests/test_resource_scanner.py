import pytest
import httpx
from typing import Dict, Any

@pytest.mark.asyncio
class TestResourceScanner:
    """Test Resource Scanner service endpoints."""
    
    async def test_health_endpoint(self, http_client: httpx.AsyncClient):
        """Test Resource Scanner health endpoint."""
        response = await http_client.get("http://localhost:5000/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "costwatch-resource-scanner"
        assert "timestamp" in data
    
    async def test_root_endpoint(self, http_client: httpx.AsyncClient):
        """Test Resource Scanner root endpoint."""
        response = await http_client.get("http://localhost:5000/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "CostWatch Resource Scanner"
        assert data["status"] == "operational"
    
    async def test_metrics_endpoint(self, http_client: httpx.AsyncClient):
        """Test metrics endpoint."""
        response = await http_client.get("http://localhost:5000/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "resource-scanner"
        assert "uptime" in data
        assert "total_scans_today" in data
    
    async def test_scan_all_resources(self, http_client: httpx.AsyncClient):
        """Test comprehensive resource scanning."""
        scan_request = {
            "regions": ["us-west-2"],
            "include_costs": True
        }
        
        response = await http_client.post(
            "http://localhost:5000/scan/all",
            json=scan_request,
            timeout=60.0  # Scanning might take longer
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "scan_id" in data
        assert "timestamp" in data
        assert "regions" in data
        assert "services" in data
        assert "summary" in data
        
        summary = data["summary"]
        assert "total_resources" in summary
        assert "total_estimated_cost" in summary
        assert "optimization_opportunities" in summary
    
    async def test_scan_ec2_resources(self, http_client: httpx.AsyncClient):
        """Test EC2 resource scanning."""
        scan_request = {
            "region": "us-west-2",
            "include_costs": True
        }
        
        response = await http_client.post(
            "http://localhost:5000/scan/ec2",
            json=scan_request
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["scan_type"] == "ec2"
        assert data["region"] == "us-west-2"
        assert "results" in data
        
        results = data["results"]
        assert "instances" in results
        assert "total_instances" in results
        assert "optimization_opportunities" in results
    
    async def test_scan_rds_resources(self, http_client: httpx.AsyncClient):
        """Test RDS resource scanning."""
        scan_request = {
            "region": "us-west-2",
            "include_costs": True
        }
        
        response = await http_client.post(
            "http://localhost:5000/scan/rds",
            json=scan_request
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["scan_type"] == "rds"
        assert data["region"] == "us-west-2"
        assert "results" in data
        
        results = data["results"]
        assert "databases" in results
        assert "total_databases" in results
    
    async def test_scan_s3_resources(self, http_client: httpx.AsyncClient):
        """Test S3 resource scanning."""
        scan_request = {
            "include_costs": True
        }
        
        response = await http_client.post(
            "http://localhost:5000/scan/s3",
            json=scan_request
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["scan_type"] == "s3"
        assert data["scope"] == "global"
        assert "results" in data
        
        results = data["results"]
        assert "buckets" in results
        assert "total_buckets" in results
    
    async def test_optimization_recommendations(self, http_client: httpx.AsyncClient):
        """Test optimization recommendations for different resource types."""
        resource_types = ["ec2", "rds", "s3"]
        
        for resource_type in resource_types:
            response = await http_client.get(f"http://localhost:5000/optimize/{resource_type}")
            assert response.status_code == 200
            
            data = response.json()
            assert data["resource_type"] == resource_type
            assert "recommendations" in data
            assert isinstance(data["recommendations"], list)
    
    async def test_invalid_optimization_type(self, http_client: httpx.AsyncClient):
        """Test invalid optimization resource type handling."""
        response = await http_client.get("http://localhost:5000/optimize/invalid")
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
    
    async def test_404_handling(self, http_client: httpx.AsyncClient):
        """Test 404 error handling."""
        response = await http_client.get("http://localhost:5000/nonexistent")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
        assert "available_endpoints" in data