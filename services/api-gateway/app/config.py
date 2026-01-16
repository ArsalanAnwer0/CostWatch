"""
Configuration management for API Gateway
"""
import os
from typing import Optional


class Config:
    """Base configuration"""

    # Application
    APP_NAME = "CostWatch API Gateway"
    VERSION = "1.0.0"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8002))

    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://costwatch_user:costwatch_password@localhost:5432/costwatch"
    )

    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_TTL = int(os.getenv("REDIS_TTL", 3600))  # 1 hour default

    # AWS
    AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-west-2")
    AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID", "000000000000")

    # Service URLs
    RESOURCE_SCANNER_URL = os.getenv(
        "RESOURCE_SCANNER_URL",
        "http://localhost:8000"
    )
    COST_ANALYZER_URL = os.getenv(
        "COST_ANALYZER_URL",
        "http://localhost:8001"
    )
    ANALYTICS_ENGINE_URL = os.getenv(
        "ANALYTICS_ENGINE_URL",
        "http://localhost:8003"
    )
    ALERT_MANAGER_URL = os.getenv(
        "ALERT_MANAGER_URL",
        "http://localhost:8004"
    )

    # API Settings
    API_KEY_HEADER = "X-API-Key"
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))  # seconds

    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", 60))
    RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", 1000))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "json")  # json or text

    # CORS
    CORS_ENABLED = os.getenv("CORS_ENABLED", "true").lower() == "true"
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", 24))


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = "INFO"
    RATE_LIMIT_PER_MINUTE = 30
    RATE_LIMIT_PER_HOUR = 500


class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    DATABASE_URL = "postgresql://test_user:test_pass@localhost:5432/test_db"
    REDIS_URL = "redis://localhost:6379/15"  # Use separate Redis DB for tests
    RATE_LIMIT_ENABLED = False


def get_config() -> Config:
    """
    Get configuration based on environment

    Returns:
        Config: Configuration object
    """
    env = os.getenv("ENVIRONMENT", "development").lower()

    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "test": TestConfig
    }

    return config_map.get(env, DevelopmentConfig)()
