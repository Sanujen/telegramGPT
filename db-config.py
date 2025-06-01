import psycopg2
import os
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.DATABASE_URL = os.getenv("DATABASE_URL")
            if not self.DATABASE_URL:
                raise ValueError("DATABASE_URL environment variable is not set")
            self.initialized = True

    def get_connection(self):
        """Get or create database connection"""
        if self._connection is None or self._connection.closed:
            try:
                self._connection = psycopg2.connect(self.DATABASE_URL)
                logger.info("Database connection established")
            except Exception as e:
                logger.error(f"Failed to connect to database: {e}")
                raise
        return self._connection

    def close_connection(self):
        """Close database connection"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")

    def execute_query(self, query: str, params: tuple = None) -> None:
        """Execute a query without returning results"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error executing query: {e}")
            raise

    def fetch_all(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a query and fetch all results"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching results: {e}")
            raise

    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Execute a query and fetch one result"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                columns = [desc[0] for desc in cur.description]
                row = cur.fetchone()
                return dict(zip(columns, row)) if row else None
        except Exception as e:
            logger.error(f"Error fetching single result: {e}")
            raise

# Create singleton instance
db = DatabaseConfig()