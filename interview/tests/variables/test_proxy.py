from oes.interview.variables.locator import parse_locator
from oes.interview.variables.proxy import SequenceProxy


def test_proxy_sequence_equality():
    proxy = SequenceProxy(parse_locator("test"), [1, 2, 3])
    assert proxy == (1, 2, 3)
    assert proxy != (1, 3, 2)
    assert proxy != (1, 2, 3, 4)
    assert proxy == [1, 2, 3]
    assert (1, 2, 3) == proxy
    assert [1, 2, 3] == proxy


def test_proxy_sequence_add():
    proxy = SequenceProxy(parse_locator("test"), [1, 2, 3])
    new = proxy + [4]
    assert list(new) == [1, 2, 3, 4]
    new2 = [0] + proxy
    assert list(new2) == [0, 1, 2, 3]
