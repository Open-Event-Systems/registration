"""Field module."""
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Sequence
from typing import Any, Generic, Mapping, Optional, Type, TypeVar, cast

import attr
from attrs import Attribute, frozen, validators
from cattrs import Converter
from oes.interview.input.types import Field, JSONSchema, Option
from oes.interview.variables.locator import Locator
from oes.template import Context, Template


@frozen(kw_only=True)
class FieldBase(Field, ABC):
    """The field implementation base class."""

    type: str
    """The field type."""

    set: Optional[Locator] = None
    """The variable to store the value in."""

    optional: bool = False
    """Whether the field is optional."""

    label: Optional[Template] = None
    """The field label."""

    default: Any = None
    """A default value.

    Only used for displaying in the client, not used for parsing.
    """

    error_messages: Optional[Mapping[str, str]] = None
    """Mapping to override error messages."""

    @property
    @abstractmethod
    def value_type(self) -> Type:
        """The Python type of the value of this field."""
        ...

    @property
    def optional_type(self) -> object:
        """The :attr:`value_type` according to the :attr:`optional` value."""
        if self.optional:
            return Optional[self.value_type]
        else:
            return self.value_type

    @property
    def field_info(self) -> Any:
        """An ``attrs`` field info object."""
        return attr.ib(
            type=self.optional_type,
            default=self.default,
            validator=self.validators,
        )

    def get_schema(self, context: Context, /) -> JSONSchema:
        schema = {
            "x-type": self.type,
        }

        if self.label is not None:
            schema["title"] = self.label.render(context)

        if self.default is not None:
            schema["default"] = self.default

        return schema

    @property
    def validators(self) -> list[Callable[[Any, Attribute, Any], Any]]:
        """Validators to add to the field."""
        v: list[Callable[[Any, Attribute, Any], Any]] = []

        if self.optional:
            v.append(validators.optional(validators.instance_of((self.value_type,))))
        else:
            v.append(validators.instance_of((self.value_type,)))

        return v


_B = TypeVar("_B", bound=Option)
_B_co = TypeVar("_B_co", covariant=True, bound=Option)


@frozen(kw_only=True)
class OptionsFieldBase(Field, Generic[_B_co], ABC):
    """Base options field."""

    type: str
    """The field type."""

    set: Optional[Locator] = None
    """The variable to store the value in."""

    label: Optional[Template] = None
    """The field label."""

    error_messages: Optional[Mapping[str, str]] = None
    """Mapping to override error messages."""

    @property
    @abstractmethod
    def options(self) -> Sequence[_B_co]:
        """The options."""
        ...

    @property
    def options_by_id(self) -> Mapping[str, _B_co]:
        """A mapping of options by ID."""
        return {
            (opt.id if opt.id is not None else str(num)): opt
            for num, opt in enumerate(self.options, start=1)
        }

    def convert_options(self, ids: Iterable[str]) -> tuple[Any, ...]:
        """Convert an iterable of option IDs to a list of values."""
        if isinstance(ids, str) or not all(isinstance(id, str) for id in ids):
            raise ValueError(f"Invalid options: {ids}")

        # remove duplicates
        id_set = {id: True for id in ids}

        return tuple(self.convert_option(id) for id in id_set)

    def convert_option(self, id: Optional[str]) -> Any:
        """Convert an option ID to its value."""
        if id is None:
            return None
        elif not isinstance(id, str):
            raise ValueError(f"Invalid option: {id}")
        else:
            try:
                opt = self.options_by_id[id]
            except KeyError as e:
                raise ValueError(f"Invalid option: {id}") from e

            return opt.value

    def get_schema(self, context: Context, /) -> JSONSchema:
        schema = {
            "x-type": self.type,
        }

        if self.label is not None:
            schema["title"] = self.label.render(context)

        return schema


def structure_field(converter: Converter, v: object, t: object) -> Field:
    """Structure a field definition from the config."""
    if isinstance(v, Mapping) and "type" in v:
        typ = v["type"]
        cls = _get_class_for_field_type(typ)
        return converter.structure(v, cls)
    else:
        raise ValueError(f"Invalid field: {v}")


def _get_class_for_field_type(typ: str) -> Type[Field]:
    # eventually make this support entry points
    from oes.interview.input.field_types.button import Button
    from oes.interview.input.field_types.date import DateField
    from oes.interview.input.field_types.number import NumberField
    from oes.interview.input.field_types.select import SelectField
    from oes.interview.input.field_types.text import TextField

    types = {
        "text": TextField,
        "number": NumberField,
        "date": DateField,
        "select": SelectField,
        "button": Button,
    }

    try:
        return cast(Type[Field], types[typ])
    except KeyError as e:
        raise ValueError(f"Unknown field type: {type}") from e
