def aggregate_scores(row):
    sem_anom = row["semantic_pred"] == -1
    beh_anom = row["behavioral_pred"] == -1
    status = str(row["status"]).upper().strip()
    details = str(row["details"]).lower()
    velocity = row.get("velocity_10s", 0)

    # 1. False Positive Suppression (Normal traffic spikes that return success)
    if beh_anom and not sem_anom and status in ["200", "SUCCESS", "OK"]:
        if velocity < 30:
            return "Normal"

    # 2. Heuristic Exploit Signature Detection (High Risk override)
    exploit_keywords = [
        "union select", "select * from", "drop table", "admin' or", "' or '1'='1",
        "/etc/passwd", "../", "..\\", "cmd.exe", "bin/sh", "bin/bash",
        "brute force", "malicious", "sql injection", "rce", "directory traversal"
    ]
    has_exploit_sig = any(kw in details for kw in exploit_keywords)

    # 3. High Risk Classification
    # - Both semantic and behavioral models flag it.
    if sem_anom and beh_anom:
        return "High Risk"
    
    # - Explicit exploit signature found.
    if has_exploit_sig:
        return "High Risk"

    # - Semantic anomaly combined with system failure / unauthorized access (e.g., successful exploit/incident indicator).
    if sem_anom and status not in ["200", "SUCCESS", "OK", "N/A"]:
        return "High Risk"

    # - Critical brute force or Denial of Service indicator (massive velocity + failure/unauthorized status).
    if velocity >= 40 and status not in ["200", "SUCCESS", "OK"]:
        return "High Risk"

    # 4. Medium Risk Classification
    # - Either model flags it.
    if sem_anom or beh_anom:
        return "Medium Risk"
        
    # - Elevated traffic spike with non-success status.
    if velocity >= 15 and status not in ["200", "SUCCESS", "OK"]:
        return "Medium Risk"

    return "Normal"
