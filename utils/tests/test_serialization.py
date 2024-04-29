from collections.abc import Sequence
from datetime import datetime, timezone
from uuid import UUID

import pytest
from cattrs import Converter
from oes.utils.serialization import configure_converter


@pytest.fixture
def converter():
    converter = Converter()
    configure_converter(converter)
    return converter


@pytest.mark.parametrize(
    "obj, typ, expected",
    [
        (
            "2020-01-01T12:00:00+00:00",
            datetime,
            datetime(2020, 1, 1, 12, tzinfo=timezone.utc),
        ),
        (
            "2020-01-01T12:00:00Z",
            datetime,
            datetime(2020, 1, 1, 12, tzinfo=timezone.utc),
        ),
        (
            "2020-01-01T12:00:00",
            datetime,
            datetime(2020, 1, 1, 12).astimezone(),
        ),
        (
            datetime(2020, 1, 1, 12).astimezone(),
            datetime,
            datetime(2020, 1, 1, 12).astimezone(),
        ),
        (
            "aa0259f0-da3c-42b7-b4f5-8997de4d161c",
            UUID,
            UUID("aa0259f0-da3c-42b7-b4f5-8997de4d161c"),
        ),
        (
            UUID("aa0259f0-da3c-42b7-b4f5-8997de4d161c"),
            UUID,
            UUID("aa0259f0-da3c-42b7-b4f5-8997de4d161c"),
        ),
        ([1, 2, 3], Sequence[int], (1, 2, 3)),
    ],
)
def test_serialization_structure(converter: Converter, obj, typ, expected):
    res = converter.structure(obj, typ)
    assert res == expected


@pytest.mark.parametrize(
    "obj, expected",
    [
        (datetime(2020, 1, 1, 12, tzinfo=timezone.utc), "2020-01-01T12:00:00+00:00"),
        (
            UUID("aa0259f0-da3c-42b7-b4f5-8997de4d161c"),
            "aa0259f0-da3c-42b7-b4f5-8997de4d161c",
        ),
    ],
)
def test_serialization_unstructure(converter: Converter, obj, expected):
    res = converter.unstructure(obj)
    assert res == expected
