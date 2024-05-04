"""Field implementation module."""

from collections.abc import Sequence
from typing import Any

from attrs import field, frozen
from oes.interview.immutable import make_immutable
from oes.interview.input.types import JSONSchema, Validator


@frozen
class Field:
    """Field object."""

    python_type: type
    optional: bool = False
    schema: JSONSchema = field(factory=dict, converter=lambda v: make_immutable(v))
    validators: Sequence[Validator] = ()

    def parse(self, value: object, /) -> Any:
        cur = value
        for validator in self.validators:
            cur = validator(cur)

        return cur
