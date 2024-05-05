"""Immutability utilities."""

from collections.abc import Callable, Iterable, Mapping, Sequence, Set
from typing import TypeVar, overload

from immutabledict import immutabledict

_K = TypeVar("_K")
_T = TypeVar("_T")


@overload
def immutable_converter(
    t: type[Mapping[_K, _T]], /
) -> Callable[[Mapping[_K, _T] | Iterable[tuple[_K, _T]]], immutabledict[_K, _T]]: ...


@overload
def immutable_converter(
    t: type[Sequence[_T]], /
) -> Callable[[Iterable[_T]], tuple[_T, ...]]: ...


def immutable_converter(t: type) -> Callable:
    """Get a field converter that calls :obj:`make_immutable` on the value."""
    return make_immutable


@overload
def make_immutable(mapping: Mapping[_K, _T], /) -> immutabledict[_K, _T]: ...


@overload
def make_immutable(sequence: Sequence[_T], /) -> tuple[_T, ...]: ...


@overload
def make_immutable(set: Set[_T], /) -> frozenset[_T]: ...


@overload
def make_immutable(other: _T, /) -> _T: ...


def make_immutable(obj):
    """Make an immutable version of ``obj``."""
    if obj is None or isinstance(obj, (str, int, float, bool, bytes, bytearray)):
        return obj
    elif isinstance(obj, Mapping):
        return immutabledict((k, make_immutable(v)) for k, v in obj.items())
    elif isinstance(obj, Sequence):
        return tuple(make_immutable(v) for v in obj)
    elif isinstance(obj, Set):
        return frozenset(obj)
    else:
        return obj
