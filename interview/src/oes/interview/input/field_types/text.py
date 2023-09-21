"""Text field type."""
from typing import Any, Literal, Mapping, Optional

import attr
from attrs import Attribute, converters, frozen, validators
from email_validator import EmailNotValidError, validate_email
from oes.interview.input.field import BaseField
from oes.interview.input.types import Context
from publicsuffixlist import PublicSuffixList

DEFAULT_MAX_LEN = 300
"""The default string max length."""


@frozen(kw_only=True)
class TextField(BaseField):
    """A text field."""

    type: Literal["text"] = "text"
    default: Optional[str] = None

    format: Optional[str] = None
    """The format."""

    min: int = 0
    """The minimum length."""

    max: int = DEFAULT_MAX_LEN
    """The maximum length."""

    regex: Optional[str] = None
    """A regex that the value must match."""

    regex_js: Optional[str] = None
    """A JS-compatible regex used for validation at the client side."""

    input_mode: Optional[str] = None
    """The HTML input mode for this field."""

    autocomplete: Optional[str] = None
    """The autocomplete type for this field's input."""

    @property
    def value_type(self) -> object:
        return str

    @property
    def field_info(self) -> Any:
        validators_ = []

        if self.regex is not None:
            validators_.append(validators.matches_re(self.regex))

        if self.format == "email":
            validators_.extend((_validate_email, _validate_email_domain))

        return attr.ib(
            type=self.optional_type,
            converter=converters.pipe(
                _strip_strings,
                _coerce_null,
            ),
            validator=[
                *self.validators,
                validators.optional(
                    [
                        validators.min_len(self.min),
                        validators.max_len(self.max),
                        *validators_,
                    ]
                ),
            ],
        )

    def get_schema(self, context: Context) -> Mapping[str, object]:
        schema = {
            "type": "string",
            "x-type": "text",
            "minLength": self.min,
            "maxLength": self.max,
            "nullable": self.optional,
        }

        if self.format is not None:
            schema["format"] = self.format

        if self.label:
            schema["title"] = self.label.render(context)

        if self.default:
            schema["default"] = self.default

        re_val = self.regex_js or self.regex
        if re_val:
            schema["pattern"] = re_val

        return schema


def _strip_strings(v):
    return v.strip() if isinstance(v, str) else v


def _coerce_null(v):
    return v if v else None


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
