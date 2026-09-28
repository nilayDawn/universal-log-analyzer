import sys
import os
import redis
from concurrent.futures import ThreadPoolExecutor

# 1. Append the project root to load standard modules
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_ROOT)
from LogAnalyzer.config import Config

# 2. Append the rca-agent/src folder directly to bypass the hyphen syntax issue
RCA_AGENT_SRC = os.path.join(PROJECT_ROOT, "rca-agent", "src")
sys.path.append(RCA_AGENT_SRC)

# 3. Import AlertOrchestrator directly from the folder search path
from alert_handler import AlertOrchestrator

from detectors.novelty import NoveltyDetector
from detectors.volume import VolumeDetector
from detectors.entity import EntityDetector
from detectors.sequence import SequenceDetector
from fusion.signal_fusion import SignalFusion

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
    
    # CRITICAL FIX 1: Set breach threshold to match the new normalized 0.0 - 1.0 range
    fusion_engine = SignalFusion(breach_threshold=0.65)
    orchestrator = AlertOrchestrator()
    
    # Create a non-blocking thread pool for slow network tasks (LLM calls)
    executor = ThreadPoolExecutor(max_workers=3) 

    # Warm-up counter
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
                # Array to hold message IDs for bulk acknowledgment
                ids_to_ack = []
                
                for msg_id, payload in msg_list:
                    processed_logs += 1
                    ids_to_ack.append(msg_id)
                    
                    # Ensure string format for cluster IDs
                    cluster_id = str(payload.get("cluster_id"))
                    emitted_at = float(payload.get("emitted_at", 0))
                    raw_log = payload.get("raw_log", "")
                    
                    # 1. Run Detectors
                    novelty_score = novelty_detector.calculate_score(cluster_id)
                    volume_score = volume_detector.calculate_score(emitted_at)
                    entity_score, block_id = entity_detector.calculate_score(raw_log)
                    sequence_score = sequence_detector.calculate_score(block_id, cluster_id)
                    
                    # 2. Fuse Signals
                    incident_score, is_breached = fusion_engine.evaluate(
                        novelty_score, volume_score, entity_score, sequence_score
                    )
                    
                    # 3. Handle Alerts
                    if is_breached and processed_logs > WARMUP_LOG_COUNT:
                        print(f"\n[CRITICAL INCIDENT] Score: {incident_score:.2f} | Block ID: {block_id}")
                        print(f"   ↳ Novelty: {novelty_score:.2f} | Sequence: {sequence_score:.2f} | Entity: {entity_score:.2f} | Volume: {volume_score:.2f}")

                        # FIX: Push the slow database query + LLM call to a background thread!
                        # This allows the loop to instantly jump to the next log message.
                        executor.submit(orchestrator.process_incident, block_id, emitted_at)
                
                #  Bulk acknowledge the entire batch in one network call
                if ids_to_ack:
                    client.xack(Config.REDIS_PARSED_STREAM_NAME, GROUP_NAME, *ids_to_ack)
                    
    except KeyboardInterrupt:
        print("\n[*] Shutting down ML worker.")

if __name__ == "__main__":
    run_ml_pipeline()
