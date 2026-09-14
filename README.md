# Telegram Group Dashboard

Watches multiple Telegram groups, parses structured messages (`Key: Value, Key: Value`)
into per-group SQLite tables, and shows the latest rows on a live dashboard.

## 1. Install dependencies

```
pip install -r requirements.txt --break-system-packages
```

## 2. Create your bot

1. Message [@BotFather](https://t.me/botfather) on Telegram, send `/newbot`, follow the
   prompts, and copy the token it gives you.
2. Still talking to BotFather: `/setprivacy` → select your bot → **Disable**.
   This lets the bot see every message in a group, not just commands directed at it.
   (If you already added the bot to a group before doing this, remove it and re-add it.)
3. Add the bot to each group you want to track.

## 3. Configure your groups

Open `config.py`:
- Paste your token into `BOT_TOKEN`.
- For each group, add an entry to `GROUPS` with the table name and the column
  names people will use in their messages.

To find a group's `chat_id`:
1. Add the bot to the group and send any message.
2. Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser.
3. Find `"chat":{"id": -100..., ...}` in the response — group IDs are negative.

## 4. Run it

In one terminal, start the bot listener (this is what saves incoming messages):

```
python bot.py
```

In another terminal, start the dashboard server:

```
uvicorn server:app --reload --port 8000
```

Open **http://localhost:8000** in a browser. It auto-refreshes every 10 seconds
and shows the most recent 15 messages per group.

## Message format

People in each group type messages like:

```
Item: Widget, Price: 20, Customer: Jane
```

The keys must match the `columns` you set for that group in `config.py` (case-insensitive).
Messages that don't include all the expected fields are ignored — so normal chit-chat
in the group won't clutter your data.

## Notes on scaling this up

- **More groups**: just add more entries to `GROUPS` — no other code changes needed.
- **Keeping the bot running 24/7**: `python bot.py` needs to stay running to keep
  polling Telegram. For real deployment, run it as a background service (e.g. `systemd`,
  `pm2`, or a small always-on VPS/Railway/Render instance) rather than a terminal window.
- **Data file**: everything is stored in `data.db` (SQLite) in this folder. You can open
  it directly with any SQLite browser, or export a table to CSV/Excel any time with:
  `sqlite3 data.db -header -csv "SELECT * FROM orders;" > orders.csv`
