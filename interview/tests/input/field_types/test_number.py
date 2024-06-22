import pytest
from oes.interview.immutable import make_immutable
from oes.interview.input.field_types.number import NumberFieldTemplate


def test_number_field_schema():
    field = NumberFieldTemplate(
        label="Title",
        default=1,
        optional=True,
        integer=True,
        min=1,
        max=5,
        input_mode="number",
        autocomplete="number",
    ).get_field({})

    assert field.schema == make_immutable(
        {
            "type": ["integer", "null"],
            "x-type": "number",
            "title": "Title",
            "default": 1,
            "minimum": 1,
            "maximum": 5,
            "x-inputMode": "number",
            "x-autoComplete": "number",
        }
    )


@pytest.mark.parametrize(
    "value, valid, expected",
    [
        (1, True, 1),
        (5.5, False, None),
        (4.9, True, 4),
        (0, False, None),
        ("1", False, None),
        (None, False, None),
    ],
)
def test_number_field_validators(value, valid, expected):
    field = NumberFieldTemplate(
        min=1,
        max=5,
        integer=True,
    ).get_field({})
    if valid:
        assert field.parse(value) == expected
    else:
        with pytest.raises(ValueError):
            field.parse(value)
