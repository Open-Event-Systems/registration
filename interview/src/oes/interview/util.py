"""Misc utilities."""
from __future__ import annotations

import re
from typing import TypeVar

from attr import Attribute

_K = TypeVar("_K")


IDENTIFIER_PATTERN = r"^(?![0-9_-])[a-zA-Z0-9_-]+(?<!-)$"
"""Valid identifier pattern."""


def validate_identifier(instance: object, attribute: Attribute, value: object):
    """Raise :class:`ValueError` if the object is not a valid identifier."""
    if not isinstance(value, str) or not re.match(IDENTIFIER_PATTERN, value, re.I):
        raise ValueError(f"Invalid identifier: {value}")
