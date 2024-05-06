"""Immutability utilities."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence, Set
from typing import TypeVar, cast, overload

from immutabledict import immutabledict

_K = TypeVar("_K")
_T = TypeVar("_T")
_T_co = TypeVar("_T_co", covariant=True)


class immutable_mapping(immutabledict[_K, _T_co]):
    """:class:`immutabledict` with a properly typed ``__new__``."""

    def __new__(
        cls, arg: Mapping[_K, _T_co] | Iterable[tuple[_K, _T_co]], /
    ) -> immutable_mapping[_K, _T_co]:
        return cast(immutable_mapping[_K, _T_co], super().__new__(cls, arg))


# def immutable_mapping(
#     k: type[_K], v: type[_T], /
# ) -> Callable[[Mapping[_K, _T] | Iterable[tuple[_K, _T]]], immutabledict[_K, _T]]:
#     """Get a properly typed constructor of :class:`immutabledict`."""
#     return immutabledict


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
