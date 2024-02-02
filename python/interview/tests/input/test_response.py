from typing import Any, Optional

import attr
import pytest
from attrs import frozen
from cattrs import ClassValidationError
from oes.interview.input.response import create_response_parser, map_field_names
from oes.interview.input.types import JSONSchema
from oes.interview.logic import ValuePointer, parse_pointer
from oes.template import Context


@frozen
class CustomField:
    field_info: object
    set: Optional[ValuePointer]
    optional: bool = False

    def get_field_info(self, context: Context) -> Any:
        return self.field_info

    def get_schema(self, context: Context) -> JSONSchema:
        return {}


def test_create_response_parser():
    fields = [
        CustomField(
            attr.ib(type=int),
            set=parse_pointer("val1"),
        ),
        CustomField(
            attr.ib(type=str),
            set=parse_pointer("val2"),
        ),
    ]

    parser = create_response_parser(
        "my-test's_class 0",
        fields,
    )

    response = map_field_names(fields, (123, "test"))

    parsed = parser(response, {})
    assert parsed == {
        parse_pointer("val1"): 123,
        parse_pointer("val2"): "test",
    }


@pytest.mark.parametrize(
    "responses",
    (
        (
            "test",
            "test",
        ),
        (
            "1",
            "test",
        ),
        (1,),
        (),
    ),
)
def test_create_response_parser_error(responses):
    fields = [
        CustomField(
            attr.ib(type=int),
            set=parse_pointer("val1"),
        ),
        CustomField(
            attr.ib(type=str),
            set=parse_pointer("val2"),
        ),
    ]

    parser = create_response_parser(
        "my-test's_class 0",
        fields,
    )

    response = map_field_names(fields, responses)

    with pytest.raises(ClassValidationError):
        parser(response, {})
