import sqlite3
from pathlib import Path



def init_db():
  
    conn = sqlite3.connect("data/logs.db")
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
    
    conn = sqlite3.connect("data/logs.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO logs (timestamp, log_type, details, status)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, log_type, details, status))
    
    conn.commit()
    conn.close()
