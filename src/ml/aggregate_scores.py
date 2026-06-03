def aggregate_scores(row):
    sem_anom = row['semantic_pred'] == -1
    beh_anom = row['behavioral_pred'] == -1
    
    # OVERRIDE: Suppress behavioral false positives on successful requests
    if beh_anom and not sem_anom:
        # If it's a standard success...
        if row['status'] in ['200', 'SUCCESS']:
            # ...only flag it if the traffic spike is massive (e.g., > 30 requests in 10s)
            # Otherwise, suppress the ML alert and force it back to Normal.
            if row['velocity_10s'] < 30:
                return "Normal"

    # Standard Aggregation Matrix
    if sem_anom and beh_anom:
        return "High Risk"
    elif sem_anom or beh_anom:
        return "Medium Risk"
    else:
        return "Normal"