"""Cattrs helpers."""
from __future__ import annotations

import contextlib
from collections.abc import Iterator
from typing import Union

with contextlib.suppress(ImportError):
    from attrs import frozen
    from cattrs import (
        BaseValidationError,
        AttributeValidationNote,
        IterableValidationNote,
    )

from typing_extensions import TypeAlias

ExcPath: TypeAlias = tuple[Union[str, int], ...]


@frozen
class ExceptionDetails:
    """Exception details class."""

    path: ExcPath = ()
    message: str = ""


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
