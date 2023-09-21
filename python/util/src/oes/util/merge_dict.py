"""Dict merge module."""
import itertools
from collections.abc import Mapping
from copy import deepcopy
from typing import Any, TypeVar

_K = TypeVar("_K")


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
                (k, merge_dict(a[k], b[k]))
                if isinstance(a[k], Mapping) and isinstance(b[k], Mapping)
                else (k, deepcopy(b[k]))
                for k in updated
            ),
        )
    )
