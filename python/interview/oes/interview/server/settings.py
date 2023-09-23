"""Settings module."""
from collections.abc import Sequence
from pathlib import Path
from typing import Union, cast

from attr.converters import pipe
from attrs import define, field
from oes.interview.config.file import load_config_file
from oes.util import urlsafe_b64decode
from typed_settings import EnvLoader, FileLoader, Secret
from typed_settings import load_settings as ts_load_settings
from typed_settings.types import OptionList, SettingsClass, SettingsDict


def _base64_decode(v: object) -> object:
    return urlsafe_b64decode(v) if isinstance(v, str) else v


def _make_secret(v: object) -> object:
    return v if isinstance(v, Secret) else Secret(v)


@define
class Settings:
    """Server settings."""

    encryption_key: Secret[bytes] = field(
        default=Secret(b""),
        converter=lambda v: pipe(_base64_decode, _make_secret)(v),
    )
    """The encryption key."""

    api_key: Secret[str] = field(
        default=Secret(""),
        converter=_make_secret,
    )
    """The API key."""

    interview_config: Path = field(default=Path("interviews.yml"))
    """Path to the interview config file."""

    allowed_origins: Union[Sequence[str]] = []
    """The CORS allowed origins."""


def _yaml_format(
    path: Path, settings_cls: SettingsClass, options: OptionList
) -> SettingsDict:
    return cast(SettingsDict, load_config_file(path))


def load_settings(config_path: Path) -> Settings:
    """Load the settings."""
    settings: Settings = ts_load_settings(
        Settings,
        (
            FileLoader(
                formats={"*.yml": _yaml_format},
                files=(config_path,),
            ),
            EnvLoader("OES_INTERVIEW_"),
        ),
    )

    if not settings.api_key or not settings.encryption_key:
        raise ValueError("encryption_key and api_key must be set")
    return settings
