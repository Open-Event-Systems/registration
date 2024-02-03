"""Immutable containers."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence, Set
from typing import Any, Mapping, TypeVar, overload

_T = TypeVar("_T")
_K = TypeVar("_K")
_V_co = TypeVar("_V_co", covariant=True)
_K2 = TypeVar("_K2")
_V2_co = TypeVar("_V2_co", covariant=True)


class ImmutableSequence(Sequence[_V_co]):
    """Immutable sequence."""

    __slots__ = "_data"

    def __init__(self, data: Iterable[_V_co], /):
        self._data = tuple(data)

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[_V_co]:
        return iter(self._data)

    @overload
    def __getitem__(self, index: int) -> _V_co:
        ...

    @overload
    def __getitem__(self, index: slice) -> ImmutableSequence[_V_co]:
        ...

    def __getitem__(self, index: int | slice) -> _V_co | ImmutableSequence[_V_co]:
        if isinstance(index, slice):
            return ImmutableSequence(self._data[index])
        else:
            return self._data[index]

    def __add__(self, other: Sequence[_V2_co], /) -> ImmutableSequence[_V_co | _V2_co]:
        return make_immutable((*self, *other))

    def __repr__(self) -> str:
        return "ImmutableSequence(" + ", ".join(repr(v) for v in self) + ")"

    def __hash__(self) -> int:
        return hash(self._data)

    def __eq__(self, other: object, /) -> bool:
        return self._data == other


class ImmutableMapping(Mapping[_K, _V_co]):
    """Immutable mapping."""

    __slots__ = ("_data", "_hash")

    def __init__(self, data: Mapping[_K, _V_co], /):
        self._data = data
        self._hash = hash(tuple(self._data.items()))

    def __getitem__(self, key: _K, /) -> _V_co:
        return self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[_K]:
        return iter(self._data)

    def __or__(
        self, other: Mapping[_K2, _V2_co]
    ) -> ImmutableMapping[_K | _K2, _V_co | _V2_co]:
        return make_immutable({**self._data, **other})

    def __repr__(self) -> str:
        return (
            "ImmutableMapping({"
            + ", ".join(f"{k!r}: {v!r}" for k, v in self._data.items())
            + "})"
        )

    def __hash__(self) -> int:
        return self._hash


@overload
def make_immutable(data: Mapping[_K, _V_co], /) -> ImmutableMapping[_K, _V_co]:
    ...


@overload
def make_immutable(data: Sequence[_V_co], /) -> ImmutableSequence[_V_co]:
    ...


@overload
def make_immutable(data: Set[_V_co], /) -> Set[_V_co]:
    ...


@overload
def make_immutable(data: _T, /) -> _T:
    ...


def make_immutable(data, /):
    """Return an immutable, hashable copy of ``data``."""
    if isinstance(data, Mapping):
        return make_immutable_mapping(data)
    elif isinstance(data, Sequence) and not isinstance(data, (str, bytes)):
        return make_immutable_sequence(data)
    elif isinstance(data, Set):
        return frozenset(data)
    else:
        return data


@overload
def make_immutable_mapping(data: Mapping[_K, _V_co], /) -> ImmutableMapping[_K, _V_co]:
    ...


@overload
def make_immutable_mapping(
    data: Iterable[tuple[_K, _V_co]], /
) -> ImmutableMapping[_K, _V_co]:
    ...


def make_immutable_mapping(
    data: Mapping | Iterable[tuple[Any, Any]], /
) -> ImmutableMapping:
    """Make an immutable mapping."""
    if isinstance(data, ImmutableMapping):
        return data
    elif isinstance(data, Mapping):
        return ImmutableMapping({k: make_immutable(v) for k, v in data.items()})
    else:
        return ImmutableMapping(dict((k, make_immutable(v)) for k, v in data))


def make_immutable_sequence(data: Sequence[_V_co]) -> ImmutableSequence[_V_co]:
    """Make an immutable sequence."""
    if isinstance(data, ImmutableSequence):
        return data
    return ImmutableSequence(make_immutable(v) for v in data)
