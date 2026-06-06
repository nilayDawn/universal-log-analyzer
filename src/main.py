# Copyright 2026 Nilay Dawn
#
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0


import re
import os
import json

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import logging

from src.config.db import save_logs, init_db
from src.llm.detective import analyze_anomaly
from src.ml.anomaly import MIN_BASELINE_LOGS, run_anomaly_pipeline
from src.utils.regex_parser import PATTERNS

logger = logging.getLogger(__name__)




logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

app = FastAPI(title= "Log Analyzer Processing Hub", version="0.0.1")
init_db()


allowed_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGINS", "*").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allowed_origins != ["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Welcome to the Log Analyzer Processing Hub!"}


def dataframe_records(df: pd.DataFrame):
    clean_df = df.copy()
    clean_df = clean_df.where(pd.notnull(clean_df), None)
    return json.loads(clean_df.to_json(orient="records", date_format="iso"))

@app.post("/api/logs")
async def receive_logs(request: Request):
    body = await request.body()
    if not body:
        return {
            "status": "success",
            "message": "Log(s) received and processed (empty payload).",
            "saved": 0,
            "unparsed": 0,
        }

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload.",
        )

    # Log can be sent as one line or as a batch of lines.
    logs = payload if isinstance(payload, list) else [payload]

    saved_count = 0
    unparsed_count = 0
    for item in logs:
        log_line = item.get("message", "Unknown payload") if isinstance(item, dict) else str(item)

        # classification logic
        matched = False
        for log_type, pattern in PATTERNS.items():
            if log_type == "UNMATCHED":
                continue
            match = re.fullmatch(pattern, log_line.strip())
            if match:
                data = match.groupdict()
                timestamp = data.get("ts", "N/A")
                status = data.get("status", "N/A")
                details = str(data)

                save_logs(timestamp, log_type, details, status)
                saved_count += 1
                matched = True
                break

        if not matched:
            # Store the raw payload so you can inspect/update parsing rules later.
            save_logs("N/A", "UNMATCHED", log_line[:2000], "N/A")
            unparsed_count += 1

    return {
        "status": "success",
        "message": "Log(s) received and processed.",
        "saved": saved_count,
        "unparsed": unparsed_count,
    }



@app.get("/api/anomalies")
def get_anomalies(min_logs: int = MIN_BASELINE_LOGS):
    df, summary = run_anomaly_pipeline(min_logs=min_logs)
    if not summary["baseline_ready"]:
        return {
            "status": "warming_up",
            "summary": summary,
            "logs": [],
            "risks": [],
        }

    risks = df[df["risk_level"] != "Normal"].sort_values(
        by="timestamp",
        ascending=False,
    )

    return {
        "status": "success",
        "summary": summary,
        "logs": dataframe_records(df),
        "risks": dataframe_records(risks),
    }


@app.post("/api/anomalies/{log_id}/analysis")
def generate_root_cause_analysis(log_id: int):
    analysis = analyze_anomaly(log_id)
    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail=f"Log ID {log_id} was not found or could not be analyzed.",
        )

    return {
        "status": "success",
        "log_id": log_id,
        "analysis": analysis,
    }




if __name__ == "__main__":
    logger.info("🚀 Starting Log Analyzer Processing Hub on http://0.0.0.0:8000/")
    uvicorn.run(app, host="0.0.0.0", port=8000)

