import pytest
from oes.interview.immutable import make_immutable
from oes.interview.logic.pointer import InvalidPointerError, get_path, parse_pointer


@pytest.mark.parametrize(
    "val",
    [
        "123",
        '"str"',
        "",
        "a-b",
        "a[01]",
        "a[00]",
        "a.b.",
        ".a",
        ".",
        "a.[1]",
        "a.1",
        "a . b",
        "a. b",
        "a .b",
        "a [0]",
    ],
)
def test_parse_invalid(val):
    with pytest.raises(InvalidPointerError):
        parse_pointer(val)


@pytest.mark.parametrize(
    "val, expected",
    [
        ("a", 1),
        ("b", {"x": 2, "z": "z"}),
        ("b.x", 2),
        ('b["x"]', 2),
        ("c[1]", 2),
        (" a ", 1),
        (" b.x ", 2),
        ("c[ 0 ]", 1),
        ('b[ "x" ]', 2),
        ("c[a]", 2),
        ("b[b.z]", "z"),
    ],
)
def test_parse_and_eval_pointer(val, expected):
    ctx = {
        "a": 1,
        "b": {"x": 2, "z": "z"},
        "c": [1, 2],
    }
    ptr = parse_pointer(val)
    assert ptr.evaluate(ctx) == expected


@pytest.mark.parametrize(
    "ctx, ptr, val, expected",
    [
        ({}, "test", "x", {"test": "x"}),
        ({"test": "x"}, "test", "y", {"test": "y"}),
        ({"a": [0, 1]}, "a[1]", 2, {"a": [0, 2]}),
        ({"a": [0, 1]}, "a", [1, 2], {"a": [1, 2]}),
        ({"a": {"b": 1}}, "a.b", 2, {"a": {"b": 2}}),
        ({"a": {"b": 1}}, "a.c", 2, {"a": {"b": 1, "c": 2}}),
        ({"a": {"b": 1}}, "a", {}, {"a": {}}),
        ({"a": {"b": 1}, "p": "b"}, "a[p]", 2, {"a": {"b": 2}, "p": "b"}),
    ],
)
def test_set(ctx, ptr, val, expected):
    parsed = parse_pointer(ptr)

    ctx = make_immutable(ctx)
    val = make_immutable(val)
    expected = make_immutable(expected)

    updated = parsed.set(ctx, val)
    assert updated == expected
    assert updated != ctx


@pytest.mark.parametrize(
    "val",
    [
        "a",
        "a.b",
        'a["b-c"]',
        'a["123"]',
        'a["0"]',
        "a[0][1]",
        'a.b[0].c["d-e"].f',
        'a["\\"quot\\""]',
        'a["esc\\\\"]',
    ],
)
def test_str(val):
    parsed = parse_pointer(val)
    assert str(parsed) == val


@pytest.mark.parametrize(
    "ptr, expected",
    [
        ("a", ("a",)),
        ("a.b", ("a", "b")),
        ("a[1].b[2].c", ("a", 1, "b", 2, "c")),
        ("a[b][0]", ("a", parse_pointer("b"), 0)),
        ("a[b.c[d]][e]", ("a", parse_pointer("b.c[d]"), parse_pointer("e"))),
    ],
)
def test_get_path(ptr, expected):
    parsed = parse_pointer(ptr)
    assert get_path(parsed) == expected
