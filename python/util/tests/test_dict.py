from oes.util import immutable_dict, make_immutable, merge_dict
from oes.util.dict import _ImmutableDict


def test_merge_dict():
    a = {
        "a": {
            "b": 1,
        },
        "c": 2,
    }

    b = {"c": 3, "a": {"c": 3}, "d": {}}

    res = merge_dict(a, b)
    assert res == {
        "a": {
            "b": 1,
            "c": 3,
        },
        "c": 3,
        "d": {},
    }

    res["a"]["b"] = 2
    res["d"]["x"] = 2

    assert a == {
        "a": {
            "b": 1,
        },
        "c": 2,
    }

    assert b == {"c": 3, "a": {"c": 3}, "d": {}}


def test_immutable_dict():
    d1 = immutable_dict({"a": 1})
    d2 = immutable_dict({"a": 1})
    d3 = immutable_dict({"b": 2})
    assert d1 == d2
    assert d1 != d3
    assert d1 == {"a": 1}
    assert hash(d1) == hash(d2)


def test_make_immutable():
    data = {"a": [1, 2], "b": {3, 4}, "c": {"d": [["e"], {"f"}]}}
    res = make_immutable(data)
    assert isinstance(res, _ImmutableDict)
    assert isinstance(res["c"], _ImmutableDict)
    assert res == {
        "a": (1, 2),
        "b": frozenset({3, 4}),
        "c": {"d": (("e",), frozenset("f"))},
    }
