from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime

@dataclass
class AWSResource:
    """Base class for AWS resources."""
    resource_id: str
    resource_type: str
    region: str
    status: str
    tags: Dict[str, str]
    creation_date: datetime
    estimated_monthly_cost: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert resource to dictionary."""
        return {
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "region": self.region,
            "status": self.status,
            "tags": self.tags,
            "creation_date": self.creation_date.isoformat(),
            "estimated_monthly_cost": self.estimated_monthly_cost
        }

@dataclass
class EC2Instance(AWSResource):
    """EC2 instance resource."""
    instance_type: str
    availability_zone: str
    cpu_utilization: float
    
    def __post_init__(self):
        self.resource_type = "EC2Instance"

@dataclass
class RDSInstance(AWSResource):
    """RDS instance resource."""
    db_instance_class: str
    engine: str
    multi_az: bool
    storage_encrypted: bool
    allocated_storage_gb: int
    
    def __post_init__(self):
        self.resource_type = "RDSInstance"

@dataclass
class S3Bucket(AWSResource):
    """S3 bucket resource."""
    size_gb: float
    object_count: int
    storage_class: str
    has_lifecycle_policy: bool
    versioning_enabled: bool
    encryption_enabled: bool
    
    def __post_init__(self):
        self.resource_type = "S3Bucket"
        self.region = "global"  # S3 is global

@dataclass
class OptimizationOpportunity:
    """Optimization opportunity for a resource."""
    resource_id: str
    opportunity_type: str
    recommendation: str
    potential_savings: float
    priority: str  # high, medium, low
    effort: str    # low, medium, high
    category: str = "cost"  # cost, security, availability, maintenance
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert opportunity to dictionary."""
        return {
            "resource_id": self.resource_id,
            "type": self.opportunity_type,
            "recommendation": self.recommendation,
            "potential_savings": self.potential_savings,
            "priority": self.priority,
            "effort": self.effort,
            "category": self.category
        }