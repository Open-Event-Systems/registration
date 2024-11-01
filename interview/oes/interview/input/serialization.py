"""Field/question serialization."""

import functools
from collections.abc import Callable, Mapping
from importlib.metadata import entry_points
from typing import Any

from cattrs import Converter
from oes.interview.input.types import FieldTemplate

ENTRY_POINT_GROUP = "oes.interview.field_types"


def make_field_template_structure_fn(
    converter: Converter,
) -> Callable[[Any, Any], FieldTemplate]:
    """Structure a :class:`FieldTemplate`."""

    def structure(v: Any, t: Any) -> FieldTemplate:
        if not isinstance(v, Mapping) or "type" not in v:
            raise ValueError(f"Invalid field config: {v}")
        field_type = v["type"]
        factory = get_field_template_factory(field_type)
        return factory(v, converter)

    return structure


@functools.cache
def get_field_template_factory(
    field_type: str,
) -> Callable[[Mapping[str, Any], Converter], FieldTemplate]:
    """Get the field template factory for a field type."""
    ep = next(iter(entry_points(group=ENTRY_POINT_GROUP, name=field_type)), None)
    if ep is None:
        raise LookupError(f"No such field type: {field_type}")
    factory = ep.load()
    return factory
