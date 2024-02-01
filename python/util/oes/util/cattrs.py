"""Cattrs helpers."""
from __future__ import annotations

__all__ = [
    "ExceptionDetails",
    "structure_datetime",
    "unstructure_datetime_isoformat",
    "get_exception_details",
]

from collections.abc import Iterator
from datetime import datetime, timezone
from typing import Any, Union

from attrs import frozen
from cattrs import AttributeValidationNote, BaseValidationError, IterableValidationNote

try:
    from ruamel.yaml.timestamp import TimeStamp
except ImportError:
    TimeStamp = None

from typing_extensions import TypeAlias

ExcPath: TypeAlias = tuple[Union[str, int], ...]


@frozen
class ExceptionDetails:
    """Exception details class."""

    path: ExcPath = ()
    message: str = ""


def structure_datetime(v: Any, t: Any) -> datetime:
    """Structure a :class:`datetime`."""
    if isinstance(v, datetime):
        return _handle_yaml_datetime(v)
    elif isinstance(v, str):
        dt = datetime.fromisoformat(v)
        return dt if dt.tzinfo is not None else dt.astimezone()
    elif isinstance(v, (float, int)):
        return datetime.fromtimestamp(v).astimezone()
    else:
        raise TypeError(f"Invalid datetime: {v}")


def unstructure_datetime_isoformat(v: datetime) -> str:
    """Unstructure a :class:`datetime` as an ISO string."""
    return v.isoformat()


def _handle_yaml_datetime(v: datetime) -> datetime:
    if TimeStamp and isinstance(v, TimeStamp):
        if "delta" in v._yaml and v._yaml.get("tz"):
            tzinfo = timezone(v._yaml["delta"])
            v = v.replace(tzinfo=timezone.utc)
            return v.astimezone(tz=tzinfo)
        else:
            return v if v.tzinfo is not None else v.astimezone()
    else:
        return v


def _handle_datetime_str(v: str) -> datetime:
    if v.endswith("Z"):
        v = v[:-1] + "+00:00"
    return datetime.fromisoformat(v)


def get_exception_details(exc: Exception) -> list[ExceptionDetails]:
    """Get a :class:`ExceptionDetails` list for a validation error."""
    return list(_get_details(exc, ()))


def _get_details(exc: Exception, path: ExcPath) -> Iterator[ExceptionDetails]:
    if isinstance(exc, BaseValidationError):
        yield from _get_group_error_details(exc, path)
    elif isinstance(exc, KeyError):
        yield _get_key_error_details(exc, path)
    else:
        yield ExceptionDetails(path, str(exc))


def _get_group_error_details(
    exc: BaseValidationError, path: ExcPath
) -> Iterator[ExceptionDetails]:
    path = _get_path_from_notes(exc, path)
    for sub in exc.exceptions:
        yield from _get_details(sub, path)  # noqa: NEW100


def _get_path_from_notes(exc: BaseValidationError, path: ExcPath) -> ExcPath:
    notes = getattr(exc, "__notes__", [])
    for note in notes:
        if isinstance(note, AttributeValidationNote):
            return path + (note.name,)
        elif isinstance(note, IterableValidationNote):
            return path + (note.index,)
    return path


def _get_key_error_details(exc: KeyError, path: ExcPath) -> ExceptionDetails:
    if len(exc.args) > 0:
        return ExceptionDetails(path, f"A value is required for {exc.args[0]!r}")
    else:
        return ExceptionDetails(path, "A required value is missing")
