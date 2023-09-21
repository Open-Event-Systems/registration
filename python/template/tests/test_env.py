import jinja2

from oes.template.env import _default_jinja2_env, get_jinja2_env, set_jinja2_env

env2 = jinja2.Environment()


def test_set_env():
    assert get_jinja2_env() is _default_jinja2_env
    with set_jinja2_env(env2) as set_env:
        assert env2 is set_env
        assert get_jinja2_env() is env2
    assert get_jinja2_env() is _default_jinja2_env
