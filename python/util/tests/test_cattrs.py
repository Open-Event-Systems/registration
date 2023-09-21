from typing import Optional

import pytest
from attrs import field, frozen, validators
from cattrs import BaseValidationError
from cattrs.preconf.json import make_converter
from oes.util.cattrs import ExceptionDetails, get_exception_details

pytest.importorskip("cattrs")


@frozen
class ClassB:
    b_val: int = field(validator=validators.ge(0))


@frozen
class ClassD:
    d_val: str


@frozen
class ClassC:
    c_val: int
    d: Optional[ClassD] = None


@frozen
class ClassA:
    b: ClassB
    c: list[ClassC]


converter = make_converter()


@pytest.mark.parametrize(
    "data, expected",
    (
        (
            {},
            (
                ExceptionDetails((), "A value is required for 'b'"),
                ExceptionDetails((), "A value is required for 'c'"),
            ),
        ),
        (
            {"b": {}, "c": [{}, {"c_val": 1, "d": {}}]},
            (
                ExceptionDetails(("b",), "A value is required for 'b_val'"),
                ExceptionDetails(("c", 0), "A value is required for 'c_val'"),
                ExceptionDetails(("c", 1, "d"), "A value is required for 'd_val'"),
            ),
        ),
        (
            {"b": {"b_val": -1}, "c": []},
            (ExceptionDetails(("b",), "'b_val' must be >= 0: -1"),),
        ),
    ),
)
def test_get_exception_details(data, expected):
    with pytest.raises(BaseValidationError) as err:
        converter.structure(data, ClassA)

    details = get_exception_details(err.value)

    assert details == list(expected)
