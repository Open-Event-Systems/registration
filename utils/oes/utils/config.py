"""Config file loading."""

from collections.abc import Iterable
from pathlib import Path

import typed_settings as ts
from ruamel.yaml import YAML
from typed_settings.loaders import Loader

__all__ = [
    "get_loaders",
]

_yaml = YAML(typ="safe")


def _load_yaml(path, settings_cls, options):
    with open(path) as f:
        doc = _yaml.load(f)
    return doc


def get_loaders(
    prefix: str, config_files: Iterable[str | Path] = ("config.yml",)
) -> list[Loader]:
    """Get the default settings loaders."""
    return [
        ts.EnvLoader(prefix),
        ts.FileLoader(
            {
                "*.yml": _load_yaml,
            },
            config_files,
            env_var="CONFIG_FILE",
        ),
    ]
