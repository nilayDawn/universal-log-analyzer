import logging
import os
import sys

import requests
from dotenv import load_dotenv

from src.config.db import get_log_by_id

load_dotenv()

logger = logging.getLogger(__name__)

# Default Ollama local endpoint. Docker overrides OLLAMA_URL with the service name.
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate").strip().strip('"')
MODEL_NAME = os.getenv("MODEL_NAME", "llama3:latest").strip().strip('"')


def analyze_anomaly(log_id: int):
    log_data = get_log_by_id(log_id)
    if not log_data:
        logger.warning("Log ID %s not found in database.", log_id)
        return None

    log_type, timestamp, details = log_data

    prompt = f"""
You are an expert System Administrator and Cybersecurity Analyst.
Our machine learning anomaly detection ensemble has flagged the following log as a HIGH RISK event.

Log Type: {log_type}
Timestamp: {timestamp}
Raw Message: {details}

Please provide:
1. Root Cause: A brief, technical explanation of what likely caused this anomaly.
2. Mitigation: A recommended immediate action to investigate or secure the system.

Keep your response highly technical, concise, and format it with clear headers. Do not use filler words.
"""

    logger.info("Sending log_id=%s to Local LLM model=%s", log_id, MODEL_NAME)

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 150,
            "temperature": 0.2
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "No response provided.")
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to Ollama at %s", OLLAMA_URL)
        return None
    except Exception:
        logger.exception("Error occurred while analyzing anomaly (log_id=%s)", log_id)
        return None


if __name__ == "__main__":
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

    if len(sys.argv) > 1:
        try:
            target_id = int(sys.argv[1])
            analyze_anomaly(target_id)
        except ValueError:
            print("Please provide a valid numeric Log ID.")
    else:
        print("Usage: python src/llm/detective.py <log_id>")

