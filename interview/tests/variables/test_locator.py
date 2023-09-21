import pytest
from oes.interview.variables.locator import (
    Index,
    InvalidLocatorError,
    Literal,
    ParametrizedIndex,
    Variable,
    literal,
    parse_locator,
    variable,
)
from pyparsing import ParseException


@pytest.mark.parametrize(
    "token, val, expected",
    (
        (literal, "0", Literal(0)),
        (literal, "1230", Literal(1230)),
        (literal, '""', Literal("")),
        (literal, '"test \\"string\\""', Literal('test "string"')),
        (variable, "test", Variable("test")),
        (variable, "test_var", Variable("test_var")),
        (variable, "test_var_", Variable("test_var_")),
    ),
)
def test_parse_tokens(token, val, expected):
    result = token.parse_string(val, parse_all=True)
    assert list(result) == [expected]


@pytest.mark.parametrize(
    "token, val",
    (
        (literal, "0123"),
        (literal, ""),
        (literal, '"test'),
        (literal, 'test"'),
        (literal, "''"),
        (variable, "_invalid"),
        (variable, "invalid-var"),
        (variable, "-invalid-var"),
        (variable, "invalid-var-"),
    ),
)
def test_parse_tokens_error(token, val):
    with pytest.raises(ParseException):
        token.parse_string(val, parse_all=True)


@pytest.mark.parametrize(
    "val, expected",
    (
        ("var", Variable("var")),
        ("a.b", Index(Variable("a"), "b")),
        ('a["b"]', Index(Variable("a"), "b")),
        ("a[0]", Index(Variable("a"), 0)),
        ("a[123]", Index(Variable("a"), 123)),
        ("a[b]", ParametrizedIndex(Variable("a"), Variable("b"))),
        ('a[b]["c"]', Index(ParametrizedIndex(Variable("a"), Variable("b")), "c")),
        ("a[b].c", Index(ParametrizedIndex(Variable("a"), Variable("b")), "c")),
        (
            "a[b[c]]",
            ParametrizedIndex(
                Variable("a"), ParametrizedIndex(Variable("b"), Variable("c"))
            ),
        ),
        ("a[ 0 ].b", Index(Index(Variable("a"), 0), "b")),
    ),
)
def test_parse_locator(val, expected):
    result = parse_locator(val)
    assert result == expected


@pytest.mark.parametrize(
    "val",
    (
        "bad var",
        "-bad-var",
        "bad-var-",
        "0",
        "123",
        "a.[b]",
        "a[b c]",
        "a[b.]",
    ),
)
def test_parse_locator_error(val):
    with pytest.raises(InvalidLocatorError):
        parse_locator(val)


@pytest.mark.parametrize(
    "val, expected",
    (
        ("f", True),
        ("a.b", [0, 1]),
        ('a["c"]', 2),
        ("d[a.b[0]].e", "c"),
        ("d[a.b[1]].e", "b"),
        ('a[d[1]["e"]][1]', 1),
    ),
)
def test_evaluate_locator(val, expected):
    doc = {
        "a": {"b": [0, 1], "c": 2},
        "d": [{"e": "c"}, {"e": "b"}],
        "f": True,
    }
    res = parse_locator(val)
    assert res.evaluate(doc) == expected


def test_set_locator():
    doc = {
        "a": {"b": [0, 1], "c": 2},
        "d": [{"e": "c"}, {"e": "b"}],
        "f": True,
    }

    loc = parse_locator('a[d[a.b[0]]["e"]]')
    loc.set("test", doc)
    assert doc["a"]["c"] == "test"


@pytest.mark.parametrize(
    "a, b, expected",
    (
        ("a", "a", True),
        ("a", "b", False),
        ("a[0]", "a[0]", True),
        ("a[0]", "a[1]", False),
        ("a[0]", "a[c]", True),
        ("a[1]", "a[c]", False),
    ),
)
def test_locator_compare(a, b, expected):
    a = parse_locator(a)
    b = parse_locator(b)

    doc = {
        "a": [0, 1],
        "b": "c",
        "c": 0,
    }

    assert a.compare(b, doc) == expected


@pytest.mark.parametrize(
    "val",
    (
        "a",
        "a.b",
        'a["b"]',
        'a["an \\"escaped\\" string"]',
        'a["b-c"]',
        "a[0]",
        'a[1][2].b[c].d[ "e"]',
    ),
)
def test_str_can_be_parsed(val):
    loc = parse_locator(val)
    as_str = str(loc)
    parsed = parse_locator(as_str)
    assert loc == parsed
    new_str = str(parsed)
    assert as_str == new_str
