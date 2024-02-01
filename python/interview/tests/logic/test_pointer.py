import pytest
from oes.interview.logic.pointer import (
    InvalidPointerError,
    PointerSegment,
    _Parsing,
    parse_pointer_impl,
)
from oes.util import make_immutable


@pytest.mark.parametrize(
    "el, val, expected",
    [
        (_Parsing.constant, "0", 0),
        (_Parsing.constant, "100", 100),
        (_Parsing.constant, '"test"', "test"),
        (_Parsing.constant, '""', ""),
        (_Parsing.name, "test_val", "test_val"),
        (_Parsing.property_access, ".test", "test"),
        (_Parsing.index_access, "[0]", 0),
        (_Parsing.index_access, '["test"]', "test"),
        (_Parsing.pointer_segment, ".test", PointerSegment("test")),
        (_Parsing.pointer_segment, '["test"]', PointerSegment("test")),
        (_Parsing.pointer_segment, "[123]", PointerSegment(123)),
        (_Parsing.pointer, "a", (PointerSegment("a"),)),
        (_Parsing.pointer, "a.b", (PointerSegment("a"), PointerSegment("b"))),
        (_Parsing.pointer, "a[1]", (PointerSegment("a"), PointerSegment(1))),
    ],
)
def test_parser_elements(el, val, expected):
    res = el.parse_string(val, parse_all=True)
    assert res[0] == expected


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
        "a[b]",
        "a.1",
        "a . b",
        "a. b",
        "a .b",
        "a [0]",
    ],
)
def test_parse_invalid(val):
    with pytest.raises(InvalidPointerError):
        parse_pointer_impl(val)


@pytest.mark.parametrize(
    "val, expected",
    [
        ("a", 1),
        ("b", {"x": 2}),
        ("b.x", 2),
        ('b["x"]', 2),
        ("c[1]", 2),
        (" a ", 1),
        (" b.x ", 2),
        ("c[ 0 ]", 1),
        ('b[ "x" ]', 2),
    ],
)
def test_parse_and_eval_pointer(val, expected):
    ctx = {
        "a": 1,
        "b": {"x": 2},
        "c": [1, 2],
    }
    ptr = parse_pointer_impl(val)
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
    ],
)
def test_set(ctx, ptr, val, expected):
    parsed = parse_pointer_impl(ptr)

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
    parsed = parse_pointer_impl(val)
    assert str(parsed) == val
