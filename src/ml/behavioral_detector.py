import pandas as pd
from sklearn.ensemble import IsolationForest

def run_behavioral_detector(df):
    print("⏳ Running Detector 2: Behavioral Pipeline (Metadata + Velocity)...")

    # 1. Feature extraction
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['invalid_timestamp'] = df['timestamp'].isna().astype(int)
    df['hour'] = df['timestamp'].dt.hour.fillna(-1).astype(int)

    # 2. MAP BEHAVIORAL FREQUENCY (VELOCITY)
    valid_mask = df['timestamp'].notna()
    valid_df = df[valid_mask].copy()
  
    # Sort chronologically and explicitly set 'id' as the index
    valid_df = valid_df.sort_values(['timestamp', 'id']).set_index('id')
    
    # Calculate velocity
    velocity = valid_df.groupby('log_type').rolling('10s', on='timestamp')['hour'].count()
    
    # Drop the 'log_type' group label, leaving a Series where the index is the unique 'id'
    velocity_series = velocity.reset_index(level=0, drop=True)
    
  
 
    # Strips out any duplicate indices caused by dirty SQLite data or Pandas bugs,
    # ensuring the .map() function never crashes.
    
    velocity_series = velocity_series[~velocity_series.index.duplicated(keep='last')]
    
    # Step E: Map the velocities back to the main DataFrame safely!
    df['velocity_10s'] = df['id'].map(velocity_series).fillna(0)

    # 3. Encode categorical features (One-Hot Encoding)
    ohe_features = pd.get_dummies(df[['log_type', 'status']], drop_first=False).astype(int)
    num_features = df[['hour', 'invalid_timestamp', 'velocity_10s']]
    
    # 4. Build feature matrix
    features = pd.concat([num_features, ohe_features], axis=1)
    features = features.fillna(0)

    # 5. Isolation Forest
    iso_forest = IsolationForest(contamination=0.02, random_state=42)
    return iso_forest.fit_predict(features)