from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
import time
import os
import psutil
from datetime import datetime

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    service: str
    version: str
    uptime: float

class DetailedHealthResponse(BaseModel):
    status: str
    timestamp: str
    service: str
    version: str
    uptime: float
    system: Dict[str, Any]
    dependencies: Dict[str, str]

# Track service start time
START_TIME = time.time()

@router.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        service="costwatch-api-gateway",
        version="1.0.0",
        uptime=time.time() - START_TIME
    )

@router.get("/ready")
async def readiness_check() -> Dict[str, str]:
    """Kubernetes readiness probe endpoint."""
    # In a real application, check if the service is ready to accept traffic
    # (database connections, external services, etc.)
    return {
        "status": "ready",
        "message": "Service is ready to accept traffic"
    }

@router.get("/live")
async def liveness_check() -> Dict[str, str]:
    """Kubernetes liveness probe endpoint."""
    # In a real application, check if the service is alive
    # (not deadlocked, not crashed, etc.)
    return {
        "status": "alive",
        "message": "Service is alive and responding"
    }

@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check() -> DetailedHealthResponse:
    """Detailed health check with system information."""
    
    # System metrics
    system_info = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
    }
    
    # Dependencies status (mock for now)
    dependencies = {
        "database": "healthy",
        "redis": "healthy", 
        "resource_scanner": "healthy",
        "cost_analyzer": "healthy"
    }
    
    return DetailedHealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        service="costwatch-api-gateway",
        version="1.0.0",
        uptime=time.time() - START_TIME,
        system=system_info,
        dependencies=dependencies
    )

@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """Prometheus-style metrics endpoint."""
    return {
        "http_requests_total": 1000,  # Mock metric
        "http_request_duration_seconds": 0.025,  # Mock metric
        "active_connections": 15,  # Mock metric
        "memory_usage_bytes": psutil.virtual_memory().used,
        "cpu_usage_percent": psutil.cpu_percent(),
        "uptime_seconds": time.time() - START_TIME
    }