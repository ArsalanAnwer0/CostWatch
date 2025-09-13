import asyncio
import time
import json
import random
import string
from typing import Dict, Any, List
import httpx

def generate_test_email() -> str:
    """Generate unique test email."""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_suffix}@costwatch.com"

def generate_test_user() -> Dict[str, str]:
    """Generate test user data."""
    return {
        "email": generate_test_email(),
        "password": "testpassword123",
        "full_name": f"Test User {random.randint(1000, 9999)}",
        "company": f"Test Company {random.randint(100, 999)}"
    }

async def wait_for_condition(
    condition_func,
    timeout: float = 30.0,
    check_interval: float = 1.0,
    *args,
    **kwargs
) -> bool:
    """Wait for a condition to be true."""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            if await condition_func(*args, **kwargs) if asyncio.iscoroutinefunction(condition_func) else condition_func(*args, **kwargs):
                return True
        except Exception:
            pass
        
        await asyncio.sleep(check_interval)
    
    return False

async def service_is_healthy(url: str) -> bool:
    """Check if service is healthy."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{url}/health")
            return response.status_code == 200
    except Exception:
        return False

def validate_cost_data_structure(cost_data: Dict[str, Any]) -> bool:
    """Validate cost data has required structure."""
    required_fields = ["service_name", "cost", "currency", "date", "region", "account_id"]
    return all(field in cost_data for field in required_fields)

def validate_optimization_recommendation(recommendation: Dict[str, Any]) -> bool:
    """Validate optimization recommendation structure."""
    required_fields = ["resource_id", "resource_type", "current_cost", "potential_savings", "recommendation", "priority"]
    return all(field in recommendation for field in required_fields)

def calculate_test_metrics(test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate test execution metrics."""
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results if result.get("status") == "passed")
    failed_tests = total_tests - passed_tests
    
    total_duration = sum(result.get("duration", 0) for result in test_results)
    avg_duration = total_duration / total_tests if total_tests > 0 else 0
    
    return {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
        "total_duration": total_duration,
        "average_duration": avg_duration
    }

class TestDataGenerator:
    """Generate test data for various scenarios."""
    
    @staticmethod
    def generate_aws_resources(count: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Generate mock AWS resources."""
        ec2_instances = []
        rds_instances = []
        s3_buckets = []
        
        for i in range(count):
            # EC2 instances
            ec2_instances.append({
                "instance_id": f"i-test{random.randint(100000000000000, 999999999999999):015x}",
                "instance_type": random.choice(["t3.micro", "t3.small", "t3.medium", "t3.large"]),
                "state": random.choice(["running", "stopped", "terminated"]),
                "region": random.choice(["us-west-2", "us-east-1", "eu-west-1"]),
                "cost": round(random.uniform(10, 500), 2),
                "cpu_utilization": round(random.uniform(5, 95), 1)
            })
            
            # RDS instances
            if i < count // 2:  # Fewer RDS instances
                rds_instances.append({
                    "db_identifier": f"test-db-{i}",
                    "db_class": random.choice(["db.t3.micro", "db.t3.small", "db.t3.medium"]),
                    "engine": random.choice(["postgres", "mysql", "mariadb"]),
                    "status": random.choice(["available", "stopped", "maintenance"]),
                    "cost": round(random.uniform(50, 300), 2)
                })
            
            # S3 buckets
            if i < count // 3:  # Even fewer S3 buckets
                s3_buckets.append({
                    "bucket_name": f"test-bucket-{i}-{random.randint(1000, 9999)}",
                    "size_gb": round(random.uniform(1, 1000), 2),
                    "storage_class": random.choice(["STANDARD", "GLACIER", "DEEP_ARCHIVE"]),
                    "cost": round(random.uniform(5, 100), 2)
                })
        
        return {
            "ec2_instances": ec2_instances,
            "rds_instances": rds_instances,
            "s3_buckets": s3_buckets
        }
    
    @staticmethod
    def generate_cost_data(days: int = 30) -> List[Dict[str, Any]]:
        """Generate cost data for testing."""
        services = ["EC2", "RDS", "S3", "Lambda", "CloudWatch", "VPC"]
        regions = ["us-west-2", "us-east-1", "eu-west-1"]
        cost_data = []
        
        for day in range(days):
            for service in services:
                cost_data.append({
                    "service_name": service,
                    "cost": round(random.uniform(10, 1000), 2),
                    "currency": "USD",
                    "date": f"2024-01-{day+1:02d}",
                    "region": random.choice(regions),
                    "account_id": "123456789012"
                })
        
        return cost_data
    
    @staticmethod
    def generate_optimization_recommendations(count: int = 10) -> List[Dict[str, Any]]:
        """Generate optimization recommendations."""
        recommendations = []
        
        for i in range(count):
            recommendations.append({
                "resource_id": f"resource-{i}",
                "resource_type": random.choice(["EC2 Instance", "RDS Database", "S3 Bucket"]),
                "current_cost": round(random.uniform(50, 500), 2),
                "potential_savings": round(random.uniform(10, 200), 2),
                "recommendation": f"Optimization recommendation {i}",
                "priority": random.choice(["High", "Medium", "Low"]),
                "estimated_effort": random.choice(["Low", "Medium", "High"])
            })
        
        return recommendations