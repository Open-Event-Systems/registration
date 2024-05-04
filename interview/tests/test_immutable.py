import pytest
from immutabledict import immutabledict
from oes.interview.immutable import make_immutable


@pytest.mark.parametrize(
    "obj, expected",
    [
        ([1, 2, 3], (1, 2, 3)),
        ("test", "test"),
        (b"test", b"test"),
        (1, 1),
        (True, True),
        (None, None),
        ({"a": "b", "c": "d"}, immutabledict({"a": "b", "c": "d"})),
        ({1, 2}, frozenset((1, 2))),
        (
            [1, [2, {"3": {"4": 5}}]],
            (1, (2, immutabledict({"3": immutabledict({"4": 5})}))),
        ),
    ],
)
def test_make_immutable(obj, expected):
    res = make_immutable(obj)
    assert res == expected
    hash(res)
