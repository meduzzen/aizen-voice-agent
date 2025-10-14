from datetime import datetime


def convert_iso_to_unix(value: str):
    dt = datetime.fromisoformat(value)
    unix_time_ms = int(dt.timestamp() * 1000)
    return unix_time_ms
