"""Question module."""

from collections.abc import Callable, Iterable, Mapping, Sequence, Set
from typing import Any

from attrs import Factory, field, frozen
from cattrs import Converter
from cattrs.gen import make_dict_structure_fn
from oes.interview.immutable import make_immutable
from oes.interview.input.field import Field
from oes.interview.input.types import FieldTemplate, JSONSchema
from oes.interview.logic.pointer import get_path
from oes.interview.logic.types import ValuePointer
from oes.utils.logic import WhenCondition
from oes.utils.template import Template, TemplateContext


@frozen
class Question:
    """A question."""

    fields: Mapping[str, Field]
    value_map: Mapping[str, ValuePointer]
    schema: JSONSchema

    def parse(self, response: Mapping[str, Any]) -> dict[ValuePointer, Any]:
        response_values = {k: response.get(k) for k in self.fields}
        parsed_values = {
            k: field.parse(response_values[k]) for k, field in self.fields.items()
        }
        mapped_values = {
            self.value_map[k]: parsed_values[k]
            for k in self.fields
            if k in self.value_map
        }
        return mapped_values


@frozen
class QuestionTemplate:
    """A question template."""

    id: str | None = None
    title: str | Template | None = None
    description: str | Template | None = None
    fields: Sequence[FieldTemplate] = ()
    when: WhenCondition = ()

    _provides: Set[Sequence[str | int]] = field(
        init=False,
        repr=False,
        default=Factory(
            lambda s: frozenset(get_path(f.set) for f in s.fields if f.set),
            takes_self=True,
        ),
    )

    def get_question(self, context: TemplateContext) -> Question:
        by_id = {_make_field_id(idx): field for idx, field in enumerate(self.fields)}
        field_by_id = {
            field_id: field.get_field(context) for field_id, field in by_id.items()
        }
        schema = self.get_schema(field_by_id, context)
        return make_question(
            (
                (field_id, field.set, field_by_id[field_id])
                for field_id, field in by_id.items()
            ),
            schema,
        )

    @property
    def provides(self) -> Set[Sequence[str | int | ValuePointer]]:
        return self._provides

    def get_schema(
        self, fields: Mapping[str, Field], context: TemplateContext
    ) -> dict[str, Any]:
        title = (
            self.title.render(context)
            if isinstance(self.title, Template)
            else self.title
        )
        desc = (
            self.description.render(context)
            if isinstance(self.description, Template)
            else self.description
        )
        schema = {
            "type": "object",
            "properties": {
                field_id: field.schema for field_id, field in fields.items()
            },
        }

        required_ids = [
            field_id for field_id, field in fields.items() if not field.optional
        ]

        schema["required"] = required_ids

        if title:
            schema["title"] = title

        if desc:
            schema["description"] = desc

        return schema


def make_question_template_structure_fn(
    converter: Converter,
) -> Callable[[Any, Any], QuestionTemplate]:
    """Make a function to structure a :class:`QuestionTemplate`."""
    return make_dict_structure_fn(QuestionTemplate, converter)


def make_question(
    fields: Iterable[tuple[str, ValuePointer | None, Field]] = (),
    schema: JSONSchema | None = None,
) -> Question:
    """Make a :class:`Question`."""
    by_id = {f[0]: f for f in fields}
    value_map = {f[0]: f[1] for f in by_id.values() if f[1] is not None}
    fields_ = {f[0]: f[2] for f in by_id.values()}
    return Question(
        fields=make_immutable(fields_),
        value_map=make_immutable(value_map),
        schema=make_immutable(schema or {}),
    )


def _make_field_id(index: int) -> str:
    return f"field_{index}"
