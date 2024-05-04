"""Undefined class module."""

from typing import Any, Type, cast

import jinja2
from jinja2.runtime import Context as Jinja2Context
from jinja2.sandbox import ImmutableSandboxedEnvironment
from jinja2.utils import missing
from oes.interview.logic.pointer import IndexAccess, Name, PropertyAccess, ValuePointer
from oes.interview.logic.proxy import ArrayProxy, ObjectProxy, make_proxy


class UndefinedError(jinja2.exceptions.UndefinedError):
    """Custom :class:`jinja2.exceptions.UndefinedError`."""

    _pointer: ValuePointer | None

    @property
    def pointer(self) -> ValuePointer | None:
        """A pointer to the undefined value."""
        return self._pointer

    def __init__(
        self,
        message: str | None = None,
        *,
        _pointer: ValuePointer | None = None,
    ):
        super().__init__(message)
        self._pointer = _pointer


class Undefined(jinja2.StrictUndefined):
    """Custom :class:`jinja2.Undefined` implementation."""

    _pointer: ValuePointer | None

    def __init__(
        self,
        hint: str | None = None,
        obj: Any = missing,
        name: str | None = None,
        exc: Type[jinja2.exceptions.TemplateRuntimeError] = UndefinedError,
    ):
        super().__init__(hint, obj, name, exc)

        if name is None:
            self._pointer = None
        elif isinstance(obj, ObjectProxy):
            self._pointer = PropertyAccess(obj._pointer, name)
        elif isinstance(obj, ArrayProxy):
            self._pointer = IndexAccess(obj._pointer, cast(int, name))
        else:
            self._pointer = Name(name)

    def _fail_with_undefined_error(self, *args, **kwargs):
        raise UndefinedError(self._undefined_message, _pointer=self._pointer)

    __add__ = __radd__ = __sub__ = __rsub__ = _fail_with_undefined_error
    __mul__ = __rmul__ = __div__ = __rdiv__ = _fail_with_undefined_error
    __truediv__ = __rtruediv__ = _fail_with_undefined_error
    __floordiv__ = __rfloordiv__ = _fail_with_undefined_error
    __mod__ = __rmod__ = _fail_with_undefined_error
    __pos__ = __neg__ = _fail_with_undefined_error
    __call__ = __getitem__ = _fail_with_undefined_error
    __lt__ = __le__ = __gt__ = __ge__ = _fail_with_undefined_error
    __int__ = __float__ = __complex__ = _fail_with_undefined_error
    __pow__ = __rpow__ = _fail_with_undefined_error
    __iter__ = __str__ = __len__ = _fail_with_undefined_error
    __eq__ = __ne__ = __bool__ = __hash__ = _fail_with_undefined_error
    __contains__ = _fail_with_undefined_error


class ProxyContext(Jinja2Context):
    """Custom :class:`jinja2.environment.Context` to wrap values in a proxy.."""

    def resolve_or_missing(self, key: str) -> Any:
        return make_proxy(Name(key), super().resolve_or_missing(key))


class ProxyContextEnvironment(ImmutableSandboxedEnvironment):
    """Custom :class:`jinja2.Environment` to use the custom :class:`ProxyContext`."""

    context_class = ProxyContext
