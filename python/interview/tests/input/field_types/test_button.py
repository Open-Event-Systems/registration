import pytest
from cattrs import BaseValidationError
from oes.interview.input.field_types.button import Button, ButtonOption
from oes.interview.input.response import create_response_parser
from oes.interview.logic import parse_pointer
from oes.template import Expression, Template

field1 = Button(
    set=parse_pointer("option"),
    options=(
        ButtonOption(
            label=Template("Yes"),
            primary=True,
            value=True,
        ),
        ButtonOption(
            label=Template("No"),
            default=True,
            value=False,
        ),
    ),
)

field2 = Button(
    set=parse_pointer("option"),
    options=(
        ButtonOption(
            id="a",
            label=Template("1"),
            default=True,
            value=1,
        ),
        ButtonOption(
            label=Template("2"),
            value=2,
        ),
    ),
)


def test_button_schema():
    schema = field1.get_schema({})
    assert schema == {
        "x-type": "button",
        "default": "2",
        "oneOf": [
            {
                "const": "1",
                "title": "Yes",
                "x-primary": True,
            },
            {
                "const": "2",
                "title": "No",
            },
        ],
    }


def test_button_schema_ids():
    schema = field2.get_schema({})
    assert schema == {
        "x-type": "button",
        "default": "a",
        "oneOf": [
            {
                "const": "a",
                "title": "1",
            },
            {
                "const": "2",
                "title": "2",
            },
        ],
    }


@pytest.mark.parametrize(
    "val, expected",
    (
        ("1", True),
        ("2", False),
    ),
)
def test_parse_button(val, expected):
    parser = create_response_parser("test", [field1])

    result = parser({"field_0": val}, {})
    assert result == {parse_pointer("option"): expected}


@pytest.mark.parametrize(
    "val, expected",
    (
        ("a", 1),
        ("2", 2),
    ),
)
def test_parse_button_ids(val, expected):
    parser = create_response_parser("test", [field2])

    result = parser({"field_0": val}, {})
    assert result == {parse_pointer("option"): expected}


@pytest.mark.parametrize(
    "val",
    (
        "3",
        1,
        "",
        None,
        True,
        False,
    ),
)
def test_parse_button_invalid(val):
    parser = create_response_parser("test", [field1])

    with pytest.raises(BaseValidationError):
        parser({"field_0": val}, {})


def test_parse_button_expr():
    field = Button(
        set=parse_pointer("option"),
        options=(
            ButtonOption(
                label=Template("Yes"),
                primary_expr=Expression("primary == 1"),
                value_expr=Expression("value1"),
            ),
            ButtonOption(
                label=Template("No"),
                default_expr=Expression("default == 2"),
                value_expr=Expression("value2"),
            ),
        ),
    )
    schema = field.get_schema({"primary": 1, "default": 2})
    assert schema["default"] == "2"
    assert schema["oneOf"][0]["x-primary"] is True  # type: ignore
    parser = create_response_parser("test", [field])
    assert parser({"field_0": "2"}, {"value2": "test"}) == {
        parse_pointer("option"): "test"
    }
