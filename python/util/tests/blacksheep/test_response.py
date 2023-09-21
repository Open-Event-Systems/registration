import pytest
from blacksheep.exceptions import NotFound
from oes.util.blacksheep import JSONResponseFunc
from oes.util.blacksheep.response import check_404


class Custom:
    pass


def _default(obj: object) -> object:
    if isinstance(obj, Custom):
        return "123"
    else:
        raise TypeError


def test_json_response():
    json_response = JSONResponseFunc(default=_default)

    response = json_response(
        {"a": 1, "b": Custom()}, headers=((b"a", b"b"),), status_code=201
    )
    assert response.status == 201
    assert dict(response.headers) == {b"a": (b"b",)}
    assert response.content.body == b'{"a":1,"b":"123"}'


def test_check_404():
    obj = object()
    assert check_404(obj) is obj

    with pytest.raises(NotFound):
        check_404(None)
