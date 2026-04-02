"""
Resource Models
"""

from .resource import AWSResource, EC2Instance, RDSInstance, S3Bucket, OptimizationOpportunity
from .scan_result import ScanResult

__all__ = [
    "AWSResource",
    "EC2Instance",
    "RDSInstance",
    "S3Bucket",
    "OptimizationOpportunity",
    "ScanResult",
]
