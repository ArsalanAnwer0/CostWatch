"""
Configuration management for Alert Manager Service
"""
import os


class Config:
    """Base configuration"""

    # Application
    APP_NAME = "CostWatch Alert Manager"
    VERSION = "1.0.0"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8004))

    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://costwatch_user:costwatch_password@localhost:5432/costwatch"
    )

    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/4")
    REDIS_TTL = int(os.getenv("REDIS_TTL", 3600))

    # AWS
    AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-west-2")
    AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID", "000000000000")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

    # SNS Settings (for notifications)
    SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")
    SNS_ENABLED = os.getenv("SNS_ENABLED", "true").lower() == "true"

    # Service URLs
    COST_ANALYZER_URL = os.getenv(
        "COST_ANALYZER_URL",
        "http://localhost:8001"
    )
    ANALYTICS_ENGINE_URL = os.getenv(
        "ANALYTICS_ENGINE_URL",
        "http://localhost:8003"
    )

    # Alert Settings
    ALERT_CHECK_INTERVAL_MINUTES = int(os.getenv("ALERT_CHECK_INTERVAL_MINUTES", 60))
    ALERT_RETENTION_DAYS = int(os.getenv("ALERT_RETENTION_DAYS", 90))
    MAX_ALERTS_PER_ACCOUNT = int(os.getenv("MAX_ALERTS_PER_ACCOUNT", 1000))

    # Notification Settings
    EMAIL_NOTIFICATIONS_ENABLED = os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "false").lower() == "true"
    SLACK_NOTIFICATIONS_ENABLED = os.getenv("SLACK_NOTIFICATIONS_ENABLED", "false").lower() == "true"
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

    # Request Settings
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "json")


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    SNS_ENABLED = False  # Don't send real alerts in dev


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = "INFO"
    SNS_ENABLED = True


class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    DATABASE_URL = "postgresql://test_user:test_pass@localhost:5432/test_db"
    REDIS_URL = "redis://localhost:6379/15"
    SNS_ENABLED = False


def get_config() -> Config:
    """Get configuration based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()

    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "test": TestConfig
    }

    return config_map.get(env, DevelopmentConfig)()
