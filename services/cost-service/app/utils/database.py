import os
import logging
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    psycopg2 = None

logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection, return None if not available."""
    if not DB_AVAILABLE:
        logger.warning("Database not available - psycopg2 not installed")
        return None

    try:
        return psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            database=os.getenv('POSTGRES_DB', 'costwatch'),
            user=os.getenv('POSTGRES_USER', 'costwatch_user'),
            password=os.getenv('POSTGRES_PASSWORD', 'costwatch_password'),
            cursor_factory=RealDictCursor
        )
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None
