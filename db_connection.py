import os
import sqlite3
import queue
import threading
from typing import Generator
from contextlib import contextmanager

class SQLiteConnectionPool:
    """
    A thread-safe SQLite connection pool implementing WAL mode to prevent
    database locks during high-concurrency operations on constrained hardware.
    """
    def __init__(self, db_path: str = None, pool_size: int = 5):
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, "data", "ailo_db.sqlite")
        self.db_path = db_path
        self.pool_size = pool_size
        self._pool = queue.Queue(maxsize=pool_size)
        self._write_lock = threading.Lock()

        # Initialize pool
        for _ in range(pool_size):
            conn = self._create_connection()
            self._pool.put(conn)

    def _create_connection(self) -> sqlite3.Connection:
        """Create a resilient connection tailored for async thread sharing."""
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=30.0  # Equivalent to busy_timeout=30000 ms
        )

        # Enable Write-Ahead Logging (WAL) for concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        # Optimization for slower SD cards on RPi
        conn.execute("PRAGMA cache_size=-64000")

        return conn

    @contextmanager
    def get_read_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager yielding a thread-safe read-only connection."""
        conn = self._pool.get()
        try:
            yield conn
        finally:
            self._pool.put(conn)

    @contextmanager
    def get_write_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager for write operations.
        Ensures strict serialization using a thread lock to prevent overlaps.
        """
        with self._write_lock:
            conn = self._pool.get()
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                self._pool.put(conn)

    def close_all(self):
        """Clean teardown of all connections in the pool."""
        while not self._pool.empty():
            conn = self._pool.get()
            conn.close()

# Singleton instance exported for application-wide usage
db_pool = SQLiteConnectionPool()
