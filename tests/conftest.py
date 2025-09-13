import pytest
import asyncio
import os
import sys
from typing import Generator, Dict, Any
import httpx
import psycopg2
import redis
import docker
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestConfig:
    """Test configuration constants."""
    API_GATEWAY_URL = os.getenv('API_GATEWAY_URL', 'http://localhost:8000')
    RESOURCE_SCANNER_URL = os.getenv('RESOURCE_SCANNER_URL', 'http://localhost:5000')
    NGINX_URL = os.getenv('NGINX_URL', 'http://localhost:80')
    TEST_EMAIL = 'test@costwatch.com'
    TEST_PASSWORD = 'testpassword123'
    TEST_TIMEOUT = 30

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def http_client():
    """Create HTTP client for API testing."""
    async with httpx.AsyncClient(timeout=TestConfig.TEST_TIMEOUT) as client:
        yield client

@pytest.fixture(scope="session")
def docker_client():
    """Create Docker client for container testing."""
    client = docker.from_env()
    yield client
    client.close()

@pytest.fixture(scope="session")
def test_user_credentials():
    """Test user credentials."""
    return {
        "email": TestConfig.TEST_EMAIL,
        "password": TestConfig.TEST_PASSWORD,
        "full_name": "Test User",
        "company": "Test Company"
    }

@pytest.fixture(scope="session")
async def auth_token(http_client: httpx.AsyncClient, test_user_credentials: Dict[str, str]):
    """Get authentication token for test user."""
    # First try to login
    login_response = await http_client.post(
        f"{TestConfig.API_GATEWAY_URL}/auth/login",
        json={
            "email": test_user_credentials["email"],
            "password": test_user_credentials["password"]
        }
    )
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        return token_data["access_token"]
    
    # If login fails, register new user
    register_response = await http_client.post(
        f"{TestConfig.API_GATEWAY_URL}/auth/register",
        json=test_user_credentials
    )
    
    if register_response.status_code != 200:
        pytest.fail(f"Failed to register test user: {register_response.text}")
    
    # Login with new user
    login_response = await http_client.post(
        f"{TestConfig.API_GATEWAY_URL}/auth/login",
        json={
            "email": test_user_credentials["email"],
            "password": test_user_credentials["password"]
        }
    )
    
    if login_response.status_code != 200:
        pytest.fail(f"Failed to login with test user: {login_response.text}")
    
    token_data = login_response.json()
    return token_data["access_token"]

@pytest.fixture(scope="session")
def auth_headers(auth_token: str):
    """Create authorization headers."""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture(scope="function")
def postgres_container():
    """Create PostgreSQL test container."""
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres

@pytest.fixture(scope="function")
def redis_container():
    """Create Redis test container."""
    with RedisContainer("redis:7-alpine") as redis_container:
        yield redis_container

@pytest.fixture(scope="session")
def sample_aws_resources():
    """Sample AWS resources for testing."""
    return {
        "ec2_instances": [
            {
                "instance_id": "i-test123456789abcdef",
                "instance_type": "t3.medium",
                "state": "running",
                "region": "us-west-2",
                "cost": 45.67
            },
            {
                "instance_id": "i-test987654321fedcba", 
                "instance_type": "t3.large",
                "state": "stopped",
                "region": "us-west-2",
                "cost": 0.0
            }
        ],
        "rds_instances": [
            {
                "db_identifier": "test-prod-db",
                "db_class": "db.t3.medium",
                "engine": "postgres",
                "status": "available",
                "cost": 78.90
            }
        ],
        "s3_buckets": [
            {
                "bucket_name": "test-costwatch-data",
                "size_gb": 150.5,
                "storage_class": "STANDARD",
                "cost": 3.45
            }
        ]
    }

@pytest.mark.asyncio
async def wait_for_service(url: str, timeout: int = 30, retries: int = 10):
    """Wait for service to be available."""
    for i in range(retries):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{url}/health")
                if response.status_code == 200:
                    return True
        except Exception:
            pass
        
        if i < retries - 1:
            await asyncio.sleep(timeout / retries)
    
    return False

@pytest.fixture(scope="session", autouse=True)
async def ensure_services_running():
    """Ensure all services are running before tests."""
    services = [
        ("API Gateway", TestConfig.API_GATEWAY_URL),
        ("Resource Scanner", TestConfig.RESOURCE_SCANNER_URL)
    ]
    
    for service_name, service_url in services:
        if not await wait_for_service(service_url):
            pytest.fail(f"{service_name} is not available at {service_url}")