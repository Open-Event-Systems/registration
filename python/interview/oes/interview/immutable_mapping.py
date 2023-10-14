"""Immutable mapping."""
from __future__ import annotations

__all__ = [
    "ImmutableMapping",
    "make_immutable",
]

import itertools
from collections.abc import Iterable, Iterator, Mapping, Sequence, Set
from typing import Any, Dict, Tuple, TypeVar, Union, overload

_T = TypeVar("_T")
_K = TypeVar("_K")
_V = TypeVar("_V", covariant=True)


class ImmutableMapping(Mapping[_K, _V]):
    """Simple immutable mapping implementation."""

    __slots__ = (
        "_data",
        "_hash",
    )

    _data: Dict[_K, _V]
    _hash: int

    @overload
    def __init__(self, mapping: Mapping[_K, _V], /):
        ...

    @overload
    def __init__(self, items: Iterable[Tuple[_K, _V]], /):
        ...

    @overload
    def __init__(self):
        ...

    def __init__(
        self, obj: Union[Mapping[_K, _V], Iterable[Tuple[_K, _V]], None] = None
    ):
        if obj is None:
            self._data = {}
            self._hash = 0
        elif isinstance(obj, ImmutableMapping):
            self._data = obj._data
            self._hash = obj._hash
        else:
            self._data = dict(obj)

            self._hash = 0
            for p in self._data.items():
                self._hash ^= hash(p)

    def __getitem__(self, key: _K, /) -> _V:
        return self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[_K]:
        return iter(self._data)

    def __or__(self, other: Mapping[_K, _V]) -> ImmutableMapping[_K, _V]:
        return ImmutableMapping(
            itertools.chain(
                self._data.items(),
                other.items(),
            )
        )

    def __repr__(self) -> str:
        return f"ImmutableMapping({self._data!r})"

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ImmutableMapping):
            return other._data == self._data
        elif isinstance(other, Mapping):
            return len(self._data) == len(other) and all(
                k in self._data and self._data[k] == v for k, v in other.items()
            )
        else:
            return NotImplemented


def make_immutable(obj: _T) -> _T:  # noqa: CCR
    """Recursively replace a collection with immutable versions."""
    v: Any
    if isinstance(obj, ImmutableMapping):
        v = obj
    elif isinstance(obj, Mapping):
        v = ImmutableMapping(((k, make_immutable(v)) for k, v in obj.items()))
    elif isinstance(obj, Sequence) and not isinstance(obj, str):
        v = tuple(make_immutable(v) for v in obj)
    elif isinstance(obj, Set) and not isinstance(obj, frozenset):
        v = frozenset(make_immutable(v) for v in obj)
    else:
        v = obj

    return v
