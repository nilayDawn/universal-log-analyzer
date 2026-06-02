import sqlite3
import requests
import sys

# Default Ollama local endpoint
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3" 

def get_log_by_id(log_id):
    conn = sqlite3.connect("data/logs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT log_type, timestamp, details FROM logs WHERE id = ?", (log_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def analyze_anomaly(log_id):
    log_data = get_log_by_id(log_id)
    if not log_data:
        print(f"❌ Log ID {log_id} not found in database.")
        return

    log_type, timestamp, details = log_data
    
    # The System Prompt configuring the LLM's behavior
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
    
    print(f"🕵️  Sending Log ID {log_id} to Local LLM ({MODEL_NAME})...\n")
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        
        print("==================================================")
        print("💡 LLM ROOT CAUSE ANALYSIS")
        print("==================================================")
        print(result.get("response", "No response provided."))
        print("==================================================\n")
        
    except requests.exceptions.ConnectionError:
        print("❌ Failed to connect to Ollama. Ensure the Ollama app is running in the background.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            target_id = int(sys.argv[1])
            analyze_anomaly(target_id)
        except ValueError:
            print("Please provide a valid numeric Log ID.")
    else:
        print("Usage: python src/llm/detective.py <log_id>")