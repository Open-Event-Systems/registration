"""Test/filter functions."""

__all__ = [
    "age_filter",
    "date_filter",
    "datetime_filter",
    "today_func",
    "now_func",
]

from datetime import date, datetime, timezone


def age_filter(value: object, current_date: object = None) -> int:
    """Return the age in years given a birthdate.

    Args:
        value: The birthdate, as a :obj:`date` or date string.
        current_date: Today's date, as a :obj:`date` or date string. Defaults to today.

    Returns:
        The age in years.
    """
    value = date_filter(value)
    current_date = date_filter(today_func() if current_date is None else current_date)

    cur_md = (current_date.month, current_date.day)
    birth_md = (value.month, value.day)

    age = current_date.year - value.year
    if cur_md < birth_md:
        age -= 1

    return age


def date_filter(value: object) -> date:
    """Parse a :obj:`date`."""
    if isinstance(value, date):
        return value
    elif isinstance(value, datetime):
        return value.date()
    else:
        dt = _parse_datetime(value)
        return dt.date()


def datetime_filter(value: object) -> datetime:
    """Parse a :obj:`datetime`."""
    if isinstance(value, datetime):
        return value
    elif isinstance(value, date):
        return datetime(value.year, value.month, value.day).astimezone()
    else:
        return _parse_datetime(value)


def _parse_datetime(v: object) -> datetime:
    if isinstance(v, str):
        dt = datetime.fromisoformat(_fix_z(v))
        return dt.astimezone() if dt.tzinfo is None else dt
    elif isinstance(v, (float, int)):
        return datetime.fromtimestamp(v, tz=timezone.utc).astimezone()
    else:
        raise ValueError(f"Invalid datetime: {v}")


def _fix_z(v: str) -> str:
    return v[:-1] + "+00:00" if v.endswith("Z") else v


def today_func() -> date:
    """Get the current date."""
    return now_func().date()


def now_func() -> datetime:
    """Get the current datetime."""
    return datetime.now().astimezone()
