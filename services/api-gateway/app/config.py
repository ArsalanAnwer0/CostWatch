"""
Configuration management for API Gateway
"""
import os


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
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "costwatch")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "costwatch_user")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "costwatch_password")

    # AWS
    AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-west-2")

    # Service URLs (internal Docker network)
    RESOURCE_SCANNER_URL = os.getenv("RESOURCE_SCANNER_URL", "http://resource-scanner:8000")
    COST_SERVICE_URL = os.getenv("COST_SERVICE_URL", "http://cost-service:8001")

    # API Settings
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))

    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", 60))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

    # Security
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", 24))


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = "INFO"
    RATE_LIMIT_PER_MINUTE = 30


def get_config() -> Config:
    env = os.getenv("ENVIRONMENT", "development").lower()
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
    }
    return config_map.get(env, DevelopmentConfig)()
