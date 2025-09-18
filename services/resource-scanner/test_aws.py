import os
import sys
sys.path.append('app')

from utils.aws_client import AWSClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

def test_aws_connection():
    print("Testing AWS connection...")
    
    try:
        client = AWSClient()
        
        # Test connection
        if client.test_connection():
            print("✓ AWS connection successful!")
        else:
            print("✗ AWS connection failed")
            return
        
        # Test S3 buckets
        buckets = client.list_s3_buckets()
        print(f"✓ Found {len(buckets)} S3 buckets:")
        for bucket in buckets:
            print(f"  - {bucket['bucket_name']}")
        
        # Test EC2 instances
        instances = client.list_ec2_instances()
        print(f"✓ Found {len(instances)} EC2 instances")
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_aws_connection()