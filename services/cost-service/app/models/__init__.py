"""
Cost Analyzer Models
"""

from .cost_analysis import CostAnalysis, OptimizationRecommendation
from .resource import Resource

__all__ = ["CostAnalysis", "OptimizationRecommendation", "Resource"]

# services/cost-analyzer/app/models/cost_analysis.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from decimal import Decimal

class CostAnalysis(BaseModel):
    """Cost analysis data model"""
    account_id: str
    total_cost: Decimal = Field(..., description="Total cost for the period")
    daily_average: Decimal = Field(..., description="Daily average cost")
    service_breakdown: Dict[str, Decimal] = Field(..., description="Cost breakdown by service")
    region_breakdown: Dict[str, Decimal] = Field(..., description="Cost breakdown by region")
    cost_trend: str = Field(..., description="Trend direction: increasing, decreasing, stable")
    period_start: datetime
    period_end: datetime
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }

class OptimizationRecommendation(BaseModel):
    """Resource optimization recommendation"""
    resource_id: str
    resource_type: str
    current_cost: Decimal
    recommended_action: str
    monthly_savings: Decimal
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    description: str
    implementation_effort: str  # low, medium, high
    risk_level: str  # low, medium, high
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }

class CostForecast(BaseModel):
    """Cost forecast model"""
    account_id: str
    forecast_date: datetime
    predicted_cost: Decimal
    confidence_interval: Dict[str, Decimal]  # upper, lower bounds
    forecast_period: str  # daily, weekly, monthly
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }
