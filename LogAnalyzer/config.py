import os

class Config:
    # Redis Configurations
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_STREAM_NAME = "log_stream"

    # Simulator Configurations
    SPEED_MULTIPLIER = int(os.getenv("SPEED_MULTIPLIER", 10))
    MAX_SLEEP_SECONDS = float(os.getenv("MAX_SLEEP_SECONDS", 1.5)) # Cap for Auto-Skip mechanism

    # Storage Configurations
    SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "logs_wal.db")