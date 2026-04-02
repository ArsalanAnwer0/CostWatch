from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from datetime import datetime
from decimal import Decimal

class Resource(BaseModel):
    """Cloud resource model"""
    resource_id: str
    resource_type: str
    account_id: str
    region: str
    service: str
    current_cost: Decimal
    utilization_metrics: Dict[str, float]
    tags: Dict[str, str] = Field(default_factory=dict)
    last_updated: datetime
    status: str  # running, stopped, terminated
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }

class EC2Resource(Resource):
    """EC2 specific resource model"""
    instance_type: str
    cpu_utilization: float
    memory_utilization: Optional[float] = None
    network_utilization: Optional[float] = None
    
class RDSResource(Resource):
    """RDS specific resource model"""
    db_instance_class: str
    engine: str
    cpu_utilization: float
    connection_count: Optional[int] = None
    iops_utilization: Optional[float] = None

class S3Resource(Resource):
    """S3 specific resource model"""
    bucket_name: str
    storage_class: str
    object_count: int
    total_size_gb: Decimal
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }
