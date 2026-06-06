import logging
import sqlite3
import time
from pathlib import Path

logger = logging.getLogger(__name__)


DB_PATH = Path("data/logs.db")


def _connect():
    # busy_timeout helps avoid immediate "database is locked" failures under concurrent writes.
    # WAL improves concurrent read/write behavior.
    conn = sqlite3.connect(str(DB_PATH), timeout=30, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=3000")
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            log_type TEXT,
            details TEXT,
            status TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_logs(timestamp, log_type, details, status, *, retries: int = 5):
    conn = _connect()
    cursor = conn.cursor()

    last_exc = None
    for attempt in range(retries):
        try:
            cursor.execute(
                """
                INSERT INTO logs (timestamp, log_type, details, status)
                VALUES (?, ?, ?, ?)
                """,
                (timestamp, log_type, details, status),
            )
            conn.commit()
            return
        except sqlite3.OperationalError as exc:
            last_exc = exc
            # Retry only for transient lock errors.
            if "locked" not in str(exc).lower():
                raise
            sleep_s = min(0.2 * (2**attempt), 1.5)
            time.sleep(sleep_s)

    logger.exception("Failed to save log after %s retries", retries)
    if last_exc:
        raise last_exc
    raise RuntimeError("Failed to save log")
    

def get_log_by_id(log_id):
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("SELECT log_type, timestamp, details FROM logs WHERE id = ?", (log_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def get_total_logs_count():
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM logs")
    count = cursor.fetchone()[0]
    conn.close()
    return count

