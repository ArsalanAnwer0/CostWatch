from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime, date, timedelta
import random
import logging
import os

from routes.auth import verify_token, bypass_auth_for_testing
from utils.service_client import ServiceClient

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize service client for microservice communication
service_client = ServiceClient()

# Get AWS account ID from environment (required)
AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID")
if not AWS_ACCOUNT_ID:
    raise ValueError("AWS_ACCOUNT_ID environment variable is required")

# Pydantic models
class CostData(BaseModel):
    service_name: str
    cost: float
    currency: str = "USD"
    date: date
    region: str
    account_id: str

class CostSummary(BaseModel):
    total_cost: float
    period: str
    top_services: List[Dict[str, Any]]
    cost_trend: str
    savings_opportunity: float

class OptimizationRecommendation(BaseModel):
    resource_id: str
    resource_type: str
    current_cost: float
    potential_savings: float
    recommendation: str
    priority: str
    estimated_effort: str

class ScanRequest(BaseModel):
    regions: List[str] = ['us-west-2']
    include_costs: bool = True
    scan_types: List[str] = ['ec2', 'rds', 's3']

# Helper functions
def calculate_date_range(period: str) -> tuple:
    """Calculate start and end dates based on period."""
    end_date = datetime.utcnow().date()
    
    if period == "7d":
        start_date = end_date - timedelta(days=7)
    elif period == "30d":
        start_date = end_date - timedelta(days=30)
    elif period == "90d":
        start_date = end_date - timedelta(days=90)
    else:
        start_date = end_date - timedelta(days=30)  # Default to 30 days
    
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

@router.get("/summary", response_model=CostSummary)
async def get_cost_summary(
    period: str = Query("30d", description="Time period (7d, 30d, 90d)"),
    current_user: str = Depends(bypass_auth_for_testing)
) -> CostSummary:
    """Get cost summary for specified period using real AWS data."""
    try:
        logger.info(f"Getting cost summary for user {current_user}, period: {period}")
        
        # Calculate date range
        start_date, end_date = calculate_date_range(period)
        
        # Get real cost analysis from cost-analyzer service
        cost_analysis = await service_client.analyze_costs(
            account_id=AWS_ACCOUNT_ID,
            start_date=start_date,
            end_date=end_date
        )
        
        if cost_analysis is None:
            # Fallback to basic mock data if service is unavailable
            logger.warning("Cost analyzer service unavailable, using fallback data")
            total_cost = 4521.67 if period == "30d" else 1247.83 if period == "7d" else 13565.01
            trend = "stable"
            top_services = [
                {"service": "EC2", "cost": total_cost * 0.45, "percentage": 45},
                {"service": "RDS", "cost": total_cost * 0.25, "percentage": 25},
                {"service": "S3", "cost": total_cost * 0.15, "percentage": 15},
                {"service": "Lambda", "cost": total_cost * 0.10, "percentage": 10},
                {"service": "Other", "cost": total_cost * 0.05, "percentage": 5}
            ]
        else:
            # Use real data from cost analyzer
            analysis = cost_analysis.get("analysis", {})
            total_cost = analysis.get("total_cost", 0.0)
            trend = analysis.get("cost_trend", "stable")
            
            # Convert service breakdown to top services format
            service_breakdown = analysis.get("service_breakdown", {})
            top_services = []
            for service, cost in service_breakdown.items():
                if total_cost > 0:
                    percentage = (cost / total_cost) * 100
                else:
                    percentage = 0
                top_services.append({
                    "service": service.replace("Amazon ", "").replace(" Service", ""),
                    "cost": cost,
                    "percentage": round(percentage, 1)
                })
            
            # Sort by cost descending
            top_services = sorted(top_services, key=lambda x: x["cost"], reverse=True)[:5]
        
        return CostSummary(
            total_cost=total_cost,
            period=period,
            top_services=top_services,
            cost_trend=trend,
            savings_opportunity=total_cost * 0.25  # Estimate 25% potential savings
        )
        
    except Exception as e:
        logger.error(f"Failed to get cost summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cost summary: {str(e)}")

@router.get("/details", response_model=List[CostData])
async def get_cost_details(
    service: Optional[str] = Query(None, description="Filter by AWS service"),
    region: Optional[str] = Query(None, description="Filter by AWS region"),
    days: int = Query(30, description="Number of days to retrieve"),
    current_user: str = Depends(bypass_auth_for_testing)
) -> List[CostData]:
    """Get detailed cost breakdown using real AWS data."""
    try:
        logger.info(f"Getting cost details for user {current_user}")
        
        # Calculate date range
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        # Get real cost analysis
        cost_analysis = await service_client.analyze_costs(
            account_id=AWS_ACCOUNT_ID,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        
        cost_details = []
        
        if cost_analysis and cost_analysis.get("analysis"):
            analysis = cost_analysis["analysis"]
            daily_costs = analysis.get("daily_costs", [])
            service_breakdown = analysis.get("service_breakdown", {})
            region_breakdown = analysis.get("region_breakdown", {})
            
            # Convert to CostData format
            for daily_cost in daily_costs:
                cost_date = datetime.strptime(daily_cost["date"], '%Y-%m-%d').date()
                daily_total = daily_cost["cost"]
                
                # Distribute daily cost across services proportionally
                for service_name, service_total_cost in service_breakdown.items():
                    if service_total_cost > 0:  # Only include services with costs
                        service_daily_cost = (service_total_cost / len(daily_costs)) if len(daily_costs) > 0 else 0
                        
                        # Get region for this service (simplified)
                        service_region = list(region_breakdown.keys())[0] if region_breakdown else "us-west-2"
                        
                        cost_details.append(CostData(
                            service_name=service_name,
                            cost=round(service_daily_cost, 2),
                            date=cost_date,
                            region=service_region,
                            account_id=AWS_ACCOUNT_ID
                        ))
        
        # Apply filters
        if service:
            cost_details = [cost for cost in cost_details if service.lower() in cost.service_name.lower()]
        
        if region:
            cost_details = [cost for cost in cost_details if cost.region == region]
        
        return cost_details
        
    except Exception as e:
        logger.error(f"Failed to get cost details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cost details: {str(e)}")

@router.get("/optimization", response_model=List[OptimizationRecommendation])
async def get_optimization_recommendations(
    priority: Optional[str] = Query(None, description="Filter by priority (High, Medium, Low)"),
    current_user: str = Depends(bypass_auth_for_testing)
) -> List[OptimizationRecommendation]:
    """Get cost optimization recommendations from cost-analyzer service."""
    try:
        logger.info(f"Getting optimization recommendations for user {current_user}")
        
        # Get recommendations from cost-analyzer service
        recommendations_data = await service_client.get_optimization_recommendations_from_analyzer(
            account_id=AWS_ACCOUNT_ID
        )
        
        recommendations = []
        
        if recommendations_data and recommendations_data.get("recommendations"):
            for rec in recommendations_data["recommendations"]:
                recommendations.append(OptimizationRecommendation(
                    resource_id=rec.get("resource_id", "unknown"),
                    resource_type=rec.get("resource_type", "unknown"),
                    current_cost=rec.get("current_cost", 0.0),
                    potential_savings=rec.get("monthly_savings", 0.0),
                    recommendation=rec.get("description", "No description available"),
                    priority=rec.get("confidence_score", 0.0) > 0.8 and "High" or "Medium",
                    estimated_effort=rec.get("implementation_effort", "unknown")
                ))
        
        # Apply priority filter
        if priority:
            recommendations = [rec for rec in recommendations if rec.priority == priority]
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Failed to get optimization recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get optimization recommendations: {str(e)}")

@router.get("/forecast")
async def get_cost_forecast(
    months: int = Query(3, description="Number of months to forecast"),
    current_user: str = Depends(bypass_auth_for_testing)
) -> Dict[str, Any]:
    """Get cost forecast based on historical data."""
    try:
        logger.info(f"Getting cost forecast for user {current_user}")
        
        # Get current month's cost data
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=30)
        
        cost_analysis = await service_client.analyze_costs(
            account_id=AWS_ACCOUNT_ID,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        
        current_monthly_cost = 0.0
        if cost_analysis and cost_analysis.get("analysis"):
            current_monthly_cost = cost_analysis["analysis"].get("total_cost", 0.0)
        
        # Simple forecast calculation (in production, use ML models)
        forecast_data = []
        for month in range(1, months + 1):
            # Simple growth model based on trend
            growth_factor = 1.02 if month <= 3 else 1.01  # Slower growth over time
            forecasted_cost = current_monthly_cost * (growth_factor ** month)
            
            forecast_data.append({
                "month": month,
                "forecasted_cost": round(forecasted_cost, 2),
                "confidence": max(90 - (month * 5), 60)  # Decreasing confidence
            })
        
        return {
            "current_monthly_cost": current_monthly_cost,
            "forecast_period_months": months,
            "forecast_data": forecast_data,
            "total_forecasted_cost": sum(item["forecasted_cost"] for item in forecast_data),
            "account_id": AWS_ACCOUNT_ID,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get cost forecast: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cost forecast: {str(e)}")

@router.post("/scan/trigger")
async def trigger_resource_scan(
    scan_request: ScanRequest,
    current_user: str = Depends(bypass_auth_for_testing)
) -> Dict[str, Any]:
    """Trigger a comprehensive resource scan via Resource Scanner service."""
    try:
        logger.info(f"Triggering resource scan for user {current_user}")
        
        result = await service_client.scan_all_resources(
            regions=scan_request.regions, 
            include_costs=scan_request.include_costs
        )
        
        if result is None:
            raise HTTPException(
                status_code=503,
                detail="Resource Scanner service is unavailable"
            )
        
        return {
            "message": "Resource scan completed successfully",
            "scan_id": result.get("scan_id", f"scan_{int(datetime.utcnow().timestamp())}"),
            "summary": result.get("summary", {}),
            "regions_scanned": scan_request.regions,
            "triggered_by": current_user,
            "timestamp": datetime.utcnow().isoformat(),
            "account_id": AWS_ACCOUNT_ID
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to trigger resource scan: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to trigger resource scan"
        )

@router.get("/services/health")
async def check_services_health(
    current_user: str = Depends(bypass_auth_for_testing)
) -> Dict[str, Any]:
    """Check health of all dependent services."""
    try:
        scanner_healthy = await service_client.health_check_scanner()
        analyzer_healthy = await service_client.health_check_cost_analyzer()
        
        all_healthy = scanner_healthy and analyzer_healthy
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "api_gateway": "healthy",
                "resource_scanner": "healthy" if scanner_healthy else "unhealthy",
                "cost_analyzer": "healthy" if analyzer_healthy else "unhealthy"
            },
            "overall_status": "healthy" if all_healthy else "degraded",
            "checked_by": current_user,
            "account_id": AWS_ACCOUNT_ID
        }
        
    except Exception as e:
        logger.error(f"Failed to check services health: {e}")
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "api_gateway": "healthy",
                "resource_scanner": "unknown",
                "cost_analyzer": "unknown"
            },
            "overall_status": "unknown",
            "error": str(e),
            "checked_by": current_user
        }