from oes.util import merge_dict


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
