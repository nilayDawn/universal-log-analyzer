import os
import sys
import time
from datetime import datetime
import redis

# Add project root to sys.path to access LogAnalyzer.config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from LogAnalyzer.config import Config

TIMESTAMP_FORMAT = "%y%m%d %H%M%S"

def parse_hdfs_timestamp(line: str) -> datetime | None:
    parts = line.strip().split()
    if len(parts) >= 2:
        date_str = f"{parts[0]} {parts[1]}"
        try:
            return datetime.strptime(date_str, TIMESTAMP_FORMAT)
        except ValueError:
            return None
    return None

def run_simulator(log_file_path: str):
    client = redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        decode_responses=True
    )

    if not os.path.exists(log_file_path):
        raise FileNotFoundError(f"Log file not found: {log_file_path}")

    print(f"[*] Starting simulator with Speed Multiplier={Config.SPEED_MULTIPLIER}x, Max Sleep={Config.MAX_SLEEP_SECONDS}s")
    
    previous_timestamp = None

    with open(log_file_path, "r") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            current_timestamp = parse_hdfs_timestamp(line)

            if previous_timestamp and current_timestamp:
                delta_seconds = (current_timestamp - previous_timestamp).total_seconds()
                if delta_seconds > 0:
                    scaled_sleep = delta_seconds / Config.SPEED_MULTIPLIER
                    sleep_time = min(scaled_sleep, Config.MAX_SLEEP_SECONDS)
                    time.sleep(sleep_time)

            previous_timestamp = current_timestamp

            # Push raw log message to Redis Stream
            payload = {
                "raw_log": line,
                "emitted_at": time.time()
            }
            msg_id = client.xadd(Config.REDIS_STREAM_NAME, payload)
            print(f"[Line {line_num}] Pushed to stream {Config.REDIS_STREAM_NAME} (ID: {msg_id})")

    print("[✓] Finished streaming log file.")

if __name__ == "__main__":
    data_path = os.path.join(os.path.dirname(__file__), "data", "HDFS.log")
    run_simulator(data_path)