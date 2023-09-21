from datetime import date

import pytest
from cattrs import ClassValidationError
from oes.interview.input.field_types.date import DateField
from oes.interview.input.response import create_response_parser
from oes.interview.variables.locator import parse_locator

field = DateField(
    set=parse_locator("value"),
    default=date(2020, 1, 1),
    min=date(2020, 1, 1),
    max=date(2020, 2, 1),
)


def test_date_field_schema():
    schema = field.get_schema({})

    assert schema == {
        "type": "string",
        "format": "date",
        "x-type": "date",
        "x-minimum": date(2020, 1, 1),
        "x-maximum": date(2020, 2, 1),
        "default": date(2020, 1, 1),
        "nullable": False,
    }


@pytest.mark.parametrize(
    "val, expected",
    (("2020-01-01", date(2020, 1, 1)),),
)
def test_date_field_parse(val, expected):
    parser = create_response_parser("test", [field])

    result = parser({"field_0": val})
    assert result == {parse_locator("value"): expected}


@pytest.mark.parametrize(
    "val",
    (
        None,
        "2020-1-1",
        "2",
    ),
)
def test_date_field_parse_error(val):
    parser = create_response_parser("test", [field])

    with pytest.raises(ClassValidationError):
        parser({"field_0": val})
