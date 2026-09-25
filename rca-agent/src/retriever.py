import sqlite3
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from LogAnalyzer.config import Config

class EvidenceRetriever:
    def __init__(self):
        self.db_path = Config.SQLITE_DB_PATH

    def get_context_window(self, block_id: str, trigger_time: float) -> str:
        """Fetches a high-performance temporal slice of cluster logs around an incident."""
        # 15 minutes before = 900 seconds, 5 minutes after = 300 seconds
        start_time = trigger_time - 900
        end_time = trigger_time + 300

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # High-efficiency index-backed temporal query
            cursor.execute("""
                SELECT log_text FROM raw_logs 
                WHERE emitted_at BETWEEN ? AND ? 
                ORDER BY emitted_at ASC
                LIMIT 500
            """, (start_time, end_time))
            
            rows = cursor.fetchall()
            logs = [row[0] for row in rows]
            return "\n".join(logs)
            
        except sqlite3.Error as e:
            print(f"[!] Database extraction failure: {str(e)}")
            return ""
        finally:
            conn.close()

if __name__ == "__main__":
    # Verifying against your exact database profile parameters
    retriever = EvidenceRetriever()
    
    # 1. Target block instance
    test_block = "blk_38865049064139660"
    
    # 2. Match the precise target epoch signature stored in your example row!
    sample_trigger_time = 1790357182.506099  
    
    print(f"[*] Extracting system state timeline for block {test_block}...")
    context = retriever.get_context_window(test_block, sample_trigger_time)
    
    print("\n--- Retrieved Database Window Output ---")
    print(context if context else "[!] Timeline slice empty. Verify index metrics or DB path.")
