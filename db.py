import sqlite3
from config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_table(conn, table, columns):
    """Create the table for a group if it doesn't exist yet, and add any
    newly configured columns to a table that already exists."""
    cols_sql = ", ".join(f'"{c}" TEXT' for c in columns)
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS "{table}" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {cols_sql},
            sender TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    existing = {row["name"] for row in conn.execute(f'PRAGMA table_info("{table}")')}
    for c in columns:
        if c not in existing:
            conn.execute(f'ALTER TABLE "{table}" ADD COLUMN "{c}" TEXT')

    conn.commit()


def insert_row(conn, table, fields, sender, sent_at):
    """Insert one parsed message into its group's table."""
    columns = list(fields.keys()) + ["sender", "timestamp"]
    values = list(fields.values()) + [sender, sent_at]
    placeholders = ", ".join("?" for _ in columns)
    col_names = ", ".join(f'"{c}"' for c in columns)
    conn.execute(
        f'INSERT INTO "{table}" ({col_names}) VALUES ({placeholders})',
        values,
    )
    conn.commit()


def fetch_latest(conn, table, limit=20):
    """Return the most recent rows for a table, oldest first (so the newest ends up last)."""
    cur = conn.execute(
        f'SELECT * FROM "{table}" ORDER BY timestamp DESC, id DESC LIMIT ?',
        (limit,),
    )
    rows = [dict(row) for row in cur.fetchall()]
    rows.reverse()
    return rows


def get_sync_state(conn):
    """Return the persisted Telegram sync state (offset, last_synced_at) as a dict."""
    conn.execute("CREATE TABLE IF NOT EXISTS _sync_state (key TEXT PRIMARY KEY, value TEXT)")
    rows = conn.execute("SELECT key, value FROM _sync_state").fetchall()
    return {row["key"]: row["value"] for row in rows}


def set_sync_state(conn, **kwargs):
    """Persist one or more sync-state values, e.g. set_sync_state(conn, offset=5, last_synced_at=...)."""
    conn.execute("CREATE TABLE IF NOT EXISTS _sync_state (key TEXT PRIMARY KEY, value TEXT)")
    for key, value in kwargs.items():
        conn.execute(
            """
            INSERT INTO _sync_state (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, str(value)),
        )
    conn.commit()
