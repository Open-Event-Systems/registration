"""Dict merge module."""

import itertools
from collections.abc import Mapping, Sequence, Set
from copy import deepcopy
from typing import Any, TypeVar, overload

_K = TypeVar("_K")
_V_co = TypeVar("_V_co", covariant=True)


def merge_dict(a: Mapping[_K, Any], b: Mapping[_K, Any], /) -> dict[_K, Any]:
    """Recursively merge two mappings into a :obj:`dict`.

    Args:
        a: The first mapping.
        b: The second mapping, which will merge/overwrite keys in ``a``.

    Returns:
        A deep copy of ``a`` and ``b`` merged together.
    """
    unchanged = a.keys() - b.keys()
    added = b.keys() - a.keys()
    updated = b.keys() - added

    return dict(
        itertools.chain(
            # copy all unchanged items
            ((k, deepcopy(a[k])) for k in unchanged),
            # copy all added items
            ((k, deepcopy(b[k])) for k in added),
            # copy or merge all updated items
            (
                (
                    (k, merge_dict(a[k], b[k]))
                    if isinstance(a[k], Mapping) and isinstance(b[k], Mapping)
                    else (k, deepcopy(b[k]))
                )
                for k in updated
            ),
        )
    )


@overload
def make_immutable(obj: Mapping[_K, _V_co], /) -> Mapping[_K, _V_co]:
    ...


@overload
def make_immutable(obj: Sequence[_V_co], /) -> tuple[_V_co, ...]:
    ...


@overload
def make_immutable(obj: Set[_V_co], /) -> frozenset[_V_co]:
    ...


@overload
def make_immutable(obj: _V_co, /) -> _V_co:
    ...


def make_immutable(obj: object, /) -> object:
    """Recursively convert mappings/sequences to immutable equivalents."""
    if isinstance(obj, Mapping):
        return immutable_dict({k: make_immutable(v) for k, v in obj.items()})
    elif isinstance(obj, Sequence) and not isinstance(obj, (str, bytes)):
        return tuple(make_immutable(v) for v in obj)
    elif isinstance(obj, Set):
        return frozenset(make_immutable(v) for v in obj)
    else:
        return obj


def immutable_dict(data: Mapping[_K, _V_co], /) -> Mapping[_K, _V_co]:
    """Create a hashable, immutable dict."""
    return _ImmutableDict(data)


class _ImmutableDict(dict):
    __slots__ = ("_hash",)

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._hash = hash(tuple(self.items()))

    def __hash__(self) -> int:  # type: ignore
        return self._hash
