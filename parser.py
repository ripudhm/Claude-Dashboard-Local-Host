def parse_message(text, expected_columns):
    """
    Parses messages formatted like:
        "Item: Widget, Price: 20, Customer: Jane"
    into {"item": "Widget", "price": "20", "customer": "Jane"}.

    Returns None if the message doesn't contain all expected fields
    (so unrelated chit-chat in the group is safely ignored).
    """
    if not text:
        return None

    fields = {}
    for part in text.split(","):
        if ":" not in part:
            continue
        key, val = part.split(":", 1)
        key = key.strip().lower()
        val = val.strip()
        if key in expected_columns and val:
            fields[key] = val

    if set(fields.keys()) == set(expected_columns):
        return fields
    return None
