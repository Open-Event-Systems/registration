from oes.util import (
    ImmutableMapping,
    ImmutableSequence,
    make_immutable_mapping,
    merge_mapping,
)


def test_merge_mapping():
    a = {
        "a": {
            "b": 1,
        },
        "c": 2,
    }

    b = {"c": 3, "a": {"c": 3}, "d": {}}

    res = merge_mapping(a, b)
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


def test_merge_constructor():
    a = {
        "a": [1, 2, 3],
        "b": {"x": {"y"}},
    }
    b = {
        "b": {"y": True},
        "c": [4],
    }
    merged = merge_mapping(a, b, constructor=make_immutable_mapping)
    assert merged == {
        "a": (1, 2, 3),
        "b": {"x": frozenset(("y",)), "y": True},
        "c": (4,),
    }
    assert isinstance(merged, ImmutableMapping)
    assert isinstance(merged["a"], ImmutableSequence)
    assert isinstance(merged["b"], ImmutableMapping)
