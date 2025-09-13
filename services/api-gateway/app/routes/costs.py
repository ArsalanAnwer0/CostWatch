from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime, date
import random
import logging

from app.routes.auth import verify_token
from app.utils.service_client import ServiceClient

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize service client for microservice communication
service_client = ServiceClient()

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

# Mock data generators
def generate_mock_cost_data(days: int = 30) -> List[CostData]:
    """Generate mock cost data for demonstration."""
    services = ["EC2", "RDS", "S3", "Lambda", "CloudWatch", "VPC", "ELB"]
    regions = ["us-west-2", "us-east-1", "eu-west-1"]
    
    costs = []
    for i in range(days):
        cost_date = datetime.now().date().replace(day=1)  # Simplified for demo
        for service in services:
            costs.append(CostData(
                service_name=service,
                cost=round(random.uniform(10, 1000), 2),
                date=cost_date,
                region=random.choice(regions),
                account_id="123456789012"
            ))
    return costs

def generate_optimization_recommendations() -> List[OptimizationRecommendation]:
    """Generate mock optimization recommendations."""
    return [
        OptimizationRecommendation(
            resource_id="i-1234567890abcdef0",
            resource_type="EC2 Instance",
            current_cost=245.60,
            potential_savings=73.68,
            recommendation="Right-size from t3.large to t3.medium based on CPU utilization",
            priority="High",
            estimated_effort="Low"
        ),
        OptimizationRecommendation(
            resource_id="vol-1234567890abcdef0",
            resource_type="EBS Volume",
            current_cost=40.00,
            potential_savings=40.00,
            recommendation="Delete unattached EBS volume",
            priority="Medium",
            estimated_effort="Low"
        ),
        OptimizationRecommendation(
            resource_id="snap-1234567890abcdef0",
            resource_type="EBS Snapshot",
            current_cost=15.50,
            potential_savings=15.50,
            recommendation="Delete old snapshots older than 30 days",
            priority="Low",
            estimated_effort="Low"
        )
    ]

@router.get("/summary", response_model=CostSummary)
async def get_cost_summary(
    period: str = Query("30d", description="Time period (7d, 30d, 90d)"),
    current_user: str = Depends(verify_token)
) -> CostSummary:
    """Get cost summary for specified period."""
    
    # Mock calculation based on period
    if period == "7d":
        total_cost = 1247.83
        trend = "increasing"
    elif period == "30d":
        total_cost = 4521.67
        trend = "stable"
    elif period == "90d":
        total_cost = 13565.01
        trend = "decreasing"
    else:
        total_cost = 4521.67
        trend = "stable"
    
    top_services = [
        {"service": "EC2", "cost": total_cost * 0.45, "percentage": 45},
        {"service": "RDS", "cost": total_cost * 0.25, "percentage": 25},
        {"service": "S3", "cost": total_cost * 0.15, "percentage": 15},
        {"service": "Lambda", "cost": total_cost * 0.10, "percentage": 10},
        {"service": "Other", "cost": total_cost * 0.05, "percentage": 5}
    ]
    
    return CostSummary(
        total_cost=total_cost,
        period=period,
        top_services=top_services,
        cost_trend=trend,
        savings_opportunity=total_cost * 0.35  # 35% potential savings
    )

@router.get("/details", response_model=List[CostData])
async def get_cost_details(
    service: Optional[str] = Query(None, description="Filter by AWS service"),
    region: Optional[str] = Query(None, description="Filter by AWS region"),
    days: int = Query(30, description="Number of days to retrieve"),
    current_user: str = Depends(verify_token)
) -> List[CostData]:
    """Get detailed cost breakdown."""
    
    cost_data = generate_mock_cost_data(days)
    
    # Apply filters
    if service:
        cost_data = [cost for cost in cost_data if cost.service_name == service]
    
    if region:
        cost_data = [cost for cost in cost_data if cost.region == region]
    
    return cost_data

@router.get("/optimization", response_model=List[OptimizationRecommendation])
async def get_optimization_recommendations(
    priority: Optional[str] = Query(None, description="Filter by priority (High, Medium, Low)"),
    current_user: str = Depends(verify_token)
) -> List[OptimizationRecommendation]:
    """Get cost optimization recommendations."""
    
    recommendations = generate_optimization_recommendations()
    
    if priority:
        recommendations = [rec for rec in recommendations if rec.priority == priority]
    
    return recommendations

@router.get("/forecast")
async def get_cost_forecast(
    months: int = Query(3, description="Number of months to forecast"),
    current_user: str = Depends(verify_token)
) -> Dict[str, Any]:
    """Get cost forecast based on historical data."""
    
    current_monthly_cost = 4521.67
    forecast_data = []
    
    for month in range(1, months + 1):
        # Simple forecast with slight variation
        forecasted_cost = current_monthly_cost * (1 + (month * 0.05))
        forecast_data.append({
            "month": month,
            "forecasted_cost": round(forecasted_cost, 2),
            "confidence": max(95 - (month * 5), 70)  # Decreasing confidence
        })
    
    return {
        "current_monthly_cost": current_monthly_cost,
        "forecast_period_months": months,
        "forecast_data": forecast_data,
        "total_forecasted_cost": sum(item["forecasted_cost"] for item in forecast_data)
    }

@router.post("/alerts")
async def create_cost_alert(
    threshold: float = Query(..., description="Cost threshold for alert"),
    period: str = Query("monthly", description="Alert period (daily, weekly, monthly)"),
    current_user: str = Depends(verify_token)
) -> Dict[str, str]:
    """Create a cost alert."""
    
    return {
        "message": "Cost alert created successfully",
        "threshold": str(threshold),
        "period": period,
        "alert_id": f"alert_{random.randint(1000, 9999)}"
    }

# New endpoints for service integration
@router.post("/scan/trigger")
async def trigger_resource_scan(
    scan_request: ScanRequest,
    current_user: str = Depends(verify_token)
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
            "scan_id": result.get("scan_id"),
            "summary": result.get("summary"),
            "regions_scanned": scan_request.regions,
            "triggered_by": current_user,
            "timestamp": datetime.utcnow().isoformat(),
            "details": {
                "total_resources": result.get("summary", {}).get("total_resources", 0),
                "estimated_cost": result.get("summary", {}).get("total_estimated_cost", 0.0),
                "optimization_opportunities": result.get("summary", {}).get("optimization_opportunities", 0)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to trigger resource scan: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to trigger resource scan"
        )

@router.post("/scan/ec2")
async def trigger_ec2_scan(
    region: str = Query("us-west-2", description="AWS region to scan"),
    include_costs: bool = Query(True, description="Include cost estimates"),
    current_user: str = Depends(verify_token)
) -> Dict[str, Any]:
    """Trigger EC2 resource scan via Resource Scanner service."""
    try:
        logger.info(f"Triggering EC2 scan for region {region}")
        
        result = await service_client.scan_ec2_resources(
            region=region,
            include_costs=include_costs
        )
        
        if result is None:
            raise HTTPException(
                status_code=503,
                detail="Resource Scanner service is unavailable"
            )
        
        return {
            "message": "EC2 scan completed successfully",
            "region": region,
            "triggered_by": current_user,
            "timestamp": datetime.utcnow().isoformat(),
            "results": result.get("results", {}),
            "summary": {
                "instances_found": len(result.get("results", {}).get("instances", [])),
                "estimated_monthly_cost": result.get("results", {}).get("estimated_monthly_cost", 0.0),
                "optimization_opportunities": len(result.get("results", {}).get("optimization_opportunities", []))
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to trigger EC2 scan: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to trigger EC2 scan"
        )

@router.get("/scan/status/{scan_id}")
async def get_scan_status(
    scan_id: str,
    current_user: str = Depends(verify_token)
) -> Dict[str, Any]:
    """Get the status of a resource scan."""
    # In a real implementation, this would query a database or cache
    # For now, return mock status based on scan_id pattern
    
    import time
    current_time = time.time()
    scan_timestamp = int(scan_id.split('_')[1]) if '_' in scan_id else current_time
    
    # Mock different statuses based on time elapsed
    time_elapsed = current_time - scan_timestamp
    
    if time_elapsed < 10:
        status = "running"
        progress = min(int(time_elapsed * 10), 90)
    else:
        status = "completed"
        progress = 100
    
    return {
        "scan_id": scan_id,
        "status": status,
        "progress": progress,
        "started_at": datetime.fromtimestamp(scan_timestamp).isoformat(),
        "completed_at": datetime.utcnow().isoformat() if status == "completed" else None,
        "resources_found": 42 if status == "completed" else None,
        "optimization_opportunities": 8 if status == "completed" else None,
        "estimated_savings": 1247.50 if status == "completed" else None
    }

@router.get("/optimization/live/{resource_type}")
async def get_live_optimization_recommendations(
    resource_type: str,
    current_user: str = Depends(verify_token)
) -> Dict[str, Any]:
    """Get live optimization recommendations from Resource Scanner service."""
    try:
        if resource_type not in ['ec2', 'rds', 's3']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported resource type: {resource_type}. Supported types: ec2, rds, s3"
            )
        
        result = await service_client.get_optimization_recommendations(resource_type)
        
        if result is None:
            raise HTTPException(
                status_code=503,
                detail="Resource Scanner service is unavailable"
            )
        
        return {
            "resource_type": resource_type,
            "timestamp": datetime.utcnow().isoformat(),
            "recommendations": result.get("recommendations", []),
            "summary": {
                "total_recommendations": len(result.get("recommendations", [])),
                "categories_covered": len(set(rec.get("category", "general") for rec in result.get("recommendations", [])))
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get optimization recommendations for {resource_type}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get optimization recommendations"
        )

@router.get("/services/health")
async def check_services_health(
    current_user: str = Depends(verify_token)
) -> Dict[str, Any]:
    """Check health of all dependent services."""
    try:
        scanner_healthy = await service_client.health_check_scanner()
        
        # Mock health checks for other services (in production, implement real checks)
        database_healthy = True  # Would implement actual DB health check
        redis_healthy = True     # Would implement actual Redis health check
        
        all_healthy = scanner_healthy and database_healthy and redis_healthy
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "api_gateway": "healthy",
                "resource_scanner": "healthy" if scanner_healthy else "unhealthy",
                "database": "healthy" if database_healthy else "unhealthy",
                "redis": "healthy" if redis_healthy else "unhealthy"
            },
            "overall_status": "healthy" if all_healthy else "degraded",
            "checked_by": current_user
        }
        
    except Exception as e:
        logger.error(f"Failed to check services health: {e}")
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "api_gateway": "healthy",
                "resource_scanner": "unknown",
                "database": "unknown",
                "redis": "unknown"
            },
            "overall_status": "unknown",
            "error": str(e),
            "checked_by": current_user
        }

@router.get("/analytics/dashboard")
async def get_analytics_dashboard(
    period: str = Query("30d", description="Analysis period"),
    current_user: str = Depends(verify_token)
) -> Dict[str, Any]:
    """Get comprehensive analytics dashboard data."""
    try:
        # In a real implementation, this would aggregate data from multiple sources
        # For now, return mock comprehensive dashboard data
        
        base_cost = 4521.67 if period == "30d" else 1247.83 if period == "7d" else 13565.01
        
        return {
            "period": period,
            "timestamp": datetime.utcnow().isoformat(),
            "cost_overview": {
                "total_spend": base_cost,
                "trend": "stable",
                "month_over_month_change": 2.3,
                "budget_utilization": 78.5
            },
            "top_cost_drivers": [
                {"service": "EC2", "cost": base_cost * 0.45, "change": "+5.2%"},
                {"service": "RDS", "cost": base_cost * 0.25, "change": "-2.1%"},
                {"service": "S3", "cost": base_cost * 0.15, "change": "+1.8%"}
            ],
            "optimization_summary": {
                "total_opportunities": 23,
                "potential_monthly_savings": base_cost * 0.35,
                "high_priority_actions": 8,
                "quick_wins": 12
            },
            "resource_utilization": {
                "ec2_utilization": 67.3,
                "rds_utilization": 82.1,
                "storage_efficiency": 74.8
            },
            "alerts": {
                "active_alerts": 3,
                "budget_warnings": 1,
                "optimization_reminders": 5
            },
            "generated_for": current_user
        }
        
    except Exception as e:
        logger.error(f"Failed to generate analytics dashboard: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate analytics dashboard"
        )

@router.post("/optimization/implement")
async def implement_optimization(
    resource_id: str = Query(..., description="Resource ID to optimize"),
    recommendation_id: str = Query(..., description="Recommendation ID to implement"),
    current_user: str = Depends(verify_token)
) -> Dict[str, Any]:
    """Mock endpoint for implementing optimization recommendations."""
    # In a real implementation, this would trigger actual AWS API calls
    # For now, return mock implementation result
    
    return {
        "message": "Optimization implementation initiated",
        "resource_id": resource_id,
        "recommendation_id": recommendation_id,
        "implementation_id": f"impl_{random.randint(10000, 99999)}",
        "status": "pending",
        "estimated_completion": "2024-01-15T10:30:00Z",
        "estimated_savings": round(random.uniform(50, 500), 2),
        "initiated_by": current_user,
        "timestamp": datetime.utcnow().isoformat()
    }