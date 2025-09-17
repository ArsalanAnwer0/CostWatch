from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal

class CostData(BaseModel):
    """Cost data model"""
    account_id: str
    service_name: str
    region: str
    cost_amount: Decimal
    usage_date: datetime
    metadata: Optional[Dict] = {}
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }

class CostQuery(BaseModel):
    """Cost query model"""
    account_id: str
    start_date: str
    end_date: str
    services: Optional[List[str]] = []
    regions: Optional[List[str]] = []