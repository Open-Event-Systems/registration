"""Serialization functions."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import datetime
from typing import TYPE_CHECKING, Any, Type, TypeVar, get_args, get_origin
from uuid import UUID

if TYPE_CHECKING:
    from cattrs import Converter

__all__ = [
    "configure_converter",
    "datetime_structure_fn",
    "datetime_unstructure_fn",
    "uuid_structure_fn",
    "uuid_unstructure_fn",
    "make_sequence_structure_fn",
]

_T = TypeVar("_T")


def configure_converter(converter: Converter):
    """Configure a :class:`Converter`."""
    converter.register_structure_hook(datetime, datetime_structure_fn)
    converter.register_unstructure_hook(datetime, datetime_unstructure_fn)

    # UUID functions to also handle sqlalchemy's subclasses
    converter.register_structure_hook_func(
        lambda cls: isinstance(cls, type) and issubclass(cls, UUID),
        uuid_structure_fn,
    )
    converter.register_unstructure_hook_func(
        lambda cls: isinstance(cls, type) and issubclass(cls, UUID), uuid_unstructure_fn
    )

    converter.register_structure_hook_factory(
        lambda cls: get_origin(cls) is Sequence,
        lambda cls: make_sequence_structure_fn(cls, converter),
    )


def datetime_structure_fn(v: Any, t: Any) -> datetime:
    """Structure a :class:`datetime`."""
    if isinstance(v, datetime):
        return v
    if not isinstance(v, str):
        raise ValueError(f"Invalid datetime: {v}")
    # python does not accept Z offset
    if v[-1] == "Z":
        v = v[:-1] + "+00:00"
    dt = datetime.fromisoformat(v)
    return dt.astimezone() if dt.tzinfo is None else dt


def datetime_unstructure_fn(v: datetime) -> str:
    """Unstructure a :class:`datetime`."""
    fmt = v.isoformat()
    return fmt


def uuid_structure_fn(v: Any, t: Any) -> UUID:
    """Structure a :class:`UUID`."""
    if isinstance(v, UUID):
        return v
    if not isinstance(v, str):
        raise ValueError(f"Invalid UUID: {v}")
    return UUID(v)


def uuid_unstructure_fn(v: UUID) -> str:
    """Structure a :class:`UUID`."""
    return str(v)


def make_sequence_structure_fn(
    seq_type: Type[Sequence[_T]],
    converter: Converter,
) -> Callable[[Any, Any], tuple[_T]]:
    """Make a func to structure a :class:`Sequence` as a tuple."""
    args: Any = get_args(seq_type)
    tuple_typ = tuple[args[0], ...] if args else tuple

    def structure(v: Any, t: Any) -> tuple[_T]:
        return converter.structure(v, tuple_typ)

    return structure
