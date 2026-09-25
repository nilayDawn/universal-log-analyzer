import sys
import os
import redis
from drain3_manager import parse_log

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from LogAnalyzer.config import Config

GROUP_NAME = "parser_group"
CONSUMER_NAME = "parser_worker_1"

def run_parser():
    client = redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        decode_responses=True
    )

    try:
        client.xgroup_create(Config.REDIS_STREAM_NAME, GROUP_NAME, id="0", mkstream=True)
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise

    print(f"[*] Parser Worker listening to Redis stream '{Config.REDIS_STREAM_NAME}'...")

    try:
        while True:
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
                    
                    # 1. Process log through Drain3
                    result = parse_log(raw_log)
                    
                    # 2. Print newly discovered templates to the terminal
                    if result.get("change_type") != "none":
                        print(f"[New Template] ID: {result['cluster_id']} | Pattern: {result['template_mined']}")
                    
                    # 3. Acknowledge successful processing
                    client.xack(Config.REDIS_STREAM_NAME, GROUP_NAME, msg_id)
                    
    except KeyboardInterrupt:
        print("\n[*] Shutting down Parser worker.")

if __name__ == "__main__":
    run_parser()