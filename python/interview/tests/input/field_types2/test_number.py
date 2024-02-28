import pytest
from oes.interview.input.field_types2.number import NumberField


def test_number_field_schema():
    field = NumberField(
        label="Title",
        default=1,
        optional=True,
        integer=True,
        min=1,
        max=5,
        input_mode="number",
        autocomplete="number",
    )

    assert field.schema == {
        "type": ["integer", "null"],
        "x-type": "number",
        "title": "Title",
        "default": 1,
        "minimum": 1,
        "maximum": 5,
        "x-input-mode": "number",
        "x-autocomplete": "number",
    }


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
    field = NumberField(
        min=1,
        max=5,
        integer=True,
    )
    if valid:
        assert field(value) == expected
    else:
        with pytest.raises(ValueError):
            field(value)
