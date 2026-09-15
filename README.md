# Telegram Group Dashboard

Watches multiple Telegram groups, parses structured messages (`Key: Value, Key: Value`)
into per-group SQLite tables, and shows the latest rows on a dashboard.

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

Just one process to start:

```
python server.py
```

(equivalently: `uvicorn server:app --port 8000` — useful if you want `--reload` while
developing)

Open **http://localhost:8000** in a browser. There's no separate bot process to run —
`server.py` checks Telegram for new messages itself: once immediately on startup, every
6 hours automatically after that, and instantly whenever you click the **Refresh** button.
The page also polls a lightweight status endpoint once a minute and reloads its data on
its own if the 6-hourly check found anything new, so you don't have to keep clicking.

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
- **Keeping it running 24/7**: `server.py` needs to stay running for the 6-hourly
  background sync to happen even when nobody's viewing the dashboard. For real
  deployment, run it as a background service (e.g. `systemd`, `pm2`, or a small
  always-on VPS/Railway/Render instance) rather than a terminal window.
- **Sync interval**: controlled by `SYNC_INTERVAL_SECONDS` in `server.py` (currently
  6 hours). Telegram holds unfetched messages for a bot for about 24 hours, so as long
  as the server stays up and checks at least that often, nothing gets missed.
- **Data file**: everything is stored in `data.db` (SQLite) in this folder. You can open
  it directly with any SQLite browser, or export a table to CSV/Excel any time with:
  `sqlite3 data.db -header -csv "SELECT * FROM orders;" > orders.csv`
