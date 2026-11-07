"""Month buckets from normalized record dates, never legacy display text."""

from datetime import date
import re


def recorded_month(record):
    """Keep full-day and month-only precision; omit years and invalid dates."""
    value = record.get("date_enacted_iso")
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"(\d{4})-(\d{2})(?:-(\d{2}))?", value)
    if not match:
        return None
    year, month, day = match.groups()
    try:
        date(int(year), int(month), int(day or 1))
    except ValueError:
        return None
    return value[:7]
