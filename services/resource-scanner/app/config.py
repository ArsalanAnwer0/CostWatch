"""
Configuration management for Resource Scanner Service
"""
import os


class Config:
    """Base configuration"""

    # Application
    APP_NAME = "CostWatch Resource Scanner"
    VERSION = "1.0.0"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))

    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://costwatch_user:costwatch_password@localhost:5432/costwatch"
    )

    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/1")
    REDIS_TTL = int(os.getenv("REDIS_TTL", 3600))

    # AWS
    AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-west-2")
    AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID", "000000000000")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

    # Scan Settings
    DEFAULT_SCAN_REGIONS = os.getenv("DEFAULT_SCAN_REGIONS", "us-west-2,us-east-1").split(",")
    SCAN_TIMEOUT_SECONDS = int(os.getenv("SCAN_TIMEOUT_SECONDS", 300))
    MAX_CONCURRENT_SCANS = int(os.getenv("MAX_CONCURRENT_SCANS", 5))

    # Resource Settings
    INCLUDE_STOPPED_INSTANCES = os.getenv("INCLUDE_STOPPED_INSTANCES", "true").lower() == "true"
    INCLUDE_TERMINATED_INSTANCES = os.getenv("INCLUDE_TERMINATED_INSTANCES", "false").lower() == "true"

    # Cost Estimation
    ESTIMATE_COSTS = os.getenv("ESTIMATE_COSTS", "true").lower() == "true"
    COST_ESTIMATION_CURRENCY = os.getenv("COST_ESTIMATION_CURRENCY", "USD")

    # Request Settings
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "json")


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    SCAN_TIMEOUT_SECONDS = 600  # Longer timeout for dev


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = "INFO"
    MAX_CONCURRENT_SCANS = 10


class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    DATABASE_URL = "postgresql://test_user:test_pass@localhost:5432/test_db"
    REDIS_URL = "redis://localhost:6379/15"
    ESTIMATE_COSTS = False


def get_config() -> Config:
    """Get configuration based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()

    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "test": TestConfig
    }

    return config_map.get(env, DevelopmentConfig)()
