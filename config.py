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


def fmt_num(n):
    """Format a computed number without a trailing .0 for whole numbers."""
    return f"{n:g}"


def fmt_pct(n):
    """Format a computed percentage with exactly 2 decimal places."""
    return f"{n:.2f}"


# Each entry defines one group's table shape.
# "columns" must match the field names people use in their messages,
# e.g. a message "Item: Widget, Price: 20, Customer: Jane" matches
# columns ["item", "price", "customer"].
#
# "computed" (optional): extra columns derived from the parsed fields and
# stored alongside them. Each value is a function that takes the fields
# dict (e.g. {"atta": "2000", "bran": "70"}) and returns the string to store.
# Add as many as you need -- every one becomes its own column automatically.
GROUPS = {
    #Testgroup
    -5363407284: {
        "table": "test",
        "columns": ["item", "price", "customer"],
    },
    -5599309160: {
        "table": "Chakki Percentage",
        "columns": ["atta", "bran"],
        "separator": "\n",
        "show_sender": False,
        "computed": {
            "total": lambda f: fmt_num(float(f["atta"]) + float(f["bran"])),
            "atta%": lambda f: fmt_pct(float(f["atta"]) / (float(f["atta"]) + float(f["bran"])) * 100),
            "bran%": lambda f: fmt_pct(float(f["bran"]) / (float(f["atta"]) + float(f["bran"])) * 100),
        },
    },
    # Add more groups here following the same pattern.
}


def all_columns(group):
    """Every column a group's table has: parsed fields plus any computed ones."""
    return group["columns"] + list(group.get("computed", {}).keys())
