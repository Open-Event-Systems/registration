"""Field module."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Sequence
from typing import Any, Generic, Mapping, Optional, Type, TypeVar, cast

import attr
from attrs import Attribute, frozen, validators
from cattrs import Converter
from oes.interview.input.types import Field, FieldType, JSONSchema, Option
from oes.interview.logic import ValuePointer
from oes.template import Context, Expression, Template

_T_co = TypeVar("_T_co", covariant=True)


@frozen(kw_only=True)
class FieldImplBase(Generic[_T_co], ABC):
    """Field implementation base class."""

    @property
    @abstractmethod
    def type(self) -> Type[_T_co]:
        """The field value type."""
        ...

    set: ValuePointer | None = None
    """The variable to store the value in."""

    label: str | None = None
    """The field label."""

    default: Any = None
    """A default value.

    Only used for displaying in the client, not used for parsing.
    """

    optional: bool = False
    """Whether the field may be None."""

    @property
    @abstractmethod
    def schema(self) -> dict[str, Any]:
        schema = {}

        if self.label:
            schema["title"] = self.label

        if self.default is not None:
            schema["default"] = self.default

        return schema

    def __call__(self, value: object, /) -> _T_co | None:
        for validator in self.validators:
            value = validator(value)
        return cast(_T_co, value)

    @property
    @abstractmethod
    def validators(self) -> Iterable[Callable[[Any], _T_co | None]]:
        """Validators to run on the field."""
        ...

    def _validate_type(self, value: Any) -> _T_co | None:
        if value is None or isinstance(value, self.type):
            return value
        else:
            raise ValueError("Invalid value")

    def _validate_optional(self, value: _T_co | None) -> _T_co | None:
        if value is None and not self.optional:
            raise ValueError("Required")
        return value


@frozen(kw_only=True)
class FieldBase(ABC):
    """The field implementation base class."""

    type: FieldType
    """The field type."""

    set: ValuePointer | None = None
    """The variable to store the value in."""

    optional: bool = False
    """Whether the field is optional."""

    label: Template | None = None
    """The field label."""

    default: Any = None
    """A default value.

    Only used for displaying in the client, not used for parsing.
    """

    default_expr: Expression | None = None
    """An expression of the default value."""

    @property
    @abstractmethod
    def value_type(self) -> Type:
        """The Python type of the value of this field."""
        ...

    @property
    def optional_type(self) -> object:
        """The optional version of the :attr:`value_type`."""
        if self.optional:
            return Optional[self.value_type]
        else:
            return self.value_type

    def get_field_info(self, context: Context) -> Any:
        """An ``attrs`` field info object."""
        return attr.ib(
            type=self.optional_type,
            validator=self.validators,
        )

    def get_schema(self, context: Context) -> JSONSchema:
        schema: dict[str, Any] = {
            "x-type": self.type,
        }

        if self.label is not None:
            schema["title"] = self.label.render(context)

        if self.default_expr is not None:
            schema["default"] = self.default_expr.evaluate(context)
        elif self.default is not None:
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


_Opt_co = TypeVar("_Opt_co", covariant=True, bound=Option)


@frozen(kw_only=True)
class OptionsFieldBase(Generic[_Opt_co], ABC):
    """Base options field."""

    type: FieldType
    """The field type."""

    set: ValuePointer | None = None
    """The variable to store the value in."""

    label: Template | None = None
    """The field label."""

    error_messages: Mapping[str, str] | None = None
    """Mapping to override error messages."""

    options: Sequence[_Opt_co] = ()
    """The options."""

    @property
    def options_by_id(self) -> Mapping[str, _Opt_co]:
        """A mapping of options by ID."""
        return {
            (opt.id if opt.id is not None else str(num)): opt
            for num, opt in enumerate(self.options, start=1)
        }

    def convert_options(self, ids: Iterable[str], context: Context) -> tuple[Any, ...]:
        """Convert an iterable of option IDs to a list of values."""
        if isinstance(ids, str) or not all(isinstance(id, str) for id in ids):
            raise ValueError(f"Invalid options: {ids}")

        # remove duplicates
        id_set = {id: True for id in ids}

        return tuple(self.convert_option(id, context) for id in id_set)

    def convert_option(self, id: str | None, context: Context) -> Any:
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

            return opt.value_expr.evaluate(context) if opt.value_expr else opt.value

    def get_schema(self, context: Context) -> JSONSchema:
        schema: dict[str, Any] = {
            "x-type": self.type,
        }

        if self.label is not None:
            schema["title"] = self.label.render(context)

        return schema


def make_field_structure_fn(converter: Converter) -> Callable[[Any, Any], Field]:
    """Get a function to structure a field definition."""

    def structure(v: Any, t: Any) -> Field:
        if isinstance(v, Mapping) and "type" in v:
            typ = v["type"]
            cls = _get_class_for_field_type(typ)
            return converter.structure(v, cls)
        else:
            raise ValueError(f"Invalid field: {v}")

    return structure


def _get_class_for_field_type(typ: str) -> Type[Field]:
    # eventually make this support entry points
    from oes.interview.input.field_types.button import Button
    from oes.interview.input.field_types.date import DateField
    from oes.interview.input.field_types.number import NumberField
    from oes.interview.input.field_types.select import SelectField
    from oes.interview.input.field_types.text import TextField

    types: dict[str, Type[Field]] = {
        "text": TextField,
        "number": NumberField,
        "date": DateField,
        "select": SelectField,
        "button": Button,
    }

    try:
        return types[typ]
    except KeyError as e:
        raise ValueError(f"Unknown field type: {type}") from e
