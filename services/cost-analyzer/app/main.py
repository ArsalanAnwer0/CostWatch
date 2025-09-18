from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv

# Fix imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))

from services.cost_calculator import CostCalculator
from services.optimizer import ResourceOptimizer
from services.trend_analyzer import TrendAnalyzer
from utils.database import get_db_connection
from utils.auth import verify_api_key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CostWatch Cost Analyzer",
    description="Advanced cloud cost analysis and optimization service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
cost_calculator = CostCalculator()
optimizer = ResourceOptimizer()
trend_analyzer = TrendAnalyzer()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "cost-analyzer",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    return {
        "status": "ready",
        "service": "cost-analyzer",
        "database": "skipped",
        "aws": "connected" if cost_calculator.ce_client else "not_configured"
    }

@app.post("/analyze/costs")
async def analyze_costs(
    account_id: str,
    start_date: str,
    end_date: str,
    # api_key: str = Depends(verify_api_key)
):
    """Analyze costs for a specific account and date range"""
    try:
        logger.info(f"Analyzing costs for account {account_id}")
        
        # Calculate costs
        cost_analysis = await cost_calculator.calculate_costs(
            account_id=account_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "account_id": account_id,
            "period": {"start": start_date, "end": end_date},
            "analysis": cost_analysis,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cost analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cost analysis failed: {str(e)}")

@app.post("/optimize/resources")
async def optimize_resources(
    account_id: str,
    resource_types: Optional[List[str]] = None,
    # api_key: str = Depends(verify_api_key)
):
    """Get optimization recommendations for resources"""
    try:
        logger.info(f"Optimizing resources for account {account_id}")
        
        # Get optimization recommendations
        recommendations = await optimizer.get_recommendations(
            account_id=account_id,
            resource_types=resource_types or ["ec2", "rds", "ebs", "s3"]
        )
        
        return {
            "account_id": account_id,
            "recommendations": recommendations,
            "potential_savings": sum(r.monthly_savings for r in recommendations),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Resource optimization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8001)),
        reload=os.getenv("ENVIRONMENT") == "development"
    )