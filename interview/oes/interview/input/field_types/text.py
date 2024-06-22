"""Text field type."""

import re
from collections.abc import Callable, Iterator, Mapping
from enum import Enum
from typing import Any, Literal

from attrs import frozen
from cattrs import Converter
from email_validator import EmailNotValidError, validate_email
from oes.interview.input.field_template import FieldTemplateBase
from oes.utils.template import Expression, TemplateContext
from publicsuffixlist import PublicSuffixList

DEFAULT_MAX_LEN = 300
"""The default string max length."""


class TextFormatType(str, Enum):
    """Text format type IDs."""

    email = "email"


@frozen
class TextFieldTemplate(FieldTemplateBase):
    """Text field template."""

    @property
    def python_type(self) -> type[str]:
        return str

    type: Literal["text"] = "text"
    optional: bool = False
    default: str | None = None
    default_expr: Expression | None = None
    min: int = 1
    max: int = 300
    regex: str | None = None
    regex_js: str | None = None
    format: str | None = None

    input_mode: str | None = None
    autocomplete: str | None = None

    @property
    def is_optional(self) -> bool:
        return self.optional

    def get_schema(self, context: TemplateContext) -> dict[str, Any]:
        schema = {
            **super().get_schema(context),
            "type": ["string", "null"] if self.is_optional else "string",
            "minLength": self.min,
            "maxLength": self.max,
        }

        if self.default_expr is not None or self.default is not None:
            schema["default"] = (
                self.default_expr.evaluate(context)
                if self.default_expr is not None
                else self.default
            )

        pattern = self.regex_js or self.regex
        if pattern:
            schema["pattern"] = pattern

        if self.input_mode:
            schema["x-inputMode"] = self.input_mode

        if self.autocomplete:
            schema["x-autoComplete"] = self.autocomplete

        format_str = _get_format_str(self.format)
        if format_str:
            schema["format"] = format_str

        return schema

    def get_validators(
        self, context: TemplateContext
    ) -> Iterator[Callable[[Any], Any]]:
        yield self.validate_type
        yield self._strip
        yield self._coerce_none
        yield self._validate_length
        if self.regex:
            yield self._validate_regex
        if self.format:
            yield from _get_format_validators(self.format)
        yield self.validate_type  # call again in case the value was coerced to None

    def _strip(self, value: str | None) -> str | None:
        return value.strip() if value else value

    def _coerce_none(self, value: str | None) -> str | None:
        return value if value else None

    def _validate_length(self, value: str | None) -> str | None:
        if value is None:
            return None
        if self.min and len(value) < self.min:
            raise ValueError(f"Must be at least {self.min} characters")
        if len(value) > self.max:
            raise ValueError(f"Must be at most {self.max} characters")
        return value

    def _validate_regex(self, value: str | None) -> str | None:
        assert self.regex
        if value is not None and not re.match(self.regex, value):
            raise ValueError("Invalid value")
        return value


def make_text_field_template(v: Mapping[str, Any], c: Converter) -> TextFieldTemplate:
    """Structure a text field template."""
    return c.structure(v, TextFieldTemplate)


def _get_format_str(format: str | None) -> str | None:
    if format == TextFormatType.email:
        return "email"
    else:
        return None


def _get_format_validators(
    type: str | None,
) -> Iterator[Callable[[Any], str | None]]:
    if type == TextFormatType.email:
        yield _validate_email
        yield _validate_email_domain


def _validate_email(value: str | None) -> str | None:
    if value is None:
        return None

    try:
        validate_email(value, check_deliverability=False)
        return value
    except EmailNotValidError as e:
        raise ValueError("Invalid email") from e


_psl = PublicSuffixList()


def _validate_email_domain(value: str | None) -> str | None:
    """Validate that an email's domain exists.

    Warning:
        This is not a good idea and generally shouldn't be done, but some services
        (e.g. Square) perform this kind of validation and will reject requests
        involving emails with unknown public suffixes. By then, the user is already
        many steps past when they entered their email, and it would be bad UX to make
        them start over to correct it.
    """
    if value is None:
        return None
    _, _, domain = value.rpartition("@")
    suffix = _psl.publicsuffix(domain, accept_unknown=False)
    if suffix is None:
        raise ValueError("Invalid email")
    return value
