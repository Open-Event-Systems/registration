"""Mapping utils."""

from collections.abc import Callable, Mapping
from typing import Any

__all__ = [
    "merge_mapping",
]


def merge_mapping(
    a: Mapping[str, Any],
    b: Mapping[str, Any],
    /,
    *,
    factory: Callable[[Mapping[str, Any]], Mapping[str, Any]] = dict,
) -> Mapping[str, Any]:
    """Deeply ``a`` and ``b``, returning a new mapping."""
    return _merge_mapping(a, b, factory)


def _merge_mapping(
    a: Mapping[str, Any],
    b: Mapping[str, Any],
    factory: Callable[[Mapping[str, Any]], Mapping[str, Any]],
) -> Mapping[str, Any]:
    merged = {**a}
    for k, v in b.items():
        cur = merged.get(k)
        if isinstance(cur, Mapping) and isinstance(v, Mapping):
            merged[k] = _merge_mapping(cur, v, factory)
        else:
            merged[k] = v
    return factory(merged)
