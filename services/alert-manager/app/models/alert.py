from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    COST_THRESHOLD = "cost_threshold"
    BUDGET_EXCEEDED = "budget_exceeded"
    COST_ANOMALY = "cost_anomaly"
    RESOURCE_WASTE = "resource_waste"
    FORECAST_ALERT = "forecast_alert"

class AlertStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

@dataclass
class Alert:
    """Alert data model"""
    alert_id: str
    alert_type: str
    severity: str
    message: str
    account_id: str
    metadata: Dict[str, Any]
    created_at: Optional[datetime] = None
    status: str = AlertStatus.PENDING.value
    
    def __post_init__(self):
        if not self.alert_id:
            self.alert_id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert alert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Alert':
        """Create alert from dictionary"""
        if 'created_at' in data and data['created_at']:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)

@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_id: str
    name: str
    condition: str
    threshold: float
    account_id: str
    notification_channels: List[str]
    enabled: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.rule_id:
            self.rule_id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert rule to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AlertRule':
        """Create rule from dictionary"""
        if 'created_at' in data and data['created_at']:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and data['updated_at']:
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)

@dataclass
class NotificationChannel:
    """Notification channel configuration"""
    channel_id: str
    channel_type: str  # slack, email, teams, webhook
    name: str
    config: Dict[str, Any]
    enabled: bool = True
    
    def to_dict(self) -> Dict:
        """Convert channel to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NotificationChannel':
        """Create channel from dictionary"""
        return cls(**data)