import os
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
from drain3.file_persistence import FilePersistence

# Ensure state directory exists for persistence
STATE_DIR = os.path.join(os.path.dirname(__file__), "state")
os.makedirs(STATE_DIR, exist_ok=True)
PERSISTENCE_FILE = os.path.join(STATE_DIR, "drain3.bin")

config = TemplateMinerConfig()
config.profiling_enabled = False

# FilePersistence guarantees the model remembers templates across restarts
persistence = FilePersistence(PERSISTENCE_FILE)
template_miner = TemplateMiner(persistence, config=config)

def parse_log(log_line: str) -> dict:
    """Passes a raw log to Drain3 and returns the structured template data."""
    result = template_miner.add_log_message(log_line)
    return result