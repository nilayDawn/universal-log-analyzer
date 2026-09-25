class SignalFusion:
    def __init__(self, breach_threshold: float = 0.6):
        # Scale the breach threshold relative to a clean 0.0 to 1.0 range
        self.breach_threshold = breach_threshold
        
        # Define clean, normalized relative weights (Sum up to 1.0)
        self.w_novelty = 0.30
        self.w_sequence = 0.40
        self.w_volume = 0.15
        self.w_entity = 0.15

    def evaluate(self, novelty: float, volume: float, entity: float, sequence: float) -> tuple[float, bool]:
        # 1. Calculate a normalized base score (Cleanly bound between 0.0 and 1.0)
        base_score = (
            (novelty * self.w_novelty) + 
            (sequence * self.w_sequence) + 
            (volume * self.w_volume) + 
            (entity * self.w_entity)
        )
        
        # 2. Add a Correlation Boost
        # If an anomaly shows up in BOTH structural (sequence/novelty) AND operational metrics,
        # it is highly likely to be a genuine outage or attack.
        structural_signal = max(novelty, sequence)
        operational_signal = max(volume, entity)
        
        # Amplify the score if structural anomalies correlate with operational anomalies
        boost = 0.20 * (structural_signal * operational_signal)
        
        # Final incident score, clamped strictly between 0.0 and 1.0
        incident_score = min(1.0, base_score + boost)
        
        is_breached = incident_score >= self.breach_threshold
        return incident_score, is_breached
