"""Jinja2 environment."""

from oes.interview.logic.undefined import ProxyContextEnvironment, Undefined
from oes.utils.template import (
    template_filter_date,
    template_filter_datetime,
    template_fn_get_now,
)

default_jinja2_env = ProxyContextEnvironment(undefined=Undefined)
"""The default :class:`jinja2.Environment` to use with interview logic."""

default_jinja2_env.globals["get_now"] = template_fn_get_now
default_jinja2_env.filters["datetime"] = template_filter_datetime
default_jinja2_env.filters["date"] = template_filter_date
