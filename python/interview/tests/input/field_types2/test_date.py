from datetime import date

import pytest
from oes.interview.input.field_types2.date import DateField


def test_date_field_schema():
    field = DateField(
        label="Title",
        default=date(2020, 1, 1),
        optional=True,
        min=date(1990, 1, 1),
        max=date(2030, 1, 1),
        input_mode="date",
        autocomplete="date",
    )

    assert field.schema == {
        "type": ["string", "null"],
        "x-type": "date",
        "format": "date",
        "title": "Title",
        "default": "2020-01-01",
        "x-minimum": "1990-01-01",
        "x-maximum": "2030-01-01",
        "x-input-mode": "date",
        "x-autocomplete": "date",
    }


@pytest.mark.parametrize(
    "value, valid, expected",
    [
        ("", False, None),
        (None, False, None),
        ("2020-13-01", False, None),
        ("2020-01-01", True, date(2020, 1, 1)),
        ("1989-12-31", False, None),
        ("2030-01-02", False, None),
    ],
)
def test_date_field_validators(value, valid, expected):
    field = DateField(
        min=date(1990, 1, 1),
        max=date(2030, 1, 1),
    )
    if valid:
        assert field(value) == expected
    else:
        with pytest.raises(ValueError):
            field(value)
