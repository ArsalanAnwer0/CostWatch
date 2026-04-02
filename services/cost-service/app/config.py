"""
Configuration management for Cost Service
"""
import os


class Config:
    APP_NAME = "CostWatch Cost Service"
    VERSION = "1.0.0"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8001))

    # Database
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "costwatch")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "costwatch_user")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "costwatch_password")

    # AWS
    AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-west-2")
    AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID", "000000000000")

    # Cost Analysis
    DEFAULT_COST_PERIOD_DAYS = int(os.getenv("DEFAULT_COST_PERIOD_DAYS", 30))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = "INFO"


def get_config() -> Config:
    env = os.getenv("ENVIRONMENT", "development").lower()
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
    }
    return config_map.get(env, DevelopmentConfig)()
