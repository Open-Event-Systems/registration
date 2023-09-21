import pytest
from cattrs import ClassValidationError
from oes.interview.input.field_types.number import NumberField
from oes.interview.input.response import create_response_parser
from oes.interview.variables.locator import parse_locator

field1 = NumberField(
    set=parse_locator("value"),
    default=1.0,
    min=0.0,
    max=2.0,
)

field2 = NumberField(
    set=parse_locator("value"),
    integer=True,
    default=1,
    min=0,
    optional=True,
)


def test_number_field_schema():
    schema = field1.get_schema({})

    assert schema == {
        "type": "number",
        "x-type": "number",
        "minimum": 0.0,
        "maximum": 2.0,
        "default": 1.0,
        "nullable": False,
    }


def test_number_field_schema_optional():
    schema = field2.get_schema({})

    assert schema == {
        "type": "integer",
        "x-type": "number",
        "minimum": 0,
        "default": 1,
        "nullable": True,
    }


@pytest.mark.parametrize(
    "val, expected",
    (
        (0, 0),
        (0.1, 0),
        (None, None),
    ),
)
def test_number_field_parse(val, expected):
    parser = create_response_parser("test", [field2])

    result = parser({"field_0": val})
    assert result == {parse_locator("value"): expected}


@pytest.mark.parametrize(
    "val",
    (
        None,
        "",
        -1,
        2.1,
    ),
)
def test_number_field_parse_error(val):
    parser = create_response_parser("test", [field1])

    with pytest.raises(ClassValidationError):
        parser({"field_0": val})


@pytest.mark.parametrize(
    "val",
    (-1,),
)
def test_number_field_parse_error_2(val):
    parser = create_response_parser("test", [field2])

    with pytest.raises(ClassValidationError):
        parser({"field_0": val})
