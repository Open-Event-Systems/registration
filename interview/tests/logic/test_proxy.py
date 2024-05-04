from collections.abc import Mapping, Sequence

import pytest
from oes.interview.logic.proxy import (
    ArrayProxy,
    ObjectProxy,
    ProxyLookupError,
    make_proxy,
)


def test_object_proxy():
    obj = {"a": {"b": "c"}}
    proxy = make_proxy(obj)
    assert isinstance(proxy, ObjectProxy)
    assert proxy["a"]["b"] == "c"


def test_object_eq():
    obj = make_proxy({"a": "b"})
    assert obj == {"a": "b"}
    assert {"a": "b"} == obj


def test_obj_lookup_error():
    obj = make_proxy({"a": {"b": "c"}})
    with pytest.raises(ProxyLookupError) as err:
        obj["a"]["c"]
    assert err.value.path == ("a",)
    assert err.value.key == "c"


def test_array_proxy():
    obj = {"a": ["0"]}

    outer = make_proxy(obj)
    proxy = outer["a"]

    assert isinstance(proxy, ArrayProxy)
    assert proxy[0] == "0"


def test_array_add():
    obj = make_proxy([1, 2])
    added = obj + [3, 4]
    assert isinstance(added, ArrayProxy)

    radded = [0] + added
    assert isinstance(radded, ArrayProxy)


def test_array_eq():
    obj = make_proxy([1, 2])
    assert obj == [1, 2]
    assert [1, 2] == obj


def test_array_lookup_error():
    obj: Sequence = make_proxy([1, [2, [3]]])
    with pytest.raises(ProxyLookupError) as err:
        obj[1][1][1]
    assert err.value.path == (1, 1)
    assert err.value.key == 1


def test_nested_lookup_error():
    obj: Mapping = make_proxy({"a": [{"b": ["c"]}, {"b": ["d"]}]})
    with pytest.raises(ProxyLookupError) as err:
        obj["a"][1]["b"][2]
    assert err.value.path == ("a", 1, "b")
    assert err.value.key == 2

    with pytest.raises(ProxyLookupError) as err:
        obj["b"][1]["b"][2]
    assert err.value.path == ()
    assert err.value.key == "b"
