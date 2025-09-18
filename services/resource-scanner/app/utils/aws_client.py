import boto3
import logging
from typing import Dict, List, Any
import os

logger = logging.getLogger(__name__)

class AWSClient:
    def __init__(self):
        """Initialize AWS client with credentials from environment variables."""
        try:
            # Get credentials from environment
            self.region = os.getenv('AWS_REGION', 'us-west-2')
            
            # Initialize boto3 session
            self.session = boto3.Session(
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=self.region
            )
            
            # Test connection
            sts = self.session.client('sts')
            identity = sts.get_caller_identity()
            logger.info(f"Connected to AWS account: {identity['Account']}")
            
        except Exception as e:
            logger.error(f"Failed to initialize AWS client: {e}")
            raise
    
    def list_ec2_instances(self) -> List[Dict[str, Any]]:
        """List EC2 instances in the current region."""
        try:
            ec2 = self.session.client('ec2')
            
            response = ec2.describe_instances()
            instances = []
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    # Extract basic instance info
                    instance_info = {
                        'instance_id': instance['InstanceId'],
                        'instance_type': instance['InstanceType'],
                        'state': instance['State']['Name'],
                        'launch_time': instance.get('LaunchTime'),
                        'availability_zone': instance['Placement']['AvailabilityZone'],
                        'tags': instance.get('Tags', [])
                    }
                    instances.append(instance_info)
            
            logger.info(f"Found {len(instances)} EC2 instances")
            return instances
            
        except Exception as e:
            logger.error(f"Failed to list EC2 instances: {e}")
            return []

    def list_s3_buckets(self) -> List[Dict[str, Any]]:
        """List S3 buckets."""
        try:
            s3 = self.session.client('s3')
            
            response = s3.list_buckets()
            buckets = []
            
            for bucket in response['Buckets']:
                bucket_info = {
                    'bucket_name': bucket['Name'],
                    'creation_date': bucket['CreationDate'],
                    'region': self.region  # Note: This is simplified
                }
                buckets.append(bucket_info)
            
            logger.info(f"Found {len(buckets)} S3 buckets")
            return buckets
            
        except Exception as e:
            logger.error(f"Failed to list S3 buckets: {e}")
            return []

    def test_connection(self) -> bool:
        """Test AWS connection."""
        try:
            sts = self.session.client('sts')
            sts.get_caller_identity()
            return True
        except Exception as e:
            logger.error(f"AWS connection test failed: {e}")
            return False