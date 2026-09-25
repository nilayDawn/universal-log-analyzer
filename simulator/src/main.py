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
            return datetime.strptime(date_str, TIMESTAMP_FORMAT)        # '081109', '203615' ---> 2008-11-09 20:36:15
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
                delta_seconds = (current_timestamp - previous_timestamp).total_seconds()    # 2008-11-09 20:38:07 - 2008-11-09 20:36:15 = 112.0 seconds
                if delta_seconds > 0:
                    scaled_sleep = delta_seconds / Config.SPEED_MULTIPLIER                   # 112.0 / 10 = 11.2 seconds
                    sleep_time = min(scaled_sleep, Config.MAX_SLEEP_SECONDS)                 # 11.2 seconds > 1.5 seconds, so sleep_time = 1.5 seconds
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
    data_path = os.path.join(os.path.dirname(__file__), "data", "HDFS_2k.log")
    run_simulator(data_path)    

# sample op:
# [Line 25] Pushed to stream log_stream (ID: 1790356210293-0)
# [Line 26] Pushed to stream log_stream (ID: 1790356210597-0)
# [Line 27] Pushed to stream log_stream (ID: 1790356211100-0)
# [Line 28] Pushed to stream log_stream (ID: 1790356212604-0)
# [Line 29] Pushed to stream log_stream (ID: 1790356214109-0)