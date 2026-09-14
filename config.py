# ----------------------------------------------------------------------
# Fill this in with your bot token and your group definitions.
#
# HOW TO FIND A GROUP'S chat_id:
#   1. Add your bot to the group.
#   2. Send any message in the group.
#   3. Visit: https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
#   4. Look for "chat":{"id": -1001234567890, ...} in the response.
#      Group chat_ids are negative numbers.
# ----------------------------------------------------------------------

from secrets import BOT_TOKEN

DB_PATH = "data.db"

# Each entry defines one group's table shape.
# "columns" must match the field names people use in their messages,
# e.g. a message "Item: Widget, Price: 20, Customer: Jane" matches
# columns ["item", "price", "customer"].
GROUPS = {
    #Testgroup
    -5363407284: {
        "table": "test",
        "columns": ["item", "price", "customer"],
    },
    -1002222222222: {
        "table": "incidents",
        "columns": ["location", "severity", "reporter"],
    },
    # Add more groups here following the same pattern.
}
