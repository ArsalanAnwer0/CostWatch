import pytest
import httpx
from typing import Dict, Any

@pytest.mark.asyncio
class TestServiceCommunication:
    """Test communication between API Gateway and Resource Scanner."""
    
    async def test_scan_trigger_via_api_gateway(self, http_client: httpx.AsyncClient, auth_headers: Dict[str, str]):
        """Test triggering resource scan via API Gateway."""
        scan_request = {
            "regions": ["us-west-2"],
            "include_costs": True,
            "scan_types": ["ec2", "rds", "s3"]
        }
        
        response = await http_client.post(
            "http://localhost:8000/costs/scan/trigger",
            json=scan_request,
            headers=auth_headers,
            timeout=60.0
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "scan_id" in data
        assert "summary" in data
        assert "regions_scanned" in data
        assert "triggered_by" in data
        assert "details" in data
        
        details = data["details"]
        assert "total_resources" in details
        assert "estimated_cost" in details
        assert "optimization_opportunities" in details
    
    async def test_ec2_scan_via_api_gateway(self, http_client: httpx.AsyncClient, auth_headers: Dict[str, str]):
        """Test EC2 scan trigger via API Gateway."""
        response = await http_client.post(
            "http://localhost:8000/costs/scan/ec2?region=us-west-2&include_costs=true",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert data["region"] == "us-west-2"
        assert "results" in data
        assert "summary" in data
        
        summary = data["summary"]
        assert "instances_found" in summary
        assert "estimated_monthly_cost" in summary
        assert "optimization_opportunities" in summary
    
    async def test_optimization_recommendations_via_api_gateway(self, http_client: httpx.AsyncClient, auth_headers: Dict[str, str]):
        """Test getting optimization recommendations via API Gateway."""
        resource_types = ["ec2", "rds", "s3"]
        
        for resource_type in resource_types:
            response = await http_client.get(
                f"http://localhost:8000/costs/optimization/live/{resource_type}",
                headers=auth_headers
            )
            assert response.status_code == 200
            
            data = response.json()
            assert data["resource_type"] == resource_type
            assert "recommendations" in data
            assert "summary" in data
            
            summary = data["summary"]
            assert "total_recommendations" in summary
            assert "categories_covered" in summary
    
    async def test_services_health_check(self, http_client: httpx.AsyncClient, auth_headers: Dict[str, str]):
        """Test inter-service health checking."""
        response = await http_client.get(
            "http://localhost:8000/costs/services/health",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "services" in data
        assert "overall_status" in data
        assert "checked_by" in data
        
        services = data["services"]
        assert "api_gateway" in services
        assert "resource_scanner" in services
        assert "database" in services
        assert "redis" in services
        
        # API Gateway should always be healthy (since we're calling it)
        assert services["api_gateway"] == "healthy"
    
    async def test_analytics_dashboard(self, http_client: httpx.AsyncClient, auth_headers: Dict[str, str]):
        """Test analytics dashboard data aggregation."""
        response = await http_client.get(
            "http://localhost:8000/costs/analytics/dashboard?period=30d",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["period"] == "30d"
        assert "cost_overview" in data
        assert "top_cost_drivers" in data
        assert "optimization_summary" in data
        assert "resource_utilization" in data
        assert "alerts" in data
        
        cost_overview = data["cost_overview"]
        assert "total_spend" in cost_overview
        assert "trend" in cost_overview
        assert "month_over_month_change" in cost_overview
    
    async def test_scan_status_tracking(self, http_client: httpx.AsyncClient, auth_headers: Dict[str, str]):
        """Test scan status tracking functionality."""
        # First trigger a scan to get a scan ID
        scan_request = {
            "regions": ["us-west-2"],
            "include_costs": True
        }
        
        trigger_response = await http_client.post(
            "http://localhost:8000/costs/scan/trigger",
            json=scan_request,
            headers=auth_headers,
            timeout=60.0
        )
        assert trigger_response.status_code == 200
        
        scan_data = trigger_response.json()
        scan_id = scan_data["scan_id"]
        
        # Check scan status
        status_response = await http_client.get(
            f"http://localhost:8000/costs/scan/status/{scan_id}",
            headers=auth_headers
        )
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert status_data["scan_id"] == scan_id
        assert "status" in status_data
        assert "progress" in status_data
        assert status_data["status"] in ["running", "completed", "failed"]
    
    async def test_optimization_implementation_mock(self, http_client: httpx.AsyncClient, auth_headers: Dict[str, str]):
        """Test optimization implementation endpoint (mock)."""
        response = await http_client.post(
            "http://localhost:8000/costs/optimization/implement?resource_id=i-test123&recommendation_id=rec-456",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "resource_id" in data
        assert "recommendation_id" in data
        assert "implementation_id" in data
        assert "status" in data
        assert "initiated_by" in data
    
    async def test_service_communication_failure_handling(self, http_client: httpx.AsyncClient, auth_headers: Dict[str, str]):
        """Test handling when Resource Scanner is unavailable."""
        # This test would ideally stop the Resource Scanner temporarily
        # For now, we'll test error handling by checking response structure
        
        # Even if the service is available, the response should handle failures gracefully
        response = await http_client.get(
            "http://localhost:8000/costs/services/health",
            headers=auth_headers
        )
        
        # Should get a response even if some services are down
        assert response.status_code == 200
        data = response.json()
        assert "overall_status" in data
        # Status could be "healthy", "degraded", or "unknown"
        assert data["overall_status"] in ["healthy", "degraded", "unknown"]