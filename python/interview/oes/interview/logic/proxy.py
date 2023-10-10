"""Value proxy."""
from collections.abc import Mapping, MutableMapping, MutableSequence, Sequence
from typing import Any, Generic, Iterable, TypeVar, Union, cast, overload

from oes.interview.logic.pointer import PointerImpl, PointerSegment

_T = TypeVar("_T")
_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


class ObjectProxy(MutableMapping[_KT, _VT], Generic[_KT, _VT]):
    """Object proxy."""

    _pointer: PointerImpl
    _target: MutableMapping[_KT, _VT]

    def __init__(self, pointer: PointerImpl, target: MutableMapping[_KT, _VT]):
        self._pointer = pointer
        self._target = target

    def __setitem__(self, key: _KT, value: _VT):
        self._target[key] = value

    def __delitem__(self, key: _KT):
        del self._target[key]

    def __getitem__(self, key: _KT) -> _VT:
        pointer = PointerImpl((*self._pointer, PointerSegment(key)))
        return make_proxy(pointer, self._target[key])

    def __len__(self):
        return len(self._target)

    def __iter__(self):
        return iter(self._target)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Mapping):
            return dict(other) == dict(self._target)
        else:
            return NotImplemented

    def __repr__(self) -> str:
        return f"ObjectProxy({self._target!r})"


class ArrayProxy(MutableSequence[_VT], Generic[_VT]):
    """Array proxy."""

    _pointer: PointerImpl
    _target: MutableSequence[_VT]

    def __init__(self, pointer: PointerImpl, target: MutableSequence[_VT]):
        self._pointer = pointer
        self._target = target

    def insert(self, index: int, value: _VT):
        self._target.insert(index, value)

    @overload
    def __getitem__(self, index: int) -> _VT:
        ...

    @overload
    def __getitem__(self, index: slice) -> MutableSequence[_VT]:
        ...

    def __getitem__(self, index: Union[int, slice]) -> Union[_VT, MutableSequence[_VT]]:
        if isinstance(index, slice):
            raise NotImplementedError("Slices are not supported")

        pointer = PointerImpl((*self._pointer, PointerSegment(index)))
        return make_proxy(pointer, self._target[index])

    @overload
    def __setitem__(self, index: int, value: _VT):
        ...

    @overload
    def __setitem__(self, index: slice, value: Iterable[_VT]):
        ...

    def __setitem__(self, index: Union[int, slice], value: Union[Iterable[_VT], _VT]):
        if isinstance(index, slice):
            raise NotImplementedError("Slices are not supported")

        self._target[index] = cast(_VT, value)

    @overload
    def __delitem__(self, index: int):
        ...

    @overload
    def __delitem__(self, index: slice):
        ...

    def __delitem__(self, index: Union[int, slice]):
        if isinstance(index, slice):
            raise NotImplementedError("Slices are not supported")
        del self._target[index]

    def __len__(self):
        return len(self._target)

    def __add__(self, other: object) -> MutableSequence[_VT]:
        if isinstance(other, Iterable):
            return ArrayProxy(self._pointer, [*self, *other])
        else:
            return NotImplemented

    def __radd__(self, other: object) -> MutableSequence[_VT]:
        if isinstance(other, Iterable):
            return ArrayProxy(self._pointer, [*other, *self])
        else:
            return NotImplemented

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Sequence) and not isinstance(other, str):
            return tuple(other) == tuple(self._target)
        else:
            return NotImplemented

    def __repr__(self) -> str:
        return f"ArrayProxy({self._target!r})"


def make_proxy(pointer: PointerImpl, obj: _T) -> _T:
    """Wrap ``obj`` in a :class:`Proxy` if it is a sequence/mapping."""
    res: Any
    if isinstance(obj, Mapping):
        res = ObjectProxy(pointer, cast(Any, obj))
    elif isinstance(obj, Sequence) and not isinstance(obj, str):
        res = ArrayProxy(pointer, cast(Any, obj))
    else:
        res = obj

    return res
