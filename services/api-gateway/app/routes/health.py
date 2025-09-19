from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
import psutil
import os

from utils.service_client import ServiceClient

router = APIRouter()
service_client = ServiceClient()

@router.get("/")
async def health_check() -> Dict[str, str]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Comprehensive readiness check."""
    try:
        # Check dependent services
        scanner_healthy = await service_client.health_check_scanner()
        analyzer_healthy = await service_client.health_check_cost_analyzer()
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        services_status = {
            "resource_scanner": "healthy" if scanner_healthy else "unhealthy",
            "cost_analyzer": "healthy" if analyzer_healthy else "unhealthy"
        }
        
        all_services_healthy = scanner_healthy and analyzer_healthy
        
        return {
            "status": "ready" if all_services_healthy else "degraded",
            "service": "api-gateway",
            "timestamp": datetime.utcnow().isoformat(),
            "services": services_status,
            "system": {
                "cpu_usage": f"{cpu_percent}%",
                "memory_usage": f"{memory.percent}%",
                "disk_usage": f"{disk.percent}%",
                "uptime": os.getenv("UPTIME", "unknown")
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Service not ready: {str(e)}"
        )

@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """Get system and service metrics."""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Service health checks
        scanner_healthy = await service_client.health_check_scanner()
        analyzer_healthy = await service_client.health_check_cost_analyzer()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system_metrics": {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "usage_percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "usage_percent": disk.percent
                }
            },
            "service_health": {
                "resource_scanner": scanner_healthy,
                "cost_analyzer": analyzer_healthy
            },
            "environment": os.getenv("ENVIRONMENT", "development")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get metrics: {str(e)}"
        )