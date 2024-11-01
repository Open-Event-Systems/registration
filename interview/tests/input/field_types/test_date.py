from datetime import date

import pytest
from oes.interview.immutable import make_immutable
from oes.interview.input.field_types.date import DateFieldTemplate


def test_date_field_schema():
    field = DateFieldTemplate(
        label="Title",
        default=date(2020, 1, 1),
        optional=True,
        min=date(1990, 1, 1),
        max=date(2030, 1, 1),
        input_mode="date",
        autocomplete="date",
    ).get_field({})

    assert field.schema == make_immutable(
        {
            "type": ["string", "null"],
            "x-type": "date",
            "format": "date",
            "title": "Title",
            "default": "2020-01-01",
            "x-minDate": "1990-01-01",
            "x-maxDate": "2030-01-01",
            "x-inputMode": "date",
            "x-autoComplete": "date",
        }
    )


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
    field = DateFieldTemplate(
        min=date(1990, 1, 1),
        max=date(2030, 1, 1),
    ).get_field({})
    if valid:
        assert field.parse(value) == expected
    else:
        with pytest.raises(ValueError):
            field.parse(value)
