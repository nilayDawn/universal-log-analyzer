import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

class Config:
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PARSED_STREAM_NAME = "parsed_stream"

    SPEED_MULTIPLIER = int(os.getenv("SPEED_MULTIPLIER", 10))
    MAX_SLEEP_SECONDS = float(os.getenv("MAX_SLEEP_SECONDS", 1.5))

    SQLITE_DB_PATH = os.getenv(
        "SQLITE_DB_PATH",
        str(PROJECT_ROOT / "data" / "logs_wal.db")
    )

    REDIS_STREAM_NAME = os.getenv("REDIS_STREAM_NAME", "log_stream")