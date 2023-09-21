from dataclasses import dataclass

import pytest

try:
    from attrs import define
except ImportError:
    pytest.skip("attrs missing", allow_module_level=True)

from oes.util import is_attrs_class, is_attrs_instance


@define
class MyClass:
    a: int


@define
class MyClass2(MyClass):
    b: int


@dataclass
class MyDataclass:
    pass


@pytest.mark.parametrize(
    "obj, expected",
    (
        (None, False),
        (object, False),
        (MyClass, True),
        (MyClass2, True),
        (MyClass(1), False),
        (MyDataclass, False),
    ),
)
def test_is_attrs_class(obj, expected):
    assert is_attrs_class(obj) == expected


@pytest.mark.parametrize(
    "obj, expected",
    (
        (None, False),
        (object(), False),
        (MyClass, False),
        (MyClass2, False),
        (MyClass(1), True),
        (MyClass2(1, 2), True),
        (MyDataclass(), False),
    ),
)
def test_is_attrs_instance(obj, expected):
    assert is_attrs_instance(obj) == expected
