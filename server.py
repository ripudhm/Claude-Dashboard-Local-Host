from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import GROUPS
from db import get_connection, ensure_table, fetch_latest

app = FastAPI(title="Telegram Group Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# table -> columns, built once from config so the frontend knows what
# every group's shape is without guessing.
TABLE_LOOKUP = {g["table"]: g["columns"] for g in GROUPS.values()}


@app.get("/api/groups")
def list_groups():
    """Every configured group, its table name, and its columns."""
    return [
        {"table": g["table"], "columns": g["columns"]}
        for g in GROUPS.values()
    ]


@app.get("/api/{table}")
def get_latest(table: str, limit: int = 15):
    if table not in TABLE_LOOKUP:
        raise HTTPException(status_code=404, detail="Unknown table")

    conn = get_connection()
    try:
        ensure_table(conn, table, TABLE_LOOKUP[table])
        rows = fetch_latest(conn, table, limit=limit)
    finally:
        conn.close()
    return rows


# Serve the dashboard UI itself at "/"
app.mount("/", StaticFiles(directory="static", html=True), name="static")
