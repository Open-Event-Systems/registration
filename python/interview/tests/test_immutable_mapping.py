from oes.interview.immutable_mapping import ImmutableMapping


def test_hash():
    d1 = ImmutableMapping((("a", 1), ("b", 2)))
    d2 = ImmutableMapping((("b", 2), ("a", 1)))
    d3 = ImmutableMapping((("a", 1), ("b", 3)))
    d4 = ImmutableMapping((("a", 1), (2, "b")))
    d5 = ImmutableMapping((("b", 2), ("a", 1), ("b", 2)))
    assert hash(d1) == hash(d2)
    assert hash(d3) != hash(d1)
    assert hash(d4) != hash(d1)
    assert hash(d1) == hash(d5)


def test_eq():
    d1 = ImmutableMapping({"a": 1, "b": 2})
    d2 = ImmutableMapping((("b", 2), ("a", 1)))
    d3 = ImmutableMapping((("b", 2), ("a", 1), ("b", 2)))
    d4 = ImmutableMapping({"a": 1, "b": 1})
    d5 = ImmutableMapping({"a": 1, "b": 2, "c": 3})
    assert d1 == d2
    assert d1 == d3
    assert d1 != d4
    assert d1 != d5

    assert d2 == d1
    assert d3 == d1
    assert d4 != d1
    assert d5 != d1


def test_eq_dict():
    d1 = ImmutableMapping({"a": 1, "b": 2})

    assert d1 == {"b": 2, "a": 1}
    assert {"b": 2, "a": 1} == d1
    assert d1 != {"b": 3, "a": 1}
    assert {"b": 3, "a": 1} != d1


def test_or():
    d1 = ImmutableMapping({"a": 1, "b": 2})
    d2 = d1 | {"a": 0, "c": 3}
    assert isinstance(d2, ImmutableMapping)
    assert list(d2.items()) == [("a", 0), ("b", 2), ("c", 3)]
    assert d1 == {"a": 1, "b": 2}

    d3 = ImmutableMapping({"c": 3}) | d1
    assert isinstance(d3, ImmutableMapping)
    assert list(d3.items()) == [("c", 3), ("a", 1), ("b", 2)]
