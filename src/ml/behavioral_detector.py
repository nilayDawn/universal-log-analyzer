import pandas as pd
from sklearn.ensemble import IsolationForest

import logging

logger = logging.getLogger(__name__)


def run_behavioral_detector(df):
    logger.info("Running Detector 2: Behavioral Pipeline (Metadata + Velocity)...")


    # 1. Feature extraction
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['invalid_timestamp'] = df['timestamp'].isna().astype(int)
    df['hour'] = df['timestamp'].dt.hour.fillna(-1).astype(int)

    # 2. MAP BEHAVIORAL FREQUENCY (VELOCITY)
    valid_mask = df['timestamp'].notna()
    valid_df = df[valid_mask].copy()
  
    # Sort by group and timestamp to ensure alignment with rolling output
    valid_df = valid_df.sort_values(['log_type', 'timestamp'])
    
    # Calculate velocity using a DatetimeIndex
    valid_df_indexed = valid_df.set_index('timestamp')
    velocity = valid_df_indexed.groupby('log_type')['hour'].rolling('10s').count()
    
    # Assign rolling counts back to sorted valid_df
    valid_df['velocity_10s'] = velocity.values
    
    # Map the velocities back to the main DataFrame via ID
    velocity_map = dict(zip(valid_df['id'], valid_df['velocity_10s']))
    df['velocity_10s'] = df['id'].map(velocity_map).fillna(0)

    # 3. Encode categorical features (One-Hot Encoding)
    ohe_features = pd.get_dummies(df[['log_type', 'status']], drop_first=False).astype(int)
    num_features = df[['hour', 'invalid_timestamp', 'velocity_10s']]
    
    # 4. Build feature matrix
    features = pd.concat([num_features, ohe_features], axis=1)
    features = features.fillna(0)

    # 5. Isolation Forest
    iso_forest = IsolationForest(contamination=0.02, random_state=42)
    return iso_forest.fit_predict(features)