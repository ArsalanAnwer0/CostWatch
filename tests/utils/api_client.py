import httpx
import asyncio
from typing import Dict, Any, Optional
import json

class CostWatchAPIClient:
    """Test client for CostWatch API interactions."""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 30.0):
        self.base_url = base_url
        self.timeout = timeout
        self.auth_token: Optional[str] = None
        
    async def authenticate(self, email: str, password: str) -> bool:
        """Authenticate and store token."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data["access_token"]
                return True
            return False
    
    @property
    def auth_headers(self) -> Dict[str, str]:
        """Get authorization headers."""
        if not self.auth_token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    async def register_user(self, email: str, password: str, full_name: str, company: str = None) -> Dict[str, Any]:
        """Register a new user."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/auth/register",
                json={
                    "email": email,
                    "password": password,
                    "full_name": full_name,
                    "company": company
                }
            )
            return {"status_code": response.status_code, "data": response.json()}
    
    async def get_cost_summary(self, period: str = "30d") -> Dict[str, Any]:
        """Get cost summary."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/costs/summary?period={period}",
                headers=self.auth_headers
            )
            return {"status_code": response.status_code, "data": response.json()}
    
    async def trigger_resource_scan(self, regions: list = None, include_costs: bool = True) -> Dict[str, Any]:
        """Trigger resource scan."""
        regions = regions or ["us-west-2"]
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/costs/scan/trigger",
                json={
                    "regions": regions,
                    "include_costs": include_costs,
                    "scan_types": ["ec2", "rds", "s3"]
                },
                headers=self.auth_headers
            )
            return {"status_code": response.status_code, "data": response.json()}
    
    async def get_scan_status(self, scan_id: str) -> Dict[str, Any]:
        """Get scan status."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/costs/scan/status/{scan_id}",
                headers=self.auth_headers
            )
            return {"status_code": response.status_code, "data": response.json()}
    
    async def get_optimization_recommendations(self, resource_type: str) -> Dict[str, Any]:
        """Get optimization recommendations."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/costs/optimization/live/{resource_type}",
                headers=self.auth_headers
            )
            return {"status_code": response.status_code, "data": response.json()}
    
    async def check_services_health(self) -> Dict[str, Any]:
        """Check health of all services."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/costs/services/health",
                headers=self.auth_headers
            )
            return {"status_code": response.status_code, "data": response.json()}
    
    async def get_analytics_dashboard(self, period: str = "30d") -> Dict[str, Any]:
        """Get analytics dashboard."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/costs/analytics/dashboard?period={period}",
                headers=self.auth_headers
            )
            return {"status_code": response.status_code, "data": response.json()}

class ResourceScannerClient:
    """Test client for Resource Scanner service."""
    
    def __init__(self, base_url: str = "http://localhost:5000", timeout: float = 30.0):
        self.base_url = base_url
        self.timeout = timeout
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Resource Scanner health."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/health")
            return {"status_code": response.status_code, "data": response.json()}
    
    async def scan_all_resources(self, regions: list = None, include_costs: bool = True) -> Dict[str, Any]:
        """Scan all resources."""
        regions = regions or ["us-west-2"]
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/scan/all",
                json={"regions": regions, "include_costs": include_costs}
            )
            return {"status_code": response.status_code, "data": response.json()}
    
    async def scan_ec2_resources(self, region: str = "us-west-2", include_costs: bool = True) -> Dict[str, Any]:
        """Scan EC2 resources."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/scan/ec2",
                json={"region": region, "include_costs": include_costs}
            )
            return {"status_code": response.status_code, "data": response.json()}
    
    async def get_optimization_recommendations(self, resource_type: str) -> Dict[str, Any]:
        """Get optimization recommendations."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/optimize/{resource_type}")
            return {"status_code": response.status_code, "data": response.json()}