"""
Cloud Account Model
Stores multi-cloud account credentials and metadata
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class CloudProvider(str, Enum):
    """Supported cloud providers"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


class CloudAccountStatus(str, Enum):
    """Account connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    PENDING = "pending"


class CloudAccountBase(BaseModel):
    """Base cloud account schema"""
    name: str = Field(..., min_length=1, max_length=100)
    provider: CloudProvider
    description: Optional[str] = Field(None, max_length=500)


class CloudAccountCreate(CloudAccountBase):
    """Schema for creating a new cloud account"""
    credentials: Dict[str, Any] = Field(..., description="Provider-specific credentials")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Production AWS",
                "provider": "aws",
                "description": "Main production environment",
                "credentials": {
                    "access_key_id": "AKIAIOSFODNN7EXAMPLE",
                    "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                    "region": "us-east-1"
                }
            }
        }


class CloudAccountUpdate(BaseModel):
    """Schema for updating cloud account"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    credentials: Optional[Dict[str, Any]] = None
    status: Optional[CloudAccountStatus] = None


class CloudAccountResponse(CloudAccountBase):
    """Schema for cloud account response (without sensitive data)"""
    id: str
    user_id: str
    status: CloudAccountStatus
    created_at: datetime
    updated_at: datetime
    last_scan_at: Optional[datetime] = None
    resource_count: int = 0
    monthly_cost: float = 0.0

    class Config:
        from_attributes = True


class CloudAccountDetail(CloudAccountResponse):
    """Detailed cloud account info including masked credentials"""
    credentials_summary: Dict[str, str] = Field(
        ...,
        description="Masked/summary of credentials (no sensitive data)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "acc_123456",
                "user_id": "user_789",
                "name": "Production AWS",
                "provider": "aws",
                "description": "Main production environment",
                "status": "connected",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "last_scan_at": "2024-01-16T08:00:00Z",
                "resource_count": 45,
                "monthly_cost": 1250.50,
                "credentials_summary": {
                    "access_key_id": "AKIA****EXAMPLE",
                    "region": "us-east-1"
                }
            }
        }


# Database model (for SQLAlchemy if we add it later)
class CloudAccountDB:
    """
    Database schema for cloud_accounts table

    Fields:
    - id: UUID primary key
    - user_id: UUID foreign key to users table
    - name: VARCHAR(100)
    - provider: VARCHAR(20) - aws, azure, gcp
    - description: TEXT
    - credentials: JSON - encrypted credentials
    - status: VARCHAR(20)
    - created_at: TIMESTAMP
    - updated_at: TIMESTAMP
    - last_scan_at: TIMESTAMP
    - resource_count: INTEGER default 0
    - monthly_cost: DECIMAL(10,2) default 0.0
    """
    pass
