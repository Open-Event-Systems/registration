"""Field implementation module."""

from collections.abc import Sequence
from typing import Any

from attrs import field, frozen
from immutabledict import immutabledict
from oes.interview.immutable import immutable_converter
from oes.interview.input.types import JSONSchema, Validator


@frozen
class Field:
    """Field object."""

    python_type: type
    optional: bool = False
    schema: JSONSchema = field(
        default=immutabledict(), converter=immutable_converter(JSONSchema)
    )
    validators: Sequence[Validator] = field(default=(), converter=tuple[Validator, ...])

    def parse(self, value: object, /) -> Any:
        cur = value
        for validator in self.validators:
            cur = validator(cur)

        return cur
