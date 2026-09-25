# Drain3 is a smart, open-source log parser that automatically turns messy, chaotic raw log messages into structured data templates in real time

import os
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
from drain3.file_persistence import FilePersistence

# Ensure state directory exists for persistence. ------>   to save its memory so it doesn't forget what it learned if the script restarts or crashes
STATE_DIR = os.path.join(os.path.dirname(__file__), "state")
os.makedirs(STATE_DIR, exist_ok=True)
PERSISTENCE_FILE = os.path.join(STATE_DIR, "drain3.bin")

config = TemplateMinerConfig()
config.load(os.path.join(os.path.dirname(__file__), "drain3.ini"))

# FilePersistence guarantees the model remembers templates across restarts
persistence = FilePersistence(PERSISTENCE_FILE)
template_miner = TemplateMiner(persistence, config=config)

def parse_log(log_line: str) -> dict:
    """Passes a raw log to Drain3 and returns the structured template data."""
    result = template_miner.add_log_message(log_line)
    return result


# "081109 203615 148 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_38865049064139660 terminating" ---->   {'change_type': 'cluster_created',
#  'cluster_id': 1, 
#  'cluster_size': 1, 
#  'template_mined': '081109 203615 148 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_38865049064139660 terminating', 'cluster_count': 1}

# "081109 203807 222 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-6952295868487656571 terminating" ---->   {'change_type': 'cluster_created', 
# 'cluster_id': 1, 
# 'cluster_size': 1, 
# 'template_mined': '081109 203807 222 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-6952295868487656571 terminating',
#  'cluster_count': 1}