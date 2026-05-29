import sqlite3
import re
import os
import sys

# Ensure we can import db_connection from the project root
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from db_connection import db_pool

# Override the default db path to match our new database
db_pool.db_path = "data/ailo_db.sqlite"

class DatabaseExecutor:
    def __init__(self):
        # Regex to catch any destructive SQL commands, case-insensitive
        # Ensures that only read queries can be processed
        self.destructive_pattern = re.compile(r'\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|REPLACE|GRANT|REVOKE)\b', re.IGNORECASE)

    def execute_read_query(self, query: str) -> dict:
        """
        Executes a strictly read-only SQL query against the SQLite database securely.
        Returns a dictionary with 'columns' and 'rows' or an 'error' block.
        """
        if not query or not query.strip():
            return {"error": "SQL_ERROR", "details": "Empty query provided."}

        # 1. SECURITY GUARD: Explicitly reject destructive queries
        if self.destructive_pattern.search(query):
            return {
                "error": "SECURITY_VIOLATION",
                "details": "Destructive command detected. Query blocked."
            }

        # 2. EXECUTION: Run the query safely
        try:
            with db_pool.get_read_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)

                # If query doesn't return data (e.g., it was an unexpected non-SELECT that bypassed regex somehow)
                if cursor.description is None:
                    return {"columns": [], "rows": []}

                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()

                return {
                    "columns": columns,
                    "rows": rows
                }
        except sqlite3.Error as e:
            # Catch standard SQL execution errors gracefully
            return {
                "error": "SQL_ERROR",
                "details": str(e)
            }
        except Exception as e:
            # Catch any broader errors to prevent crashing the executor pipeline
            return {
                "error": "SQL_ERROR",
                "details": f"Unexpected execution error: {str(e)}"
            }
