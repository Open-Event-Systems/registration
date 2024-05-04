import pytest
from oes.interview.immutable import make_immutable
from oes.interview.input.field_types.text import TextFieldTemplate, TextFormatType
from oes.interview.logic.pointer import parse_pointer


def test_text_field_schema():
    field = TextFieldTemplate(
        set=parse_pointer("field"),
        label="Title",
        default="Test",
        optional=True,
        min=2,
        max=10,
        regex_js="test",
        input_mode="number",
        autocomplete="username",
    ).get_field({})

    assert field.schema == make_immutable(
        {
            "type": ["string", "null"],
            "x-type": "text",
            "title": "Title",
            "default": "Test",
            "minLength": 2,
            "maxLength": 10,
            "pattern": "test",
            "x-input-mode": "number",
            "x-autocomplete": "username",
        }
    )


@pytest.mark.parametrize(
    "value, valid, expected",
    [
        ("", False, None),
        ("test", True, "test"),
        ("  test  ", True, "test"),
        ("  a   ", False, None),
        ("               test    ", True, "test"),
        (123, False, None),
        (None, False, None),
        ("abcdefghijlmnop", False, None),
        ("test1", False, None),
    ],
)
def test_text_field_validators(value, valid, expected):
    field = TextFieldTemplate(
        min=2,
        max=10,
        regex=r"^[a-zA-Z]*$",
    ).get_field({})

    if valid:
        assert field.parse(value) == expected
    else:
        with pytest.raises(ValueError):
            field.parse(value)


@pytest.mark.parametrize(
    "value, valid",
    [
        ("test@test.com", True),
        ("test@test.co.uk", True),
        ("test@test.con", False),
        ("test@test.", False),
        ("test@test", False),
        ("@test", False),
    ],
)
def test_text_field_format_validators(value, valid):
    field = TextFieldTemplate(
        format=TextFormatType.email,
    ).get_field({})

    if valid:
        field.parse(value)
    else:
        with pytest.raises(ValueError):
            field.parse(value)
