import sqlite3
from config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_table(conn, table, columns):
    """Create the table for a group if it doesn't exist yet."""
    cols_sql = ", ".join(f'"{c}" TEXT' for c in columns)
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS "{table}" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {cols_sql},
            sender TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()


def insert_row(conn, table, fields, sender):
    """Insert one parsed message into its group's table."""
    columns = list(fields.keys()) + ["sender"]
    values = list(fields.values()) + [sender]
    placeholders = ", ".join("?" for _ in columns)
    col_names = ", ".join(f'"{c}"' for c in columns)
    conn.execute(
        f'INSERT INTO "{table}" ({col_names}) VALUES ({placeholders})',
        values,
    )
    conn.commit()


def fetch_latest(conn, table, limit=20):
    """Return the most recent rows for a table, newest first."""
    cur = conn.execute(
        f'SELECT * FROM "{table}" ORDER BY timestamp DESC, id DESC LIMIT ?',
        (limit,),
    )
    return [dict(row) for row in cur.fetchall()]
