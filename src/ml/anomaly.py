# Copyright 2026 Nilay Dawn
#
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0


from src.utils.load_data import load_data
from .semantic_detector import run_semantic_detector
from .behavioral_detector import run_behavioral_detector
from .aggregate_scores import aggregate_scores

MIN_BASELINE_LOGS = 25


def run_anomaly_pipeline(min_logs=MIN_BASELINE_LOGS):
    df = load_data()
    if len(df) < min_logs:
        return df, {
            "baseline_ready": False,
            "min_logs": min_logs,
            "total_logs": len(df),
            "high_risk": 0,
            "medium_risk": 0,
            "message": "Waiting for enough logs to build a baseline.",
        }

    df = df.copy()
    df['semantic_pred'] = run_semantic_detector(df)
    df['behavioral_pred'] = run_behavioral_detector(df)

    # risk aggregation
    df['risk_level'] = [
        aggregate_scores(row)
        for _, row in df.iterrows()
    ]
    
    summary = {
        "baseline_ready": True,
        "min_logs": min_logs,
        "total_logs": len(df),
        "high_risk": int((df['risk_level'] == 'High Risk').sum()),
        "medium_risk": int((df['risk_level'] == 'Medium Risk').sum()),
        "message": "Anomaly pipeline completed.",
    }
    return df, summary

def main():
    df, summary = run_anomaly_pipeline(min_logs=50)
    if not summary["baseline_ready"]:
        print("⚠️ Waiting for more logs to train PCA effectively...")
        return
    
    # Filter and Display Results
    risks = df[df['risk_level'] != 'Normal']
    
    print("\n==================================================")
    print("📊 ENSEMBLE ANOMALY DETECTION REPORT")
    print("==================================================")
    
    if risks.empty:
        print("✅ System normal. No anomalies detected.")
    else:
        for _, row in risks.iterrows():
            print(f"\n🚨 [{row['risk_level'].upper()}]")
            print(f"ID: {row['id']} | Type: {row['log_type']} | TS: {row['timestamp']}")
            print(f"Message: {row['details']}")
            
            # Print the specific trigger
            if row['semantic_pred'] == -1:
                print("   -> Trigger: Unusual Semantic Pattern")
            if row['behavioral_pred'] == -1:
                print("   -> Trigger: Unusual Behavioral Metadata")
            
            if row['risk_level'] == 'High Risk':
                print(f"\n High Risk Log ID {row['id']} is ready for root cause analysis via the FastAPI endpoint.")

            
if __name__ == "__main__":
    main()
