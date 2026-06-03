import sqlite3
import pandas as pd

from src.config.db import  init_db

def load_data():
    init_db()
    conn = sqlite3.connect("data/logs.db")
    df = pd.read_sql_query("SELECT * FROM logs", conn)
    conn.close()
    return df