from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import os
from typing import Dict, Any

# Fix imports - add path setup 
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Use absolute imports with app prefix for proper module resolution
from app.routes import auth, costs, health
from app.middleware.logging import LoggingMiddleware

# Application metadata
app = FastAPI(
    title="CostWatch API Gateway",
    description="Smart cloud cost optimization platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security middleware
allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts
)

# CORS middleware - configure based on environment
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)

# Custom logging middleware
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(costs.router, prefix="/costs", tags=["Cost Analysis"])

@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint providing API information."""
    return {
        "service": "CostWatch API Gateway",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/info")
async def info() -> Dict[str, Any]:
    """Service information and health metrics."""
    return {
        "service": "costwatch-api-gateway",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "python_version": "3.13+",
        "framework": "FastAPI"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )