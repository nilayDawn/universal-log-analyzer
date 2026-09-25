import sqlite3
import os
import sys

# Access central config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from LogAnalyzer.config import Config

if not os.path.exists(os.path.dirname(Config.SQLITE_DB_PATH)):
    os.makedirs(os.path.dirname(Config.SQLITE_DB_PATH), exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(Config.SQLITE_DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")  # Enable concurrent reads/writes
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_text TEXT,
            emitted_at REAL,
            ingested_at DEFAULT (strftime('%s', 'now'))
        )
    """)
    # Index for fast temporal context queries later
    conn.execute("CREATE INDEX IF NOT EXISTS idx_emitted_at ON raw_logs(emitted_at);")
    conn.commit()
    conn.close()
    print(f"[*] SQLite DB initialized at {Config.SQLITE_DB_PATH} in WAL mode.")