import pytest
from oes.registration.hook.models import HookConfig, HookConfigEntry, HookEvent
from oes.registration.serialization import get_config_converter
from ruamel.yaml import YAML

config_str = """
hooks:
  - on: registration.created
    url: http://localhost:8000/created
  - on: cart.price
    url: http://localhost:8000/price
"""

yaml = YAML(typ="safe")


@pytest.fixture
def hook_config():
    doc = yaml.load(config_str)
    return get_config_converter().structure(doc, HookConfig)


def test_build_hook_config(hook_config: HookConfig):
    expected = HookConfig(
        (
            HookConfigEntry(
                on=HookEvent.registration_created,
                url="http://localhost:8000/created",
            ),
            HookConfigEntry(
                on=HookEvent.cart_price,
                url="http://localhost:8000/price",
            ),
        )
    )

    assert list(hook_config) == list(expected.hooks)
    assert hook_config == expected


def test_get_hooks_by_event(hook_config: HookConfig):
    assert list(hook_config.get_by_event(HookEvent.cart_price)) == [
        HookConfigEntry(
            on=HookEvent.cart_price,
            url="http://localhost:8000/price",
        )
    ]
