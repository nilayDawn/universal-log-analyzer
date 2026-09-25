from collections import deque

class VolumeDetector:
    def __init__(self, window_seconds: int = 10):
        self.window_seconds = window_seconds
        self.timestamps = deque()
        self.moving_average = 0.0

    def calculate_score(self, current_timestamp: float) -> float:
        self.timestamps.append(current_timestamp)

        # Evict logs that fall outside the sliding window
        while self.timestamps and self.timestamps[0] < current_timestamp - self.window_seconds:
            self.timestamps.popleft()

        current_volume = len(self.timestamps)

        if self.moving_average == 0.0:
            self.moving_average = current_volume
            return 0.0

        # Compare current window volume against the historical baseline
        ratio = current_volume / max(self.moving_average, 1)

        # Update the moving average slowly (Exponential Moving Average)
        self.moving_average = (0.95 * self.moving_average) + (0.05 * current_volume)

        # Flag an anomaly if the current volume is >150% of the normal baseline
        if ratio > 1.5:
            score = (ratio - 1.5) / 2.0
            return min(score, 1.0) # Cap score at 1.0
            
        return 0.0