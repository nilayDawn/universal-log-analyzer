# What it does: It pulls out and tracks specific objects or items hidden inside the text (like Block IDs, IP addresses, or Usernames)
# Simple Example: It scans your logs, ignores the generic text, and isolates the specific entity blk_-78781211 or IP 10.251.73.220.
# Why it matters: It allows you to cross-reference logs. For example, you can trace exactly what happened to one single data block across 5 different servers.

import re
from collections import defaultdict

class EntityDetector:
    def __init__(self):
        self.block_counts = defaultdict(int)
        self.global_avg = 0.0

    def extract_block_id(self, raw_log: str) -> str:
        # HDFS Block IDs typically follow the format blk_ followed by numbers
        match = re.search(r'(blk_-?\d+)', raw_log)
        return match.group(1) if match else "unknown"

    def calculate_score(self, raw_log: str) -> tuple[float, str]:
        block_id = self.extract_block_id(raw_log)
        if block_id == "unknown":
            return 0.0, block_id
            
        self.block_counts[block_id] += 1
        count = self.block_counts[block_id]
        
        # Calculate new global average
        total_blocks = max(len(self.block_counts), 1)
        total_logs = sum(self.block_counts.values())
        self.global_avg = total_logs / total_blocks

        # Flag if this specific block generates >3x the global average (with a minimum baseline)
        if self.global_avg > 5 and count > (self.global_avg * 3):
            score = min((count / (self.global_avg * 3)) - 1.0, 1.0)
            return score, block_id
            
        return 0.0, block_id