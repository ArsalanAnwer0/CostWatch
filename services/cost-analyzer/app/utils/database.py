import os
import psycopg2
import logging
from typing import Optional

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

def execute_query(query: str, params: Optional[tuple] = None):
    """Execute database query"""
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
            return cursor.rowcount
            
    except Exception as e:
        if connection:
            connection.rollback()
        logger.error(f"Query execution failed: {e}")
        raise
    finally:
        if connection:
            connection.close()