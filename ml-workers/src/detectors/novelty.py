# What it does: It looks for log patterns or errors that the system has never seen before.
# Simple Example: If your HDFS cluster usually prints "Received block" and suddenly prints "Disk failure on sector 4", the novelty detector flags it immediately.
# Why it matters: It catches brand-new bugs, zero-day security attacks, or critical hardware failures the moment they happen for the first time.

class NoveltyDetector:
    def __init__(self, decay_threshold=10):
        self.template_counts = {}
        self.decay_threshold = decay_threshold

    def calculate_score(self, cluster_id: str) -> float:
        """Returns an anomaly score from 0.0 to 1.0 based on occurrence frequency."""
        # 1. Get current count BEFORE updating it
        current_count = self.template_counts.get(cluster_id, 0)
        
        # 2. Update the tracker state
        self.template_counts[cluster_id] = current_count + 1
        
        # 3. Calculate score based on previous familiarity
        if current_count == 0:
            return 1.0  # Absolutely brand new!
            
        if current_count < self.decay_threshold:
            # Smoothly decay score: 1st repeat = 0.9, 2nd repeat = 0.8 ... 9th repeat = 0.1
            return 1.0 - (current_count / self.decay_threshold)
            
        return 0.0  # Fully normalized/common template