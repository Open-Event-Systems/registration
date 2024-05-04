"""Value proxy."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from typing import TypeVar, cast, overload

from oes.interview.logic.pointer import IndexAccess, PropertyAccess, ValuePointer

_V_co = TypeVar("_V_co", covariant=True)
_V2_co = TypeVar("_V2_co", covariant=True)
_T = TypeVar("_T")


class ArrayProxy(Sequence[_V_co]):
    """Array proxy."""

    __slots__ = (
        "_pointer",
        "_target",
    )

    def __init__(self, pointer: ValuePointer, target: Sequence[_V_co]):
        self._pointer = pointer
        self._target = target

    @overload
    def __getitem__(self, index: int) -> _V_co: ...

    @overload
    def __getitem__(self, index: slice) -> ArrayProxy[_V_co]: ...

    def __getitem__(self, index: int | slice) -> _V_co | ArrayProxy[_V_co]:
        if isinstance(index, slice):
            raise ValueError("Slices are not supported")

        return make_proxy(IndexAccess(self._pointer, index), self._target[index])

    def __iter__(self) -> Iterator[_V_co]:
        return iter(self._target)

    def __len__(self) -> int:
        return len(self._target)

    def __add__(self, other: Sequence[_V2_co], /) -> ArrayProxy[_V_co | _V2_co]:
        if not isinstance(other, Sequence):
            return NotImplemented
        return ArrayProxy(self._pointer, (*self._target, *other))

    def __radd__(self, other: Sequence[_V2_co], /) -> ArrayProxy[_V_co | _V2_co]:
        if not isinstance(other, Sequence):
            return NotImplemented
        return ArrayProxy(self._pointer, (*other, *self._target))

    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, Sequence) or isinstance(other, (str, bytes)):
            return NotImplemented
        return len(other) == len(self._target) and all(
            a == b for a, b in zip(self._target, other)
        )


class ObjectProxy(Mapping[str, _V_co]):
    """Object proxy."""

    __slots__ = (
        "_pointer",
        "_target",
    )

    def __init__(self, pointer: ValuePointer, target: Mapping[str, _V_co]):
        self._pointer = pointer
        self._target = target

    def __getitem__(self, key: str, /) -> _V_co:
        return make_proxy(PropertyAccess(self._pointer, key), self._target[key])

    def __iter__(self) -> Iterator[str]:
        return iter(self._target)

    def __len__(self) -> int:
        return len(self._target)

    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, Mapping):
            return NotImplemented
        return self._target == other


def make_proxy(pointer: ValuePointer, obj: _T, /) -> _T:
    """Wrap an object in a proxy if it is a sequence or mapping."""
    if isinstance(obj, Mapping):
        return cast(_T, ObjectProxy(pointer, obj))
    elif isinstance(obj, Sequence) and not isinstance(obj, (str, bytes)):
        return cast(_T, ArrayProxy(pointer, obj))
    else:
        return obj
