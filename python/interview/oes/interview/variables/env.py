"""Jinja2 env."""
from oes.interview.variables.undefined import Environment, Undefined
from oes.template import age_filter, date_filter

jinja2_env = Environment(undefined=Undefined)
"""The Jinja2 environment."""

jinja2_env.filters["age"] = age_filter
jinja2_env.filters["date"] = date_filter
