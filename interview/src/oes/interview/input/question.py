"""Question module."""
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Optional, Union

from attrs import Factory, field, frozen
from cattrs import Converter, override
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn
from oes.interview.input.response import create_response_parser, map_field_names
from oes.interview.input.types import Field, ResponseParser, Whenable
from oes.interview.util import validate_identifier
from oes.template import Context, Template, ValueOrEvaluable


@frozen
class Question(Whenable):
    """A question object."""

    id: str = field(validator=validate_identifier)
    """The question ID."""

    title: Optional[Template] = None
    """The question title."""

    description: Optional[Template] = None
    """The question description."""

    fields: Sequence[Field] = ()
    """Fields in the question."""

    when: Union[ValueOrEvaluable, Sequence[ValueOrEvaluable]] = ()
    """``when`` conditions"""

    _response_parser: ResponseParser = field(
        default=Factory(lambda s: _make_parser(s), takes_self=True),
        init=False,
        eq=False,
    )

    @property
    def response_parser(self) -> ResponseParser:
        """The user response parser function."""
        return self._response_parser

    def get_schema(self, context: Context) -> Mapping[str, object]:
        """Get the JSON schema for this question.

        Args:
            context: The context to use to render templates.
        """
        by_name = map_field_names(self.fields, self.fields)

        properties = {nm: field.get_schema(context) for nm, field in by_name.items()}

        required = [
            nm
            for nm, field_schema in properties.items()
            if not _is_optional(field_schema)
        ]

        schema = {
            "type": "object",
            "properties": properties,
            "required": required,
        }

        if self.title:
            schema["title"] = self.title.render(context)

        if self.description:
            schema["description"] = self.description.render(context)

        return schema


def make_question_structure_fn(
    converter: Converter,
) -> Callable[[Mapping[str, Any], Any], Question]:
    """Get a function to structure a :class:`Question`."""

    return make_dict_structure_fn(
        Question,
        converter,
        _response_parser=override(omit=True),
    )


def make_question_unstructure_fn(
    converter: Converter,
) -> Callable[[Question], Mapping[str, Any]]:
    """Get a function to unstructure a :class:`Question`."""

    return make_dict_unstructure_fn(
        Question,
        converter,
        _response_parser=override(omit=True),
    )


def _make_parser(question: Question) -> ResponseParser:
    return create_response_parser(question.id, question.fields)


def _is_optional(schema: Mapping[str, object]) -> bool:
    return schema.get("nullable") is True
