"""OES shared utilities library."""

from .date import get_now
from .dict import merge_dict, merge_mapping
from .immutable import (
    ImmutableMapping,
    ImmutableSequence,
    make_immutable,
    make_immutable_mapping,
    make_immutable_sequence,
)
from .urlsafe_base64 import urlsafe_b64decode, urlsafe_b64encode

__all__ = [
    "get_now",
    "ImmutableSequence",
    "ImmutableMapping",
    "make_immutable",
    "make_immutable_sequence",
    "make_immutable_mapping",
    "merge_mapping",
    "merge_dict",
    "urlsafe_b64encode",
    "urlsafe_b64decode",
    # modules
    "blacksheep",
    "attrs",
    "cattrs",
    "logging",
]
