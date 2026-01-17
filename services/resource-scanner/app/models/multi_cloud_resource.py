"""
Multi-Cloud Provider-Agnostic Resource Models
Unified models that work across AWS, Azure, and GCP
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class CloudProvider(str, Enum):
    """Cloud provider enum"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


class ResourceType(str, Enum):
    """Resource type enum"""
    COMPUTE = "compute"
    DATABASE = "database"
    STORAGE = "storage"
    NETWORK = "network"
    SERVERLESS = "serverless"


class ResourceStatus(str, Enum):
    """Resource status enum"""
    RUNNING = "running"
    STOPPED = "stopped"
    TERMINATED = "terminated"
    PENDING = "pending"
    ERROR = "error"


@dataclass
class CloudResource:
    """Base class for multi-cloud resources."""
    # Common fields across all clouds
    resource_id: str
    provider: CloudProvider
    resource_type: ResourceType
    name: str
    region: str
    status: ResourceStatus
    created_at: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    estimated_monthly_cost: Optional[float] = None

    # Provider-specific metadata
    provider_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert resource to dictionary."""
        return {
            "resource_id": self.resource_id,
            "provider": self.provider.value,
            "resource_type": self.resource_type.value,
            "name": self.name,
            "region": self.region,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "tags": self.tags,
            "estimated_monthly_cost": self.estimated_monthly_cost,
            "provider_metadata": self.provider_metadata
        }


@dataclass
class ComputeInstance(CloudResource):
    """
    Unified compute instance across clouds.
    AWS: EC2, Azure: Virtual Machine, GCP: Compute Engine
    """
    instance_type: str  # e.g., t3.micro (AWS), Standard_B1s (Azure), e2-micro (GCP)
    vcpus: int
    memory_gb: float
    availability_zone: str
    cpu_utilization: float = 0.0
    network_utilization: float = 0.0

    def __post_init__(self):
        self.resource_type = ResourceType.COMPUTE

    @classmethod
    def from_aws_ec2(cls, ec2_data: Dict[str, Any]) -> 'ComputeInstance':
        """Create from AWS EC2 instance"""
        return cls(
            resource_id=ec2_data['InstanceId'],
            provider=CloudProvider.AWS,
            resource_type=ResourceType.COMPUTE,
            name=next((tag['Value'] for tag in ec2_data.get('Tags', []) if tag['Key'] == 'Name'), ec2_data['InstanceId']),
            region=ec2_data.get('Placement', {}).get('AvailabilityZone', '')[:-1],  # Remove zone letter
            status=ResourceStatus.RUNNING if ec2_data['State']['Name'] == 'running' else ResourceStatus.STOPPED,
            created_at=ec2_data['LaunchTime'],
            instance_type=ec2_data['InstanceType'],
            vcpus=0,  # Would need to lookup from instance type
            memory_gb=0.0,  # Would need to lookup from instance type
            availability_zone=ec2_data.get('Placement', {}).get('AvailabilityZone', ''),
            tags={tag['Key']: tag['Value'] for tag in ec2_data.get('Tags', [])},
            provider_metadata={
                'platform': ec2_data.get('Platform', 'linux'),
                'architecture': ec2_data.get('Architecture', 'x86_64'),
                'public_ip': ec2_data.get('PublicIpAddress'),
                'private_ip': ec2_data.get('PrivateIpAddress'),
            }
        )

    @classmethod
    def from_azure_vm(cls, vm_data: Dict[str, Any]) -> 'ComputeInstance':
        """Create from Azure Virtual Machine"""
        return cls(
            resource_id=vm_data['id'],
            provider=CloudProvider.AZURE,
            resource_type=ResourceType.COMPUTE,
            name=vm_data['name'],
            region=vm_data['location'],
            status=ResourceStatus.RUNNING if vm_data.get('powerState') == 'running' else ResourceStatus.STOPPED,
            created_at=datetime.fromisoformat(vm_data.get('created_at', datetime.utcnow().isoformat())),
            instance_type=vm_data['vmSize'],
            vcpus=vm_data.get('vcpus', 0),
            memory_gb=vm_data.get('memory_gb', 0.0),
            availability_zone=vm_data.get('zone', ''),
            tags=vm_data.get('tags', {}),
            provider_metadata={
                'os_type': vm_data.get('osType', 'Linux'),
                'disk_type': vm_data.get('diskType', 'Standard_LRS'),
            }
        )

    @classmethod
    def from_gcp_instance(cls, gcp_data: Dict[str, Any]) -> 'ComputeInstance':
        """Create from GCP Compute Engine instance"""
        return cls(
            resource_id=gcp_data['id'],
            provider=CloudProvider.GCP,
            resource_type=ResourceType.COMPUTE,
            name=gcp_data['name'],
            region=gcp_data['zone'].split('/')[-1][:-2],  # Extract region from zone
            status=ResourceStatus.RUNNING if gcp_data['status'] == 'RUNNING' else ResourceStatus.STOPPED,
            created_at=datetime.fromisoformat(gcp_data['creationTimestamp']),
            instance_type=gcp_data['machineType'].split('/')[-1],
            vcpus=0,  # Would need to lookup
            memory_gb=0.0,  # Would need to lookup
            availability_zone=gcp_data['zone'].split('/')[-1],
            tags=gcp_data.get('labels', {}),
            provider_metadata={
                'preemptible': gcp_data.get('scheduling', {}).get('preemptible', False),
                'network_tier': gcp_data.get('networkTier', 'PREMIUM'),
            }
        )


@dataclass
class DatabaseInstance(CloudResource):
    """
    Unified database instance across clouds.
    AWS: RDS, Azure: SQL Database, GCP: Cloud SQL
    """
    db_engine: str  # e.g., postgres, mysql, sqlserver, mongodb
    db_version: str
    db_instance_class: str
    storage_gb: int
    storage_type: str
    multi_az: bool = False
    encrypted: bool = False
    backup_retention_days: int = 7

    def __post_init__(self):
        self.resource_type = ResourceType.DATABASE

    @classmethod
    def from_aws_rds(cls, rds_data: Dict[str, Any]) -> 'DatabaseInstance':
        """Create from AWS RDS instance"""
        return cls(
            resource_id=rds_data['DBInstanceIdentifier'],
            provider=CloudProvider.AWS,
            resource_type=ResourceType.DATABASE,
            name=rds_data['DBInstanceIdentifier'],
            region=rds_data['AvailabilityZone'][:-1] if rds_data.get('AvailabilityZone') else '',
            status=ResourceStatus.RUNNING if rds_data['DBInstanceStatus'] == 'available' else ResourceStatus.PENDING,
            created_at=rds_data['InstanceCreateTime'],
            db_engine=rds_data['Engine'],
            db_version=rds_data['EngineVersion'],
            db_instance_class=rds_data['DBInstanceClass'],
            storage_gb=rds_data['AllocatedStorage'],
            storage_type=rds_data.get('StorageType', 'gp2'),
            multi_az=rds_data.get('MultiAZ', False),
            encrypted=rds_data.get('StorageEncrypted', False),
            backup_retention_days=rds_data.get('BackupRetentionPeriod', 7),
            tags={tag['Key']: tag['Value'] for tag in rds_data.get('TagList', [])},
            provider_metadata={
                'endpoint': rds_data.get('Endpoint', {}).get('Address'),
                'port': rds_data.get('Endpoint', {}).get('Port'),
                'publicly_accessible': rds_data.get('PubliclyAccessible', False),
            }
        )


@dataclass
class StorageContainer(CloudResource):
    """
    Unified storage container across clouds.
    AWS: S3 Bucket, Azure: Blob Container, GCP: Cloud Storage Bucket
    """
    size_gb: float
    object_count: int
    storage_class: str  # e.g., STANDARD, GLACIER, HOT, COLD
    versioning_enabled: bool = False
    lifecycle_policy: bool = False
    public_access: bool = False

    def __post_init__(self):
        self.resource_type = ResourceType.STORAGE

    @classmethod
    def from_aws_s3(cls, s3_data: Dict[str, Any]) -> 'StorageContainer':
        """Create from AWS S3 bucket"""
        return cls(
            resource_id=s3_data['Name'],
            provider=CloudProvider.AWS,
            resource_type=ResourceType.STORAGE,
            name=s3_data['Name'],
            region=s3_data.get('region', 'us-east-1'),
            status=ResourceStatus.RUNNING,
            created_at=s3_data['CreationDate'],
            size_gb=s3_data.get('size_gb', 0.0),
            object_count=s3_data.get('object_count', 0),
            storage_class=s3_data.get('storage_class', 'STANDARD'),
            versioning_enabled=s3_data.get('versioning', False),
            lifecycle_policy=s3_data.get('lifecycle_policy', False),
            public_access=s3_data.get('public_access', False),
            tags=s3_data.get('tags', {}),
            provider_metadata={
                'bucket_arn': f"arn:aws:s3:::{s3_data['Name']}",
                'encryption': s3_data.get('encryption'),
            }
        )


@dataclass
class MultiCloudSummary:
    """Summary of resources across all cloud providers"""
    total_resources: int
    total_monthly_cost: float
    by_provider: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    by_type: Dict[str, int] = field(default_factory=dict)
    by_region: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_resources": self.total_resources,
            "total_monthly_cost": self.total_monthly_cost,
            "by_provider": self.by_provider,
            "by_type": self.by_type,
            "by_region": self.by_region,
        }
