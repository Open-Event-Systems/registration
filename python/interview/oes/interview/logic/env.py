"""Jinja2 environment."""
from oes.interview.logic.undefined import ProxyContextEnvironment, Undefined
from oes.template import age_filter, date_filter, now_func, today_func

default_jinja2_env = ProxyContextEnvironment(undefined=Undefined)
"""The default :class:`jinja2.Environment` to use with interview logic."""


default_jinja2_env.filters["date"] = date_filter
default_jinja2_env.filters["age"] = age_filter
default_jinja2_env.globals["get_today"] = today_func
default_jinja2_env.globals["get_now"] = now_func
