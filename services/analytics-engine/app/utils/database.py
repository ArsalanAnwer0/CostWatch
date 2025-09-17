import os
import psycopg2
import logging
from typing import Optional, List, Tuple, Any

logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection"""
    try:
        connection = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database=os.getenv("POSTGRES_DB", "costwatch"),
            user=os.getenv("POSTGRES_USER", "costwatch_user"),
            password=os.getenv("POSTGRES_PASSWORD", "password")
        )
        return connection
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def execute_query(query: str, params: Optional[Tuple] = None) -> List[Tuple]:
    """Execute database query and return results"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
            return result
        else:
            connection.commit()
            return []
            
    except Exception as e:
        if connection:
            connection.rollback()
        logger.error(f"Query execution failed: {e}")
        raise
    finally:
        if connection:
            connection.close()

def init_analytics_database():
    """Initialize database tables for analytics engine"""
    try:
        # Create analytics_reports table
        create_reports_table = """
        CREATE TABLE IF NOT EXISTS analytics_reports (
            report_id VARCHAR(255) PRIMARY KEY,
            account_id VARCHAR(255) NOT NULL,
            report_type VARCHAR(100) NOT NULL,
            report_data TEXT NOT NULL,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create analytics_cache table for performance
        create_cache_table = """
        CREATE TABLE IF NOT EXISTS analytics_cache (
            cache_key VARCHAR(255) PRIMARY KEY,
            account_id VARCHAR(255) NOT NULL,
            data TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create indexes
        create_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_analytics_reports_account ON analytics_reports(account_id);",
            "CREATE INDEX IF NOT EXISTS idx_analytics_cache_account ON analytics_cache(account_id);",
            "CREATE INDEX IF NOT EXISTS idx_analytics_cache_expires ON analytics_cache(expires_at);"
        ]
        
        execute_query(create_reports_table)
        execute_query(create_cache_table)
        
        for index_query in create_indexes:
            execute_query(index_query)
        
        logger.info("Analytics database tables initialized successfully")
        
    except Exception as e:
        logger.error(f"Analytics database initialization failed: {e}")
        raise