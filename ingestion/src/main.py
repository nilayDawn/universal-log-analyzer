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

    BATCH_SIZE = 50
    buffer = []

    try:
        while True:
            # 1. Read from Redis (blocks for up to 2 seconds)
            messages = client.xreadgroup(
                GROUP_NAME, 
                CONSUMER_NAME, 
                {Config.REDIS_STREAM_NAME: ">"}, 
                count=BATCH_SIZE, 
                block=2000
            )
            
            # 2. Collect any incoming messages into the buffer
            if messages:
                for stream, msg_list in messages:
                    for msg_id, payload in msg_list:
                        buffer.append((msg_id, payload))
            
            # 3. SMART FLUSH: Trigger when batch is full OR when Redis runs dry (timeout)
            if len(buffer) >= BATCH_SIZE or (not messages and len(buffer) > 0):
                
                for msg_id, payload in buffer:
                    raw_log = payload.get("raw_log", "")
                    emitted_at = float(payload.get("emitted_at", 0))
                    
                    conn.execute(
                        "INSERT INTO raw_logs (log_text, emitted_at) VALUES (?, ?)",
                        (raw_log, emitted_at)
                    )
                    client.xack(Config.REDIS_STREAM_NAME, GROUP_NAME, msg_id)
                
                conn.commit()
                
                # CRITICAL FIX: Print len(buffer), NOT len(msg_list)
                print(f"[✓] Sunk {len(buffer)} logs into SQLite WAL.")
                
                # Clear the container for the next batch
                buffer.clear() 
                print("[*]Ingestion Buffer cleared. Awaiting next batch...")
                
    except KeyboardInterrupt:
        print("\n[*] Shutting down ingestion worker.")
    finally:
        conn.close()

if __name__ == "__main__":
    run_ingestion()