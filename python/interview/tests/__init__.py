# flake8: noqa
import pytest

try:
    import importlib_metadata
    import jinja2
    import pyparsing
    import ruamel.yaml
except ImportError:
    pytest.skip(
        "Install the `advanced` extra to run these tests",
        allow_module_level=True,
    )
