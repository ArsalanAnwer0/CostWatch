"""
Configuration management for Analytics Engine Service
"""
import os


class Config:
    """Base configuration"""

    # Application
    APP_NAME = "CostWatch Analytics Engine"
    VERSION = "1.0.0"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8003))

    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://costwatch_user:costwatch_password@localhost:5432/costwatch"
    )

    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/3")
    REDIS_TTL = int(os.getenv("REDIS_TTL", 3600))

    # AWS
    AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-west-2")
    AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID", "000000000000")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

    # S3 Settings (for report storage)
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "costwatch-reports")
    S3_REPORTS_PREFIX = os.getenv("S3_REPORTS_PREFIX", "analytics-reports")

    # Service URLs
    COST_ANALYZER_URL = os.getenv(
        "COST_ANALYZER_URL",
        "http://localhost:8001"
    )

    # Analytics Settings
    ML_MODEL_PATH = os.getenv("ML_MODEL_PATH", "/app/models")
    PREDICTION_CONFIDENCE_THRESHOLD = float(os.getenv("PREDICTION_CONFIDENCE_THRESHOLD", 0.7))
    ANOMALY_DETECTION_SENSITIVITY = os.getenv("ANOMALY_DETECTION_SENSITIVITY", "medium")

    # Request Settings
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "json")


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = "INFO"
    PREDICTION_CONFIDENCE_THRESHOLD = 0.8


class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    DATABASE_URL = "postgresql://test_user:test_pass@localhost:5432/test_db"
    REDIS_URL = "redis://localhost:6379/15"


def get_config() -> Config:
    """Get configuration based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()

    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "test": TestConfig
    }

    return config_map.get(env, DevelopmentConfig)()
