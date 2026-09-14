import sqlite3
import pandas as pd

conn = sqlite3.connect("data.db")
tables = ["test"]  # your table names

with pd.ExcelWriter("export.xlsx") as writer:
    for table in tables:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        df.to_excel(writer, sheet_name=table, index=False)

conn.close()