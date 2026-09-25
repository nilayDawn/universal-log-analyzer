import sys
import os
import time
import redis
from storage import init_db, get_db_connection

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from LogAnalyzer.config import Config

GROUP_NAME = "ingestion_group"
CONSUMER_NAME = "ingestion_worker_1"

def run_ingestion():
    init_db()
    
    client = redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        decode_responses=True
    )

    # Initialize the Consumer Group
    try:
        client.xgroup_create(Config.REDIS_STREAM_NAME, GROUP_NAME, id="0", mkstream=True)
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise

    print(f"[*] Ingestion Worker listening to Redis stream '{Config.REDIS_STREAM_NAME}'...")
    conn = get_db_connection()

    try:
        while True:
            # Block for up to 2 seconds waiting for new logs
            messages = client.xreadgroup(
                GROUP_NAME, 
                CONSUMER_NAME, 
                {Config.REDIS_STREAM_NAME: ">"}, 
                count=50, 
                block=2000
            )
            
            if not messages:
                continue
            
            for stream, msg_list in messages:
                for msg_id, payload in msg_list:
                    raw_log = payload.get("raw_log", "")
                    emitted_at = float(payload.get("emitted_at", 0))
                    
                    conn.execute(
                        "INSERT INTO raw_logs (log_text, emitted_at) VALUES (?, ?)",
                        (raw_log, emitted_at)
                    )
                    # Acknowledge message processing
                    client.xack(Config.REDIS_STREAM_NAME, GROUP_NAME, msg_id)
                
                conn.commit()
                print(f"[✓] Sunk {len(msg_list)} logs into SQLite WAL.")
                
    except KeyboardInterrupt:
        print("\n[*] Shutting down ingestion worker.")
    finally:
        conn.close()

if __name__ == "__main__":
    run_ingestion()