"""JSON-safe UTC timestamps for APIs (fixes naive SQLite datetimes vs browser parsing)."""

from __future__ import annotations

from datetime import datetime, timezone


def datetime_to_utc_z(value: datetime | None) -> str:
    """
    Emit RFC 3339 instant with Z suffix.

    SQLite / SQLAlchemy often return *naive* datetimes for ``CURRENT_TIMESTAMP`` (UTC wall
    clock). ``isoformat()`` omits offset; browsers then parse as *local* time → wrong
    “5h ago” style drift. We treat naive as UTC and serialize with Z.
    """
    if value is None:
        return ""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    out = value.astimezone(timezone.utc)
    text = out.isoformat(timespec="milliseconds")
    if text.endswith("+00:00"):
        return text[:-6] + "Z"
    return text
