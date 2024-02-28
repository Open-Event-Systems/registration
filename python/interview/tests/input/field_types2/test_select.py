import pytest
from oes.interview.input.field_types2.select import SelectField, SelectOption


def test_select_field_schema():
    field = SelectField(
        label="Title",
        component="checkbox",
        options=(
            SelectOption(
                id="1",
                label="Option 1",
            ),
            SelectOption(
                id="2",
                label="Option 2",
                default=True,
            ),
        ),
        min=0,
        max=1,
        input_mode="test",
        autocomplete="test",
    )

    assert field.schema == {
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
        "x-input-mode": "test",
        "x-autocomplete": "test",
    }


def test_select_field_schema_multi():
    field = SelectField(
        label="Title",
        component="checkbox",
        options=(
            SelectOption(
                id="1",
                label="Option 1",
            ),
            SelectOption(
                id="2",
                label="Option 2",
                default=True,
            ),
        ),
        min=1,
        max=2,
        input_mode="test",
        autocomplete="test",
    )

    assert field.schema == {
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
        "x-input-mode": "test",
        "x-autocomplete": "test",
    }


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
    field = SelectField(
        options=(
            SelectOption(
                id="1",
                label="Option 1",
                value=1,
            ),
            SelectOption(
                id="2",
                label="Option 2",
                default=True,
                value=2,
            ),
        ),
        min=1,
        max=1,
    )

    if valid:
        assert field(value) == expected
    else:
        with pytest.raises(ValueError):
            field(value)


@pytest.mark.parametrize(
    "value, valid, expected",
    [
        (["1"], True, [1]),
        (["2", "1"], True, [2, 1]),
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
    field = SelectField(
        options=(
            SelectOption(
                id="1",
                label="Option 1",
                value=1,
            ),
            SelectOption(
                id="2",
                label="Option 2",
                default=True,
                value=2,
            ),
            SelectOption(
                id="3",
                label="Option 3",
                value=3,
            ),
        ),
        min=1,
        max=2,
    )

    if valid:
        assert field(value) == expected
    else:
        with pytest.raises(ValueError):
            field(value)
