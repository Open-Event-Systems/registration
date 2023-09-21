"""Test/filter functions."""
from datetime import date
from typing import Union


def date_filter(value: Union[str, date]) -> date:
    """Parse a string into a :obj:`date`."""
    return value if isinstance(value, date) else date.fromisoformat(str(value))


def age_filter(
    value: Union[str, date], current_date: Union[str, date, None] = None
) -> int:
    """Return the age in years given a birthdate.

    Args:
        value: The birthdate, as a :obj:`date` or date string.
        current_date: Today's date, as a :obj:`date` or date string. Defaults to today.

    Returns:
        The age in years.
    """
    value = date_filter(value)
    current_date = date_filter(date.today() if current_date is None else current_date)

    cur_md = (current_date.month, current_date.day)
    birth_md = (value.month, value.day)

    age = current_date.year - value.year
    if cur_md < birth_md:
        age -= 1

    return age
