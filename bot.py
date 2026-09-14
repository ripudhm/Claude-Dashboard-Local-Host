import logging
from telegram.ext import Application, MessageHandler, filters

from config import BOT_TOKEN, GROUPS
from db import get_connection, ensure_table, insert_row
from parser import parse_message

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("bot")


async def handle_message(update, context):
    message = update.message
    if not message:
        return

    chat_id = message.chat_id
    group = GROUPS.get(chat_id)
    if not group:
        # Bot is in a chat we haven't configured -- ignore.
        return

    fields = parse_message(message.text, group["columns"])
    if not fields:
        # Didn't match this group's template -- ignore (e.g. chit-chat).
        return

    sender = message.from_user.username or message.from_user.first_name

    conn = get_connection()
    try:
        ensure_table(conn, group["table"], group["columns"])
        insert_row(conn, group["table"], fields, sender)
        log.info("Saved to %s: %s (from %s)", group["table"], fields, sender)
    finally:
        conn.close()


def main():
    if BOT_TOKEN == "PUT_YOUR_BOT_TOKEN_HERE":
        raise SystemExit("Set BOT_TOKEN in config.py before running the bot.")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    log.info("Bot starting, listening for messages...")
    app.run_polling()


if __name__ == "__main__":
    main()
