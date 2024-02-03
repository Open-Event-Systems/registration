import pytest
from oes.interview.logic.pointer import InvalidPointerError, parse_pointer
from oes.util import make_immutable


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
        parse_pointer(val)


_TYPING_INTERNALS = [
    "__parameters__",
    "__orig_bases__",
    "__orig_class__",
    "_is_protocol",
    "_is_runtime_protocol",
]

_SPECIAL_NAMES = [
    "__abstractmethods__",
    "__annotations__",
    "__dict__",
    "__doc__",
    "__init__",
    "__module__",
    "__new__",
    "__slots__",
    "__subclasshook__",
    "__weakref__",
    "__class_getitem__",
]

# These special attributes will be not collected as protocol members.
EXCLUDED_ATTRIBUTES = _TYPING_INTERNALS + _SPECIAL_NAMES + ["_MutableMapping__marker"]


def _get_protocol_attrs(cls):
    """Collect protocol members from a protocol class objects.

    This includes names actually defined in the class dictionary, as well
    as names that appear in annotations. Special names (above) are skipped.
    """
    attrs = set()
    for base in cls.__mro__[:-1]:  # without object
        if base.__name__ in ("Protocol", "Generic"):
            continue
        annotations = getattr(base, "__annotations__", {})
        for attr in list(base.__dict__.keys()) + list(annotations.keys()):
            if not attr.startswith("_abc_") and attr not in EXCLUDED_ATTRIBUTES:
                attrs.add(attr)
    return attrs


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
