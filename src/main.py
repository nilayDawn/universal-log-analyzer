from fastapi import FastAPI, Request
import uvicorn 

app = FastAPI(title= "Log Analyzer Processing Hub", version="0.0.1")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Welcome to the Log Analyzer Processing Hub!"}

@app.post("/api/v1/logs")
async def receive_logs(request: Request):
    payload = await request.json()
    
    #Log can be send in one line or at batch of lines. We will handle both cases.
    if isinstance(payload, list):
        for log in payload:
            message = log.get("message", "Unknown payload")
            print(f"[BATCH LOG] Received log: {message.strip()}")
    else:
        message = payload.get("message", "Unknown payload")
        print(f"[SINGLE LOG] Received log: {message.strip()}")
    return{
        "status": "success",
        "message": "Log(s) received and processed."
    }

if __name__ == "__main__":
    print("🚀 Starting Log Analyzer Processing Hub on http://0.0.0.0:8000/")
    uvicorn.run(app, host="0.0.0.0", port=8000)