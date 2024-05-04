"""Jinja2 environment."""

from oes.interview.logic.undefined import ProxyContextEnvironment, Undefined

default_jinja2_env = ProxyContextEnvironment(undefined=Undefined)
"""The default :class:`jinja2.Environment` to use with interview logic."""
