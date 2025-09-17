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

def init_database():
    """Initialize database tables for alert manager"""
    try:
        # Create alert_rules table
        create_rules_table = """
        CREATE TABLE IF NOT EXISTS alert_rules (
            rule_id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            condition VARCHAR(500) NOT NULL,
            threshold DECIMAL(15,2) NOT NULL,
            account_id VARCHAR(255) NOT NULL,
            notification_channels TEXT,
            enabled BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create alert_history table
        create_history_table = """
        CREATE TABLE IF NOT EXISTS alert_history (
            alert_id VARCHAR(255) PRIMARY KEY,
            alert_type VARCHAR(100) NOT NULL,
            severity VARCHAR(50) NOT NULL,
            message TEXT NOT NULL,
            account_id VARCHAR(255) NOT NULL,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(50) DEFAULT 'sent'
        );
        """
        
        # Create indexes
        create_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_alert_rules_account ON alert_rules(account_id);",
            "CREATE INDEX IF NOT EXISTS idx_alert_history_account ON alert_history(account_id);",
            "CREATE INDEX IF NOT EXISTS idx_alert_history_created ON alert_history(created_at);"
        ]
        
        execute_query(create_rules_table)
        execute_query(create_history_table)
        
        for index_query in create_indexes:
            execute_query(index_query)
        
        logger.info("Database tables initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise