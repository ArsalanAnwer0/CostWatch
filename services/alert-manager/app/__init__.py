"""
Alert Manager Service - CostWatch Platform
Handles multi-channel notifications and alert management
"""

__version__ = "1.0.0"

from .main import create_app

__all__ = ["create_app"]