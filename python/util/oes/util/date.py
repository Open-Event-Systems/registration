"""Date utils."""
from datetime import datetime


def get_now(*, seconds_only: bool = False) -> datetime:
    """Get the current datetime in the system's timezone.

    Args:
        seconds_only: If True, do not include microseconds..
    """
    now = datetime.now().astimezone()
    return now.replace(microsecond=0) if seconds_only else now
