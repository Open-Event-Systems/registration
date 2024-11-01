import pytest
from oes.utils.mapping import merge_mapping


class _MyDict(dict):
    def __eq__(self, other):
        if not isinstance(other, _MyDict):
            return False
        return super().__eq__(other)


@pytest.mark.parametrize(
    "a, b, factory, expected",
    [
        ({"a": True}, {"b": False}, dict, {"a": True, "b": False}),
        ({"a": True}, {"a": False, "b": False}, dict, {"a": False, "b": False}),
        (
            {"a": {"b": True}},
            {"a": {"c": True}, "b": False},
            dict,
            {"a": {"b": True, "c": True}, "b": False},
        ),
        (
            {"a": {"b": True}},
            {"a": {"b": False, "c": True}, "b": False},
            dict,
            {"a": {"b": False, "c": True}, "b": False},
        ),
        (
            {"a": 123},
            {"a": {"b": False, "c": True}, "b": False},
            dict,
            {"a": {"b": False, "c": True}, "b": False},
        ),
        ({"a": {"b": True}}, {"a": 123, "b": False}, dict, {"a": 123, "b": False}),
        (
            {"a": {"b": True}},
            {"a": {"b": False, "c": True}, "b": False},
            _MyDict,
            _MyDict({"a": _MyDict({"b": False, "c": True}), "b": False}),
        ),
    ],
)
def test_mapping(a, b, factory, expected):
    merged = merge_mapping(a, b, factory=factory)
    assert merged == expected
