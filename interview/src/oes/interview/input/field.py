"""Field module."""
import importlib
import itertools
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Sequence
from typing import Any, Generic, Mapping, Optional, Type, TypeVar

import attr
import importlib_metadata
from attrs import Attribute, frozen, validators
from cattrs import Converter
from oes.interview.input.types import Field, FieldWithOptions, FieldWithType, Option
from oes.interview.variables.locator import Locator
from oes.template import Template


@frozen(kw_only=True)
class BaseField(FieldWithType, ABC):
    """The field implementation base class."""

    set: Optional[Locator] = None

    optional: bool = False
    """Whether the field is optional."""

    label: Optional[Template] = None
    """The field label."""

    error_messages: Optional[Mapping[str, str]] = None
    """Mapping to override error messages."""

    @property
    @abstractmethod
    def default(self) -> Optional[object]:
        """A default value.

        Only used for displaying in the client, not used for parsing.
        """
        ...

    @property
    @abstractmethod
    def value_type(self) -> type:
        """The type of the value of this field."""
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
        """An attrs field info object."""

        return attr.ib(
            type=self.optional_type,
            default=self.default,
            validator=self.validators,
        )

    @property
    def validators(self) -> list[Callable[[Any, Attribute, Any], Any]]:
        """Validators to add to the field."""
        v: list[Callable[[Any, Attribute, Any], Any]] = [
            validate_optional(self.optional),
            validators.optional([validators.instance_of((self.value_type,))]),
        ]
        return v


_B = TypeVar("_B", bound=Option)
_B_co = TypeVar("_B_co", covariant=True, bound=Option)


class BaseOptionsField(FieldWithOptions, Generic[_B_co], ABC):
    """Base options field."""

    @property
    @abstractmethod
    def options(self) -> Sequence[_B_co]:
        """The options."""
        ...

    @property
    def options_by_id(self) -> Mapping[str, _B_co]:
        """A mapping of options by ID."""

        return {
            (opt.id or str(num)): opt for num, opt in enumerate(self.options, start=1)
        }

    def convert_options(self, __ids: Iterable[str]) -> list[Any]:
        """Convert an iterable of option IDs to a list of values."""
        if not all(isinstance(id, str) for id in __ids):
            raise ValueError(f"Invalid options: {__ids}")
        return [self.convert_option(id) for id in __ids]

    def convert_option(self, __id: Optional[str]) -> Any:
        """Convert an option ID to its value."""
        if __id is not None:
            try:
                opt = self.options_by_id[__id]
            except KeyError as e:
                raise ValueError(f"Invalid option: {__id}") from e

            return opt.value
        else:
            return None


def _button_id_gen(
    i: BaseOptionsField[_B], a: Attribute, v: object
) -> Mapping[str, _B]:
    ct = itertools.count(1)
    map = {}

    for opt in i.options:
        num = next(ct)
        if opt.id:
            map[opt.id] = opt
        else:
            map[str(num)] = opt

    return map


def validate_optional(
    optional: Optional[bool] = None,
) -> Callable[[object, Attribute, object], None]:
    """Get a validator to check for null values."""

    def validate(i: object, a: Attribute, v: object):
        if v is None and not optional:
            raise ValueError("A value is required")

    return validate


def structure_field(converter: Converter, v: object, t: object) -> Field:
    """Structure a field definition from the config."""
    if isinstance(v, Mapping) and "type" in v:
        typ = v["type"]
        cls = get_class_for_field_type(typ)
        return converter.structure(v, cls)
    else:
        raise ValueError(f"Invalid field: {v}")


def get_class_for_field_type(field_type: str) -> Type[Field]:
    path = _get_dotted_name_for_field_type(field_type)
    return _import_type(path)


def _get_dotted_name_for_field_type(field_type: str) -> str:
    eps = importlib_metadata.entry_points(group="oes.interview.field")
    for ep in eps:
        if ep.name == field_type:
            return ep.value
    else:
        raise LookupError(f"Unknown field type: {field_type}")


def _import_type(path: str) -> Any:
    mod_name, _, name = path.partition(":")
    mod = importlib.import_module(mod_name)
    parts = name.split(".")
    cur = mod
    for part in parts:
        cur = getattr(cur, part)

    return cur
