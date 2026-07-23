import sqlite3
import os
from typing import List, Dict, Any, Tuple, Optional

from config import Config

DB_FILE_PATH = Config.DATABASE_PATH
SCHEMA_FILE_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

class DatabaseHelper:
    @staticmethod
    def get_connection(db_path: str = DB_FILE_PATH) -> sqlite3.Connection:
        """
        Creates and returns a connection to the SQLite database.
        Enforces foreign keys and configures row factory to return dictionary-like objects.
        """
        conn = sqlite3.connect(db_path)
        # Enable dictionary-like row access
        conn.row_factory = sqlite3.Row
        # Enable foreign key support in SQLite (disabled by default)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    @classmethod
    def init_db(cls, schema_path: str = SCHEMA_FILE_PATH, db_path: str = DB_FILE_PATH) -> None:
        """
        Initializes the database using the SQL statements from schema.sql.
        """
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found at: {schema_path}")
            
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        conn = cls.get_connection(db_path)
        try:
            with conn:
                conn.executescript(schema_sql)
        finally:
            conn.close()

    @classmethod
    def execute_query(cls, query: str, params: Tuple[Any, ...] = (), db_path: str = DB_FILE_PATH) -> List[Dict[str, Any]]:
        """
        Executes a read query (SELECT) and returns a list of dictionaries matching the rows.
        """
        conn = cls.get_connection(db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    @classmethod
    def execute_query_one(cls, query: str, params: Tuple[Any, ...] = (), db_path: str = DB_FILE_PATH) -> Optional[Dict[str, Any]]:
        """
        Executes a read query (SELECT) and returns the first row as a dictionary, or None.
        """
        conn = cls.get_connection(db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    @classmethod
    def execute_write(cls, query: str, params: Tuple[Any, ...] = (), db_path: str = DB_FILE_PATH) -> int:
        """
        Executes a write query (INSERT, UPDATE, DELETE).
        Returns the lastinserted row ID (for INSERTs) or the number of rows affected.
        """
        conn = cls.get_connection(db_path)
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                # If it's an insert, return the last inserted row ID
                if query.strip().upper().startswith("INSERT"):
                    return cursor.lastrowid
                # Otherwise return affected row count
                return cursor.rowcount
        finally:
            conn.close()

    @classmethod
    def execute_transaction(cls, queries_with_params: List[Tuple[str, Tuple[Any, ...]]], db_path: str = DB_FILE_PATH) -> bool:
        """
        Executes multiple write queries inside a single ACID transaction.
        If any query fails, the transaction is rolled back.
        Returns True if successful, raises the SQLite exception otherwise.
        """
        conn = cls.get_connection(db_path)
        try:
            with conn: # conn context manager automatically commits on success, rolls back on error
                cursor = conn.cursor()
                for query, params in queries_with_params:
                    cursor.execute(query, params)
            return True
        finally:
            conn.close()
