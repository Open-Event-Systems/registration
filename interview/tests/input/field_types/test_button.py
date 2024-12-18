import pytest
from oes.interview.immutable import make_immutable
from oes.interview.input.field_types.button import (
    ButtonFieldOption,
    ButtonFieldTemplate,
)


def test_button_field_schema():
    field = ButtonFieldTemplate(
        label="Title",
        options=(
            ButtonFieldOption(
                id="1",
                label="Option 1",
                primary=True,
                default=True,
            ),
            ButtonFieldOption(
                id="2",
                label="Option 2",
            ),
        ),
    ).get_field({})

    assert field.schema == make_immutable(
        {
            "type": "string",
            "x-type": "button",
            "title": "Title",
            "default": "1",
            "oneOf": [
                {
                    "const": "1",
                    "title": "Option 1",
                    "x-primary": True,
                },
                {
                    "const": "2",
                    "title": "Option 2",
                },
            ],
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
def test_button_field_validators(value, valid, expected):
    field = ButtonFieldTemplate(
        options=(
            ButtonFieldOption(
                id="1",
                label="Option 1",
                value=1,
            ),
            ButtonFieldOption(
                id="2",
                label="Option 2",
                default=True,
                value=2,
            ),
        ),
    ).get_field({})

    if valid:
        assert field.parse(value) == expected
    else:
        with pytest.raises(ValueError):
            field.parse(value)
