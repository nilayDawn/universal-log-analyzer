def aggregate_scores(row):
    # -1 is Anomaly, 1 is Normal in scikit-learn
    sem_anom = row['semantic_pred'] == -1
    beh_anom = row['behavioral_pred'] == -1
    
    if sem_anom and beh_anom:
        return "High Risk"
    elif sem_anom or beh_anom:
        return "Medium Risk"
    else:
        return "Normal"