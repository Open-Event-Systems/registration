"""Attrs helpers."""
from __future__ import annotations

import contextlib
from typing import Type

from typing_extensions import TypeGuard

with contextlib.suppress(ImportError):
    from attrs import AttrsInstance


def is_attrs_instance(obj: object) -> TypeGuard[AttrsInstance]:
    """Get whether the given object is a :obj:`attrs` class instance."""
    return is_attrs_class(type(obj))


def is_attrs_class(obj: object) -> TypeGuard[Type[AttrsInstance]]:
    """Get whether the given object is a :obj:`attrs` class."""
    return isinstance(obj, type) and hasattr(obj, "__attrs_attrs__")
