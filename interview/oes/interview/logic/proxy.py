"""Array/object proxies."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from typing import TypeVar, overload

_V_co = TypeVar("_V_co", covariant=True)
_V2_co = TypeVar("_V2_co", covariant=True)
_T = TypeVar("_T")


class ProxyLookupError(LookupError):
    """A :class:`LookupError` with path information."""

    __slots__ = ("key", "path")

    def __init__(self, key: str | int, path: Sequence[str | int] = ()):
        super().__init__(key)
        self.key = key
        self.path = path

    def __str__(self) -> str:
        return " -> ".join(repr(k) for k in (*self.path, self.key))

    def __repr__(self) -> str:
        return f"<ProxyLookupError {str(self)} >"


class ArrayProxy(Sequence[_V_co]):
    """Array proxy."""

    __slots__ = (
        "_path",
        "_target",
    )

    def __init__(self, target: Sequence[_V_co], path: Sequence[str | int]):
        self._path = path
        self._target = target

    @overload
    def __getitem__(self, index: int) -> _V_co: ...

    @overload
    def __getitem__(self, index: slice) -> ArrayProxy[_V_co]: ...

    def __getitem__(self, index: int | slice) -> _V_co | ArrayProxy[_V_co]:
        if isinstance(index, slice):
            raise ValueError("Slices are not supported")

        try:
            child = self._target[index]
        except LookupError as exc:
            raise ProxyLookupError(index, self._path) from exc

        return make_proxy(child, (*self._path, index))

    def __iter__(self) -> Iterator[_V_co]:
        return iter(self._target)

    def __len__(self) -> int:
        return len(self._target)

    def __add__(self, other: Sequence[_V2_co], /) -> ArrayProxy[_V_co | _V2_co]:
        if not isinstance(other, Sequence):
            return NotImplemented
        return ArrayProxy((*self._target, *other), self._path)

    def __radd__(self, other: Sequence[_V2_co], /) -> ArrayProxy[_V_co | _V2_co]:
        if not isinstance(other, Sequence):
            return NotImplemented
        return ArrayProxy((*other, *self._target), self._path)

    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, Sequence) or isinstance(
            other, (str, bytes, bytearray)
        ):
            return NotImplemented
        return len(other) == len(self._target) and all(
            a == b for a, b in zip(self._target, other)
        )

    def __hash__(self) -> int:
        return hash(self._target)


class ObjectProxy(Mapping[str, _V_co]):
    """Object proxy."""

    __slots__ = (
        "_path",
        "_target",
    )

    def __init__(self, target: Mapping[str, _V_co], path: Sequence[str | int]):
        self._path = path
        self._target = target

    def __getitem__(self, key: str, /) -> _V_co:
        try:
            child = self._target[key]
        except LookupError as exc:
            raise ProxyLookupError(key, self._path) from exc

        return make_proxy(child, (*self._path, key))

    def __iter__(self) -> Iterator[str]:
        return iter(self._target)

    def __len__(self) -> int:
        return len(self._target)

    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, Mapping):
            return NotImplemented
        return self._target == other

    def __hash__(self) -> int:
        return hash(self._target)


@overload
def make_proxy(
    obj: Mapping[str, _V_co], path: Sequence[int | str] = ()
) -> ObjectProxy[_V_co]: ...


@overload
def make_proxy(obj: Sequence[_T], path: Sequence[int | str] = ()) -> ArrayProxy[_T]: ...


@overload
def make_proxy(obj: _T, path: Sequence[int | str] = ()) -> _T: ...


def make_proxy(obj, path=()):
    """Wrap an object in a proxy if it is a sequence or mapping."""
    if isinstance(obj, Mapping):
        return ObjectProxy(obj, path)
    elif isinstance(obj, Sequence) and not isinstance(obj, (str, bytes)):
        return ArrayProxy(obj, path)
    else:
        return obj
