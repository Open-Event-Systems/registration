from oes.util.immutable import (
    ImmutableMapping,
    ImmutableSequence,
    make_immutable,
    make_immutable_mapping,
)


def test_immutable_sequence():
    seq = make_immutable([1, 2, 3])
    assert seq == (1, 2, 3)


def test_immutable_sequence_add():
    seq = make_immutable([1, 2, 3])
    new = seq + (4,)
    assert seq == (1, 2, 3)
    assert new == (1, 2, 3, 4)
    assert isinstance(new, ImmutableSequence)


def test_immutable_mapping():
    m = make_immutable({"a": 1, "b": 2})
    assert m == {"a": 1, "b": 2}


def test_immutable_mapping_tuples():
    m = make_immutable_mapping((("a", 1), ("b", 2)))
    assert m == {"a": 1, "b": 2}


def test_immutable_mapping_or():
    m = make_immutable({"a": 1, "b": 2})
    m2 = m | {"b": 3, "c": 4}
    assert m == {"a": 1, "b": 2}
    assert m2 == {"a": 1, "b": 3, "c": 4}
    assert isinstance(m2, ImmutableMapping)


def test_make_immutable():
    data = {"a": [1, 2], "b": {3, 4}, "c": {"d": [["e"], {"f"}]}}
    res = make_immutable(data)
    assert isinstance(res, ImmutableMapping)
    assert isinstance(res["c"], ImmutableMapping)
    assert isinstance(res["a"], ImmutableSequence)
    assert isinstance(res["c"]["d"], ImmutableSequence)
    assert isinstance(res["c"]["d"][0], ImmutableSequence)
    assert res == {
        "a": (1, 2),
        "b": frozenset({3, 4}),
        "c": {"d": (("e",), frozenset("f"))},
    }
