"""
Cost Analyzer Service - CostWatch Platform
Analyzes cloud costs and provides optimization recommendations
"""

__version__ = "1.0.0"

# services/cost-analyzer/app/main.py
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from .models.cost_analysis import CostAnalysis, OptimizationRecommendation
from .models.resource import Resource
from .services.cost_calculator import CostCalculator
from .services.optimizer import ResourceOptimizer
from .services.trend_analyzer import TrendAnalyzer
from .utils.database import get_db_connection
from .utils.auth import verify_api_key

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
    try:
        # Check database connection
        db = get_db_connection()
        db.execute("SELECT 1")
        db.close()
        
        return {
            "status": "ready",
            "service": "cost-analyzer",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.post("/analyze/costs")
async def analyze_costs(
    account_id: str,
    start_date: str,
    end_date: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Analyze costs for a specific account and date range
    """
    try:
        logger.info(f"Analyzing costs for account {account_id} from {start_date} to {end_date}")
        
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
    api_key: str = Depends(verify_api_key)
):
    """
    Get optimization recommendations for resources
    """
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

@app.get("/trends/{account_id}")
async def get_cost_trends(
    account_id: str,
    days: int = 30,
    api_key: str = Depends(verify_api_key)
):
    """
    Get cost trends and predictions
    """
    try:
        logger.info(f"Analyzing cost trends for account {account_id}")
        
        # Analyze trends
        trends = await trend_analyzer.analyze_trends(
            account_id=account_id,
            days=days
        )
        
        return {
            "account_id": account_id,
            "period_days": days,
            "trends": trends,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Trend analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")

@app.post("/reports/monthly")
async def generate_monthly_report(
    account_id: str,
    month: str,  # Format: YYYY-MM
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """
    Generate comprehensive monthly cost report
    """
    try:
        logger.info(f"Generating monthly report for account {account_id}, month {month}")
        
        # Add background task for report generation
        background_tasks.add_task(
            _generate_monthly_report_task,
            account_id,
            month
        )
        
        return {
            "message": "Monthly report generation started",
            "account_id": account_id,
            "month": month,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Monthly report generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@app.get("/savings/summary/{account_id}")
async def get_savings_summary(
    account_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Get savings summary and opportunities
    """
    try:
        logger.info(f"Getting savings summary for account {account_id}")
        
        # Calculate potential savings
        savings_summary = await cost_calculator.calculate_savings_opportunities(account_id)
        
        return {
            "account_id": account_id,
            "savings_summary": savings_summary,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Savings summary failed: {e}")
        raise HTTPException(status_code=500, detail=f"Savings calculation failed: {str(e)}")

async def _generate_monthly_report_task(account_id: str, month: str):
    """Background task for monthly report generation"""
    try:
        logger.info(f"Generating monthly report for {account_id} - {month}")
        
        # Generate comprehensive report
        report = await cost_calculator.generate_monthly_report(account_id, month)
        
        # Store report in database
        db = get_db_connection()
        db.execute(
            "INSERT INTO monthly_reports (account_id, month, report_data, created_at) VALUES (%s, %s, %s, %s)",
            (account_id, month, report, datetime.utcnow())
        )
        db.commit()
        db.close()
        
        logger.info(f"Monthly report completed for {account_id} - {month}")
        
    except Exception as e:
        logger.error(f"Monthly report task failed: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8001)),
        reload=os.getenv("ENVIRONMENT") == "development"
    )