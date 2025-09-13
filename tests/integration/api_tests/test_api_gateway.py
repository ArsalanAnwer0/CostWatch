import pytest
import httpx
from typing import Dict, Any

@pytest.mark.asyncio
class TestAPIGateway:
    """Test API Gateway endpoints and functionality."""
    
    async def test_health_endpoint(self, http_client: httpx.AsyncClient):
        """Test API Gateway health endpoint."""
        response = await http_client.get("http://localhost:8000/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "costwatch-api-gateway"
        assert "timestamp" in data
        assert "uptime" in data
    
    async def test_root_endpoint(self, http_client: httpx.AsyncClient):
        """Test API Gateway root endpoint."""
        response = await http_client.get("http://localhost:8000/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "CostWatch API Gateway"
        assert data["status"] == "operational"
    
    async def test_info_endpoint(self, http_client: httpx.AsyncClient):
        """Test API Gateway info endpoint."""
        response = await http_client.get("http://localhost:8000/info")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "costwatch-api-gateway"
        assert data["version"] == "1.0.0"
    
    async def test_openapi_docs(self, http_client: httpx.AsyncClient):
        """Test API documentation is accessible."""
        response = await http_client.get("http://localhost:8000/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    async def test_authentication_flow(self, http_client: httpx.AsyncClient, test_user_credentials: Dict[str, str]):
        """Test complete authentication flow."""
        # Test registration
        register_response = await http_client.post(
            "http://localhost:8000/auth/register",
            json={
                "email": f"test_auth_{hash(str(test_user_credentials))}@costwatch.com",
                "password": test_user_credentials["password"],
                "full_name": "Auth Test User",
                "company": "Test Company"
            }
        )
        
        # Should succeed or fail gracefully if user exists
        assert register_response.status_code in [200, 400]
        
        # Test login
        login_response = await http_client.post(
            "http://localhost:8000/auth/login",
            json={
                "email": f"test_auth_{hash(str(test_user_credentials))}@costwatch.com",
                "password": test_user_credentials["password"]
            }
        )
        
        if register_response.status_code == 200:
            assert login_response.status_code == 200
            
            token_data = login_response.json()
            assert "access_token" in token_data
            assert "token_type" in token_data
            assert token_data["token_type"] == "bearer"
    
    async def test_cost_summary_authenticated(self, http_client: httpx.AsyncClient, auth_headers: Dict[str, str]):
        """Test cost summary endpoint with authentication."""
        response = await http_client.get(
            "http://localhost:8000/costs/summary",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "total_cost" in data
        assert "period" in data
        assert "top_services" in data
        assert "cost_trend" in data
        assert "savings_opportunity" in data
    
    async def test_cost_details_authenticated(self, http_client: httpx.AsyncClient, auth_headers: Dict[str, str]):
        """Test cost details endpoint with authentication."""
        response = await http_client.get(
            "http://localhost:8000/costs/details?days=7",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if data:  # If there's data, validate structure
            cost_item = data[0]
            assert "service_name" in cost_item
            assert "cost" in cost_item
            assert "currency" in cost_item
            assert "date" in cost_item
            assert "region" in cost_item
    
    async def test_unauthorized_access(self, http_client: httpx.AsyncClient):
        """Test that protected endpoints require authentication."""
        protected_endpoints = [
            "/costs/summary",
            "/costs/details", 
            "/costs/optimization",
            "/costs/forecast"
        ]
        
        for endpoint in protected_endpoints:
            response = await http_client.get(f"http://localhost:8000{endpoint}")
            assert response.status_code == 401
    
    async def test_cost_forecast(self, http_client: httpx.AsyncClient, auth_headers: Dict[str, str]):
        """Test cost forecasting endpoint."""
        response = await http_client.get(
            "http://localhost:8000/costs/forecast?months=3",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "current_monthly_cost" in data
        assert "forecast_period_months" in data
        assert "forecast_data" in data
        assert len(data["forecast_data"]) == 3
        
        for forecast_item in data["forecast_data"]:
            assert "month" in forecast_item
            assert "forecasted_cost" in forecast_item
            assert "confidence" in forecast_item
    
    async def test_alert_creation(self, http_client: httpx.AsyncClient, auth_headers: Dict[str, str]):
        """Test cost alert creation."""
        response = await http_client.post(
            "http://localhost:8000/costs/alerts?threshold=1000&period=monthly",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "alert_id" in data
        assert "threshold" in data
        assert "period" in data