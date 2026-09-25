import sqlite3
import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from LogAnalyzer.config import Config

def setup_incident_table():
    conn = sqlite3.connect(Config.SQLITE_DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            block_id TEXT,
            root_cause_summary TEXT,
            confidence_level REAL,
            remediation_steps TEXT,
            detected_at DEFAULT (datetime('now', 'localtime'))
        )
    """)
    
    # Insert the mock data you just generated in the previous test
    mock_data = {
        "root_cause_summary": "The logs indicate normal operations for HDFS block blk_-1608999687919862906, including block allocation and successful packet transmission.",
        "confidence_level": 1.0,
        "remediation_steps": ["No remediation actions are required."]
    }
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM incidents WHERE block_id = ?", ("blk_-1608999687919862906",))
    if cursor.fetchone()[0] == 0:
        conn.execute("""
            INSERT INTO incidents (block_id, root_cause_summary, confidence_level, remediation_steps)
            VALUES (?, ?, ?, ?)
        """, (
            "blk_-1608999687919862906",
            mock_data["root_cause_summary"],
            mock_data["confidence_level"],
            json.dumps(mock_data["remediation_steps"])
        ))
    
    conn.commit()
    conn.close()
    print("[*] Incident table configured and populated with test data.")

if __name__ == "__main__":
    setup_incident_table()