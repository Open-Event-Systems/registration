import pytest
from cattrs import BaseValidationError
from oes.interview.input.field_types.button import Button, ButtonOption
from oes.interview.input.response import create_response_parser
from oes.interview.variables.locator import parse_locator
from oes.template import Template

field1 = Button(
    set=parse_locator("option"),
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
    set=parse_locator("option"),
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

    result = parser({"field_0": val})
    assert result == {parse_locator("option"): expected}


@pytest.mark.parametrize(
    "val, expected",
    (
        ("a", 1),
        ("2", 2),
    ),
)
def test_parse_button_ids(val, expected):
    parser = create_response_parser("test", [field2])

    result = parser({"field_0": val})
    assert result == {parse_locator("option"): expected}


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
        parser({"field_0": val})
