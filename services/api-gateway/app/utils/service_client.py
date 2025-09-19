import httpx
import logging
from typing import Dict, Any, Optional, List
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class ServiceClient:
    """Client for communicating with other microservices."""
    
    def __init__(self):
        self.resource_scanner_url = os.getenv(
            'RESOURCE_SCANNER_URL', 
            'http://localhost:8000'
        )
        self.cost_analyzer_url = os.getenv(
            'COST_ANALYZER_URL',
            'http://localhost:8001'  # Add cost-analyzer service
        )
        self.timeout = 30.0
    
    async def scan_all_resources(
        self, 
        regions: list = None, 
        include_costs: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Trigger comprehensive resource scan via Resource Scanner service."""
        try:
            data = {
                'regions': regions or ['us-west-2'],
                'include_costs': include_costs
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.resource_scanner_url}/scan/all",
                    json=data
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"Failed to communicate with Resource Scanner: {e}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"Resource Scanner returned error {e.response.status_code}: {e.response.text}")
            return None
    
    async def scan_ec2_resources(
        self, 
        region: str = 'us-west-2',
        include_costs: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Scan EC2 resources via Resource Scanner service."""
        try:
            data = {
                'region': region,
                'include_costs': include_costs
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.resource_scanner_url}/scan/ec2",
                    json=data
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to scan EC2 resources: {e}")
            return None
    
    async def get_optimization_recommendations(
        self, 
        resource_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get optimization recommendations via Resource Scanner service."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.resource_scanner_url}/optimize/{resource_type}"
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to get optimization recommendations: {e}")
            return None
    
    async def health_check_scanner(self) -> bool:
        """Check if Resource Scanner service is healthy."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.resource_scanner_url}/health")
                return response.status_code == 200
        except Exception:
            return False
    
    async def analyze_costs(
        self, 
        account_id: str, 
        start_date: str, 
        end_date: str
    ) -> Optional[Dict[str, Any]]:
        """Get cost analysis from cost-analyzer service."""
        try:
            params = {
                'account_id': account_id,
                'start_date': start_date, 
                'end_date': end_date
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.cost_analyzer_url}/analyze/costs",
                    params=params
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to get cost analysis: {e}")
            return None

    async def get_optimization_recommendations_from_analyzer(
        self,
        account_id: str,
        resource_types: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get optimization recommendations from cost-analyzer service."""
        try:
            params = {
                'account_id': account_id,
                'resource_types': resource_types or ["ec2", "rds", "ebs", "s3"]
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.cost_analyzer_url}/optimize/resources", 
                    params=params
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to get optimization recommendations: {e}")
            return None

    async def health_check_cost_analyzer(self) -> bool:
        """Check if cost-analyzer service is healthy."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.cost_analyzer_url}/health")
                return response.status_code == 200
        except Exception:
            return False