import asyncio
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import GROUPS
from db import get_connection, ensure_table, fetch_latest, get_sync_state
from telegram_sync import sync_messages

log = logging.getLogger("server")
SYNC_INTERVAL_SECONDS = 6 * 60 * 60

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


@app.post("/api/sync")
async def manual_sync():
    """Triggered by the dashboard's Refresh button -- checks Telegram immediately."""
    await sync_messages()
    return {"status": "ok"}


@app.get("/api/status")
def sync_status():
    conn = get_connection()
    try:
        state = get_sync_state(conn)
    finally:
        conn.close()
    return {"last_synced_at": state.get("last_synced_at")}


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


@app.on_event("startup")
async def start_background_sync():
    await sync_messages()

    async def sync_loop():
        while True:
            await asyncio.sleep(SYNC_INTERVAL_SECONDS)
            try:
                await sync_messages()
            except Exception:
                log.exception("Scheduled Telegram sync failed")

    asyncio.create_task(sync_loop())


# Serve the dashboard UI itself at "/"
app.mount("/", StaticFiles(directory="static", html=True), name="static")
