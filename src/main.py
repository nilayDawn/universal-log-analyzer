import re
from fastapi import FastAPI, Request
import uvicorn 
from config.db import save_logs, init_db
from utils.regex_parser import PATTERNS



app = FastAPI(title= "Log Analyzer Processing Hub", version="0.0.1")
init_db()

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Welcome to the Log Analyzer Processing Hub!"}

@app.post("/api/logs")
async def receive_logs(request: Request):
    payload = await request.json()
    log_line = ""
    #Log can be send in one line or at batch of lines. We will handle both cases.
    if isinstance(payload, list):
        for log in payload:
            log_line = log.get("message", "Unknown payload")
    else:
        log_line = payload.get("message", "Unknown payload")

    #classification logic
    for log_type, pattern in PATTERNS.items():
        match = re.match(pattern, log_line)
        if match:
            data = match.groupdict()

            timestamp = data.get("ts", "N/A")
            status = data.get("status", "N/A")
            details = str(data)

            save_logs(timestamp, log_type, details, status)

            print(f"Stored {log_type} log.")
            break
    
    return{
        "status": "success",
        "message": "Log(s) received and processed."
    }

if __name__ == "__main__":
    print("🚀 Starting Log Analyzer Processing Hub on http://0.0.0.0:8000/")
    uvicorn.run(app, host="0.0.0.0", port=8000)