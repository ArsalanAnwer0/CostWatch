import os
import logging

logger = logging.getLogger(__name__)

def verify_api_key(api_key: str) -> bool:
    """Verify API key authentication"""
    try:
        if not api_key:
            return False
        
        expected_key = os.getenv("API_KEY", "dev-api-key")
        
        if api_key != expected_key:
            logger.warning("Invalid API key provided")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"API key verification failed: {e}")
        return False