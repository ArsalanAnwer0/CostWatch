from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime

from utils.service_client import ServiceClient

router = APIRouter()
service_client = ServiceClient()


@router.get("/")
async def health_check() -> Dict[str, str]:
    """Basic health check."""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Check if gateway and downstream services are ready."""
    scanner_healthy = await service_client.health_check_scanner()
    cost_healthy = await service_client.health_check_cost_service()

    all_healthy = scanner_healthy and cost_healthy

    return {
        "status": "ready" if all_healthy else "degraded",
        "service": "api-gateway",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "resource_scanner": "healthy" if scanner_healthy else "unhealthy",
            "cost_service": "healthy" if cost_healthy else "unhealthy",
        }
    }
