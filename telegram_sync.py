import logging
from datetime import datetime, timezone

from telegram import Bot

from config import BOT_TOKEN, GROUPS, all_columns
from db import get_connection, ensure_table, insert_row, get_sync_state, set_sync_state
from parser import parse_message

log = logging.getLogger("telegram_sync")
bot = Bot(token=BOT_TOKEN)


async def sync_messages():
    """One-shot check: pull any new Telegram messages since the last sync and save the matching ones."""
    conn = get_connection()
    try:
        state = get_sync_state(conn)
        offset = int(state["offset"]) if "offset" in state else None

        updates = await bot.get_updates(offset=offset, timeout=0)

        for update in updates:
            offset = update.update_id + 1
            message = update.message
            if not message or not message.text:
                continue

            group = GROUPS.get(message.chat_id)
            if not group:
                continue

            fields = parse_message(message.text, group["columns"], group.get("separator", ","))
            if not fields:
                continue

            for col_name, formula in group.get("computed", {}).items():
                try:
                    fields[col_name] = formula(fields)
                except Exception:
                    log.warning("Could not compute %s for %s: %s", col_name, group["table"], fields)

            sender = message.from_user.username or message.from_user.first_name
            sent_at = message.date.strftime("%Y-%m-%d %H:%M:%S")

            ensure_table(conn, group["table"], all_columns(group))
            insert_row(conn, group["table"], fields, sender, sent_at)
            log.info("Saved to %s: %s (from %s)", group["table"], fields, sender)

        sync_state = {"last_synced_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}
        if offset is not None:
            sync_state["offset"] = offset
        set_sync_state(conn, **sync_state)
    finally:
        conn.close()
