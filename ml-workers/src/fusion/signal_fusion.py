class SignalFusion:
    def __init__(self, breach_threshold=1.5):
        self.breach_threshold = breach_threshold

    def evaluate(self, novelty: float, volume: float, entity: float, sequence: float) -> tuple[float, bool]:
        # Sequence and Novelty receive higher weights as they directly indicate structural breaks
        incident_score = (novelty * 1.0) + (sequence * 1.5) + (volume * 0.5) + (entity * 0.5)
        
        is_breached = incident_score >= self.breach_threshold
        return incident_score, is_breached