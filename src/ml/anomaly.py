from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.utils.load_data import load_data
from src.ml.semantic_detector import run_semantic_detector
from src.ml.behavioral_detector import run_behavioral_detector
from src.ml.aggregate_scores import aggregate_scores

def main():
    df = load_data()
    if len(df) < 50:  # Arbitrary threshold for minimum data
        print("⚠️ Waiting for more logs to train PCA effectively...")
        return
        
    # Run Detectors
    df['semantic_pred'] = run_semantic_detector(df)
    df['behavioral_pred'] = run_behavioral_detector(df)

    # # Debug: Print predictions
    # print("\n🔍 Semantic Detector Predictions:")
    # print(df['semantic_pred'].value_counts())
    # print("\n🔍 Behavioral Detector Predictions:")
    # print(df['behavioral_pred'].value_counts())
    
    
    
    # Aggregate
    df['risk_level'] = df.apply(aggregate_scores, axis=1)
    
    # print("\n🔍 Risk Level:")
    # print(df['risk_level'])
    
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

if __name__ == "__main__":
    main()