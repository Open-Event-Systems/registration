import pytest
from cattrs import BaseValidationError
from oes.interview.input.field_types.select import SelectField, SelectFieldOption
from oes.interview.input.response import create_response_parser
from oes.interview.variables.locator import parse_locator
from oes.template import Template

field_single = SelectField(
    set=parse_locator("option"),
    component="radio",
    options=(
        SelectFieldOption(
            label=Template("Option 1"),
            value=1,
        ),
        SelectFieldOption(
            label=Template("Option 2"),
            value=2,
            default=True,
        ),
    ),
)

field_single_optional = SelectField(
    set=parse_locator("option"),
    min=0,
    component="checkbox",
    options=(
        SelectFieldOption(
            label=Template("Option 1"),
            value=1,
        ),
        SelectFieldOption(
            label=Template("Option 2"),
            value=2,
            default=True,
        ),
    ),
)

field_multi = SelectField(
    set=parse_locator("option"),
    min=1,
    max=2,
    options=(
        SelectFieldOption(
            label=Template("Option 1"),
            value=1,
        ),
        SelectFieldOption(
            label=Template("Option 2"),
            value=2,
            default=True,
        ),
        SelectFieldOption(
            label=Template("Option 3"),
            value=3,
            default=True,
        ),
    ),
)

field_multi_optional = SelectField(
    set=parse_locator("option"),
    min=0,
    max=2,
    options=(
        SelectFieldOption(
            label=Template("Option 1"),
            value=1,
        ),
        SelectFieldOption(
            label=Template("Option 2"),
            value=2,
            default=True,
        ),
        SelectFieldOption(
            label=Template("Option 3"),
            value=3,
            default=True,
        ),
    ),
)


def test_select_schema():
    schema = field_single.get_schema({})
    assert schema == {
        "type": "string",
        "x-type": "select",
        "x-component": "radio",
        "default": "2",
        "oneOf": [
            {
                "const": "1",
                "title": "Option 1",
            },
            {
                "const": "2",
                "title": "Option 2",
            },
        ],
        "nullable": False,
    }


def test_optional_select_schema():
    schema = field_single_optional.get_schema({})
    assert schema == {
        "type": "string",
        "x-type": "select",
        "x-component": "checkbox",
        "default": "2",
        "oneOf": [
            {
                "const": "1",
                "title": "Option 1",
            },
            {
                "const": "2",
                "title": "Option 2",
            },
            {"type": "null"},
        ],
        "nullable": True,
    }


def test_multi_select_schema():
    schema = field_multi.get_schema({})
    assert schema == {
        "type": "array",
        "x-type": "select",
        "x-component": "dropdown",
        "default": ["2", "3"],
        "items": {
            "oneOf": [
                {
                    "const": "1",
                    "title": "Option 1",
                },
                {
                    "const": "2",
                    "title": "Option 2",
                },
                {
                    "const": "3",
                    "title": "Option 3",
                },
            ],
        },
        "minItems": 1,
        "maxItems": 2,
        "uniqueItems": True,
    }


def test_multi_select_optional_schema():
    schema = field_multi_optional.get_schema({})
    assert schema == {
        "type": "array",
        "x-type": "select",
        "x-component": "dropdown",
        "default": ["2", "3"],
        "items": {
            "oneOf": [
                {
                    "const": "1",
                    "title": "Option 1",
                },
                {
                    "const": "2",
                    "title": "Option 2",
                },
                {
                    "const": "3",
                    "title": "Option 3",
                },
            ],
        },
        "minItems": 0,
        "maxItems": 2,
        "uniqueItems": True,
    }


@pytest.mark.parametrize(
    "field, val, expected",
    (
        (field_single, "1", 1),
        (field_single, "2", 2),
        (field_single_optional, None, None),
        (field_multi, ["1", "3"], [1, 3]),
        (field_multi_optional, [], []),
    ),
)
def test_select_field(field, val, expected):
    parser = create_response_parser("test", [field])

    result = parser({"field_0": val})
    assert result == {parse_locator("option"): expected}


@pytest.mark.parametrize(
    "field, val",
    (
        (field_single, None),
        (field_single, "4"),
        (field_single_optional, "4"),
        (field_multi, []),
        (field_multi, [1]),
        (field_multi, ["1", None]),
        (field_multi, ["1", "4"]),
        (field_multi_optional, None),
        (field_multi_optional, [None]),
    ),
)
def test_select_field_invalid(field, val):
    parser = create_response_parser("test", [field])

    with pytest.raises(BaseValidationError):
        parser({"field_0": val})


def test_boolean_schema():
    field = SelectField(
        min=0,
        max=1,
        component="checkbox",
        options=[
            SelectFieldOption(
                label=Template("Enable"),
                value=True,
            )
        ],
    )

    assert field.get_schema({}) == {
        "type": "string",
        "x-type": "select",
        "x-component": "checkbox",
        "nullable": True,
        "oneOf": [
            {
                "const": "1",
                "title": "Enable",
            },
            {"type": "null"},
        ],
    }


@pytest.mark.parametrize(
    "val, valid, expected",
    [
        ("1", True, True),
        (None, True, None),
        ("2", False, None),
        ("True", False, None),
    ],
)
def test_boolean(val, valid, expected):
    parser = create_response_parser(
        "test",
        [
            SelectField(
                set=parse_locator("value"),
                min=0,
                max=1,
                options=[
                    SelectFieldOption(
                        label=Template("Enable"),
                        value=True,
                    )
                ],
            )
        ],
    )

    if valid:
        assert parser({"field_0": val}) == {parse_locator("value"): expected}
    else:
        with pytest.raises(BaseValidationError):
            parser({"field_0": val})
