import pandas as pd

from src.config.db import init_db, _connect

def load_data():
    init_db()
    conn = _connect()
    df = pd.read_sql_query("SELECT * FROM logs", conn)
    conn.close()
    return df