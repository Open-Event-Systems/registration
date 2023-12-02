"""Serialization used internally for configuration."""
import base64
from collections.abc import Sequence
from typing import Tuple, get_args, get_origin

from cattrs import Converter
from oes.registration.models.config import Base64Bytes
from oes.registration.models.logic import WhenCondition
from oes.registration.serialization.common import CustomConverter
from oes.registration.serialization.common import (
    configure_converter as configure_common,
)
from oes.template import (
    Expression,
    LogicAnd,
    LogicNot,
    LogicOr,
    Template,
    ValueOrEvaluable,
    structure_expression,
    structure_template,
    structure_value_or_evaluable,
    unstructure_expression,
    unstructure_logic,
    unstructure_template,
)

converter = CustomConverter()
configure_common(converter)


def configure_converter(c: Converter):
    """Configure a converter to work with configuration related types."""
    c.register_structure_hook(Base64Bytes, structure_base64_bytes)
    c.register_structure_hook_func(
        lambda cls: get_origin(cls) is Sequence,
        lambda v, t: structure_sequence(c, v, t),
    )
    c.register_structure_hook(Template, structure_template)
    c.register_structure_hook(Expression, structure_expression)
    c.register_structure_hook(
        ValueOrEvaluable, lambda v, t: structure_value_or_evaluable(c, v, t)
    )
    c.register_structure_hook_func(
        lambda cls: cls == WhenCondition,
        lambda v, t: structure_value_or_evaluable_sequence(c, v, t),
    )

    c.register_unstructure_hook(Base64Bytes, unstructure_base64_bytes)
    c.register_unstructure_hook(Template, unstructure_template)
    c.register_unstructure_hook(Expression, unstructure_expression)

    c.register_unstructure_hook_func(
        lambda cls: isinstance(cls, type)
        and issubclass(cls, (LogicAnd, LogicOr, LogicNot)),
        lambda v: unstructure_logic(c, v),
    )


# Sequence[T] is structured as tuple[T, ...]
def structure_sequence(c, v, t):
    """Structure :class:`Sequence` into a tuple."""
    args = get_args(t)
    return c.structure(v, Tuple[args[0], ...])


def structure_base64_bytes(v, t):
    """Structure a base64 string into bytes."""
    if isinstance(v, (bytes, bytearray)):
        return bytes(v)
    elif not isinstance(v, str):
        raise TypeError(f"Invalid base64 data: {v!r}")

    decoded = base64.b64decode(v)
    return Base64Bytes(decoded)


def structure_value_or_evaluable_sequence(c, v, t):
    """Structure a value or evaluable sequence."""
    if isinstance(v, Sequence) and not isinstance(v, str):
        return c.structure(v, Sequence[ValueOrEvaluable])
    else:
        return c.structure(v, ValueOrEvaluable)


def unstructure_base64_bytes(v):
    """Unstructure bytes into a base64 string."""
    if isinstance(v, str):
        return v
    elif not isinstance(v, (bytes, bytearray)):
        raise TypeError(f"Invalid bytes: {v!r}")

    encoded = base64.b64encode(v)
    return encoded.decode()


configure_converter(converter)
