"""Text field type."""

from collections.abc import Sequence
from enum import Enum
from typing import Any, Callable, Literal, Type

import attr
from attrs import Attribute, converters, frozen, validators
from email_validator import EmailNotValidError, validate_email
from oes.interview.input.field import FieldBase
from oes.interview.input.types import Context, FieldType, JSONSchema
from publicsuffixlist import PublicSuffixList

DEFAULT_MAX_LEN = 300
"""The default string max length."""


class TextFormatType(str, Enum):
    """Text format type IDs."""

    email = "email"


@frozen(kw_only=True)
class TextField(FieldBase):
    """A text field."""

    type: Literal[FieldType.text] = FieldType.text
    default: str | None = None

    format: TextFormatType | None = None
    """The format."""

    min: int = 0
    """The minimum length."""

    max: int = DEFAULT_MAX_LEN
    """The maximum length."""

    regex: str | None = None
    """A regex that the value must match."""

    regex_js: str | None = None
    """A JS-compatible regex used for validation at the client side."""

    input_mode: str | None = None
    """The HTML input mode for this field."""

    autocomplete: str | None = None
    """The autocomplete type for this field's input."""

    @property
    def value_type(self) -> Type:
        return str

    @property
    def validators(self) -> list[Callable[[Any, Attribute, Any], Any]]:
        validators_ = super().validators
        extra_validators: list[Callable[[Any, Attribute, Any], Any]] = [
            validators.min_len(self.min),
            validators.max_len(self.max),
        ]

        if self.regex is not None:
            extra_validators.append(validators.matches_re(self.regex))

        extra_validators.extend(_get_format_validators(self.format))

        return [*validators_, validators.optional(extra_validators)]

    def get_field_info(self, context: Context) -> Any:
        return attr.ib(
            type=self.optional_type,
            converter=converters.pipe(
                _strip_strings,
                _coerce_null,
            ),
            validator=self.validators,
        )

    def get_schema(self, context: Context) -> JSONSchema:
        schema = {
            **super().get_schema(context),
            "type": ["string", "null"] if self.optional else "string",
            "minLength": self.min,
            "maxLength": self.max,
        }

        if self.format is not None:
            schema["format"] = self.format

        re_val = self.regex_js or self.regex
        if re_val:
            schema["pattern"] = re_val

        if self.autocomplete:
            schema["x-autocomplete"] = self.autocomplete

        if self.input_mode:
            schema["x-input-mode"] = self.input_mode

        return schema


def _strip_strings(v):
    return v.strip() if isinstance(v, str) else v


def _coerce_null(v):
    return v if v else None


def _get_format_validators(
    type: TextFormatType | None,
) -> Sequence[Callable[[Any, Attribute, Any], Any]]:
    validators_ = []

    if type == TextFormatType.email:
        validators_.append(_validate_email)
        validators_.append(_validate_email_domain)

    return validators_


def _validate_email(i: Any, a: Attribute, v: Any):
    try:
        validate_email(v, check_deliverability=False)
    except EmailNotValidError as e:
        raise ValueError(f"Invalid email: {v}") from e


_psl = PublicSuffixList()


def _validate_email_domain(i: Any, a: Attribute, v: Any):
    """Validate that an email's domain exists.

    Warning:
        This is not a good idea and generally shouldn't be done, but some services
        (e.g. Square) perform this kind of validation and will reject requests
        involving emails with unknown public suffixes. By then, the user is already
        many steps past when they entered their email, and it would be bad UX to make
        them start over to correct it.
    """
    _, _, domain = v.rpartition("@")
    suffix = _psl.publicsuffix(domain, accept_unknown=False)
    if suffix is None:
        raise ValueError(f"Invalid email: {v}")
