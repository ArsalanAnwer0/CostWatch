import httpx
import logging
from typing import Dict, Any, Optional
import os

logger = logging.getLogger(__name__)


class ServiceClient:
    """Client for communicating with other microservices."""

    def __init__(self):
        self.resource_scanner_url = os.getenv(
            'RESOURCE_SCANNER_URL',
            'http://resource-scanner:8000'
        )
        self.cost_service_url = os.getenv(
            'COST_SERVICE_URL',
            'http://cost-service:8001'
        )
        self.timeout = 30.0

    async def scan_all_resources(
        self,
        regions: list = None,
        include_costs: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Trigger resource scan via Resource Scanner service."""
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
            logger.error(f"Resource Scanner returned error {e.response.status_code}")
            return None

    async def analyze_costs(
        self,
        account_id: str,
        start_date: str,
        end_date: str
    ) -> Optional[Dict[str, Any]]:
        """Get cost analysis from cost-service."""
        try:
            data = {
                'account_id': account_id,
                'start_date': start_date,
                'end_date': end_date
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.cost_service_url}/analyze/costs",
                    json=data
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Failed to get cost analysis: {e}")
            return None

    async def health_check_scanner(self) -> bool:
        """Check if Resource Scanner is healthy."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.resource_scanner_url}/health")
                return response.status_code == 200
        except Exception:
            return False

    async def health_check_cost_service(self) -> bool:
        """Check if Cost Service is healthy."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.cost_service_url}/health")
                return response.status_code == 200
        except Exception:
            return False
