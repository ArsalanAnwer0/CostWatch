from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime, date
import random

from app.routes.auth import verify_token

router = APIRouter()

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