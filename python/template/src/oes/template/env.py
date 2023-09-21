"""Functions for working with the Jinja2 environment."""
from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import ContextManager

import jinja2
from jinja2.sandbox import ImmutableSandboxedEnvironment

from oes.template.functions import age_filter, date_filter

_default_jinja2_env = ImmutableSandboxedEnvironment()
"""The default Jinja2 environment."""

_default_jinja2_env.filters["date"] = date_filter
_default_jinja2_env.filters["age"] = age_filter

_jinja2_env_context: ContextVar[jinja2.Environment] = ContextVar(
    "jinja2_env_context", default=_default_jinja2_env
)
"""The context var for the configured Jinja2 environment."""


def get_jinja2_env() -> jinja2.Environment:
    """Get the currently configured Jinja2 environment."""
    return _jinja2_env_context.get()


def set_jinja2_env(env: jinja2.Environment) -> ContextManager[jinja2.Environment]:
    """Set the Jinja2 environment.

    Args:
        env: The environment.

    Returns:
        A context manager to automatically reset the environment value.
    """

    token = _jinja2_env_context.set(env)

    @contextmanager
    def manager() -> Generator[jinja2.Environment, None, None]:
        try:
            yield env
        finally:
            _jinja2_env_context.reset(token)

    return manager()
