# What it does: It monitors the amount or frequency of logs over a specific period.
# Simple Example: If a DataNode usually generates 10 logs per minute, and suddenly it blasts out 50,000 logs in 5 seconds, the volume detector sounds the alarm.
# Why it matters: It flags massive loops, network spam, DDoS attacks, or a broken component screaming error messages into the log file.

from collections import deque

class VolumeDetector:
    def __init__(self, window_seconds: int = 10):
        self.window_seconds = window_seconds
        self.timestamps = deque()
        self.moving_average = 0.0

    def calculate_score(self, current_timestamp: float) -> float:
        # Prevent math errors if historical data or out-of-order logs arrive
        self.timestamps.append(current_timestamp)

        # 1. Clear out logs older than our window window
        cutoff_time = current_timestamp - self.window_seconds
        while self.timestamps and self.timestamps[0] < cutoff_time:
            self.timestamps.popleft()

        current_volume = len(self.timestamps)

        # 2. Warm up phase for the baseline
        if self.moving_average == 0.0:
            self.moving_average = max(current_volume, 1.0)
            return 0.0

        # 3. Calculate anomaly ratio
        ratio = current_volume / self.moving_average

        # 4. Check for anomalies
        if ratio > 1.5:
            # Scale anomaly response up towards 1.0 cleanly
            score = min((ratio - 1.5) / 2.0, 1.0)
            # DO NOT feed extreme spikes into the long-term baseline!
            # Instead, simulate a controlled growth step to prevent contamination
            self.moving_average = (0.99 * self.moving_average) + (0.01 * current_volume)
            return score
            
        # 5. Normal traffic: Update moving average using the standard EMA weight
        self.moving_average = (0.95 * self.moving_average) + (0.05 * current_volume)
        return 0.0
