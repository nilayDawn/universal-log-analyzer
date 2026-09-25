import sqlite3
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from LogAnalyzer.config import Config

class EvidenceRetriever:
    def __init__(self):
        self.db_path = Config.SQLITE_DB_PATH

    def get_context_window(self, block_id: str, trigger_time: float) -> str:
        """Fetches logs for a specific block ID from T-15m to T+5m."""
        # 15 minutes before = 900 seconds, 5 minutes after = 300 seconds
        start_time = trigger_time - 900
        end_time = trigger_time + 300

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # SQLite uses standard SQL wildcard (%) to match the block_id anywhere in the raw text
        cursor.execute("""
            SELECT log_text FROM raw_logs 
            WHERE emitted_at BETWEEN ? AND ? 
            AND log_text LIKE ?
            ORDER BY emitted_at ASC
        """, (start_time, end_time, f"%{block_id}%"))
        
        rows = cursor.fetchall()
        conn.close()

        # Compile into a single text block for the LLM prompt
        logs = [row[0] for row in rows]
        return "\n".join(logs)

if __name__ == "__main__":
    # Quick local test using one of the Block IDs from your ML output
    import time
    retriever = EvidenceRetriever()
    test_block = "blk_-1608999687919862906"
    print(f"[*] Querying DB for {test_block}...")
    
    # We use current time assuming the simulator recently pushed these logs
    context = retriever.get_context_window(test_block, time.time()) 
    print("--- Retrieved Context ---")
    print(context)