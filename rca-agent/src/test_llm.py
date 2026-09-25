import sqlite3
import os
import sys
from llm_client import generate_rca

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from LogAnalyzer.config import Config

def run_test():
    db_path = os.path.abspath(Config.SQLITE_DB_PATH)
    
    if not os.path.exists(db_path):
        print(f"[!] Database not found at {db_path}. Ensure your ingestion worker is running.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    test_block = "blk_-1608999687919862906"
    
    try:
        cursor.execute("SELECT log_text FROM raw_logs WHERE log_text LIKE ? LIMIT 50", (f"%{test_block}%",))
        rows = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"[!] SQLite Error: {e}")
        print("[!] The database file exists, but the 'raw_logs' table is missing. Start your Ingestion Worker to create it.")
        conn.close()
        return
        
    conn.close()

    if not rows:
        print(f"[!] No logs found for {test_block}. Ensure your simulator has pushed logs into the database.")
        return

    context = "\n".join([row[0] for row in rows])
    print(f"[*] Fetched {len(rows)} logs for {test_block}. Sending to Gemini...")
    
    result = generate_rca(test_block, context)
    print("\n--- Gemini RCA JSON Output ---")
    print(result)

if __name__ == "__main__":
    run_test()