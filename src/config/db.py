import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "logs.db"

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS logs(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   timestamp TEXT,
                   log_type TEXT,
                   details TEXT,
                   status TEXT
                   )
        ''')
    conn.commit()
    conn.close()

def save_logs(timestamp, log_type, details, status):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO logs (timestamp, log_type, details, status)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, log_type, details, status))
    
    conn.commit()
    conn.close()
