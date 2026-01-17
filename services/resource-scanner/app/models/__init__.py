"""
Resource Models
"""

from .resource import AWSResource, EC2Instance, RDSInstance, S3Bucket, OptimizationOpportunity
from .scan_result import ScanResult
from .multi_cloud_resource import (
    CloudResource,
    ComputeInstance,
    DatabaseInstance,
    StorageContainer,
    MultiCloudSummary,
    CloudProvider,
    ResourceType,
    ResourceStatus
)

__all__ = [
    # AWS-specific models
    "AWSResource",
    "EC2Instance",
    "RDSInstance",
    "S3Bucket",
    "OptimizationOpportunity",
    "ScanResult",

    # Multi-cloud models
    "CloudResource",
    "ComputeInstance",
    "DatabaseInstance",
    "StorageContainer",
    "MultiCloudSummary",
    "CloudProvider",
    "ResourceType",
    "ResourceStatus",
]
