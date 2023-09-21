"""Variable locator."""
from __future__ import annotations

import re
from abc import abstractmethod
from typing import Any, MutableMapping, Union

import pyparsing as pp
from attrs import frozen
from oes.template import Context, Evaluable
from typing_extensions import Protocol, TypeAlias

# Types


class InvalidLocatorError(ValueError):
    """Raised when a locator cannot be parsed."""

    pass


MutableContext: TypeAlias = MutableMapping[str, Any]
"""Mutable :class:`Context`."""


class Locator(Evaluable, Protocol):
    """A variable locator."""

    @abstractmethod
    def evaluate(self, __context: Context) -> object:
        """Return the value of this locator."""
        ...

    @abstractmethod
    def set(self, __value: object, __context: MutableContext):
        """Set the value at this locator."""
        ...

    @abstractmethod
    def compare(self, __other: Locator, __context: Context) -> bool:
        """Whether two locators are equal."""
        ...


@frozen(repr=False)
class Literal(Locator):
    """A literal value."""

    value: Union[str, int]

    def evaluate(self, context: Context) -> object:
        """Return the value of this locator."""
        return self.value

    def set(self, value: object, context: MutableContext):
        """Set the value at this locator."""
        raise TypeError("Cannot assign a literal")

    def compare(self, other: Locator, context: Context) -> bool:
        """Whether two locators are equal."""
        return isinstance(other, Literal) and other.value == self.value

    def __str__(self) -> str:
        if isinstance(self.value, str):
            escaped = self.value.replace('"', '\\"')
            return f'"{escaped}"'
        else:
            return str(self.value)

    def __repr__(self) -> str:
        return repr(self.value)


@frozen(repr=False)
class Variable(Locator):
    """A top-level variable."""

    name: str

    def evaluate(self, context: Context) -> object:
        """Return the value of this locator."""
        try:
            return context[self.name]
        except LookupError as e:
            raise UndefinedError(self) from e

    def set(self, value: object, context: MutableContext):
        """Set the value at this locator."""
        context[self.name] = value

    def compare(self, other: Locator, context: Context) -> bool:
        """Whether two locators are equal."""
        return isinstance(other, Variable) and other.name == self.name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


@frozen(repr=False)
class Index(Locator):
    """An index/property access, like ``a.b`` or ``a["b"]``."""

    target: Locator
    index: Union[str, int]

    def evaluate(self, context: Context) -> object:
        """Return the value of this locator."""
        target_val = self.target.evaluate(context)
        if hasattr(target_val, "__getitem__"):
            try:
                return target_val[self.index]
            except LookupError as e:
                raise UndefinedError(self) from e
        else:
            raise TypeError(f"Not a list/dict: {target_val}")

    def set(self, value: object, context: MutableContext):
        """Set the value at this locator."""
        target_val = self.target.evaluate(context)
        if hasattr(target_val, "__setitem__"):
            target_val[self.index] = value
        else:
            raise TypeError(f"Not a list/dict: {target_val}")

    def compare(self, other: Locator, context: Context) -> bool:
        """Whether two locators are equal."""
        if isinstance(other, ParametrizedIndex):
            return other.compare(self, context)
        else:
            return (
                isinstance(other, Index)
                and other.index == self.index
                and self.target.compare(other.target, context)
            )

    def __str__(self) -> str:
        return f"{self.target}{self._format()}"

    def __repr__(self) -> str:
        return f"{self.target!r}{self._format()}"

    def _format(self) -> str:
        if isinstance(self.index, str) and re.match(
            r"^[a-z0-9_]+$", self.index, flags=re.I
        ):
            return f".{self.index}"
        else:
            return f"[{Literal(self.index)}]"


@frozen(repr=False)
class ParametrizedIndex(Locator):
    """An index/property access with a variable, like ``a[n]``."""

    target: Locator
    index: Locator

    def evaluate_index(self, context: Context) -> Index:
        """Evaluate the ``index``, returning a :class:`Index`."""
        index_val = self.index.evaluate(context)
        if isinstance(index_val, (str, int)):
            return Index(self.target, index_val)
        else:
            raise TypeError(f"Not a valid index: {index_val}")

    def evaluate(self, context: Context) -> object:
        """Return the value of this locator."""
        return self.evaluate_index(context).evaluate(context)

    def set(self, value: object, context: MutableContext):
        """Set the value at this locator."""
        return self.evaluate_index(context).set(value, context)

    def compare(self, other: Locator, context: Context) -> bool:
        """Whether two locators are equal."""
        try:
            eval_ = self.evaluate_index(context)
        except LookupError:
            return False
        return eval_.compare(other, context)

    def __str__(self) -> str:
        return f"{self.target}[{self.index}]"

    def __repr__(self) -> str:
        return f"{self.target!r}[{self.index!r}]"


class UndefinedError(LookupError):
    """Exception raised when an undefined value is accessed."""

    locator: Locator

    def __init__(self, locator: Locator):
        self.locator = locator

    def __repr__(self) -> str:
        return f"UndefinedError({self.locator})"


# numbers
zero = pp.Literal("0")
non_zero_number = pp.Word("123456789", pp.nums)
number = zero | non_zero_number


@number.set_parse_action
def _parse_number(res: pp.ParseResults) -> Literal:
    return Literal(int(res[0]))


# A string literal
string_literal = pp.QuotedString(
    quote_char='"',
    esc_char="\\",
)


@string_literal.set_parse_action
def _parse_string_literal(res: pp.ParseResults) -> Literal:
    return Literal(res[0])


# A literal expression
literal = string_literal | number

# An identifier
name = pp.Regex(r"(?![0-9_])[a-z0-9_]+(?<!-)", re.I)

# A top-level variable
variable = name.copy()


@variable.set_parse_action
def _parse_variable(res: pp.ParseResults) -> Variable:
    return Variable(res[0])


name_literal = name.copy()


@name_literal.set_parse_action
def _parse_name_literal(res: pp.ParseResults) -> Literal:
    return Literal(res[0])


locator = pp.Forward()

property_access = "." + name_literal("index")
index_access = "[" + literal("index") + "]"
param_index_access = "[" + locator("index_param") + "]"

locator << variable + pp.Group(property_access | param_index_access | index_access)[...]


@locator.set_parse_action
def _parse_locator(res: pp.ParseResults) -> Locator:
    return _parse_locator_recursive(res[:-1], res[-1])


def _parse_locator_recursive(
    left: list[Union[Locator, pp.ParseResults]], right: Union[Locator, pp.ParseResults]
) -> Locator:
    if isinstance(right, pp.ParseResults):
        target = _parse_locator_recursive(left[:-1], left[-1])
        if "index_param" in right:
            return ParametrizedIndex(target, right["index_param"])
        else:
            return Index(target, right["index"].value)
    else:
        return right


def parse_locator(value: str) -> Locator:
    """Parse a :class:`Locator` from a string."""
    try:
        return locator.parse_string(value, parse_all=True)[0]
    except pp.ParseException as e:
        raise InvalidLocatorError(f"Invalid locator: {e}") from e
