"""Custom undefined class module."""

import jinja2
from jinja2.sandbox import ImmutableSandboxedEnvironment
from oes.interview.variables.locator import Index, UndefinedError, Variable
from oes.interview.variables.proxy import MappingProxy, SequenceProxy, _make_proxy


class Undefined(jinja2.StrictUndefined):
    """Custom :class:`jinja2.Undefined` instance to raise a custom UndefinedError."""

    # def __getstate__(self) -> dict:
    #     return {
    #         "_undefined_obj": self._undefined_obj,
    #         "_undefined_name": self._undefined_name
    #     }
    #
    # def __setstate__(self, state: dict):
    #     self._undefined_obj = state["_undefined_obj"]
    #     self._undefined_name = state["_undefined_name"]

    def _fail_with_undefined_error(self, *args, **kwargs):
        obj = self._undefined_obj
        name = self._undefined_name

        if isinstance(obj, (MappingProxy, SequenceProxy)):
            expr = Index(obj._expression, name)
        else:
            expr = Variable(name)

        raise UndefinedError(expr)


# Override _fail_with_undefined_error
for attr in dir(Undefined):
    attr_val = getattr(Undefined, attr)
    if attr_val is jinja2.Undefined._fail_with_undefined_error:
        setattr(Undefined, attr, Undefined._fail_with_undefined_error)


class Context(jinja2.environment.Context):
    """Jinja2 context that returns proxy instances when appropriate."""

    def resolve_or_missing(self, key: str):
        val = super().resolve_or_missing(key)
        return _make_proxy(Variable(key), val)


class Environment(ImmutableSandboxedEnvironment):
    """Jinja2 environment using the custom :class:`Context` class."""

    context_class = Context
