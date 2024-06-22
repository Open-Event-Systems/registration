"""Field template module."""

import functools
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any

from attrs import field, frozen
from oes.interview.input.field import Field, Validator
from oes.interview.logic.types import ValuePointer
from oes.utils.logic import WhenCondition, evaluate
from oes.utils.template import Expression, Template, TemplateContext


@frozen
class FieldTemplateBase(ABC):
    """Base class for field template types."""

    @property
    @abstractmethod
    def python_type(self) -> type: ...

    type: str
    set: ValuePointer | None = None
    label: str | Template | None = None

    @property
    @abstractmethod
    def is_optional(self) -> bool: ...

    def get_field(self, context: TemplateContext) -> Field:
        schema = self.get_schema(context)
        validators = self.get_validators(context)
        return Field(self.python_type, self.is_optional, schema, tuple(validators))

    def get_schema(self, context: TemplateContext) -> dict[str, Any]:
        schema = {
            "x-type": self.type,
        }

        if self.label:
            schema["title"] = (
                self.label.render(context)
                if isinstance(self.label, Template)
                else self.label
            )

        return schema

    def get_validators(self, context: TemplateContext) -> Iterable[Validator]:
        yield self.validate_type

    def validate_type(self, value):
        """Validate the value type."""
        if not (value is None and self.is_optional) and not isinstance(
            value, self.python_type
        ):
            raise ValueError("Invalid value")
        return value


@frozen
class SelectFieldOptionBase:
    """Base option for a select field type."""

    id: str | None = None
    label: str | Template | None = None
    value: Any = None
    value_expr: Expression | None = None
    default: bool = False
    when: WhenCondition = True

    def get_schema(self, id: str, context: TemplateContext) -> dict[str, Any]:
        label = (
            self.label.render(context)
            if isinstance(self.label, Template)
            else self.label
        )

        schema = {
            "const": id,
            "title": label,
        }
        return schema


@frozen
class SelectFieldTemplateBase(FieldTemplateBase, ABC):
    """Base class for select field template types."""

    options: Sequence[SelectFieldOptionBase] = field(
        default=(), converter=tuple[SelectFieldOptionBase, ...]
    )

    @property
    @abstractmethod
    def multi(self) -> bool: ...

    def get_options(
        self, context: TemplateContext
    ) -> Mapping[str, SelectFieldOptionBase]:
        with_idx = enumerate(self.options)
        return {
            self.get_option_id(idx, opt): opt
            for idx, opt in with_idx
            if evaluate(opt, context)
        }

    def get_option_id(self, index: int, option: SelectFieldOptionBase) -> str:
        if option.id:
            return option.id
        return f"{index + 1}"

    def get_schema(self, context: TemplateContext) -> dict[str, Any]:
        if self.multi:
            return self._get_multi_schema(context)
        else:
            return self._get_scalar_schema(context)

    def _get_multi_schema(self, context: TemplateContext) -> dict[str, Any]:
        opts = self.get_options(context)
        schema = {
            **super().get_schema(context),
            "type": "array",
            "items": {
                "oneOf": [
                    opt.get_schema(opt_id, context) for opt_id, opt in opts.items()
                ]
            },
            "uniqueItems": True,
        }
        return schema

    def _get_scalar_schema(self, context: TemplateContext) -> dict[str, Any]:
        opts = self.get_options(context)
        items = [opt.get_schema(opt_id, context) for opt_id, opt in opts.items()]
        if self.is_optional:
            items.append({"type": "null"})
        schema = {
            **super().get_schema(context),
            "type": ["string", "null"] if self.is_optional else "string",
            "oneOf": items,
        }
        return schema

    def get_validators(
        self, context: Mapping[str, Any]
    ) -> Iterable[Callable[[Any], Any]]:
        yield self.validate_type
        options = self.get_options(context)
        if self.multi:
            yield self.validate_unique
        yield functools.partial(self.validate_value, options, context)

    def validate_value(
        self,
        options: Mapping[str, SelectFieldOptionBase],
        context: TemplateContext,
        value: object,
    ) -> Any | None:
        if self.multi:
            converted = self.convert_options(options, context, value)
            return converted
        else:
            if value is None and self.is_optional:
                return value
            return self.convert_option(options, context, value)

    def convert_options(
        self,
        options: Mapping[str, SelectFieldOptionBase],
        context: TemplateContext,
        values: object,
    ) -> Sequence[Any]:
        if not isinstance(values, Sequence) or isinstance(values, str):
            raise ValueError("Invalid value")
        return tuple(self.convert_option(options, context, id) for id in values)

    def convert_option(
        self,
        options: Mapping[str, SelectFieldOptionBase],
        context: TemplateContext,
        id: object,
    ) -> Any:
        if not isinstance(id, str) or id not in options:
            raise ValueError("Invalid value")

        opt = options[id]
        val = (
            opt.value_expr.evaluate(context)
            if opt.value_expr is not None
            else opt.value
        )
        return val

    def validate_unique(self, values: Sequence[Any]) -> Sequence[Any]:
        ids_ = {k: None for k in values}  # preserve order
        return tuple(ids_)

    def validate_type(self, value: object) -> Any | None:
        if self.multi:
            if (
                not isinstance(value, Sequence)
                or isinstance(value, str)
                or any(not isinstance(v, str) for v in value)
            ):
                raise ValueError("Invalid value")
            return value
        else:
            if value is not None and not isinstance(value, str):
                raise ValueError("Invalid value")
            return value
