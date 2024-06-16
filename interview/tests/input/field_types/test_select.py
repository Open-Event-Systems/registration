import pytest
from oes.interview.immutable import make_immutable
from oes.interview.input.field_types.select import (
    SelectFieldOption,
    SelectFieldTemplate,
)


def test_select_field_schema():
    field = SelectFieldTemplate(
        label="Title",
        component="checkbox",
        options=(
            SelectFieldOption(
                id="1",
                label="Option 1",
            ),
            SelectFieldOption(
                id="2",
                label="Option 2",
                default=True,
            ),
        ),
        min=0,
        max=1,
        autocomplete="test",
    ).get_field({})

    assert field.schema == make_immutable(
        {
            "type": ["string", "null"],
            "x-type": "select",
            "x-component": "checkbox",
            "title": "Title",
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
            "x-autoComplete": "test",
        }
    )


def test_select_field_schema_multi():
    field = SelectFieldTemplate(
        label="Title",
        component="checkbox",
        options=(
            SelectFieldOption(
                id="1",
                label="Option 1",
            ),
            SelectFieldOption(
                id="2",
                label="Option 2",
                default=True,
            ),
        ),
        min=1,
        max=2,
        autocomplete="test",
    ).get_field({})

    assert field.schema == make_immutable(
        {
            "type": "array",
            "x-type": "select",
            "x-component": "checkbox",
            "title": "Title",
            "default": ["2"],
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
                ],
            },
            "minItems": 1,
            "maxItems": 2,
            "uniqueItems": True,
            "x-autoComplete": "test",
        }
    )


def test_select_field_buttons_primary():
    field = SelectFieldTemplate(
        label="Title",
        component="buttons",
        options=(
            SelectFieldOption(
                id="1",
                label="Option 1",
            ),
            SelectFieldOption(
                id="2",
                label="Option 2",
                default=True,
                primary=True,
            ),
        ),
        min=0,
        max=1,
        autocomplete="test",
    ).get_field({})

    assert field.schema == make_immutable(
        {
            "type": ["string", "null"],
            "x-type": "select",
            "x-component": "buttons",
            "title": "Title",
            "default": "2",
            "oneOf": [
                {
                    "const": "1",
                    "title": "Option 1",
                },
                {
                    "const": "2",
                    "title": "Option 2",
                    "x-primary": True,
                },
                {"type": "null"},
            ],
            "x-autoComplete": "test",
        }
    )


@pytest.mark.parametrize(
    "value, valid, expected",
    [
        (None, False, None),
        (1, False, None),
        ("1", True, 1),
        ("2", True, 2),
        (["1"], False, None),
        ([1], False, None),
    ],
)
def test_select_field_validators(value, valid, expected):
    field = SelectFieldTemplate(
        options=(
            SelectFieldOption(
                id="1",
                label="Option 1",
                value=1,
            ),
            SelectFieldOption(
                id="2",
                label="Option 2",
                default=True,
                value=2,
            ),
        ),
        min=1,
        max=1,
    ).get_field({})

    if valid:
        assert field.parse(value) == expected
    else:
        with pytest.raises(ValueError):
            field.parse(value)


@pytest.mark.parametrize(
    "value, valid, expected",
    [
        (["1"], True, (1,)),
        (["2", "1"], True, (2, 1)),
        ([], False, None),
        (["1", "2", "3"], False, None),
        (["4"], False, None),
        ("1", False, None),
        (1, False, None),
        (None, False, None),
        ([1], False, None),
        ([None], False, None),
    ],
)
def test_select_field_validators_multi(value, valid, expected):
    field = SelectFieldTemplate(
        options=(
            SelectFieldOption(
                id="1",
                label="Option 1",
                value=1,
            ),
            SelectFieldOption(
                id="2",
                label="Option 2",
                default=True,
                value=2,
            ),
            SelectFieldOption(
                id="3",
                label="Option 3",
                value=3,
            ),
        ),
        min=1,
        max=2,
    ).get_field({})

    if valid:
        assert field.parse(value) == expected
    else:
        with pytest.raises(ValueError):
            field.parse(value)
