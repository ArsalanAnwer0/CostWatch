import boto3
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AWSResourceScanner:
    """Base class for AWS resource scanning."""
    
    def __init__(self):
        """Initialize AWS scanner with default configuration."""
        self.session = None
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize AWS session with credentials."""
        try:
            # In production, use IAM roles or proper credential management
            self.session = boto3.Session()
            logger.info("AWS session initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize AWS session: {e}")
            self.session = None
    
    def get_client(self, service_name: str, region: str = 'us-west-2'):
        """Get AWS service client for specified region."""
        if not self.session:
            logger.warning("AWS session not available, returning mock client")
            return MockAWSClient(service_name)
        
        try:
            return self.session.client(service_name, region_name=region)
        except Exception as e:
            logger.warning(f"Failed to create {service_name} client: {e}")
            return MockAWSClient(service_name)
    
    def calculate_monthly_cost(self, hourly_cost: float) -> float:
        """Calculate monthly cost from hourly cost."""
        hours_per_month = 24 * 30  # Approximate
        return round(hourly_cost * hours_per_month, 2)
    
    def get_cost_estimate(self, instance_type: str, service_type: str = "ec2") -> float:
        """Get cost estimate for instance type."""
        # Mock pricing data (in production, use AWS Pricing API)
        pricing_data = {
            "ec2": {
                "t3.micro": 0.0104,
                "t3.small": 0.0208,
                "t3.medium": 0.0416,
                "t3.large": 0.0832,
                "t3.xlarge": 0.1664,
                "m5.large": 0.096,
                "m5.xlarge": 0.192,
                "m5.2xlarge": 0.384
            },
            "rds": {
                "db.t3.micro": 0.017,
                "db.t3.small": 0.034,
                "db.t3.medium": 0.068,
                "db.t3.large": 0.136,
                "db.m5.large": 0.192,
                "db.m5.xlarge": 0.384
            }
        }
        
        return pricing_data.get(service_type, {}).get(instance_type, 0.05)  # Default fallback


class MockAWSClient:
    """Mock AWS client for development/demo purposes."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self._generate_mock_data()
    
    def _generate_mock_data(self):
        """Generate realistic mock data for demonstration."""
        if self.service_name == "ec2":
            self._mock_ec2_data()
        elif self.service_name == "rds":
            self._mock_rds_data()
        elif self.service_name == "s3":
            self._mock_s3_data()
    
    def _mock_ec2_data(self):
        """Generate mock EC2 data."""
        self.mock_instances = [
            {
                "InstanceId": "i-1234567890abcdef0",
                "InstanceType": "t3.medium",
                "State": {"Name": "running"},
                "LaunchTime": datetime.utcnow() - timedelta(days=30),
                "Tags": [{"Key": "Name", "Value": "Web Server 1"}],
                "Placement": {"AvailabilityZone": "us-west-2a"},
                "CpuUtilization": 15.5  # Mock metric
            },
            {
                "InstanceId": "i-0987654321fedcba0",
                "InstanceType": "t3.large",
                "State": {"Name": "running"},
                "LaunchTime": datetime.utcnow() - timedelta(days=5),
                "Tags": [{"Key": "Name", "Value": "Database Server"}],
                "Placement": {"AvailabilityZone": "us-west-2b"},
                "CpuUtilization": 75.2  # Mock metric
            },
            {
                "InstanceId": "i-abcdef1234567890",
                "InstanceType": "t3.micro",
                "State": {"Name": "stopped"},
                "LaunchTime": datetime.utcnow() - timedelta(days=60),
                "Tags": [{"Key": "Name", "Value": "Development Server"}],
                "Placement": {"AvailabilityZone": "us-west-2a"},
                "CpuUtilization": 0.0  # Stopped instance
            }
        ]
    
    def _mock_rds_data(self):
        """Generate mock RDS data."""
        self.mock_databases = [
            {
                "DBInstanceIdentifier": "production-db",
                "DBInstanceClass": "db.t3.medium",
                "DBInstanceStatus": "available",
                "Engine": "postgres",
                "InstanceCreateTime": datetime.utcnow() - timedelta(days=90),
                "AvailabilityZone": "us-west-2a",
                "MultiAZ": True,
                "StorageEncrypted": True,
                "AllocatedStorage": 100,
                "CpuUtilization": 45.3  # Mock metric
            },
            {
                "DBInstanceIdentifier": "staging-db",
                "DBInstanceClass": "db.t3.small",
                "DBInstanceStatus": "available",
                "Engine": "mysql",
                "InstanceCreateTime": datetime.utcnow() - timedelta(days=30),
                "AvailabilityZone": "us-west-2b",
                "MultiAZ": False,
                "StorageEncrypted": False,
                "AllocatedStorage": 20,
                "CpuUtilization": 8.7  # Low utilization
            }
        ]
    
    def _mock_s3_data(self):
        """Generate mock S3 data."""
        self.mock_buckets = [
            {
                "Name": "costwatch-prod-data",
                "CreationDate": datetime.utcnow() - timedelta(days=365),
                "Size": 1024 * 1024 * 1024 * 50,  # 50 GB
                "ObjectCount": 10000,
                "StorageClass": "STANDARD"
            },
            {
                "Name": "costwatch-logs-archive",
                "CreationDate": datetime.utcnow() - timedelta(days=180),
                "Size": 1024 * 1024 * 1024 * 200,  # 200 GB
                "ObjectCount": 50000,
                "StorageClass": "GLACIER"
            },
            {
                "Name": "costwatch-temp-uploads",
                "CreationDate": datetime.utcnow() - timedelta(days=7),
                "Size": 1024 * 1024 * 100,  # 100 MB
                "ObjectCount": 50,
                "StorageClass": "STANDARD"
            }
        ]
    
    def describe_instances(self, **kwargs):
        """Mock EC2 describe_instances."""
        return {
            "Reservations": [
                {"Instances": [instance]} for instance in self.mock_instances
            ]
        }
    
    def describe_db_instances(self, **kwargs):
        """Mock RDS describe_db_instances."""
        return {"DBInstances": self.mock_databases}
    
    def list_buckets(self, **kwargs):
        """Mock S3 list_buckets."""
        return {"Buckets": self.mock_buckets}