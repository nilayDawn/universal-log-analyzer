import sys
import os
import redis

from detectors.novelty import NoveltyDetector
from detectors.volume import VolumeDetector
from detectors.entity import EntityDetector
from detectors.sequence import SequenceDetector
from fusion.signal_fusion import SignalFusion

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

    # Initialize Phase 3 Components
    novelty_detector = NoveltyDetector()
    volume_detector = VolumeDetector(window_seconds=10)
    entity_detector = EntityDetector()
    sequence_detector = SequenceDetector()
    fusion_engine = SignalFusion(breach_threshold=1.75) # Set critical alert threshold

    # Add a warm-up counter
    WARMUP_LOG_COUNT = 3000 
    processed_logs = 0

    print(f"[*] ML Worker active. Listening to '{Config.REDIS_PARSED_STREAM_NAME}'...")
    print(f"[*] Silently baselining the first {WARMUP_LOG_COUNT} logs...")

    try:
        while True:
            messages = client.xreadgroup(
                GROUP_NAME, CONSUMER_NAME, {Config.REDIS_PARSED_STREAM_NAME: ">"}, count=50, block=2000
            )
            
            if not messages:
                continue
                
            for stream, msg_list in messages:
                for msg_id, payload in msg_list:
                    processed_logs += 1
                    
                    cluster_id = payload.get("cluster_id")
                    emitted_at = float(payload.get("emitted_at", 0))
                    raw_log = payload.get("raw_log", "")
                    
                    # 1. Run Detectors (Learning happens here)
                    novelty_score = novelty_detector.calculate_score(cluster_id)
                    volume_score = volume_detector.calculate_score(emitted_at)
                    entity_score, block_id = entity_detector.calculate_score(raw_log)
                    sequence_score = sequence_detector.calculate_score(block_id, cluster_id)
                    
                    # 2. Fuse Signals
                    incident_score, is_breached = fusion_engine.evaluate(
                        novelty_score, volume_score, entity_score, sequence_score
                    )
                    
                    # 3. Only trigger alerts AFTER the warm-up period
                    if is_breached and processed_logs > WARMUP_LOG_COUNT:
                        print(f"\n[CRITICAL INCIDENT] Score: {incident_score:.2f} | Block ID: {block_id}")
                        print(f"   ↳ Novelty: {novelty_score:.2f} | Sequence: {sequence_score:.2f} | Entity: {entity_score:.2f} | Volume: {volume_score:.2f}")
                    
                    client.xack(Config.REDIS_PARSED_STREAM_NAME, GROUP_NAME, msg_id)
                    
    except KeyboardInterrupt:
        print("\n[*] Shutting down ML worker.")

if __name__ == "__main__":
    run_ml_pipeline()