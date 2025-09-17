from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
import uuid

class PredictionType(Enum):
    COST_FORECAST = "cost_forecast"
    CAPACITY_PLANNING = "capacity_planning"
    BUDGET_PROJECTION = "budget_projection"
    RESOURCE_OPTIMIZATION = "resource_optimization"

class AnalysisType(Enum):
    COST_OPTIMIZATION = "cost_optimization"
    TREND_ANALYSIS = "trend_analysis"
    ANOMALY_DETECTION = "anomaly_detection"
    BENCHMARK_COMPARISON = "benchmark_comparison"

class ReportType(Enum):
    EXECUTIVE_SUMMARY = "executive_summary"
    DETAILED_ANALYSIS = "detailed_analysis"
    COST_BREAKDOWN = "cost_breakdown"
    OPTIMIZATION_REPORT = "optimization_report"

@dataclass
class AnalyticsQuery:
    """Query model for analytics requests"""
    account_id: str
    start_date: str
    end_date: str
    metrics: List[str]
    filters: Dict[str, Any]
    query_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.query_id:
            self.query_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class PredictionRequest:
    """Request model for ML predictions"""
    account_id: str
    prediction_type: str
    time_horizon: int  # days
    historical_data: Dict[str, Any]
    features: List[str]
    request_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class ReportRequest:
    """Request model for report generation"""
    account_id: str
    report_type: str
    period: str
    include_predictions: bool
    custom_metrics: List[str]
    request_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class AnalyticsResult:
    """Result model for analytics operations"""
    result_id: str
    account_id: str
    analysis_type: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        return data

@dataclass
class Prediction:
    """Prediction result model"""
    prediction_id: str
    account_id: str
    prediction_type: str
    predicted_values: List[Dict[str, Any]]
    confidence_intervals: Dict[str, Any]
    model_accuracy: float
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        return data

@dataclass
class Anomaly:
    """Anomaly detection result"""
    anomaly_id: str
    account_id: str
    anomaly_type: str
    detected_at: datetime
    severity: str
    description: str
    affected_metrics: List[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['detected_at'] = self.detected_at.isoformat()
        return data

@dataclass
class Insight:
    """Business insight model"""
    insight_id: str
    account_id: str
    insight_type: str
    title: str
    description: str
    impact_score: float
    recommended_actions: List[str]
    supporting_data: Dict[str, Any]
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        return data