import sys
import os
import redis
from detectors.novelty import NoveltyDetector
from detectors.volume import VolumeDetector

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from LogAnalyzer.config import Config

GROUP_NAME = "ml_group"
CONSUMER_NAME = "ml_worker_1"

def run_ml_pipeline():
    client = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)
    
    try:
        client.xgroup_create(Config.REDIS_PARSED_STREAM_NAME, GROUP_NAME, id="0", mkstream=True)
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise

    novelty_detector = NoveltyDetector()
    volume_detector = VolumeDetector(window_seconds=10)
    print(f"[*] ML Worker listening to '{Config.REDIS_PARSED_STREAM_NAME}'...")

    try:
        while True:
            messages = client.xreadgroup(
                GROUP_NAME, CONSUMER_NAME, {Config.REDIS_PARSED_STREAM_NAME: ">"}, count=50, block=2000
            )
            
            if not messages:
                continue
                
            for stream, msg_list in messages:
                for msg_id, payload in msg_list:
                    cluster_id = payload.get("cluster_id")
                    emitted_at = float(payload.get("emitted_at", 0))
                    
                    # 1. Run Detectors
                    novelty_score = novelty_detector.calculate_score(cluster_id)
                    volume_score = volume_detector.calculate_score(emitted_at)
                    
                    # 2. Print high-scoring anomalies for testing
                    if novelty_score > 0.2:
                        print(f"[Novelty Spike] Template {cluster_id} | Score: {novelty_score:.2f}")
                    if volume_score > 0.5:
                        print(f"[Volume Spike] Sudden burst detected | Score: {volume_score:.2f}")
                    
                    client.xack(Config.REDIS_PARSED_STREAM_NAME, GROUP_NAME, msg_id)
                    
    except KeyboardInterrupt:
        print("\n[*] Shutting down ML worker.")

if __name__ == "__main__":
    run_ml_pipeline()