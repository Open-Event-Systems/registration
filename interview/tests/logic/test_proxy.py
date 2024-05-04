from oes.interview.logic.pointer import Name, parse_pointer
from oes.interview.logic.proxy import ArrayProxy, ObjectProxy, make_proxy

_name = Name("test")


def test_object_proxy():
    obj = {"a": {"b": "c"}}
    proxy = make_proxy(_name, obj)
    assert isinstance(proxy, ObjectProxy)
    assert proxy["a"]["b"] == "c"


def test_object_eq():
    ptr = parse_pointer("a")
    obj = make_proxy(ptr, {"a": "b"})
    assert obj == {"a": "b"}
    assert {"a": "b"} == obj


def test_array_proxy():
    obj = {"a": ["0"]}

    outer = make_proxy(_name, obj)
    proxy = outer["a"]

    assert isinstance(proxy, ArrayProxy)
    assert proxy[0] == "0"


def test_array_add():
    ptr = parse_pointer("a")
    obj = make_proxy(ptr, [1, 2])
    added = obj + [3, 4]
    assert isinstance(added, ArrayProxy)

    radded = [0] + added
    assert isinstance(radded, ArrayProxy)


def test_array_eq():
    ptr = parse_pointer("a")
    obj = make_proxy(ptr, [1, 2])
    assert obj == [1, 2]
    assert [1, 2] == obj
