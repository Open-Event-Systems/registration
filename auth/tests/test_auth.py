import pytest
from oes.auth.auth import Scopes


@pytest.mark.parametrize(
    "val, expected",
    [
        (("a", "b", "c"), frozenset({"a", "b", "c"})),
        ("a b  c", frozenset({"a", "b", "c"})),
        ("", frozenset()),
    ],
)
def test_scope_constructor(val, expected):
    res = Scopes(val)
    assert res == expected


@pytest.mark.parametrize(
    "val, expected",
    [
        (("c", "a", "b"), "a b c"),
        ((), ""),
    ],
)
def test_scope_str(val, expected):
    res = str(Scopes(val))
    assert res == expected
