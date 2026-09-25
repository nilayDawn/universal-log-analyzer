class NoveltyDetector:
    def __init__(self):
        self.template_counts = {}
        self.decay_threshold = 10 # After 10 occurrences, score is 0

    def calculate_score(self, cluster_id: str) -> float:
        """Returns an anomaly score from 0.0 to 1.0 based on occurrence frequency."""
        count = self.template_counts.get(cluster_id, 0) + 1
        self.template_counts[cluster_id] = count
        
        if count <= self.decay_threshold:
            # Score decays inversely: 1.0 -> 0.5 -> 0.33 -> 0.25...
            return 1.0 / count
        
        return 0.0