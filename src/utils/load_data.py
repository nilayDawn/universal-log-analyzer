import pandas as pd

from src.config.db import init_db, _connect

def load_data(limit: int = 1000):
    init_db()
    conn = _connect()
    # Query latest logs first, then reverse to chronological order
    df = pd.read_sql_query(f"SELECT * FROM logs ORDER BY id DESC LIMIT {limit}", conn)
    conn.close()
    if not df.empty:
        df = df.iloc[::-1].reset_index(drop=True)
    return df