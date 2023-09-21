"""Proxy module."""
from collections.abc import Mapping, Sequence
from typing import Iterator, TypeVar, Union, cast, overload

from oes.interview.variables.locator import Index, Locator

_K = TypeVar("_K", str, int)
_V = TypeVar("_V")
_T = TypeVar("_T")


class MappingProxy(Mapping[_K, _V]):
    _expression: Locator
    _target: Mapping[_K, _V]

    def __init__(self, expression: Locator, target: Mapping[_K, _V]):
        self._expression = expression
        self._target = target

    def __getitem__(self, item: _K) -> _V:
        new_expr = Index(self._expression, item)
        val = self._target.__getitem__(item)
        return _make_proxy(new_expr, val)

    def __len__(self) -> int:
        return len(self._target)

    def __iter__(self) -> Iterator[_K]:
        return iter(self._target)

    def __repr__(self) -> str:
        return repr(self._target)


class SequenceProxy(Sequence[_T]):
    _expression: Locator
    _target: Sequence[_T]

    def __init__(self, expression: Locator, target: Sequence[_T]):
        self._expression = expression
        self._target = target

    @overload
    def __getitem__(self, item: int) -> _T:
        ...

    @overload
    def __getitem__(self, item: slice) -> Sequence[_T]:
        ...

    def __getitem__(self, item: Union[int, slice]) -> Union[_T, Sequence[_T]]:
        if isinstance(item, slice):
            raise TypeError("Slices not supported")

        new_expr = Index(self._expression, item)
        val = self._target.__getitem__(item)
        return _make_proxy(new_expr, val)

    def __len__(self) -> int:
        return len(self._target)

    def __repr__(self) -> str:
        return repr(self._target)

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, (list, tuple, Sequence))
            and not isinstance(other, (str, bytes))
            and len(self) == len(other)
            and tuple(self) == tuple(other)
        )

    def __add__(self, other) -> Sequence[_T]:
        if isinstance(other, (list, tuple, Sequence)):
            return list(self._target) + list(other)
        else:
            return NotImplemented

    def __radd__(self, other) -> Sequence[_T]:
        if isinstance(other, (list, tuple, Sequence)):
            return list(other) + list(self._target)
        else:
            return NotImplemented


def _make_proxy(expression: Locator, value: _T) -> _T:
    if isinstance(value, Mapping):
        return cast("_T", MappingProxy(expression, value))
    elif isinstance(value, Sequence) and not isinstance(value, str):
        return cast("_T", SequenceProxy(expression, value))
    else:
        return cast("_T", value)
