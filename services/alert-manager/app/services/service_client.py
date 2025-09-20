import httpx
import logging
from typing import Dict, Any, Optional, List
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class ServiceClient:
    """Client for communicating with other microservices."""
    
    def __init__(self):
        self.cost_analyzer_url = os.getenv(
            'COST_ANALYZER_URL',
            'http://localhost:8001'
        )
        self.analytics_engine_url = os.getenv(
            'ANALYTICS_ENGINE_URL',
            'http://localhost:8003'
        )
        self.resource_scanner_url = os.getenv(
            'RESOURCE_SCANNER_URL', 
            'http://localhost:8000'
        )
        self.timeout = 30.0
    
    async def get_cost_analysis(
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

    async def get_optimization_recommendations(
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

    async def get_analytics_insights(
        self,
        account_id: str,
        analysis_type: str = 'cost_optimization'
    ) -> Optional[Dict[str, Any]]:
        """Get analytics insights from analytics-engine service."""
        try:
            data = {
                'account_id': account_id,
                'analysis_type': analysis_type
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.analytics_engine_url}/analytics/insights",
                    json=data
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to get analytics insights: {e}")
            return None

    async def get_anomaly_detection(
        self,
        account_id: str,
        sensitivity: str = 'medium'
    ) -> Optional[Dict[str, Any]]:
        """Get anomaly detection from analytics-engine service."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.analytics_engine_url}/analytics/anomalies/{account_id}",
                    params={'sensitivity': sensitivity}
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to get anomaly detection: {e}")
            return None

    async def get_dashboard_data(
        self,
        account_id: str,
        period: str = 'last_30_days'
    ) -> Optional[Dict[str, Any]]:
        """Get dashboard data from analytics-engine service."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.analytics_engine_url}/analytics/dashboard/{account_id}",
                    params={'period': period}
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return None

    async def health_check_cost_analyzer(self) -> bool:
        """Check if cost-analyzer service is healthy."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.cost_analyzer_url}/health")
                return response.status_code == 200
        except Exception:
            return False

    async def health_check_analytics_engine(self) -> bool:
        """Check if analytics-engine service is healthy."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.analytics_engine_url}/health")
                return response.status_code == 200
        except Exception:
            return False

    async def health_check_resource_scanner(self) -> bool:
        """Check if resource-scanner service is healthy."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.resource_scanner_url}/health")
                return response.status_code == 200
        except Exception:
            return False