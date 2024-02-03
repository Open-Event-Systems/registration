"""Dict merge module."""

import itertools
from collections.abc import Callable, Iterable, Mapping
from copy import deepcopy
from typing import TypeVar, overload

_K = TypeVar("_K")
_V_co = TypeVar("_V_co", covariant=True)
_K2 = TypeVar("_K2")
_V2_co = TypeVar("_V2_co", covariant=True)

_MT = TypeVar("_MT", bound=Mapping)


@overload
def merge_mapping(
    a: Mapping[_K, _V_co], b: Mapping[_K2, _V2_co], /
) -> dict[_K | _K2, _V_co | _V2_co]:
    ...


@overload
def merge_mapping(
    a: Mapping[_K, _V_co],
    b: Mapping[_K2, _V2_co],
    /,
    *,
    constructor: Callable[[Iterable[tuple[_K | _K2, _V_co | _V2_co]]], _MT],
) -> _MT:
    ...


def merge_mapping(
    a: Mapping, b: Mapping, /, *, constructor: Callable[..., Mapping] = dict
) -> Mapping:
    """Recursively merge two mappings into a :obj:`dict`.

    Args:
        a: The first mapping.
        b: The second mapping, which will merge/overwrite keys in ``a``.
        constructor: The mapping constructor, defaults to ``dict``.

    Returns:
        A deep copy of ``a`` and ``b`` merged together.
    """
    unchanged = a.keys() - b.keys()
    added = b.keys() - a.keys()
    updated = b.keys() - added

    return constructor(
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


merge_dict = merge_mapping  # deprecated alias
